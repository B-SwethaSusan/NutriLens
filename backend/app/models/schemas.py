from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=120)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    email: EmailStr
    full_name: str | None
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    user: UserRead


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    filename: str
    source: str | None
    author: str | None
    page_count: int
    chunk_count: int
    file_size: int
    status: str
    error_message: str | None
    created_at: datetime
    updated_at: datetime | None


class DocumentUpdate(BaseModel):
    filename: str | None = Field(default=None, min_length=1, max_length=512)
    source: str | None = None


class IngestResponse(BaseModel):
    document_id: str
    status: str
    message: str


class IngestRequest(BaseModel):
    document_id: str


class Citation(BaseModel):
    filename: str
    page_number: int
    chunk_number: int
    similarity: float


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    conversation_id: str | None = None
    stream: bool = False


class ChatResponse(BaseModel):
    conversation_id: str
    answer: str
    citations: list[Citation]


class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    role: str
    content: str
    citations: list[dict[str, Any]] | None
    created_at: datetime


class ConversationRead(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime | None
    messages: list[MessageRead] = []


class SettingsRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    chunk_size: int
    chunk_overlap: int
    top_k: int
    temperature: float
    llm_model: str | None
    embedding_model: str


ActivityLevel = Literal["sedentary", "light", "moderate", "active", "very_active"]
Goal = Literal["lose", "gain", "maintain"]
Sex = Literal["male", "female"]


class HealthProfileUpdate(BaseModel):
    age: int = Field(ge=10, le=100)
    sex: Sex
    height_cm: float = Field(ge=100, le=250)
    weight_kg: float = Field(ge=25, le=300)
    activity_level: ActivityLevel = "moderate"
    goal: Goal = "maintain"
    goal_rate_kg_per_week: float = Field(default=0.0, ge=0, le=1.5)
    conditions: list[str] = Field(default_factory=list)
    allergies: list[str] = Field(default_factory=list)
    dietary_preferences: list[str] = Field(default_factory=list)
    notes: str | None = Field(default=None, max_length=2000)


class HealthProfileRead(HealthProfileUpdate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime
    updated_at: datetime | None


class MacroTargets(BaseModel):
    calories_kcal: int
    protein_g: int
    carbs_g: int
    fat_g: int
    fiber_g: int


class MealTiming(BaseModel):
    meal: str
    time_window: str
    calories_kcal: int
    guidance: str


class DietPlanResponse(BaseModel):
    bmr_kcal: int
    tdee_kcal: int
    targets: MacroTargets
    meal_timing: list[MealTiming]
    condition_guidance: list[str]
    explanation: str
    citations: list[Citation]
    disclaimer: str = (
        "This plan is AI-generated educational guidance based on general nutrition "
        "science and the retrieved reference documents. It is not a medical diagnosis "
        "or individualized clinical advice. Please consult a registered dietitian or "
        "physician before making significant dietary changes, especially with an "
        "existing medical condition."
    )


class SymptomCheckRequest(BaseModel):
    description: str = Field(min_length=3, max_length=2000)


class SymptomCheckResponse(BaseModel):
    detected_conditions: list[str]
    confidence: Literal["low", "medium", "high"]
    rationale: str
    suggested_next_step: str


class ProgressLogCreate(BaseModel):
    log_date: datetime
    weight_kg: float | None = Field(default=None, ge=20, le=400)
    waist_cm: float | None = Field(default=None, ge=30, le=250)
    adherence_pct: float | None = Field(default=None, ge=0, le=100)
    note: str | None = Field(default=None, max_length=1000)


class ProgressLogRead(ProgressLogCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime


class ProgressTrend(BaseModel):
    slope_kg_per_week: float
    projected_weight_kg: float
    projected_date: datetime | None
    on_track: bool | None
    message: str


class ProgressSummary(BaseModel):
    logs: list[ProgressLogRead]
    trend: ProgressTrend | None


class NutritionPer100g(BaseModel):
    calories_kcal: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fibre_g: float | None = None  # None = not known for this dish (shown as "—", never guessed)
    sugar_g: float | None = None


class ServingUnit(BaseModel):
    label: str
    grams: float


class NutritionSource(BaseModel):
    name: str
    code: str | None = None
    recipe: str | None = None


class FoodDish(BaseModel):
    name: str
    region: str
    category: str
    diet: Literal["veg", "non-veg", "varies"]
    description: str
    ingredients: list[str]
    food_groups: list[str]
    per_100g: NutritionPer100g | None
    default_serving: ServingUnit
    units: list[ServingUnit]
    source: NutritionSource
    reliability: Literal["high", "medium", "low", "unavailable"]
    reliability_note: str | None = None


class FoodPrediction(BaseModel):
    label: str
    name: str
    confidence: float  # temperature-calibrated, 0-1


class FoodModelInfo(BaseModel):
    calibrated: bool
    num_classes: int
    reject_below: float
    high_at: float
    heldout_top1_accuracy: float | None = None


class FoodPhotoResponse(BaseModel):
    status: Literal["recognized", "uncertain"]
    confidence_level: Literal["high", "medium", "low"]
    top_prediction: FoodPrediction
    alternatives: list[FoodPrediction]
    dishes: dict[str, FoodDish]  # catalogue entries for the top prediction + alternatives
    model_info: FoodModelInfo
    note: str


class FoodDishListItem(FoodDish):
    label: str


class HomeRemedyCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    problem_tags: list[str] = Field(min_length=1, max_length=10)
    ingredients: list[str] = Field(min_length=1, max_length=20)
    instructions: str = Field(min_length=10, max_length=2000)
    caution: str | None = Field(default=None, max_length=500)
    language: str = Field(default="en", max_length=8)


class HomeRemedyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    title: str
    problem_tags: list[str]
    ingredients: list[str]
    instructions: str
    caution: str | None
    language: str
    source: Literal["curated", "community"]
    upvotes: int
    created_at: datetime


class HomeRemedySubmitResponse(BaseModel):
    remedy: HomeRemedyRead | None
    moderation: dict


class AgentAskRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    conversation_id: str | None = None


class AgentAskResponse(BaseModel):
    agent: str
    content: Any
    warnings: list[str] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)


class SettingsUpdate(BaseModel):
    chunk_size: int = Field(default=1000, ge=200, le=5000)
    chunk_overlap: int = Field(default=200, ge=0, le=1000)
    top_k: int = Field(default=5, ge=1, le=20)
    temperature: float = Field(default=0.2, ge=0, le=1)
    llm_model: str | None = Field(default=None, max_length=120)
    embedding_model: str = Field(default="models/text-embedding-004", min_length=1, max_length=160)
