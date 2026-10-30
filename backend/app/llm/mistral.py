import httpx

from app.config import get_settings
from app.llm.local import LocalLLMProvider
from app.utils.retry import async_retry


class MistralProvider:
    def __init__(self, api_key: str, model: str, base_url: str):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.fallback = LocalLLMProvider()

    @async_retry(attempts=3)
    async def generate(self, messages: list[dict[str, str]], temperature: float = 0.2) -> str:
        if not self.api_key:
            return await self.fallback.generate(messages, temperature)
        async with httpx.AsyncClient(timeout=60) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={"model": self.model, "messages": messages, "temperature": temperature, "stream": False},
                )
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                # Previously this exception crashed straight through to an
                # unhandled 500 with no detail message, which is why Chat
                # and "Generate my diet plan" both showed a generic
                # "Something went wrong" error. Now it carries the real
                # reason (e.g. 401 = bad/invalid MISTRAL_API_KEY) up to the
                # API response.
                body = exc.response.text[:300]
                raise RuntimeError(
                    f"Mistral API error {exc.response.status_code}: {body}. "
                    "Check that MISTRAL_API_KEY in backend/.env is a valid, current key from "
                    "https://console.mistral.ai/api-keys."
                ) from exc
            except httpx.RequestError as exc:
                raise RuntimeError(f"Could not reach Mistral API at {self.base_url}: {exc}") from exc
            return response.json()["choices"][0]["message"]["content"]


def get_llm_provider(model: str | None = None):
    """Single entry point every service uses to get the active LLM
    provider. Which one is "active" is controlled by LLM_PROVIDER in
    backend/.env ("gemini" or "mistral") — switching providers (e.g. if one
    is rate-limited) is a one-line .env change, no code change needed."""
    settings = get_settings()
    if settings.llm_provider == "gemini":
        from app.llm.gemini import get_gemini_chat_provider

        return get_gemini_chat_provider(model)
    return MistralProvider(settings.mistral_api_key, model or settings.mistral_model, settings.mistral_base_url)
