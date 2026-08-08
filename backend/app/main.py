import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api import auth, chat, documents, health
from app.config import get_settings
from app.database.base import Base
from app.database.session import engine
from app.utils.logging import configure_logging
from app.utils.rate_limit import InMemoryRateLimitMiddleware

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    if engine.dialect.name == "postgresql":
        with engine.begin() as connection:
            connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(bind=engine)
    if engine.dialect.name == "postgresql":
        with engine.begin() as connection:
            connection.execute(text("CREATE INDEX IF NOT EXISTS ix_document_chunks_embedding_hnsw ON document_chunks USING hnsw (embedding vector_cosine_ops)"))
    logger.info("Nutrition RAG API started environment=%s", settings.environment)
    yield


app = FastAPI(title=settings.app_name, version="1.0.0", description="Document-grounded nutrition Q&A API", lifespan=lifespan)
app.add_middleware(InMemoryRateLimitMiddleware, limit=settings.rate_limit_per_minute)
app.add_middleware(CORSMiddleware, allow_origins=settings.allowed_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(documents.router, prefix=settings.api_prefix)
app.include_router(chat.router, prefix=settings.api_prefix)
app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(health.router)


@app.get("/")
def root():
    return {"name": settings.app_name, "docs": "/docs", "health": "/health"}
