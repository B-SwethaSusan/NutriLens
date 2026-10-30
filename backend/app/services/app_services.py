from functools import lru_cache

from app.agents.intake_agent import IntakeAgent
from app.agents.orchestrator import AgentOrchestrator
from app.agents.planner_agent import PlannerAgent
from app.agents.progress_agent import ProgressAgent
from app.agents.remedy_agent import RemedyAgent
from app.agents.vision_agent import VisionAgent
from app.embeddings.gemini import get_embedding_provider
from app.llm.mistral import get_llm_provider
from app.services.chat import ChatService
from app.services.diet_plan import DietPlanService
from app.services.ingestion import IngestionService
from app.services.moderation import ModerationService
from app.services.retrieval import RetrievalService
from app.services.storage import storage_service
from app.services.symptom_classifier import SymptomClassifierService


@lru_cache
def get_ingestion_service() -> IngestionService:
    return IngestionService(storage_service, get_embedding_provider())


@lru_cache
def get_retrieval_service(model: str | None = None) -> RetrievalService:
    return RetrievalService(get_embedding_provider(model))


@lru_cache
def get_chat_service() -> ChatService:
    return ChatService(get_retrieval_service, get_llm_provider)


@lru_cache
def get_diet_plan_service() -> DietPlanService:
    return DietPlanService(get_retrieval_service, get_llm_provider)


@lru_cache
def get_symptom_classifier_service() -> SymptomClassifierService:
    return SymptomClassifierService(get_llm_provider)


@lru_cache
def get_moderation_service() -> ModerationService:
    return ModerationService(get_llm_provider)


@lru_cache
def get_agent_orchestrator() -> AgentOrchestrator:
    intake = IntakeAgent(get_symptom_classifier_service())
    planner = PlannerAgent(get_diet_plan_service())
    progress = ProgressAgent()
    vision = VisionAgent()
    remedy = RemedyAgent()
    return AgentOrchestrator(get_llm_provider, intake, planner, progress, vision, remedy, get_chat_service())
