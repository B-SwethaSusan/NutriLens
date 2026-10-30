from pathlib import Path

from app.agents.base import AgentResult

_MODEL_PATH = Path(__file__).resolve().parents[2] / "models" / "food_classifier.onnx"


def model_path() -> Path:
    return _MODEL_PATH


class VisionAgent:
    """Classifies a food photo and returns dish info + nutrition. The ONNX
    model is trained offline (see backend/training/train_food_classifier.py)
    on a GPU machine and dropped into backend/models/; this agent degrades
    gracefully with a clear message if that model isn't present yet, so the
    rest of the orchestrator keeps working either way."""

    def is_ready(self) -> bool:
        return _MODEL_PATH.exists()

    async def handle(self, image_bytes: bytes) -> AgentResult:
        if not self.is_ready():
            return AgentResult(
                agent="vision",
                content=None,
                warnings=[
                    "Food-photo classification isn't configured yet: "
                    f"expected a trained model at {_MODEL_PATH}. "
                    "Run backend/training/train_food_classifier.py locally and export to this path."
                ],
            )
        # imported lazily: onnxruntime is optional until the model exists
        from app.services.food_vision import FoodVisionService, InvalidImageError

        try:
            result = await FoodVisionService(_MODEL_PATH).classify(image_bytes)
        except InvalidImageError as exc:
            return AgentResult(agent="vision", content=None, warnings=[f"INVALID_IMAGE:{exc}"])
        return AgentResult(agent="vision", content=result)
