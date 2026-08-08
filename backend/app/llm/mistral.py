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
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"model": self.model, "messages": messages, "temperature": temperature, "stream": False},
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]


def get_llm_provider(model: str | None = None):
    settings = get_settings()
    return MistralProvider(settings.mistral_api_key, model or settings.mistral_model, settings.mistral_base_url)
