import logging
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, Query, UploadFile, status
from sqlalchemy import func, select

from app.config import get_settings
from app.dependencies import CurrentUser, DbSession
from app.models import Document, DocumentChunk
from app.models.schemas import DocumentRead, DocumentUpdate, IngestRequest, IngestResponse
from app.services.app_services import get_ingestion_service
from app.services.pdf import extract_pdf
from app.services.storage import storage_service

logger = logging.getLogger(__name__)
router = APIRouter(tags=["documents"])


async def _ingest(document_id: str, owner_id: str, chunk_size: int, overlap: int):
    from app.database.session import SessionLocal
    from app.models import UserSettings
    from app.embeddings.gemini import get_embedding_provider
    from app.services.ingestion import IngestionService

    db = SessionLocal()
    try:
        document = db.scalar(select(Document).where(Document.id == document_id, Document.owner_id == owner_id))
        if document:
            user_settings = db.scalar(select(UserSettings).where(UserSettings.owner_id == owner_id))
            configured_chunk_size = user_settings.chunk_size if user_settings else chunk_size
            configured_overlap = user_settings.chunk_overlap if user_settings else overlap
            embedding_model = user_settings.embedding_model if user_settings else None
            service = IngestionService(storage_service, get_embedding_provider(embedding_model))
            await service.ingest(db, document, configured_chunk_size, configured_overlap)
    except Exception:
        logger.exception("Background ingestion failed document=%s", document_id)
    finally:
        db.close()


@router.post("/upload", response_model=DocumentRead, status_code=status.HTTP_202_ACCEPTED)
async def upload_pdf(background_tasks: BackgroundTasks, db: DbSession, user: CurrentUser, file: UploadFile = File(...)):
    settings = get_settings()
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="The uploaded file is empty")
    if len(content) > settings.max_upload_size_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"PDF exceeds the {settings.max_upload_size_mb}MB upload limit")
    try:
        metadata = extract_pdf(content)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    safe_name = file.filename.replace("/", "_").replace("\\", "_")
    storage_path = f"{user.id}/{uuid4()}-{safe_name}"
    stored_path = await storage_service.upload(storage_path, content)
    document = Document(owner_id=user.id, filename=safe_name, storage_path=stored_path, source=safe_name, author=metadata.author,
                        page_count=metadata.page_count, file_size=len(content), status="uploaded")
    db.add(document)
    db.commit()
    db.refresh(document)
    background_tasks.add_task(_ingest, document.id, user.id, settings.chunk_size, settings.chunk_overlap)
    logger.info("Uploaded document id=%s user=%s", document.id, user.id)
    return document


@router.post("/ingest/{document_id}", response_model=IngestResponse)
async def ingest_pdf(document_id: str, background_tasks: BackgroundTasks, db: DbSession, user: CurrentUser):
    document = db.scalar(select(Document).where(Document.id == document_id, Document.owner_id == user.id))
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    settings = get_settings()
    background_tasks.add_task(_ingest, document.id, user.id, settings.chunk_size, settings.chunk_overlap)
    return IngestResponse(document_id=document.id, status="processing", message="Ingestion started")


@router.post("/ingest", response_model=IngestResponse)
async def ingest_document(payload: IngestRequest, background_tasks: BackgroundTasks, db: DbSession, user: CurrentUser):
    return await ingest_pdf(payload.document_id, background_tasks, db, user)


@router.get("/documents", response_model=list[DocumentRead])
def list_documents(db: DbSession, user: CurrentUser, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100)):
    statement = select(Document).where(Document.owner_id == user.id).order_by(Document.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    return list(db.scalars(statement))


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(document_id: str, db: DbSession, user: CurrentUser):
    document = db.scalar(select(Document).where(Document.id == document_id, Document.owner_id == user.id))
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    await storage_service.delete(document.storage_path)
    db.delete(document)
    db.commit()


@router.put("/documents/{document_id}", response_model=DocumentRead)
def update_document(document_id: str, payload: DocumentUpdate, db: DbSession, user: CurrentUser):
    document = db.scalar(select(Document).where(Document.id == document_id, Document.owner_id == user.id))
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    if payload.filename is not None:
        document.filename = payload.filename
    if payload.source is not None:
        document.source = payload.source
    db.commit()
    db.refresh(document)
    return document


@router.get("/documents/stats/summary")
def document_stats(db: DbSession, user: CurrentUser):
    documents = list(db.scalars(select(Document).where(Document.owner_id == user.id)))
    return {"total_pdfs": len(documents), "total_chunks": sum(item.chunk_count for item in documents), "storage_used": sum(item.file_size for item in documents), "recent_uploads": [DocumentRead.model_validate(item) for item in documents[:5]]}
