from fastapi import APIRouter
from sqlalchemy import select

from app.config import get_settings
from app.dependencies import CurrentUser, DbSession
from app.models import UserSettings
from app.models.schemas import AgentAskRequest, AgentAskResponse, Citation
from app.services.app_services import get_agent_orchestrator

router = APIRouter(tags=["agent"])


@router.post("/agent/ask", response_model=AgentAskResponse)
async def agent_ask(payload: AgentAskRequest, db: DbSession, user: CurrentUser):
    """Single entry point for the multi-agent system: classifies the
    message's intent and routes it to whichever specialist agent
    (Intake/Planner/Progress/general chat) owns that capability."""
    settings = db.scalar(select(UserSettings).where(UserSettings.owner_id == user.id))
    defaults = get_settings()
    top_k = settings.top_k if settings else defaults.top_k
    temperature = settings.temperature if settings else defaults.temperature
    embedding_model = settings.embedding_model if settings else defaults.embedding_model
    llm_model = settings.llm_model if settings else None

    result = await get_agent_orchestrator().route(
        db, user, payload.message, payload.conversation_id, top_k, temperature, embedding_model, llm_model,
    )
    return AgentAskResponse(
        agent=result.agent,
        content=result.content,
        warnings=result.warnings,
        citations=[Citation(**c) for c in result.citations],
    )
