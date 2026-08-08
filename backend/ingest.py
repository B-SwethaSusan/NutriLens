"""CLI ingestion helper: python ingest.py path/to/file.pdf --user-id <uuid>."""
import argparse
import asyncio
from pathlib import Path

from app.database.session import SessionLocal
from app.embeddings.gemini import get_embedding_provider
from app.models import Document
from app.services.ingestion import IngestionService
from app.services.storage import storage_service


async def main(path: Path, user_id: str):
    db = SessionLocal()
    try:
        storage_path = f"{user_id}/cli-{path.name}"
        await storage_service.upload(storage_path, path.read_bytes())
        document = Document(owner_id=user_id, filename=path.name, storage_path=storage_path, source=str(path), file_size=path.stat().st_size)
        db.add(document)
        db.commit()
        db.refresh(document)
        await IngestionService(storage_service, get_embedding_provider()).ingest(db, document)
        print(f"Ingested {document.filename}: {document.chunk_count} chunks")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--user-id", required=True)
    args = parser.parse_args()
    asyncio.run(main(args.pdf, args.user_id))
