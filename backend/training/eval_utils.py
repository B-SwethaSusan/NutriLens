"""Evaluation, calibration and duplicate-detection helpers for the food
classifier. Deliberately numpy/PIL-only (no torch import) so they can be
unit-tested and reused anywhere, including on the CPU-only backend.

Everything here works on raw model logits — shape (N, num_classes) — plus
integer ground-truth labels y of shape (N,).
"""

from __future__ import annotations

from collections import Counter

import numpy as np
from PIL import Image


def softmax(logits: np.ndarray, temperature: float = 1.0) -> np.ndarray:
    z = np.asarray(logits, dtype=np.float64) / temperature
    z = z - z.max(axis=-1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=-1, keepdims=True)


def fit_temperature(logits: np.ndarray, y: np.ndarray, grid: np.ndarray | None = None) -> float:
    """Temperature scaling (Guo et al., 2017): pick the single scalar T that
    minimises negative log-likelihood on a held-out calibration set. A grid
    search is plenty for one parameter and has no optimiser edge cases.
    T > 1 softens over-confident predictions; it never changes which class
    is ranked first, so accuracy is unaffected."""
    if grid is None:
        # Lower bound below 1: label smoothing during training tends to make
        # the model UNDER-confident, which needs T < 1 to correct.
        grid = np.linspace(0.3, 5.0, 189)
    best_t, best_nll = 1.0, np.inf
    for t in grid:
        p = softmax(logits, t)
        nll = -np.mean(np.log(p[np.arange(len(y)), y] + 1e-12))
        if nll < best_nll:
            best_t, best_nll = float(t), nll
    return best_t


def expected_calibration_error(probs: np.ndarray, y: np.ndarray, bins: int = 15) -> float:
    conf = probs.max(axis=1)
    correct = (probs.argmax(axis=1) == y).astype(float)
    edges = np.linspace(0.0, 1.0, bins + 1)
    ece = 0.0
    for lo, hi in zip(edges[:-1], edges[1:]):
        in_bin = (conf > lo) & (conf <= hi)
        if in_bin.any():
            ece += in_bin.mean() * abs(correct[in_bin].mean() - conf[in_bin].mean())
    return float(ece)


def brier_score(probs: np.ndarray, y: np.ndarray) -> float:
    onehot = np.eye(probs.shape[1])[y]
    return float(np.mean(np.sum((probs - onehot) ** 2, axis=1)))


def reliability_table(probs: np.ndarray, y: np.ndarray, bins: int = 10) -> list[dict]:
    """Data for a reliability diagram: per confidence bin, how often the
    model was actually right. A perfectly calibrated model has
    accuracy == mean_confidence in every bin."""
    conf = probs.max(axis=1)
    correct = (probs.argmax(axis=1) == y).astype(float)
    edges = np.linspace(0.0, 1.0, bins + 1)
    rows = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        in_bin = (conf > lo) & (conf <= hi)
        if in_bin.any():
            rows.append({
                "bin": f"{lo:.1f}-{hi:.1f}",
                "count": int(in_bin.sum()),
                "mean_confidence": round(float(conf[in_bin].mean()), 4),
                "accuracy": round(float(correct[in_bin].mean()), 4),
            })
    return rows


def choose_thresholds(probs: np.ndarray, y: np.ndarray,
                      reject_target_acc: float = 0.92, high_target_acc: float = 0.97,
                      default_reject: float = 0.60, default_high: float = 0.85) -> dict:
    """Pick confidence cut-offs from held-out data instead of guessing:
      - reject_below: below this, the app says "couldn't identify confidently"
        instead of naming a dish. Lowest threshold at which the predictions
        we DO accept are at least `reject_target_acc` accurate.
      - high_at: at or above this, confidence is labelled "High". Lowest
        threshold at which accepted predictions are `high_target_acc` accurate.
    Falls back to the defaults if the held-out set never reaches a target."""
    conf = probs.max(axis=1)
    correct = probs.argmax(axis=1) == y
    grid = np.round(np.arange(0.30, 0.96, 0.05), 2)

    def first_reaching(target: float, fallback: float) -> float:
        for th in grid:
            kept = conf >= th
            if kept.sum() >= max(20, 0.3 * len(y)) and correct[kept].mean() >= target:
                return float(th)
        return fallback

    # Floor of 0.55: the held-out set only contains dishes the model was
    # trained on, so it can't show how confident the model gets on foods it
    # has NEVER seen. Measured on the 31-class model, those unseen foods
    # averaged ~0.70 raw confidence — so a threshold tuned on known dishes
    # alone comes out too lenient (0.45) to catch them. Stay conservative.
    reject_below = max(first_reaching(reject_target_acc, default_reject), 0.55)
    high_at = max(first_reaching(high_target_acc, default_high), reject_below + 0.05)
    kept = conf >= reject_below
    return {
        "reject_below": round(reject_below, 2),
        "high_at": round(min(high_at, 0.95), 2),
        "heldout_coverage_at_reject": round(float(kept.mean()), 4),
        "heldout_accuracy_when_accepted": round(float(correct[kept].mean()) if kept.any() else 0.0, 4),
    }


def classification_report(probs: np.ndarray, y: np.ndarray, classes: list[str], top_confusions: int = 15) -> dict:
    pred = probs.argmax(axis=1)
    top5 = np.argsort(probs, axis=1)[:, ::-1][:, :5]
    n = len(classes)
    cm = np.zeros((n, n), dtype=int)
    for t, p in zip(y, pred):
        cm[t, p] += 1

    per_class = {}
    precisions, recalls, f1s = [], [], []
    for i, name in enumerate(classes):
        support = int(cm[i].sum())
        if support == 0:
            continue  # class absent from this held-out set — exclude from macro averages
        tp = cm[i, i]
        precision = tp / cm[:, i].sum() if cm[:, i].sum() else 0.0
        recall = tp / support
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
        per_class[name] = {"support": support, "accuracy": round(float(recall), 4),
                           "precision": round(float(precision), 4), "f1": round(float(f1), 4)}
        precisions.append(precision)
        recalls.append(recall)
        f1s.append(f1)

    confusions = Counter()
    for t, p in zip(y, pred):
        if t != p:
            confusions[(classes[t], classes[p])] += 1

    return {
        "num_images": int(len(y)),
        "num_classes_evaluated": len(per_class),
        "top1_accuracy": round(float((pred == y).mean()), 4),
        "top5_accuracy": round(float(np.mean([y[i] in top5[i] for i in range(len(y))])), 4),
        "macro_precision": round(float(np.mean(precisions)), 4),
        "macro_recall": round(float(np.mean(recalls)), 4),
        "macro_f1": round(float(np.mean(f1s)), 4),
        "per_class": per_class,
        "top_confusions": [{"true": t, "predicted": p, "count": c} for (t, p), c in confusions.most_common(top_confusions)],
        "confusion_matrix": cm.tolist(),
    }


def dhash(image: Image.Image, size: int = 8) -> int:
    """64-bit difference hash. Two images with the same dhash are almost
    certainly the same photo (possibly re-saved/resized) — used to stop
    near-identical images appearing in both the training set and the
    held-out set, which would inflate reported accuracy."""
    gray = image.convert("L").resize((size + 1, size), Image.BILINEAR)
    px = np.asarray(gray, dtype=np.int16)
    bits = (px[:, 1:] > px[:, :-1]).flatten()
    return int("".join("1" if b else "0" for b in bits), 2)
