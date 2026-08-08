import hashlib
import math
from collections.abc import Sequence


class LocalEmbeddingProvider:
    """Deterministic fallback for local development and tests without Gemini credentials."""

    def __init__(self, dimensions: int = 768, model: str = "local-hash-embedding"):
        self.dimensions = dimensions
        self.model = model

    def _embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        tokens = text.lower().split()
        for index, token in enumerate(tokens):
            digest = hashlib.sha256(f"{index}:{token}".encode()).digest()
            bucket = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] % 2 else -1.0
            vector[bucket] += sign * (1.0 + (digest[5] / 255.0))
        norm = math.sqrt(sum(item * item for item in vector)) or 1.0
        return [item / norm for item in vector]

    async def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    async def embed_query(self, text: str) -> list[float]:
        return self._embed(text)
