"""Serves the ONNX-exported food classifier at inference time.

`onnxruntime` is imported lazily (see app/agents/vision_agent.py) so the API
can start and run every other feature even without a trained model.

Confidence handling
-------------------
Raw softmax scores are NOT treated as probabilities. The training script
fits a temperature on held-out photos (temperature scaling) and picks two
cut-offs from held-out data, saved in models/food_classifier_meta.json:
    confidence >= high_at       -> "high"
    reject_below <= c < high_at -> "medium"
    confidence <  reject_below  -> "low": the app says it couldn't identify
                                   the dish confidently instead of naming one
                                   (unknown-food rejection).
"""

import io
import json
import logging
import threading
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError

from app.data.food_catalog import get_dish

logger = logging.getLogger(__name__)

IMAGE_SIZE = 224
_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)

# Used only if a model has no food_classifier_meta.json. Values measured on
# held-out photos for the original 31-class model (see report in README).
DEFAULT_META = {"temperature": 1.0, "reject_below": 0.60, "high_at": 0.85}


class InvalidImageError(ValueError):
    pass


def _preprocess(image_bytes: bytes) -> np.ndarray:
    try:
        image = Image.open(io.BytesIO(image_bytes))
        image = ImageOps.exif_transpose(image)  # phone photos: honour the rotation the user sees
        image = image.convert("RGB")
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise InvalidImageError("This file couldn't be read as an image.") from exc
    # Shorter side -> 256, centre-crop 224: identical to the training
    # script's evaluation transform, so inference sees the same input distribution.
    ratio = 256 / min(image.size)
    image = image.resize((max(IMAGE_SIZE, round(image.width * ratio)), max(IMAGE_SIZE, round(image.height * ratio))),
                         Image.BILINEAR)
    left = (image.width - IMAGE_SIZE) // 2
    top = (image.height - IMAGE_SIZE) // 2
    image = image.crop((left, top, left + IMAGE_SIZE, top + IMAGE_SIZE))

    array = np.asarray(image, dtype=np.float32) / 255.0
    array = (array - _MEAN) / _STD
    return array.transpose(2, 0, 1)[np.newaxis, :, :, :].astype(np.float32)  # NCHW


def _softmax(logits: np.ndarray, temperature: float = 1.0) -> np.ndarray:
    z = np.asarray(logits, dtype=np.float64) / temperature
    exp = np.exp(z - z.max())
    return exp / exp.sum()


def confidence_level(confidence: float, meta: dict) -> str:
    if confidence >= meta["high_at"]:
        return "high"
    if confidence >= meta["reject_below"]:
        return "medium"
    return "low"


def interpret(logits: np.ndarray, labels: list[str], meta: dict, top_k: int = 3) -> dict:
    """Pure function: raw logits -> the API response body (minus model_info)."""
    probs = _softmax(logits, meta["temperature"])
    top_indices = [int(i) for i in np.argsort(probs)[::-1][:top_k]]

    def describe(idx: int) -> dict:
        label = labels[idx] if idx < len(labels) else f"class_{idx}"
        dish = get_dish(label)
        return {"label": label, "name": dish["name"] if dish else label.replace("_", " ").title(),
                "confidence": round(float(probs[idx]), 4)}

    predictions = [describe(i) for i in top_indices]
    level = confidence_level(predictions[0]["confidence"], meta)
    dishes = {p["label"]: get_dish(p["label"]) for p in predictions if get_dish(p["label"])}
    return {
        "status": "uncertain" if level == "low" else "recognized",
        "confidence_level": level,
        "top_prediction": predictions[0],
        "alternatives": predictions[1:],
        "dishes": dishes,
    }


class _LoadedModel:
    def __init__(self, model_path: Path):
        import onnxruntime as ort  # lazy import — see module docstring

        self.mtime = model_path.stat().st_mtime
        self.session = ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])
        labels_path = model_path.with_name("food_classifier_labels.json")
        self.labels: list[str] = json.loads(labels_path.read_text()) if labels_path.exists() else []
        meta_path = model_path.with_name("food_classifier_meta.json")
        self.calibrated = meta_path.exists()
        self.meta = {**DEFAULT_META, **(json.loads(meta_path.read_text()) if self.calibrated else {})}


_cache: dict[str, _LoadedModel] = {}
_lock = threading.Lock()


def load_model(model_path: Path) -> _LoadedModel:
    """Loads the model once and keeps it in memory (previously it was
    reloaded from disk on every upload). Reloads automatically if the .onnx
    file is replaced, e.g. after retraining."""
    key = str(model_path)
    with _lock:
        cached = _cache.get(key)
        if cached is None or cached.mtime != model_path.stat().st_mtime:
            cached = _LoadedModel(model_path)
            _cache[key] = cached
            logger.info("Loaded food classifier: %d classes, calibrated=%s", len(cached.labels), cached.calibrated)
        return cached


class FoodVisionService:
    def __init__(self, model_path: Path):
        self.model = load_model(model_path)

    def supported_labels(self) -> list[str]:
        return list(self.model.labels)

    async def classify(self, image_bytes: bytes) -> dict:
        input_array = _preprocess(image_bytes)
        (logits,) = self.model.session.run(["logits"], {"input": input_array})
        result = interpret(logits[0], self.model.labels, self.model.meta)
        meta = self.model.meta
        result["model_info"] = {
            "calibrated": self.model.calibrated,
            "num_classes": len(self.model.labels),
            "reject_below": meta["reject_below"],
            "high_at": meta["high_at"],
            "heldout_top1_accuracy": meta.get("heldout_top1_accuracy"),
        }
        result["note"] = (
            "A photo can identify the dish but cannot measure its weight. Nutrition is shown for a "
            "reference serving you can adjust to what you actually ate — it is general information, "
            "not an individual dietary prescription."
        )
        top = result["top_prediction"]
        logger.info("Food photo: %s confidence=%.3f level=%s", top["label"], top["confidence"], result["confidence_level"])
        return result
