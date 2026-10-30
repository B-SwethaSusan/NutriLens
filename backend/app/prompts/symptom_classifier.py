import json

CONDITION_TAXONOMY = ["diabetes", "hypertension", "pcos", "thyroid", "ckd", "gi_issues", "none"]

SYSTEM_PROMPT = """You are a triage assistant that maps a user's free-text description of symptoms, diagnoses, or goals \
onto a FIXED set of dietary-relevant condition categories. You do not diagnose; you only route the text to categories \
so a nutrition planner can apply the right dietary rules.

Allowed categories (use ONLY these strings, lowercase, exactly as written):
diabetes, hypertension, pcos, thyroid, ckd, gi_issues, none

Respond with ONLY a single JSON object, no prose, no markdown fences, in this exact shape:
{"detected_conditions": ["<category>", ...], "confidence": "<low|medium|high>", "rationale": "<one sentence>", "suggested_next_step": "<one sentence, always recommend confirming with a doctor/dietitian for anything beyond general wellness>"}

If the text describes no condition relevant to the taxonomy (e.g., "I just want to eat healthier"), return \
detected_conditions: ["none"]. If the text is ambiguous or sounds like it needs clinical evaluation (e.g., severe or \
urgent symptoms), set confidence to "low" and say so in suggested_next_step.
Never include a category not in the allowed list. Never output anything except the JSON object.
"""


def build_messages(description: str) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"User text: {description}"},
    ]


def try_parse(raw: str) -> dict | None:
    """Best-effort JSON extraction: strips markdown fences and surrounding
    prose some models add despite instructions."""
    text = raw.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1 or end < start:
        return None
    try:
        data = json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict) or "detected_conditions" not in data:
        return None
    data["detected_conditions"] = [c for c in data.get("detected_conditions", []) if c in CONDITION_TAXONOMY] or ["none"]
    data.setdefault("confidence", "low")
    data.setdefault("rationale", "")
    data.setdefault("suggested_next_step", "Consider confirming with a doctor or registered dietitian.")
    return data
