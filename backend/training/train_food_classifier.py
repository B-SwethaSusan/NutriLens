"""Fine-tunes an image classifier on Indian food photos, evaluates it on
HELD-OUT images it never trained on, calibrates its confidence, and exports
it to ONNX for the FastAPI backend.

Run on a machine with a GPU (e.g. your RTX 5060) — NOT in the deployed
backend. torch/torchvision stay out of backend/requirements.txt.

Usage:
    cd backend/training
    python train_food_classifier.py                       # recommended defaults
    python train_food_classifier.py --arch mobilenet_v3_small   # smaller/faster old architecture

What a run produces (all in backend/models/):
    food_classifier.onnx            the model the backend serves
    food_classifier_labels.json     class names, in the model's output order
    food_classifier_meta.json       calibration temperature + confidence thresholds
                                    (read by app/services/food_vision.py)
    food_classifier_report.json     held-out metrics: top-1/top-5, macro P/R/F1,
                                    per-class accuracy, confusions, ECE/Brier,
                                    reliability table, inference time
    food_classifier_checkpoint.pt   best PyTorch weights (for --export-only)

Datasets (--dataset, default "indian"):
    indian  -> 33 classes merged from two Hugging Face sources:
               rajistics/indian_food_images (20 classes, incl. pizza & burger;
               train + official test split) and
               SKSKCulinaryAI/Indian_Food_Images_Dataset (25 classes;
               train + validation split). Same dishes named differently
               across sources are merged via SOURCE_B_ALIASES.
    food101 -> ethz/food101, 101 international classes (train + validation).

Held-out evaluation: each source's own test/validation split is used —
never the training split. Any held-out image whose perceptual hash matches
a training image is dropped (the two sources overlap), so the reported
accuracy isn't inflated by near-duplicate photos. The held-out pool is then
split 50/50 (stratified, fixed seed) into:
    - a CALIBRATION half: picks the best epoch, fits temperature scaling,
      chooses confidence thresholds;
    - a TEST half: used ONLY for the final reported metrics.
"""

import argparse
import json
import random
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import ConcatDataset, DataLoader, Dataset, Subset
from torchvision import transforms
from torchvision.models import (
    EfficientNet_B0_Weights,
    MobileNet_V3_Small_Weights,
    efficientnet_b0,
    mobilenet_v3_small,
)

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # so `app.data...` imports work
sys.path.insert(0, str(Path(__file__).resolve().parent))      # so `eval_utils` imports work
from app.data.food101_nutrition import FOOD101_CLASSES  # noqa: E402
from app.data.indian_food_nutrition import INDIAN_FOOD_CLASSES  # noqa: E402
from eval_utils import (  # noqa: E402
    brier_score,
    choose_thresholds,
    classification_report,
    dhash,
    expected_calibration_error,
    fit_temperature,
    reliability_table,
    softmax,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "backend" / "training" / "data"
MODELS_DIR = REPO_ROOT / "backend" / "models"
IMAGE_SIZE = 224
MEAN, STD = [0.485, 0.456, 0.406], [0.229, 0.224, 0.225]

# SKSKCulinaryAI/Indian_Food_Images_Dataset labels its folders in Title Case
# with its own spelling. This maps each label onto INDIAN_FOOD_CLASSES.
SOURCE_B_ALIASES: dict[str, str] = {
    "Biryani": "biryani", "Butter chicken": "butter_chicken", "Chappati": "chapati",
    "Chicken tandoori": "tandoori_chicken", "Chole bhature": "chole_bhature", "Dal makhani": "dal_makhani",
    "Dhokla": "dhokla", "Dosa": "masala_dosa", "Gajar halwa": "gajar_halwa", "Ghevar": "ghevar",
    "Gulab jamun": "gulab_jamun", "Idli": "idli", "Jalebi": "jalebi", "Kadai_paneer": "kadai_paneer",
    "Kathi roll": "kaathi_rolls", "Kofta": "kofta", "Masala bhindi": "masala_bhindi", "Meduvada": "meduvada",
    "Pani puri": "paani_puri", "Pav bhaji": "pav_bhaji", "Poori": "poori", "Rasgulla": "rasgulla",
    "Samosa": "samosa", "Toor dal": "toor_dal", "Vada pav": "vada_pav",
}

# dataset -> classes + sources. Each source: (repo_id, alias_map, train_split, heldout_split)
DATASETS = {
    "indian": {
        "classes": INDIAN_FOOD_CLASSES,
        "sources": [
            ("rajistics/indian_food_images", {}, "train", "test"),
            ("SKSKCulinaryAI/Indian_Food_Images_Dataset", SOURCE_B_ALIASES, "train", "validation"),
        ],
    },
    "food101": {
        "classes": FOOD101_CLASSES,
        "sources": [("ethz/food101", {}, "train", "validation")],
    },
}


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def build_transforms():
    # Training augmentation: varied crops/flips/lighting/rotation, so the model
    # learns the dish rather than one camera angle or lighting condition.
    train_tf = transforms.Compose([
        transforms.RandomResizedCrop(IMAGE_SIZE, scale=(0.6, 1.0)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.02),
        transforms.ToTensor(),
        transforms.Normalize(MEAN, STD),
    ])
    # Evaluation: MUST match app/services/food_vision.py's _preprocess
    # (shorter side -> 256, centre-crop 224, ImageNet normalisation).
    eval_tf = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(IMAGE_SIZE),
        transforms.ToTensor(),
        transforms.Normalize(MEAN, STD),
    ])
    return train_tf, eval_tf


class HFFoodDataset(Dataset):
    """A Hugging Face image-classification split, relabelled onto our own
    class-list order (so ONNX output index i always means classes[i])."""

    def __init__(self, hf_dataset, hf_class_names, alias_map, classes, transform, label: str):
        name_to_idx = {name: i for i, name in enumerate(classes)}
        self.hf_to_ours: dict[int, int] = {}
        for hf_i, hf_name in enumerate(hf_class_names):
            mapped = alias_map.get(hf_name, hf_name)
            if mapped in name_to_idx:
                self.hf_to_ours[hf_i] = name_to_idx[mapped]
        if not self.hf_to_ours:
            raise RuntimeError(
                f"None of {label!r}'s class names matched the class list (after alias_map). "
                "Compare hf_dataset.features['label'].names against app/data/indian_food_nutrition.py."
            )
        keep = [i for i, lab in enumerate(hf_dataset["label"]) if lab in self.hf_to_ours]
        self.hf_dataset = hf_dataset.select(keep) if len(keep) < len(hf_dataset) else hf_dataset
        self.labels = [self.hf_to_ours[lab] for lab in self.hf_dataset["label"]]
        self.transform = transform

    def __len__(self):
        return len(self.hf_dataset)

    def raw_image(self, index: int):
        return self.hf_dataset[index]["image"].convert("RGB")

    def __getitem__(self, index: int):
        return self.transform(self.raw_image(index)), self.labels[index]


def load_split(sources, classes, transform, which: str) -> list[HFFoodDataset]:
    from datasets import load_dataset

    parts = []
    for repo_id, alias_map, train_split, heldout_split in sources:
        split = train_split if which == "train" else heldout_split
        print(f"  loading {repo_id} [{split}]")
        hf = load_dataset(repo_id, split=split, cache_dir=str(DATA_DIR))
        part = HFFoodDataset(hf, hf.features["label"].names, alias_map, classes, transform, f"{repo_id}:{split}")
        print(f"    kept {len(part)} images")
        parts.append(part)
    return parts


def remove_heldout_duplicates(train_parts, heldout_parts) -> list[Subset]:
    """Drop held-out images that are (near-)identical to any training image."""
    print("Checking held-out images for duplicates of training images (perceptual hash)...")
    t0 = time.time()
    train_hashes = set()
    for part in train_parts:
        for i in range(len(part)):
            train_hashes.add(dhash(part.raw_image(i)))
    cleaned, dropped = [], 0
    for part in heldout_parts:
        keep = []
        for i in range(len(part)):
            if dhash(part.raw_image(i)) in train_hashes:
                dropped += 1
            else:
                keep.append(i)
        cleaned.append(Subset(part, keep))
    print(f"  dropped {dropped} held-out images that duplicate training images ({time.time() - t0:.0f}s)")
    return cleaned


def subset_labels(subset: Subset) -> list[int]:
    return [subset.dataset.labels[i] for i in subset.indices]


def stratified_halves(heldout_parts: list[Subset], seed: int):
    """Split the held-out pool 50/50 per class into calibration and test."""
    flat = []  # (part_index, index_within_part, label)
    for p, part in enumerate(heldout_parts):
        for j, lab in zip(part.indices, subset_labels(part)):
            flat.append((p, j, lab))
    rng = random.Random(seed)
    by_class: dict[int, list] = {}
    for item in flat:
        by_class.setdefault(item[2], []).append(item)
    calib, test = [], []
    for items in by_class.values():
        rng.shuffle(items)
        half = len(items) // 2
        calib += items[:half]
        test += items[half:]

    def to_dataset(items):
        per_part: dict[int, list] = {}
        for p, j, _ in items:
            per_part.setdefault(p, []).append(j)
        return ConcatDataset([Subset(heldout_parts[p].dataset, js) for p, js in per_part.items()])

    return to_dataset(calib), to_dataset(test)


def build_model(num_classes: int, arch: str = "efficientnet_b0", freeze_backbone: bool = False) -> nn.Module:
    if arch == "efficientnet_b0":
        model = efficientnet_b0(weights=EfficientNet_B0_Weights.IMAGENET1K_V1)
    elif arch == "mobilenet_v3_small":
        model = mobilenet_v3_small(weights=MobileNet_V3_Small_Weights.IMAGENET1K_V1)
    else:
        raise ValueError(f"Unknown arch {arch!r}")
    for param in model.features.parameters():
        param.requires_grad = not freeze_backbone
    in_features = model.classifier[-1].in_features
    model.classifier[-1] = nn.Linear(in_features, num_classes)
    return model


def class_weights(labels: list[int], num_classes: int) -> torch.Tensor:
    """Inverse-frequency weights so classes with few training photos aren't
    drowned out by classes with many."""
    counts = np.bincount(labels, minlength=num_classes).astype(np.float64)
    present = counts > 0
    weights = np.zeros(num_classes)
    weights[present] = counts[present].sum() / (present.sum() * counts[present])
    # Normalise over present classes only — an absent class must not drag
    # every other class's weight down.
    weights[present] /= weights[present].mean()
    return torch.tensor(weights, dtype=torch.float32)


@torch.no_grad()
def collect_logits(model, loader, device):
    model.eval()
    all_logits, all_labels = [], []
    for images, labels in loader:
        all_logits.append(model(images.to(device)).float().cpu().numpy())
        all_labels.append(labels.numpy())
    return np.concatenate(all_logits), np.concatenate(all_labels)


def train(model, train_loader, calib_loader, device, args, weights):
    model.to(device)
    criterion = nn.CrossEntropyLoss(weight=weights.to(device), label_smoothing=0.1)
    if args.freeze_backbone_only:
        params = [{"params": model.classifier.parameters(), "lr": args.lr}]
    else:
        # Backbone adapts gently (1/10 LR); the new classifier head learns at full LR.
        params = [
            {"params": model.features.parameters(), "lr": args.lr * 0.1},
            {"params": model.classifier.parameters(), "lr": args.lr},
        ]
    optimizer = torch.optim.AdamW(params, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)

    best_acc, best_state, stale = -1.0, None, 0
    for epoch in range(args.epochs):
        model.train()
        running_loss, correct, total = 0.0, 0, 0
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * images.size(0)
            correct += (outputs.argmax(1) == labels).sum().item()
            total += images.size(0)
        scheduler.step()

        logits, y = collect_logits(model, calib_loader, device)
        val_acc = float((logits.argmax(1) == y).mean())
        print(f"Epoch {epoch + 1}/{args.epochs}  loss={running_loss / total:.4f}  "
              f"train_acc={correct / total:.3f}  heldout_calib_acc={val_acc:.3f}")
        if val_acc > best_acc:
            best_acc, stale = val_acc, 0
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
        else:
            stale += 1
            if stale >= args.patience:
                print(f"Early stopping: no held-out improvement for {args.patience} epochs.")
                break

    model.load_state_dict(best_state)
    print(f"Restored best epoch (held-out calibration accuracy {best_acc:.3f})")
    return best_acc


def export_onnx(model: nn.Module, classes: list[str], device) -> Path:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    model.eval()
    dummy = torch.randn(1, 3, IMAGE_SIZE, IMAGE_SIZE, device=device)
    onnx_path = MODELS_DIR / "food_classifier.onnx"
    # dynamo=False: the legacy exporter handles these CNNs fine and needs no extra packages.
    torch.onnx.export(
        model, dummy, onnx_path,
        input_names=["input"], output_names=["logits"],
        dynamic_axes={"input": {0: "batch"}, "logits": {0: "batch"}},
        opset_version=17, dynamo=False,
    )
    (MODELS_DIR / "food_classifier_labels.json").write_text(json.dumps(classes, indent=2))
    print(f"Exported model to {onnx_path}")
    return onnx_path


def onnx_latency_ms(onnx_path: Path) -> float | None:
    """Median single-image CPU inference time — what the deployed backend will see."""
    try:
        import onnxruntime as ort
    except ImportError:
        print("  (onnxruntime not installed — skipping latency measurement)")
        return None
    session = ort.InferenceSession(str(onnx_path), providers=["CPUExecutionProvider"])
    x = np.random.randn(1, 3, IMAGE_SIZE, IMAGE_SIZE).astype(np.float32)
    for _ in range(3):
        session.run(["logits"], {"input": x})
    times = []
    for _ in range(20):
        t0 = time.perf_counter()
        session.run(["logits"], {"input": x})
        times.append((time.perf_counter() - t0) * 1000)
    return round(float(np.median(times)), 1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=list(DATASETS), default="indian")
    parser.add_argument("--arch", choices=["efficientnet_b0", "mobilenet_v3_small"], default="efficientnet_b0",
                        help="efficientnet_b0 (default): more accurate. mobilenet_v3_small: the older, smaller model.")
    parser.add_argument("--epochs", type=int, default=15)
    parser.add_argument("--patience", type=int, default=4, help="Early-stop after this many epochs without held-out improvement.")
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--num-workers", type=int, default=4)
    parser.add_argument("--freeze-backbone-only", action="store_true",
                        help="Train only the classifier head (much faster, noticeably less accurate).")
    parser.add_argument("--skip-dedupe", action="store_true", help="Skip the duplicate check (faster, but metrics may be inflated).")
    parser.add_argument("--subset", type=int, default=0, help="Train on only the first N classes (quick demo). 0 = all.")
    parser.add_argument("--export-only", action="store_true",
                        help="Skip training; re-export food_classifier_checkpoint.pt (same --dataset/--arch/--subset as the run that made it).")
    args = parser.parse_args()

    set_seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    if device.type != "cuda":
        print("WARNING: no GPU detected by PyTorch. Training will be slow — check your CUDA/driver install.")

    config = DATASETS[args.dataset]
    classes = config["classes"][: args.subset] if args.subset else config["classes"]
    print(f"Dataset: {args.dataset} — {len(classes)} classes — architecture: {args.arch}")
    checkpoint_path = MODELS_DIR / "food_classifier_checkpoint.pt"
    model = build_model(len(classes), args.arch, args.freeze_backbone_only)

    if args.export_only:
        model.load_state_dict(torch.load(checkpoint_path, map_location=device))
        model.to(device)
        export_onnx(model, classes, device)
        print("NOTE: --export-only does not refresh food_classifier_meta.json / report.json.")
        return

    train_tf, eval_tf = build_transforms()
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print("Loading training splits...")
    train_parts = load_split(config["sources"], classes, train_tf, "train")
    print("Loading held-out splits (never used for training)...")
    heldout_parts = load_split(config["sources"], classes, eval_tf, "heldout")
    if args.skip_dedupe:
        heldout_clean = [Subset(p, list(range(len(p)))) for p in heldout_parts]
    else:
        heldout_clean = remove_heldout_duplicates(train_parts, heldout_parts)
    calib_set, test_set = stratified_halves(heldout_clean, args.seed)

    train_set = ConcatDataset(train_parts)
    train_labels = [lab for part in train_parts for lab in part.labels]
    counts = np.bincount(train_labels, minlength=len(classes))
    print(f"Training images: {len(train_set)} | held-out calibration: {len(calib_set)} | held-out test: {len(test_set)}")
    print("Training images per class: " + ", ".join(f"{c}={n}" for c, n in zip(classes, counts)))
    missing = [c for c, n in zip(classes, counts) if n == 0]
    if missing:
        print(f"WARNING: no training images for: {missing}")

    loader_kw = dict(batch_size=args.batch_size, num_workers=args.num_workers, pin_memory=device.type == "cuda")
    train_loader = DataLoader(train_set, shuffle=True, **loader_kw)
    calib_loader = DataLoader(calib_set, shuffle=False, **loader_kw)
    test_loader = DataLoader(test_set, shuffle=False, **loader_kw)

    train(model, train_loader, calib_loader, device, args, class_weights(train_labels, len(classes)))
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), checkpoint_path)
    print(f"Saved best checkpoint to {checkpoint_path}")

    # --- Calibration (on the calibration half only) ---
    calib_logits, calib_y = collect_logits(model, calib_loader, device)
    temperature = fit_temperature(calib_logits, calib_y)
    thresholds = choose_thresholds(softmax(calib_logits, temperature), calib_y)

    # --- Final metrics (on the untouched test half only) ---
    test_logits, test_y = collect_logits(model, test_loader, device)
    raw_probs, cal_probs = softmax(test_logits), softmax(test_logits, temperature)
    report = classification_report(cal_probs, test_y, classes)
    report["calibration"] = {
        "temperature": round(temperature, 3),
        "ece_before": round(expected_calibration_error(raw_probs, test_y), 4),
        "ece_after": round(expected_calibration_error(cal_probs, test_y), 4),
        "brier_before": round(brier_score(raw_probs, test_y), 4),
        "brier_after": round(brier_score(cal_probs, test_y), 4),
        "reliability_table": reliability_table(cal_probs, test_y),
    }
    report["thresholds"] = thresholds
    report["setup"] = {
        "arch": args.arch, "dataset": args.dataset, "num_classes": len(classes),
        "train_images": len(train_set), "calibration_images": len(calib_set), "test_images": len(test_set),
        "train_images_per_class": {c: int(n) for c, n in zip(classes, counts)},
        "sources": [s[0] for s in config["sources"]], "seed": args.seed,
    }

    onnx_path = export_onnx(model, classes, device)
    report["inference_ms_cpu_median"] = onnx_latency_ms(onnx_path)
    (MODELS_DIR / "food_classifier_report.json").write_text(json.dumps(report, indent=2))
    (MODELS_DIR / "food_classifier_meta.json").write_text(json.dumps({
        "arch": args.arch,
        "temperature": round(temperature, 3),
        "reject_below": thresholds["reject_below"],
        "high_at": thresholds["high_at"],
        "heldout_top1_accuracy": report["top1_accuracy"],
        "heldout_top5_accuracy": report["top5_accuracy"],
        "trained_at": time.strftime("%Y-%m-%d %H:%M"),
    }, indent=2))

    print("\n================ HELD-OUT TEST RESULTS ================")
    print(f"Images: {report['num_images']} across {report['num_classes_evaluated']} classes")
    print(f"Top-1 accuracy: {report['top1_accuracy']:.3f}   Top-5: {report['top5_accuracy']:.3f}   Macro F1: {report['macro_f1']:.3f}")
    c = report["calibration"]
    print(f"Calibration: T={c['temperature']}  ECE {c['ece_before']:.3f} -> {c['ece_after']:.3f}  "
          f"Brier {c['brier_before']:.3f} -> {c['brier_after']:.3f}")
    print(f"Thresholds: reject below {thresholds['reject_below']}, high confidence at {thresholds['high_at']}")
    print(f"CPU inference (median): {report['inference_ms_cpu_median']} ms/image")
    print("Weakest classes:")
    for name, m in sorted(report["per_class"].items(), key=lambda kv: kv[1]["accuracy"])[:8]:
        print(f"  {name:18s} {m['accuracy']:.2f}  (n={m['support']})")
    for focus in ("biryani", "pizza", "burger"):
        if focus in report["per_class"]:
            print(f"  -> {focus}: {report['per_class'][focus]['accuracy']:.2f} (n={report['per_class'][focus]['support']})")
    print("Full report: backend/models/food_classifier_report.json")


if __name__ == "__main__":
    main()
