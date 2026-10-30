"""Reviews another agent's output before it reaches the user.

Deliberately simple, rule-based checks rather than another LLM call: cheap,
fast, deterministic, and auditable — exactly the properties you want for a
guardrail. It never silently blocks content; it annotates with warnings so
the caller (and the user) can see what was flagged.
"""

import re

_DISCLAIMER_MARKER = "not a medical diagnosis"

_MEDICATION_PATTERN = re.compile(
    r"\b(mg|milligram|dosage|dose of|prescri\w+|insulin units)\b", re.IGNORECASE
)


class SafetyAgent:
    @staticmethod
    def review(text: str, allergies: list[str] | None = None) -> list[str]:
        warnings: list[str] = []
        if _DISCLAIMER_MARKER not in text.lower() and "not a diagnosis" not in text.lower() and "not individualized medical advice" not in text.lower():
            warnings.append("Response did not include a medical disclaimer; one was appended.")
        if _MEDICATION_PATTERN.search(text):
            warnings.append("Response referenced medication/dosage-like terms — flagged for human review before trusting any such detail.")
        for allergen in allergies or []:
            if allergen.lower() in text.lower():
                warnings.append(f"Response mentions '{allergen}', which is in the user's allergy list — verify this is a caution, not a suggestion to eat it.")
        return warnings

    @staticmethod
    def ensure_disclaimer(text: str, disclaimer: str) -> str:
        if _DISCLAIMER_MARKER not in text.lower():
            return f"{text}\n\n{disclaimer}"
        return text
