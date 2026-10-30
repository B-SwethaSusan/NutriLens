import json

INTENTS = ["diet_plan", "symptom_check", "progress_check", "food_photo", "home_remedy", "general_chat"]

SYSTEM_PROMPT = """You route a user's message to ONE of these intents (use the string exactly):
- diet_plan: the user wants a diet/meal plan, calorie or macro targets, or to update their health profile
- symptom_check: the user is describing a symptom, condition, or diagnosis and wants it factored into their diet
- progress_check: the user is logging or asking about their weight/progress trend over time
- food_photo: the user is asking about analyzing a food photo/image for nutrition
- home_remedy: the user wants a traditional/household remedy for a minor ailment (e.g. cold, cough, indigestion, headache), or wants to share one
- general_chat: anything else, including general document Q&A

Respond with ONLY JSON: {"intent": "<one of the above>", "confidence": "<low|medium|high>"}
"""


def build_messages(message: str) -> list[dict[str, str]]:
    return [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": message}]


_KEYWORD_RULES = {
    "food_photo": ["photo", "picture", "image", "snap", "upload a pic"],
    "progress_check": ["weight log", "progress", "trend", "how am i doing", "lost weight", "gained weight"],
    "diet_plan": ["diet plan", "meal plan", "calories", "macro", "what should i eat"],
    "home_remedy": ["home remedy", "remedy", "kitchen remedy", "natural remedy", "grandma", "household cure"],
    "symptom_check": ["i have", "diagnosed", "symptom", "condition", "pcos", "diabetes", "thyroid", "hypertension", "kidney"],
}


def keyword_fallback(message: str) -> str:
    text = message.lower()
    for intent, keywords in _KEYWORD_RULES.items():
        if any(kw in text for kw in keywords):
            return intent
    return "general_chat"


def try_parse(raw: str) -> str | None:
    text = raw.strip().strip("`")
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        return None
    try:
        data = json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None
    intent = data.get("intent")
    return intent if intent in INTENTS else None
