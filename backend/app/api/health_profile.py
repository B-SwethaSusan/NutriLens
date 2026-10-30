from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.config import get_settings
from app.dependencies import CurrentUser, DbSession
from app.models import HealthProfile, UserSettings
from app.models.schemas import (
    Citation, DietPlanResponse, HealthProfileRead, HealthProfileUpdate, MacroTargets, MealTiming,
    SymptomCheckRequest, SymptomCheckResponse,
)
from app.services.app_services import get_diet_plan_service, get_moderation_service, get_symptom_classifier_service

router = APIRouter(tags=["health"])


def _get_profile(db: DbSession, user: CurrentUser) -> HealthProfile | None:
    return db.scalar(select(HealthProfile).where(HealthProfile.owner_id == user.id))


@router.get("/health-profile", response_model=HealthProfileRead)
def get_health_profile(db: DbSession, user: CurrentUser):
    profile = _get_profile(db, user)
    if not profile:
        raise HTTPException(status_code=404, detail="Health profile not set up yet")
    return profile


@router.put("/health-profile", response_model=HealthProfileRead)
async def upsert_health_profile(payload: HealthProfileUpdate, db: DbSession, user: CurrentUser):
    if payload.notes and payload.notes.strip():
        settings = db.scalar(select(UserSettings).where(UserSettings.owner_id == user.id))
        llm_model = settings.llm_model if settings else None
        moderation = await get_moderation_service().check(payload.notes, "a short personal note about diet or health", llm_model)
        if not moderation["allowed"]:
            raise HTTPException(status_code=422, detail=f"Notes couldn't be saved: {moderation['reason']}")

    profile = _get_profile(db, user)
    if not profile:
        profile = HealthProfile(owner_id=user.id, **payload.model_dump())
        db.add(profile)
    else:
        for key, value in payload.model_dump().items():
            setattr(profile, key, value)
    db.commit()
    db.refresh(profile)
    return profile


@router.post("/diet-plan", response_model=DietPlanResponse)
async def generate_diet_plan(db: DbSession, user: CurrentUser):
    profile = _get_profile(db, user)
    if not profile:
        raise HTTPException(status_code=400, detail="Set up your health profile first via PUT /api/health-profile")

    settings = db.scalar(select(UserSettings).where(UserSettings.owner_id == user.id))
    defaults = get_settings()
    top_k = settings.top_k if settings else defaults.top_k
    temperature = settings.temperature if settings else defaults.temperature
    embedding_model = settings.embedding_model if settings else defaults.embedding_model
    llm_model = settings.llm_model if settings else None

    targets, meal_timing, explanation, citations = await get_diet_plan_service().generate(
        db, user, profile, top_k, temperature, embedding_model, llm_model,
    )

    return DietPlanResponse(
        bmr_kcal=targets.bmr_kcal,
        tdee_kcal=targets.tdee_kcal,
        targets=MacroTargets(
            calories_kcal=targets.target_calories_kcal, protein_g=targets.protein_g,
            carbs_g=targets.carbs_g, fat_g=targets.fat_g, fiber_g=targets.fiber_g,
        ),
        meal_timing=[MealTiming(**meal) for meal in meal_timing],
        condition_guidance=targets.condition_guidance,
        explanation=explanation,
        citations=[Citation(**c) for c in citations],
    )


@router.post("/symptom-check", response_model=SymptomCheckResponse)
async def symptom_check(payload: SymptomCheckRequest, db: DbSession, user: CurrentUser):
    """Maps free-text symptom/goal descriptions onto the fixed condition
    taxonomy used by the diet-plan rules engine. Does not write to the
    health profile automatically — the caller decides whether to merge
    `detected_conditions` into their profile via PUT /api/health-profile."""
    settings = db.scalar(select(UserSettings).where(UserSettings.owner_id == user.id))
    llm_model = settings.llm_model if settings else None

    moderation = await get_moderation_service().check(payload.description, "a description of symptoms, a diagnosis, or a health goal", llm_model)
    if not moderation["allowed"]:
        raise HTTPException(status_code=422, detail=f"Couldn't process this input: {moderation['reason']}")

    result = await get_symptom_classifier_service().classify(payload.description, llm_model)
    detected = [c for c in result["detected_conditions"] if c != "none"]
    return SymptomCheckResponse(
        detected_conditions=detected,
        confidence=result["confidence"],
        rationale=result["rationale"],
        suggested_next_step=result["suggested_next_step"],
    )
