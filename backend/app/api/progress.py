from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.dependencies import CurrentUser, DbSession
from app.models import HealthProfile, ProgressLog, UserSettings
from app.models.schemas import ProgressLogCreate, ProgressLogRead, ProgressSummary, ProgressTrend
from app.services.app_services import get_moderation_service
from app.services.progress import ProgressService

router = APIRouter(tags=["progress"])


@router.post("/progress", response_model=ProgressLogRead, status_code=201)
async def log_progress(payload: ProgressLogCreate, db: DbSession, user: CurrentUser):
    if payload.note and payload.note.strip():
        settings = db.scalar(select(UserSettings).where(UserSettings.owner_id == user.id))
        llm_model = settings.llm_model if settings else None
        moderation = await get_moderation_service().check(payload.note, "a short progress-log note about diet or exercise adherence", llm_model)
        if not moderation["allowed"]:
            raise HTTPException(status_code=422, detail=f"Note couldn't be saved: {moderation['reason']}")

    existing = db.scalar(
        select(ProgressLog).where(ProgressLog.owner_id == user.id, ProgressLog.log_date == payload.log_date)
    )
    if existing:
        for key, value in payload.model_dump().items():
            setattr(existing, key, value)
        db.commit()
        db.refresh(existing)
        return existing
    log = ProgressLog(owner_id=user.id, **payload.model_dump())
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("/progress", response_model=ProgressSummary)
def get_progress(db: DbSession, user: CurrentUser):
    logs = list(db.scalars(select(ProgressLog).where(ProgressLog.owner_id == user.id).order_by(ProgressLog.log_date)))
    profile = db.scalar(select(HealthProfile).where(HealthProfile.owner_id == user.id))
    trend_data = ProgressService.compute_trend(logs, profile)
    return ProgressSummary(
        logs=[ProgressLogRead.model_validate(log) for log in logs],
        trend=ProgressTrend(**trend_data) if trend_data else None,
    )


@router.delete("/progress/{log_id}", status_code=204)
def delete_progress(log_id: str, db: DbSession, user: CurrentUser):
    log = db.scalar(select(ProgressLog).where(ProgressLog.id == log_id, ProgressLog.owner_id == user.id))
    if log:
        db.delete(log)
        db.commit()
