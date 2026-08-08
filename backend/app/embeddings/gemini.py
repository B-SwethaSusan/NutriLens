import logging
from collections.abc import Sequence

import httpx

from app.config import get_settings
from app.embeddings.local import LocalEmbeddingProvider
from app.utils.retry import async_retry

logger = logging.getLogger(__name__)


class GeminiEmbeddingProvider:
    def __init__(self, api_key: str, model: str, dimensions: int):
        self.api_key = api_key
        self.model = model.removeprefix("models/")
        self.dimensions = dimensions
        self.fallback = LocalEmbeddingProvider(dimensions, "local-fallback")

    @async_retry(attempts=3)
    async def _embed_one(self, text: str, task_type: str) -> list[float]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:embedContent"
        payload = {"model": f"models/{self.model}", "content": {"parts": [{"text": text}]}, "taskType": task_type}
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                response = await client.post(url, params={"key": self.api_key}, json=payload)
            except httpx.RequestError as exc:
                logger.warning("Embedding request failed for model=%s, using local fallback: %s", self.model, exc)
                return await self.fallback.embed_query(text) if task_type == "RETRIEVAL_QUERY" else (await self.fallback.embed_documents([text]))[0]
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                status = exc.response.status_code
                if status in {403, 404}:
                    logger.warning(
                        "Embedding service unavailable for model=%s status=%s, using local fallback",
                        self.model,
                        status,
                    )
                    return await self.fallback.embed_query(text) if task_type == "RETRIEVAL_QUERY" else (await self.fallback.embed_documents([text]))[0]
                raise
            values = response.json()["embedding"]["values"]
            return [float(value) for value in values]

    async def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        if not self.api_key:
            return await self.fallback.embed_documents(texts)
        try:
            return [await self._embed_one(text, "RETRIEVAL_DOCUMENT") for text in texts]
        except Exception as exc:
            logger.warning("Embedding documents failed for model=%s, using local fallback: %s", self.model, exc)
            return await self.fallback.embed_documents(texts)

    async def embed_query(self, text: str) -> list[float]:
        if not self.api_key:
            return await self.fallback.embed_query(text)
        try:
            return await self._embed_one(text, "RETRIEVAL_QUERY")
        except Exception as exc:
            logger.warning("Embedding query failed for model=%s, using local fallback: %s", self.model, exc)
            return await self.fallback.embed_query(text)


def get_embedding_provider(model: str | None = None):
    settings = get_settings()
    return GeminiEmbeddingProvider(settings.gemini_api_key, model or settings.embedding_model, settings.embedding_dimensions)
