from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select

from app.dependencies import CurrentUser, DbSession
from app.models import HomeRemedy, UserSettings
from app.models.schemas import HomeRemedyCreate, HomeRemedyRead, HomeRemedySubmitResponse
from app.services.app_services import get_moderation_service
from app.services.remedies import RemedyService

router = APIRouter(tags=["remedies"])


def _llm_model(db: DbSession, user: CurrentUser) -> str | None:
    settings = db.scalar(select(UserSettings).where(UserSettings.owner_id == user.id))
    return settings.llm_model if settings else None


@router.get("/remedies", response_model=list[HomeRemedyRead])
def search_remedies(db: DbSession, query: str | None = Query(default=None), tag: str | None = Query(default=None)):
    return RemedyService.search(db, query, tag)


@router.get("/remedies/{remedy_id}", response_model=HomeRemedyRead)
def get_remedy(remedy_id: str, db: DbSession):
    remedy = db.scalar(select(HomeRemedy).where(HomeRemedy.id == remedy_id, HomeRemedy.status == "approved"))
    if not remedy:
        raise HTTPException(status_code=404, detail="Remedy not found")
    return remedy


@router.post("/remedies", response_model=HomeRemedySubmitResponse)
async def submit_remedy(payload: HomeRemedyCreate, db: DbSession, user: CurrentUser):
    """Community remedy submission, gated by the multilingual moderation
    check: rejects abusive content and content that doesn't actually look
    like a home remedy (spam/gibberish/off-topic), in whichever language it
    was written in."""
    llm_model = _llm_model(db, user)
    combined_text = f"{payload.title}\n{payload.instructions}"
    moderation = await get_moderation_service().check(combined_text, "a traditional home remedy: a title and step-by-step instructions using kitchen ingredients", llm_model)

    if not moderation["allowed"]:
        return HomeRemedySubmitResponse(remedy=None, moderation=moderation)

    remedy = HomeRemedy(
        **payload.model_dump(), source="community", status="approved",
        moderation_note=moderation.get("reason"), submitted_by=user.id,
    )
    db.add(remedy)
    db.commit()
    db.refresh(remedy)
    return HomeRemedySubmitResponse(remedy=HomeRemedyRead.model_validate(remedy), moderation=moderation)


@router.post("/remedies/{remedy_id}/upvote", response_model=HomeRemedyRead)
def upvote_remedy(remedy_id: str, db: DbSession):
    remedy = db.scalar(select(HomeRemedy).where(HomeRemedy.id == remedy_id, HomeRemedy.status == "approved"))
    if not remedy:
        raise HTTPException(status_code=404, detail="Remedy not found")
    remedy.upvotes += 1
    db.commit()
    db.refresh(remedy)
    return remedy
