import logging
import math
import re
from dataclasses import dataclass

from sqlalchemy import Float, select
from sqlalchemy.orm import Session

from app.embeddings.base import EmbeddingProvider
from app.models import DocumentChunk

logger = logging.getLogger(__name__)


@dataclass
class RetrievedChunk:
    text: str
    filename: str
    page_number: int
    chunk_number: int
    source: str | None
    section_title: str | None
    similarity: float


def cosine_similarity(left: list[float], right: list[float]) -> float:
    numerator = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left)) or 1.0
    right_norm = math.sqrt(sum(a * a for a in right)) or 1.0
    return numerator / (left_norm * right_norm)


def lexical_score(query: str, text: str) -> float:
    query_terms = set(re.findall(r"\w+", query.lower()))
    text_terms = set(re.findall(r"\w+", text.lower()))
    return len(query_terms & text_terms) / max(len(query_terms), 1)


class RetrievalService:
    def __init__(self, embeddings: EmbeddingProvider):
        self.embeddings = embeddings

    async def search(self, db: Session, owner_id: str | None, query: str, top_k: int = 5, document_id: str | None = None) -> list[RetrievedChunk]:
        query_embedding = await self.embeddings.embed_query(query)
        if owner_id is None:
            logger.warning("Skipping retrieval for anonymous user; owner_id is required")
            return []
        statement = select(DocumentChunk)
        if owner_id:
            statement = statement.where(DocumentChunk.owner_id == owner_id)
        if document_id:
            statement = statement.where(DocumentChunk.document_id == document_id)
        scored: list[tuple[float, DocumentChunk]] = []
        if db.bind is not None and db.bind.dialect.name == "postgresql":
            # The HNSW index created at startup can satisfy this ordered LIMIT.
            # The custom vector operator inherits the left-hand Vector type;
            # cast the scalar distance so pgvector does not decode it as a vector.
            distance = DocumentChunk.embedding.cosine_distance(query_embedding).cast(Float)
            rows = db.execute(statement.add_columns(distance.label("distance")).order_by(distance).limit(max(top_k * 4, 20))).all()
            for row, distance_value in rows:
                vector_score = 1.0 - float(distance_value)
                score = 0.75 * vector_score + 0.25 * lexical_score(query, row.text)
                scored.append((score, row))
        else:
            rows = list(db.scalars(statement))
            for row in rows:
                vector = row.embedding or []
                vector_score = cosine_similarity(query_embedding, vector) if vector else 0.0
                score = 0.75 * vector_score + 0.25 * lexical_score(query, row.text)
                scored.append((score, row))
        scored.sort(key=lambda item: item[0], reverse=True)
        results = [RetrievedChunk(
            text=row.text,
            filename=row.metadata_json.get("filename", "unknown"),
            page_number=row.page_number,
            chunk_number=row.chunk_number,
            source=row.source,
            section_title=row.section_title,
            similarity=round(max(0.0, min(1.0, score)), 4),
        ) for score, row in scored[:top_k]]
        logger.info("Retrieved owner=%s query=%r results=%s", owner_id or "guest", query[:80], len(results))
        return results
