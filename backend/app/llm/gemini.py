import httpx

from app.config import get_settings
from app.llm.local import LocalLLMProvider
from app.utils.retry import async_retry


class GeminiProvider:
    """Chat/text generation via Google's Gemini API. Uses the same
    GEMINI_API_KEY already configured for embeddings — no extra key needed.

    Gemini's generateContent API doesn't use the OpenAI-style
    {role, content} message list directly: it wants a separate
    `systemInstruction` plus a `contents` list where roles are "user"/
    "model" (not "assistant"). _convert() does that translation so the
    rest of the app (prompts/*.py, which all build OpenAI-style messages)
    doesn't need to know which provider is active.
    """

    def __init__(self, api_key: str, model: str, base_url: str = "https://generativelanguage.googleapis.com/v1beta"):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.fallback = LocalLLMProvider()

    @staticmethod
    def _convert(messages: list[dict[str, str]]) -> tuple[str | None, list[dict]]:
        system_text = None
        contents = []
        for message in messages:
            role = message["role"]
            text = message["content"]
            if role == "system":
                system_text = text if system_text is None else f"{system_text}\n\n{text}"
            else:
                gemini_role = "model" if role == "assistant" else "user"
                contents.append({"role": gemini_role, "parts": [{"text": text}]})
        return system_text, contents

    @async_retry(attempts=3)
    async def generate(self, messages: list[dict[str, str]], temperature: float = 0.2) -> str:
        if not self.api_key:
            return await self.fallback.generate(messages, temperature)

        system_text, contents = self._convert(messages)
        payload: dict = {"contents": contents, "generationConfig": {"temperature": temperature}}
        if system_text:
            payload["systemInstruction"] = {"parts": [{"text": system_text}]}

        url = f"{self.base_url}/models/{self.model}:generateContent"
        async with httpx.AsyncClient(timeout=60) as client:
            try:
                response = await client.post(url, params={"key": self.api_key}, json=payload)
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                body = exc.response.text[:300]
                raise RuntimeError(
                    f"Gemini API error {exc.response.status_code}: {body}. "
                    "Check that GEMINI_API_KEY in backend/.env is valid and that the model "
                    f"{self.model!r} is available for it (see https://ai.google.dev/gemini-api/docs/models)."
                ) from exc
            except httpx.RequestError as exc:
                raise RuntimeError(f"Could not reach Gemini API at {self.base_url}: {exc}") from exc

            data = response.json()
            candidates = data.get("candidates") or []
            if not candidates:
                # Most commonly: the prompt or response was blocked by Gemini's
                # safety filters, so there's no normal "candidates" content.
                reason = data.get("promptFeedback", {}).get("blockReason", "no candidates returned")
                raise RuntimeError(f"Gemini returned no answer (reason: {reason}).")
            parts = candidates[0].get("content", {}).get("parts", [])
            return "".join(part.get("text", "") for part in parts).strip()


def get_gemini_chat_provider(model: str | None = None):
    settings = get_settings()
    return GeminiProvider(settings.gemini_api_key, model or settings.gemini_chat_model)
