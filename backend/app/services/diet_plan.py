import logging

from sqlalchemy.orm import Session

from app.models import HealthProfile, User
from app.prompts.diet_plan import build_messages
from app.services.nutrition_calc import build_meal_timing, build_targets
from app.services.retrieval import RetrievalService

logger = logging.getLogger(__name__)


class DietPlanService:
    """Combines the deterministic nutrition-science layer with RAG-grounded,
    LLM-generated explanation. Numbers always come from nutrition_calc, never
    from the LLM, so the plan stays reproducible and auditable."""

    def __init__(self, retrieval_factory, llm_factory):
        self.retrieval_factory = retrieval_factory
        self.llm_factory = llm_factory

    @staticmethod
    def _profile_summary(profile: HealthProfile) -> str:
        parts = [
            f"{profile.age}yo {profile.sex}", f"{profile.height_cm}cm", f"{profile.weight_kg}kg",
            f"activity={profile.activity_level}", f"goal={profile.goal}",
        ]
        if profile.conditions:
            parts.append(f"conditions={', '.join(profile.conditions)}")
        if profile.allergies:
            parts.append(f"allergies={', '.join(profile.allergies)}")
        if profile.dietary_preferences:
            parts.append(f"preferences={', '.join(profile.dietary_preferences)}")
        return "; ".join(parts)

    async def generate(self, db: Session, user: User, profile: HealthProfile, top_k: int = 5,
                        temperature: float = 0.3, embedding_model: str | None = None, llm_model: str | None = None):
        targets = build_targets(profile)
        meal_timing = build_meal_timing(targets)

        query = (
            f"dietary guidance for {', '.join(profile.conditions) if profile.conditions else 'general healthy adult'} "
            f"goal {profile.goal} weight"
        )
        retrieval: RetrievalService = self.retrieval_factory(embedding_model)
        chunks = await retrieval.search(db, user.id, query, top_k)

        targets_summary = (
            f"BMR {targets.bmr_kcal} kcal, TDEE {targets.tdee_kcal} kcal, target {targets.target_calories_kcal} kcal/day; "
            f"protein {targets.protein_g}g, carbs {targets.carbs_g}g, fat {targets.fat_g}g, fiber {targets.fiber_g}g; "
            f"{targets.meals_per_day} meals/day"
        )
        messages = build_messages(self._profile_summary(profile), targets_summary, chunks)
        explanation = await self.llm_factory(llm_model).generate(messages, temperature)

        citations = [
            {"filename": c.filename, "page_number": c.page_number, "chunk_number": c.chunk_number, "similarity": c.similarity}
            for c in chunks
        ]
        logger.info("Generated diet plan owner=%s conditions=%s citations=%s", user.id, profile.conditions, len(chunks))
        return targets, meal_timing, explanation, citations
