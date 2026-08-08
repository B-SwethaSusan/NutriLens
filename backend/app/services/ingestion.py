import hashlib
import logging
import re

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.embeddings.base import EmbeddingProvider
from app.models import Document, DocumentChunk
from app.services.pdf import extract_pdf, split_text
from app.services.storage import StorageService

logger = logging.getLogger(__name__)


class IngestionService:
    def __init__(self, storage: StorageService, embeddings: EmbeddingProvider):
        self.storage = storage
        self.embeddings = embeddings

    async def ingest(self, db: Session, document: Document, chunk_size: int = 1000, overlap: int = 200) -> Document:
        logger.info("Ingesting document id=%s filename=%s", document.id, document.filename)
        document.status = "processing"
        document.error_message = None
        db.commit()
        try:
            content = await self.storage.download(document.storage_path)
            parsed = extract_pdf(content)
            chunk_records: list[dict] = []
            for page in parsed.pages:
                if not page.text:
                    continue
                section = next((line for line in page.text.splitlines() if len(line) < 120 and not line.endswith(".")), None)
                for local_index, text in enumerate(split_text(page.text, chunk_size, overlap)):
                    chunk_records.append({
                        "text": text,
                        "page_number": page.page_number,
                        "chunk_number": len(chunk_records),
                        "section_title": section,
                        "source": document.source or document.filename,
                        "content_hash": hashlib.sha256(text.encode()).hexdigest(),
                    })
            if not chunk_records:
                raise ValueError("The PDF has no usable text after cleaning")
            vectors = await self.embeddings.embed_documents([item["text"] for item in chunk_records])
            if len(vectors) != len(chunk_records):
                raise RuntimeError("Embedding provider returned an unexpected number of vectors")
            db.execute(delete(DocumentChunk).where(DocumentChunk.document_id == document.id))
            for item, vector in zip(chunk_records, vectors):
                db.add(DocumentChunk(document_id=document.id, owner_id=document.owner_id, embedding=vector, metadata_json={
                    "filename": document.filename, "page_number": item["page_number"], "chunk_number": item["chunk_number"],
                    "section_title": item["section_title"], "source": item["source"],
                }, **item))
            document.page_count = parsed.page_count
            document.author = document.author or parsed.author
            document.chunk_count = len(chunk_records)
            document.status = "ready"
            db.commit()
            logger.info("Ingestion complete id=%s chunks=%s", document.id, len(chunk_records))
            return document
        except Exception as exc:
            db.rollback()
            document = db.get(Document, document.id)
            if document:
                document.status = "failed"
                document.error_message = str(exc)[:2000]
                db.commit()
            logger.exception("Ingestion failed id=%s", document.id)
            raise
