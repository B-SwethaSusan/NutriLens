from collections.abc import Sequence
from typing import Protocol


class EmbeddingProvider(Protocol):
    model: str
    dimensions: int

    async def embed_documents(self, texts: Sequence[str]) -> list[list[float]]: ...

    async def embed_query(self, text: str) -> list[float]: ...
