from app.agents.base import AgentResult
from app.services.symptom_classifier import SymptomClassifierService


class IntakeAgent:
    """Parses free-text symptom/goal descriptions into the fixed condition
    taxonomy the Planner Agent's rules engine understands."""

    def __init__(self, classifier: SymptomClassifierService):
        self.classifier = classifier

    async def handle(self, description: str, llm_model: str | None = None) -> AgentResult:
        result = await self.classifier.classify(description, llm_model)
        warnings = []
        if result["confidence"] == "low":
            warnings.append("Low confidence in detected conditions — consider confirming manually in your health profile.")
        return AgentResult(agent="intake", content=result, warnings=warnings)
