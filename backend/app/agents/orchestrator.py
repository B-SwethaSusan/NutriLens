import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.agents.base import AgentResult
from app.agents.intake_agent import IntakeAgent
from app.agents.planner_agent import PlannerAgent
from app.agents.progress_agent import ProgressAgent
from app.agents.remedy_agent import RemedyAgent
from app.agents.vision_agent import VisionAgent
from app.llm.base import LLMProvider
from app.models import HealthProfile, User
from app.prompts.agent_router import build_messages, keyword_fallback, try_parse
from app.services.chat import ChatService

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Single entry point that classifies a free-text message's intent and
    routes it to the specialist agent that owns that capability. This is the
    'multi-agent architecture': a transparent router over scoped agents,
    not a black-box framework."""

    def __init__(self, llm_factory, intake: IntakeAgent, planner: PlannerAgent, progress: ProgressAgent,
                 vision: VisionAgent, remedy: RemedyAgent, chat_service: ChatService):
        self.llm_factory = llm_factory
        self.intake = intake
        self.planner = planner
        self.progress = progress
        self.vision = vision
        self.remedy = remedy
        self.chat_service = chat_service

    async def classify_intent(self, message: str, llm_model: str | None = None) -> str:
        provider: LLMProvider = self.llm_factory(llm_model)
        raw = await provider.generate(build_messages(message), temperature=0.0)
        intent = try_parse(raw)
        if intent is None:
            intent = keyword_fallback(message)
            logger.info("Agent router falling back to keyword intent classification: %s", intent)
        return intent

    async def route(self, db: Session, user: User, message: str, conversation_id: str | None,
                     top_k: int, temperature: float, embedding_model: str | None, llm_model: str | None) -> AgentResult:
        intent = await self.classify_intent(message, llm_model)
        logger.info("Routing message to intent=%s owner=%s", intent, user.id)

        if intent == "symptom_check":
            return await self.intake.handle(message, llm_model)

        if intent == "diet_plan":
            profile = db.scalar(select(HealthProfile).where(HealthProfile.owner_id == user.id))
            if not profile:
                return AgentResult(
                    agent="router", content=None,
                    warnings=["No health profile found — set one up via PUT /api/health-profile before requesting a diet plan."],
                )
            return await self.planner.handle(db, user, profile, top_k, temperature, embedding_model, llm_model)

        if intent == "progress_check":
            return await self.progress.handle(db, user)

        if intent == "home_remedy":
            return self.remedy.handle(db, message)

        if intent == "food_photo":
            return AgentResult(
                agent="router", content=None,
                warnings=["This endpoint routes text only. Upload the photo to POST /api/food-photo directly."],
            )

        # general_chat falls through to the existing document-grounded chat service
        conversation_id, answer, chunks = await self.chat_service.answer(
            db, user, message, conversation_id, top_k, temperature, embedding_model, llm_model,
        )
        citations = [self.chat_service.citation(chunk) for chunk in chunks]
        return AgentResult(agent="router", content={"conversation_id": conversation_id, "answer": answer}, citations=citations)
