import json

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.agents.vision_agent import VisionAgent, model_path
from app.data.food_catalog import FOOD_CATALOG
from app.dependencies import CurrentUser
from app.models.schemas import FoodDishListItem, FoodPhotoResponse

router = APIRouter(tags=["food-photo"])
_vision_agent = VisionAgent()

_MAX_IMAGE_BYTES = 10 * 1024 * 1024  # 10MB
_ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}


@router.post("/food-photo", response_model=FoodPhotoResponse)
async def analyze_food_photo(user: CurrentUser, file: UploadFile = File(...)):
    if file.content_type not in _ALLOWED_TYPES:
        raise HTTPException(status_code=415, detail="Upload a JPEG, PNG, or WEBP image")
    image_bytes = await file.read(_MAX_IMAGE_BYTES + 1)
    if len(image_bytes) > _MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="Image too large (max 10MB)")
    if not image_bytes:
        raise HTTPException(status_code=400, detail="The uploaded file is empty")

    result = await _vision_agent.handle(image_bytes)
    if result.content is None:
        # Invalid image -> 400 (user's fault); missing model -> 503 (server not ready).
        status = 400 if result.warnings and result.warnings[0].startswith("INVALID_IMAGE:") else 503
        detail = "; ".join(w.removeprefix("INVALID_IMAGE:") for w in result.warnings) or "Food-photo model not available"
        raise HTTPException(status_code=status, detail=detail)
    return FoodPhotoResponse(**result.content)


@router.get("/food-photo/dishes", response_model=list[FoodDishListItem])
async def list_supported_dishes(user: CurrentUser):
    """Dishes the deployed model can recognise, with their catalogue info —
    powers the searchable dish list and manual nutrition lookup. Read from the
    model's own labels file, so the list always matches the live model."""
    labels_path = model_path().with_name("food_classifier_labels.json")
    labels = json.loads(labels_path.read_text()) if labels_path.exists() else []
    return [FoodDishListItem(label=label, **FOOD_CATALOG[label]) for label in labels if label in FOOD_CATALOG]
