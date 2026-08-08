from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from types import SimpleNamespace

from app.config import get_settings
from app.dependencies import CurrentUser, DbSession
from app.models import Conversation, Message, UserSettings
from app.models.schemas import ChatRequest, ChatResponse, Citation, ConversationRead, MessageRead, SettingsRead, SettingsUpdate
from app.services.app_services import get_chat_service

router = APIRouter(tags=["chat"])


def _default_settings() -> SimpleNamespace:
    defaults = get_settings()
    return SimpleNamespace(chunk_size=defaults.chunk_size, chunk_overlap=defaults.chunk_overlap, top_k=defaults.top_k, temperature=defaults.temperature,
                           llm_model=defaults.mistral_model, embedding_model=defaults.embedding_model)


def _settings(db: DbSession, user: CurrentUser) -> UserSettings:
    settings = db.scalar(select(UserSettings).where(UserSettings.owner_id == user.id))
    if not settings:
        defaults = get_settings()
        settings = UserSettings(owner_id=user.id, chunk_size=defaults.chunk_size, chunk_overlap=defaults.chunk_overlap,
                                top_k=defaults.top_k, temperature=defaults.temperature, llm_model=defaults.mistral_model,
                                embedding_model=defaults.embedding_model)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, db: DbSession, user: CurrentUser):
    settings = _settings(db, user)
    conversation_id, answer, chunks = await get_chat_service().answer(
        db, user, payload.question, payload.conversation_id, settings.top_k, settings.temperature,
        settings.embedding_model, settings.llm_model,
    )
    citations = [Citation(filename=item.filename, page_number=item.page_number, chunk_number=item.chunk_number, similarity=item.similarity) for item in chunks]
    if payload.stream:
        # The final answer and citations are persisted before streaming; clients receive SSE text chunks.
        return StreamingResponse(get_chat_service().stream_answer(answer), media_type="text/event-stream", headers={"X-Conversation-Id": conversation_id})
    return ChatResponse(conversation_id=conversation_id, answer=answer, citations=citations)


@router.get("/history", response_model=list[ConversationRead])
def history(db: DbSession, user: CurrentUser):
    conversations = list(db.scalars(select(Conversation).where(Conversation.owner_id == user.id).order_by(Conversation.updated_at.desc())))
    return [ConversationRead(id=item.id, title=item.title, created_at=item.created_at, updated_at=item.updated_at,
                             messages=[MessageRead.model_validate(message) for message in item.messages]) for item in conversations]


@router.delete("/history/{conversation_id}", status_code=204)
def clear_conversation(conversation_id: str, db: DbSession, user: CurrentUser):
    conversation = db.scalar(select(Conversation).where(Conversation.id == conversation_id, Conversation.owner_id == user.id))
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    db.delete(conversation)
    db.commit()


@router.get("/settings", response_model=SettingsRead)
def get_user_settings(db: DbSession, user: CurrentUser):
    return _settings(db, user)


@router.put("/settings", response_model=SettingsRead)
def update_user_settings(payload: SettingsUpdate, db: DbSession, user: CurrentUser):
    settings = _settings(db, user)
    allowed = {"chunk_size", "chunk_overlap", "top_k", "temperature", "llm_model", "embedding_model"}
    for key, value in payload.model_dump().items():
        if key in allowed:
            setattr(settings, key, value)
    if settings.chunk_overlap >= settings.chunk_size:
        raise HTTPException(status_code=422, detail="chunk_overlap must be smaller than chunk_size")
    db.commit()
    db.refresh(settings)
    return settings
