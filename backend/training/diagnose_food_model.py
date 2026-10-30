"""Diagnostic: compares the raw PyTorch checkpoint's prediction against the
exported ONNX model's prediction, on the SAME real photo, using the SAME
preprocessing the live backend uses (imported directly from
app.services.food_vision, so there's no risk of the diagnostic's own
preprocessing silently drifting from what's actually served).

Why this script: if PyTorch and ONNX disagree on the same image, the bug is
in the ONNX export step. If they agree (both wrong), the bug is upstream —
in training, the data, or the label mapping — not in serving.

Usage:
    cd backend/training
    python diagnose_food_model.py path\\to\\biryani_photo.jpg path\\to\\pizza_photo.jpg
"""

import json
import sys
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # so `app....` imports work
from app.services.food_vision import _preprocess, _softmax  # noqa: E402
from train_food_classifier import build_model  # noqa: E402

MODELS_DIR = Path(__file__).resolve().parents[1] / "models"
CHECKPOINT_PATH = MODELS_DIR / "food_classifier_checkpoint.pt"
ONNX_PATH = MODELS_DIR / "food_classifier.onnx"
# Class order comes from the labels file written alongside the model — not
# from the current source list, which may have changed since that model was trained.
LABELS: list[str] = json.loads((MODELS_DIR / "food_classifier_labels.json").read_text())


def _checkpoint_arch() -> str:
    # Models trained before food_classifier_meta.json existed were all MobileNetV3-small.
    meta_path = MODELS_DIR / "food_classifier_meta.json"
    if meta_path.exists():
        return json.loads(meta_path.read_text()).get("arch", "mobilenet_v3_small")
    return "mobilenet_v3_small"


def predict_pytorch(image_bytes: bytes, top_k: int = 5):
    model = build_model(len(LABELS), _checkpoint_arch(), freeze_backbone=False)
    model.load_state_dict(torch.load(CHECKPOINT_PATH, map_location="cpu"))
    model.eval()

    input_array = _preprocess(image_bytes)  # identical preprocessing to serving
    with torch.no_grad():
        logits = model(torch.from_numpy(input_array)).numpy()[0]
    probs = _softmax(logits)
    return _top_k(probs, top_k)


def predict_onnx(image_bytes: bytes, top_k: int = 5):
    import onnxruntime as ort

    session = ort.InferenceSession(str(ONNX_PATH), providers=["CPUExecutionProvider"])
    input_array = _preprocess(image_bytes)
    (logits,) = session.run(["logits"], {"input": input_array})
    probs = _softmax(logits[0])
    return _top_k(probs, top_k)


def _top_k(probs, k: int):
    import numpy as np

    top_indices = np.argsort(probs)[::-1][:k]
    return [(LABELS[i], round(float(probs[i]) * 100, 1)) for i in top_indices]


def main():
    if len(sys.argv) < 2:
        print("Usage: python diagnose_food_model.py <image_path> [<image_path> ...]")
        sys.exit(1)

    if not CHECKPOINT_PATH.exists():
        print(f"ERROR: checkpoint not found at {CHECKPOINT_PATH} — run training first.")
        sys.exit(1)
    if not ONNX_PATH.exists():
        print(f"ERROR: ONNX model not found at {ONNX_PATH} — run training first.")
        sys.exit(1)

    print(f"Classes (first 5 of {len(LABELS)}): {LABELS[:5]} ...")
    print()

    for image_path in sys.argv[1:]:
        path = Path(image_path)
        if not path.exists():
            print(f"SKIPPING — file not found: {path}")
            continue
        image_bytes = path.read_bytes()

        print(f"=== {path.name} ===")
        pt_top5 = predict_pytorch(image_bytes)
        onnx_top5 = predict_onnx(image_bytes)

        print(f"  PyTorch checkpoint top-5: {pt_top5}")
        print(f"  ONNX export      top-5: {onnx_top5}")
        agree = pt_top5[0][0] == onnx_top5[0][0]
        print(f"  Top prediction MATCHES between PyTorch and ONNX: {agree}")
        print()


if __name__ == "__main__":
    main()
