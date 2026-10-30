import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api import agent, auth, chat, documents, food_photo, health, health_profile, progress, remedies
from app.config import get_settings
from app.database.base import Base
from app.database.session import SessionLocal, engine
from app.services.remedies import seed_home_remedies
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
    seed_db = SessionLocal()
    try:
        seed_home_remedies(seed_db)
    finally:
        seed_db.close()
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
app.include_router(health_profile.router, prefix=settings.api_prefix)
app.include_router(progress.router, prefix=settings.api_prefix)
app.include_router(agent.router, prefix=settings.api_prefix)
app.include_router(food_photo.router, prefix=settings.api_prefix)
app.include_router(remedies.router, prefix=settings.api_prefix)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Without this, any uncaught backend error (an LLM API failure, a bad
    # DB query, etc.) falls through to Starlette's default plain-text 500
    # response, which has no JSON `detail` field. The frontend's error
    # handling everywhere (Chat, Diet Plan, Upload, ...) looks for
    # `err.response.data.detail` and falls back to a generic "Something
    # went wrong" message when it's missing — this handler ensures that
    # field is always present with the real error, so the UI shows what
    # actually broke instead of a dead end. Full traceback still goes to
    # the server log via logger.exception.
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": str(exc)})


@app.get("/")
def root():
    return {"name": settings.app_name, "docs": "/docs", "health": "/health"}
