from functools import lru_cache

from app.embeddings.gemini import get_embedding_provider
from app.llm.mistral import get_llm_provider
from app.services.chat import ChatService
from app.services.ingestion import IngestionService
from app.services.retrieval import RetrievalService
from app.services.storage import storage_service


@lru_cache
def get_ingestion_service() -> IngestionService:
    return IngestionService(storage_service, get_embedding_provider())


@lru_cache
def get_retrieval_service(model: str | None = None) -> RetrievalService:
    return RetrievalService(get_embedding_provider(model))


@lru_cache
def get_chat_service() -> ChatService:
    return ChatService(get_retrieval_service, get_llm_provider)
