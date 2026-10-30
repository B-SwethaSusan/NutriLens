import logging

from app.prompts.symptom_classifier import CONDITION_TAXONOMY, build_messages, try_parse

logger = logging.getLogger(__name__)

_KEYWORD_RULES: dict[str, list[str]] = {
    "diabetes": ["diabetes", "diabetic", "blood sugar", "glucose", "insulin", "a1c"],
    "hypertension": ["hypertension", "high blood pressure", "bp high", "blood pressure"],
    "pcos": ["pcos", "polycystic", "irregular periods", "insulin resistance"],
    "thyroid": ["thyroid", "hypothyroid", "hyperthyroid", "tsh"],
    "ckd": ["kidney disease", "ckd", "dialysis", "renal", "creatinine"],
    "gi_issues": ["ibs", "bloating", "acid reflux", "gerd", "stomach pain", "constipation", "diarrhea", "gastritis"],
}


def _keyword_fallback(description: str) -> dict:
    """Deterministic classification used when the LLM is unavailable (no API
    key configured) or its output can't be parsed as JSON. Mirrors the
    project's existing pattern of deterministic local fallbacks for
    providers (see embeddings/local.py, llm/local.py)."""
    text = description.lower()
    detected = [condition for condition, keywords in _KEYWORD_RULES.items() if any(kw in text for kw in keywords)]
    if not detected:
        detected = ["none"]
    return {
        "detected_conditions": detected,
        "confidence": "low",
        "rationale": "Matched by keyword search (LLM classification unavailable); please confirm manually.",
        "suggested_next_step": "Add your condition manually in your health profile, or configure MISTRAL_API_KEY for better detection.",
    }


class SymptomClassifierService:
    def __init__(self, llm_factory):
        self.llm_factory = llm_factory

    async def classify(self, description: str, llm_model: str | None = None) -> dict:
        provider = self.llm_factory(llm_model)
        raw = await provider.generate(build_messages(description), temperature=0.0)
        parsed = try_parse(raw)
        if parsed is None:
            logger.info("Symptom classifier falling back to keyword matching; model output was not parseable JSON")
            return _keyword_fallback(description)
        assert all(c in CONDITION_TAXONOMY for c in parsed["detected_conditions"])
        return parsed
