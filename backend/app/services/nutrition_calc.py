"""Deterministic nutrition-science calculations.

Kept free of any LLM call on purpose: calorie/macro targets must be
reproducible, auditable, and never hallucinated. The RAG/LLM layer only
explains and contextualizes numbers computed here.
"""

from dataclasses import dataclass

from app.models.entities import HealthProfile

_ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
}

# kcal per kg of body mass change (standard ~7700 kcal/kg fat tissue approximation)
_KCAL_PER_KG = 7700

# Condition-specific macro adjustments & meal-timing rules.
# Expressed as overrides/multipliers on top of the baseline split so the
# rules stay composable when a user has more than one condition.
CONDITION_RULES: dict[str, dict] = {
    "diabetes": {
        "carb_pct": 0.40,
        "protein_pct": 0.25,
        "fat_pct": 0.35,
        "meals_per_day": 5,
        "guidance": "Favor low-glycemic-index carbohydrates, distribute carbs evenly across smaller meals, and avoid sugary drinks.",
    },
    "hypertension": {
        "sodium_cap_mg": 1500,
        "guidance": "Limit sodium to under 1,500 mg/day, emphasize potassium-rich vegetables and fruits, and minimize processed/packaged foods.",
    },
    "pcos": {
        "carb_pct": 0.35,
        "protein_pct": 0.30,
        "fat_pct": 0.35,
        "meals_per_day": 4,
        "guidance": "Favor low-glycemic, high-fiber carbohydrates and consistent protein at each meal to help with insulin sensitivity.",
    },
    "thyroid": {
        "guidance": "Ensure adequate iodine and selenium intake (dairy, fish, nuts) and maintain consistent meal timing to support metabolism.",
    },
    "ckd": {
        "protein_pct": 0.15,
        "sodium_cap_mg": 1500,
        "potassium_caution": True,
        "guidance": "Moderate protein intake, limit sodium and potassium-dense foods; follow your nephrologist's specific protein target closely.",
    },
    "gi_issues": {
        "meals_per_day": 5,
        "guidance": "Smaller, more frequent meals with easily digestible foods; identify and avoid personal trigger foods.",
    },
}

_DEFAULT_SPLIT = {"carb_pct": 0.45, "protein_pct": 0.25, "fat_pct": 0.30}


@dataclass
class NutritionTargets:
    bmr_kcal: int
    tdee_kcal: int
    target_calories_kcal: int
    protein_g: int
    carbs_g: int
    fat_g: int
    fiber_g: int
    meals_per_day: int
    condition_guidance: list[str]


def calculate_bmr(profile: HealthProfile) -> float:
    """Mifflin-St Jeor equation."""
    base = 10 * profile.weight_kg + 6.25 * profile.height_cm - 5 * profile.age
    return base + (5 if profile.sex == "male" else -161)


def calculate_tdee(bmr: float, activity_level: str) -> float:
    multiplier = _ACTIVITY_MULTIPLIERS.get(activity_level, _ACTIVITY_MULTIPLIERS["moderate"])
    return bmr * multiplier


def _goal_adjustment_kcal(profile: HealthProfile) -> float:
    if profile.goal == "maintain" or not profile.goal_rate_kg_per_week:
        return 0.0
    weekly_kcal_delta = profile.goal_rate_kg_per_week * _KCAL_PER_KG
    daily_delta = weekly_kcal_delta / 7
    return -daily_delta if profile.goal == "lose" else daily_delta


def _merged_condition_rules(conditions: list[str]) -> dict:
    """Merge rules for all of a user's conditions; later conditions can
    tighten (never loosen) a cap that an earlier condition already set."""
    merged: dict = {}
    guidance: list[str] = []
    for condition in conditions:
        rule = CONDITION_RULES.get(condition)
        if not rule:
            continue
        for key, value in rule.items():
            if key == "guidance":
                guidance.append(value)
                continue
            if key.endswith("_cap_mg") and key in merged:
                merged[key] = min(merged[key], value)
            else:
                merged[key] = value
    merged["guidance"] = guidance
    return merged


def build_targets(profile: HealthProfile) -> NutritionTargets:
    bmr = calculate_bmr(profile)
    tdee = calculate_tdee(bmr, profile.activity_level)
    target_calories = max(1200, tdee + _goal_adjustment_kcal(profile))

    rules = _merged_condition_rules(profile.conditions or [])
    carb_pct = rules.get("carb_pct", _DEFAULT_SPLIT["carb_pct"])
    protein_pct = rules.get("protein_pct", _DEFAULT_SPLIT["protein_pct"])
    fat_pct = rules.get("fat_pct", _DEFAULT_SPLIT["fat_pct"])
    # Normalize in case condition rules don't sum to 1.0
    total_pct = carb_pct + protein_pct + fat_pct
    carb_pct, protein_pct, fat_pct = (p / total_pct for p in (carb_pct, protein_pct, fat_pct))

    protein_g = round((target_calories * protein_pct) / 4)
    carbs_g = round((target_calories * carb_pct) / 4)
    fat_g = round((target_calories * fat_pct) / 9)
    fiber_g = round(14 * (target_calories / 1000))  # ~14g fiber per 1000 kcal, standard dietary guideline

    return NutritionTargets(
        bmr_kcal=round(bmr),
        tdee_kcal=round(tdee),
        target_calories_kcal=round(target_calories),
        protein_g=protein_g,
        carbs_g=carbs_g,
        fat_g=fat_g,
        fiber_g=fiber_g,
        meals_per_day=rules.get("meals_per_day", 3),
        condition_guidance=rules.get("guidance", []),
    )


def build_meal_timing(targets: NutritionTargets) -> list[dict]:
    """Split daily calories across meals with sensible time windows.
    More frequent, smaller meals for conditions that call for it."""
    schedules = {
        3: [("Breakfast", "7:00–8:30 AM", 0.30), ("Lunch", "12:30–1:30 PM", 0.40), ("Dinner", "7:00–8:00 PM", 0.30)],
        4: [("Breakfast", "7:00–8:00 AM", 0.25), ("Lunch", "12:30–1:30 PM", 0.35),
            ("Snack", "4:00–4:30 PM", 0.10), ("Dinner", "7:00–8:00 PM", 0.30)],
        5: [("Breakfast", "7:00–7:30 AM", 0.20), ("Mid-morning snack", "10:00–10:30 AM", 0.10),
            ("Lunch", "1:00–1:30 PM", 0.30), ("Evening snack", "4:30–5:00 PM", 0.10),
            ("Dinner", "7:30–8:00 PM", 0.30)],
    }
    plan = schedules.get(targets.meals_per_day, schedules[3])
    return [
        {
            "meal": name,
            "time_window": window,
            "calories_kcal": round(targets.target_calories_kcal * fraction),
            "guidance": "Keep portions consistent day-to-day to stabilize blood sugar and digestion."
            if targets.meals_per_day >= 4 else "Balance a plate: half vegetables, quarter protein, quarter whole grains.",
        }
        for name, window, fraction in plan
    ]
