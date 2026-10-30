"""Merged nutrition lookup across every trainable food-classifier dataset
(Food-101 and the Indian Food Images dataset), so the serving code
(app/services/food_vision.py) doesn't need to know which dataset the
currently-deployed model.onnx was trained on — it just looks up whatever
label the model predicts.

A class name present in both tables is unambiguous in practice: only one
model (one dataset) is ever deployed as backend/models/food_classifier.onnx
at a time, so predicted labels only ever come from that one dataset's class
list.
"""

from app.data.food101_nutrition import NUTRITION_TABLE as _FOOD101_TABLE
from app.data.indian_food_nutrition import NUTRITION_TABLE as _INDIAN_TABLE

NUTRITION_TABLE: dict[str, dict] = {**_FOOD101_TABLE, **_INDIAN_TABLE}


def get_nutrition(label: str) -> dict | None:
    return NUTRITION_TABLE.get(label)
