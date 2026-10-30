from sqlalchemy.orm import Session

from app.agents.base import AgentResult
from app.agents.safety_agent import SafetyAgent
from app.models import HealthProfile, User
from app.services.diet_plan import DietPlanService


class PlannerAgent:
    """Produces the diet plan: deterministic targets + RAG-grounded
    explanation. Runs every output through the Safety Agent before
    returning it."""

    def __init__(self, diet_plan_service: DietPlanService):
        self.diet_plan_service = diet_plan_service

    async def handle(self, db: Session, user: User, profile: HealthProfile, top_k: int, temperature: float,
                      embedding_model: str | None, llm_model: str | None) -> AgentResult:
        targets, meal_timing, explanation, citations = await self.diet_plan_service.generate(
            db, user, profile, top_k, temperature, embedding_model, llm_model,
        )
        warnings = SafetyAgent.review(explanation, profile.allergies)
        explanation = SafetyAgent.ensure_disclaimer(
            explanation,
            "This plan is educational information, not a medical diagnosis or individualized clinical advice. "
            "Please consult a registered dietitian or physician before making significant dietary changes.",
        )
        return AgentResult(
            agent="planner",
            content={"targets": targets, "meal_timing": meal_timing, "explanation": explanation},
            warnings=warnings,
            citations=citations,
        )
