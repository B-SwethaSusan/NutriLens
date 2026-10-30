"""
Seed the RAG knowledge base with free, publicly available nutrition guideline
documents, so the Diet Plan Generator has real authoritative source material
to cite from the first time anyone uses it -- even before they upload their
own PDFs.

Sources (all free, public, no login or payment):
  - ICMR-NIN "Dietary Guidelines for Indians" (2024 edition)
  - "Dietary Guidelines for Americans 2020-2025" (US HHS/USDA)
  - WHO "Diabetes and Hypertension Management Manual"

These cover general nutrition + two of the six condition rules (diabetes,
hypertension) out of the box. PCOS / thyroid / CKD / GI guidance still
benefits from the user uploading their own reference PDFs via the Documents
page -- there isn't an equally stable free direct-PDF link for those yet.

This script downloads each PDF (skipping ones already downloaded), then runs
them through the exact same ingestion pipeline the "Add a PDF" upload uses,
seeding them for every existing user (including the guest user used when
no one has signed in). It's safe to re-run: already-seeded documents are
skipped.

Run once, after your database is set up and the backend can import cleanly:

    cd backend
    python scripts/seed_knowledge_base.py
"""
import asyncio
import logging
import sys
from pathlib import Path
from uuid import uuid4

import httpx
from sqlalchemy import select

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.session import SessionLocal  # noqa: E402
from app.embeddings.gemini import get_embedding_provider  # noqa: E402
from app.models import Document, User, UserSettings  # noqa: E402
from app.services.ingestion import IngestionService  # noqa: E402
from app.services.pdf import extract_pdf  # noqa: E402
from app.services.storage import storage_service  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("seed_knowledge_base")

# Marks seeded documents so they're never confused with a user's own uploads
# and so re-running this script is idempotent.
KB_SOURCE_TAG = "knowledge-base-seed"

SOURCE_DOCUMENTS = [
    {
        "filename": "ICMR-NIN_Dietary_Guidelines_for_Indians_2024.pdf",
        "title": "ICMR-NIN Dietary Guidelines for Indians (2024)",
        "url": "https://www.nin.res.in/dietaryguidelines/pdfjs/locale/DGI24thJune2024fin.pdf",
    },
    {
        "filename": "Dietary_Guidelines_for_Americans_2020-2025.pdf",
        "title": "Dietary Guidelines for Americans 2020-2025",
        "url": "https://www.dietaryguidelines.gov/sites/default/files/2020-12/Dietary_Guidelines_for_Americans_2020-2025.pdf",
    },
    {
        "filename": "WHO_Diabetes_and_Hypertension_Management_Manual.pdf",
        "title": "WHO Diabetes and Hypertension Management Manual",
        "url": "https://extranet.who.int/ncdccs/Data/DMA_B6_Diabetes%20and%20Hypertension%20Management%20Manual%2015%20Mar%202011-%20Final2%5B3%5D.pdf",
    },
]

DOWNLOAD_DIR = Path(__file__).resolve().parent.parent / "data" / "knowledge_base"


def _download(url: str, dest: Path) -> bool:
    if dest.exists() and dest.stat().st_size > 0:
        logger.info("Already downloaded: %s", dest.name)
        return True
    try:
        with httpx.Client(follow_redirects=True, timeout=60) as client:
            resp = client.get(url, headers={"User-Agent": "Mozilla/5.0 (NutriLens knowledge-base seeder)"})
            resp.raise_for_status()
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(resp.content)
        logger.info("Downloaded %s (%d bytes)", dest.name, dest.stat().st_size)
        return True
    except Exception as exc:
        logger.warning("Could not download %s (%s) -- skipping this source. You can also download it "
                        "yourself and drop it into %s, or upload it via the app's Documents page instead.",
                        dest.name, exc, DOWNLOAD_DIR)
        return False


async def _seed_for_user(db, user: User, embedding_model: str | None) -> None:
    service = IngestionService(storage_service, get_embedding_provider(embedding_model))
    for source in SOURCE_DOCUMENTS:
        local_path = DOWNLOAD_DIR / source["filename"]
        if not local_path.exists():
            continue

        existing = db.scalar(
            select(Document).where(
                Document.owner_id == user.id,
                Document.source == KB_SOURCE_TAG,
                Document.filename == source["filename"],
            )
        )
        if existing and existing.status == "ready":
            logger.info("Already seeded for %s: %s", user.email, source["title"])
            continue

        content = local_path.read_bytes()
        try:
            metadata = extract_pdf(content)
        except ValueError as exc:
            logger.warning("Skipping unreadable PDF %s: %s", source["filename"], exc)
            continue

        storage_path = f"{user.id}/{uuid4()}-{source['filename']}"
        stored_path = await storage_service.upload(storage_path, content)

        if existing:
            document = existing
            document.storage_path = stored_path
            document.status = "uploaded"
            document.error_message = None
        else:
            document = Document(
                owner_id=user.id, filename=source["filename"], storage_path=stored_path,
                source=KB_SOURCE_TAG, author=metadata.author or source["title"],
                page_count=metadata.page_count, file_size=len(content), status="uploaded",
            )
            db.add(document)
        db.commit()
        db.refresh(document)

        try:
            await service.ingest(db, document)
            logger.info("Seeded for %s: %s (%d chunks)", user.email, source["title"], document.chunk_count)
        except Exception:
            logger.exception("Ingestion failed for %s / %s", user.email, source["title"])


async def main() -> None:
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    for source in SOURCE_DOCUMENTS:
        _download(source["url"], DOWNLOAD_DIR / source["filename"])

    if not any((DOWNLOAD_DIR / s["filename"]).exists() for s in SOURCE_DOCUMENTS):
        logger.warning("No guideline PDFs were available to seed (all downloads failed or were blocked). "
                        "Nothing to ingest this run -- the app still works, it'll just rely on PDFs you upload yourself.")
        return

    db = SessionLocal()
    try:
        users = list(db.scalars(select(User)))
        if not users:
            logger.warning("No users exist yet -- open the app once (it auto-creates the guest user on first "
                            "request), then re-run this script.")
            return
        for user in users:
            user_settings = db.scalar(select(UserSettings).where(UserSettings.owner_id == user.id))
            embedding_model = user_settings.embedding_model if user_settings else None
            await _seed_for_user(db, user, embedding_model)
    finally:
        db.close()

    logger.info("Done. The Diet Plan Generator's citations should now draw on these guideline documents "
                 "alongside anything you've uploaded yourself.")


if __name__ == "__main__":
    asyncio.run(main())
