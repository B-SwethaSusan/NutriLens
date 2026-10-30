"""Tests for the food-photo feature: confidence calibration/rejection logic,
the dish catalogue, and the API's input validation.

Tests that need the real trained model run only when
FOOD_MODEL_PATH points at a food_classifier.onnx (skipped otherwise, since
the model is trained offline and isn't committed to the repo)."""

import io
import os
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from app.data.food_catalog import FOOD_CATALOG
from app.data.indian_food_nutrition import INDIAN_FOOD_CLASSES
from app.models.schemas import FoodDish
from app.services.food_vision import _softmax, confidence_level, interpret

META = {"temperature": 1.4, "reject_below": 0.60, "high_at": 0.85}
LABELS = ["biryani", "idli", "pizza", "samosa"]
REAL_MODEL = Path(os.environ.get("FOOD_MODEL_PATH", "/nonexistent/food_classifier.onnx"))


# ---------- confidence & rejection ----------

def test_confident_prediction_is_recognized_high():
    result = interpret(np.array([9.0, 1.0, 0.5, 0.2]), LABELS, META)
    assert result["status"] == "recognized"
    assert result["confidence_level"] == "high"
    assert result["top_prediction"]["label"] == "biryani"
    assert result["top_prediction"]["name"] == "Biryani"
    assert len(result["alternatives"]) == 2
    assert "biryani" in result["dishes"]


def test_ambiguous_prediction_is_rejected_not_guessed():
    result = interpret(np.array([1.0, 0.9, 0.8, 0.7]), LABELS, META)
    assert result["status"] == "uncertain"
    assert result["confidence_level"] == "low"
    assert result["top_prediction"]["confidence"] < META["reject_below"]


def test_confidence_levels_follow_thresholds():
    assert confidence_level(0.90, META) == "high"
    assert confidence_level(0.85, META) == "high"
    assert confidence_level(0.70, META) == "medium"
    assert confidence_level(0.60, META) == "medium"
    assert confidence_level(0.59, META) == "low"


def test_temperature_softens_confidence_but_never_changes_ranking():
    logits = np.array([4.0, 2.5, 1.0, 0.0])
    raw, calibrated = _softmax(logits, 1.0), _softmax(logits, 1.4)
    assert calibrated.max() < raw.max()
    assert raw.argmax() == calibrated.argmax()
    assert abs(calibrated.sum() - 1.0) < 1e-9


def test_unknown_label_from_model_does_not_crash():
    result = interpret(np.array([5.0, 0.0]), ["some_food101_class", "idli"], META)
    assert result["top_prediction"]["name"] == "Some Food101 Class"
    assert "some_food101_class" not in result["dishes"]


# ---------- dish catalogue ----------

def test_catalog_covers_every_trainable_class():
    assert set(FOOD_CATALOG) == set(INDIAN_FOOD_CLASSES)


@pytest.mark.parametrize("label", sorted(FOOD_CATALOG))
def test_catalog_entry_is_valid(label):
    dish = FoodDish(**FOOD_CATALOG[label])
    assert dish.default_serving.grams > 0
    if dish.reliability in ("high", "medium"):
        assert dish.source.code, "databank-backed dishes must cite their INDB recipe code"
        assert dish.per_100g.fibre_g is not None
    if dish.reliability == "low":
        assert dish.per_100g is not None and dish.per_100g.fibre_g is None, "estimates must not claim fibre values"
    if dish.reliability == "unavailable":
        assert dish.per_100g is None
    if dish.per_100g:
        p = dish.per_100g
        # Energy should roughly equal 4*protein + 4*carbs + 9*fat (Atwater factors).
        atwater = 4 * p.protein_g + 4 * p.carbs_g + 9 * p.fat_g
        assert abs(atwater - p.calories_kcal) <= 0.15 * p.calories_kcal + 10, (label, atwater, p.calories_kcal)
        assert p.fat_g <= 40, "deep-fry-inflated INDB rows must not be used"


def test_serving_math_example():
    # 2 slices of pizza (200 g) from per-100 g values
    pizza = FOOD_CATALOG["pizza"]
    grams = pizza["default_serving"]["grams"]
    kcal = pizza["per_100g"]["calories_kcal"] * grams / 100
    assert round(kcal) == round(249.5 * 2)


# ---------- API ----------

def _auth(client) -> dict:
    token = client.post("/api/auth/signup", json={"email": "food@example.com", "password": "password123"}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _jpeg(color=(200, 120, 40), size=(300, 260)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", size, color).save(buf, format="JPEG")
    return buf.getvalue()


def test_food_photo_allows_guest_mode(client, monkeypatch):
    # The app intentionally lets logged-out visitors use a shared guest
    # workspace (see app/dependencies.py), so no token != 401.
    import app.agents.vision_agent as va
    monkeypatch.setattr(va, "_MODEL_PATH", Path("/nonexistent/food_classifier.onnx"))
    r = client.post("/api/food-photo", files={"file": ("a.jpg", _jpeg(), "image/jpeg")})
    assert r.status_code == 503  # reached the model check, i.e. not blocked by auth


def test_unsupported_format_rejected(client):
    r = client.post("/api/food-photo", headers=_auth(client), files={"file": ("a.gif", b"GIF89a...", "image/gif")})
    assert r.status_code == 415


def test_oversized_image_rejected(client):
    r = client.post("/api/food-photo", headers=_auth(client),
                    files={"file": ("big.jpg", b"\xff" * (10 * 1024 * 1024 + 10), "image/jpeg")})
    assert r.status_code == 413


def test_empty_file_rejected(client):
    r = client.post("/api/food-photo", headers=_auth(client), files={"file": ("e.jpg", b"", "image/jpeg")})
    assert r.status_code == 400


def test_missing_model_gives_clear_503(client, monkeypatch):
    import app.agents.vision_agent as va
    monkeypatch.setattr(va, "_MODEL_PATH", Path("/nonexistent/food_classifier.onnx"))
    r = client.post("/api/food-photo", headers=_auth(client), files={"file": ("a.jpg", _jpeg(), "image/jpeg")})
    assert r.status_code == 503
    assert "isn't configured" in r.json()["detail"]


@pytest.fixture
def real_model(monkeypatch):
    if not REAL_MODEL.exists():
        pytest.skip("set FOOD_MODEL_PATH to a trained food_classifier.onnx to run")
    import app.agents.vision_agent as va
    monkeypatch.setattr(va, "_MODEL_PATH", REAL_MODEL)
    return REAL_MODEL


def test_corrupt_image_gives_400_not_500(client, real_model):
    r = client.post("/api/food-photo", headers=_auth(client),
                    files={"file": ("bad.jpg", b"\xff\xd8\xffnot really a jpeg", "image/jpeg")})
    assert r.status_code == 400
    assert "couldn't be read" in r.json()["detail"]


def test_real_model_full_response_shape(client, real_model):
    r = client.post("/api/food-photo", headers=_auth(client), files={"file": ("a.jpg", _jpeg(), "image/jpeg")})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] in ("recognized", "uncertain")
    assert 0.0 <= body["top_prediction"]["confidence"] <= 1.0
    assert body["model_info"]["num_classes"] >= 31


def test_plain_colour_image_is_not_confidently_named(client, real_model):
    # A flat orange rectangle is not food; the model must not claim high confidence.
    r = client.post("/api/food-photo", headers=_auth(client), files={"file": ("a.jpg", _jpeg(), "image/jpeg")})
    assert r.json()["confidence_level"] != "high"


def test_dish_list_matches_model_labels(client, real_model):
    r = client.get("/api/food-photo/dishes", headers=_auth(client))
    assert r.status_code == 200
    labels = [d["label"] for d in r.json()]
    assert "idli" in labels and len(labels) >= 31
