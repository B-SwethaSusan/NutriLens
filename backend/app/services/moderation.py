"""Multilingual content moderation for free-text user input.

Primary path: LLM-based classification (Mistral, already integrated), which
can reason across English, Hindi, Telugu, Tamil, and other Indian languages
or code-mixed text without needing a maintained per-language wordlist.

Fallback path (no API key configured, or the model's output can't be
parsed): a small, intentionally minimal English-only keyword check. This is
a deliberately weak last resort, NOT a real multilingual profanity filter —
hand-writing slur lists across many languages isn't something to improvise
well or responsibly. For production-grade offline coverage, plug in a
maintained package/dataset (e.g. a vetted multilingual profanity-detection
library or API) here instead of growing this list.
"""

import logging

from app.prompts.moderation import build_messages, try_parse

logger = logging.getLogger(__name__)

_FALLBACK_BLOCKLIST = {"fuck", "shit", "bastard", "bitch", "asshole", "slut", "whore"}


def _keyword_fallback(text: str) -> dict:
    lowered = text.lower()
    hit = any(word in lowered for word in _FALLBACK_BLOCKLIST)
    return {
        "allowed": not hit,
        "abusive": hit,
        "off_topic": False,  # cannot assess relevance without the LLM; fail open on this axis
        "detected_language": "unknown",
        "reason": "Matched a basic English keyword filter (LLM moderation unavailable); "
        "non-English abusive content would not be caught by this fallback.",
    }


class ModerationService:
    def __init__(self, llm_factory):
        self.llm_factory = llm_factory

    async def check(self, text: str, expected_content: str, llm_model: str | None = None) -> dict:
        if not text or not text.strip():
            return {"allowed": True, "abusive": False, "off_topic": False, "detected_language": "unknown", "reason": "Empty input."}
        provider = self.llm_factory(llm_model)
        raw = await provider.generate(build_messages(text, expected_content), temperature=0.0)
        parsed = try_parse(raw)
        if parsed is None:
            logger.info("Moderation falling back to keyword filter; model output was not parseable JSON")
            return _keyword_fallback(text)
        return parsed
