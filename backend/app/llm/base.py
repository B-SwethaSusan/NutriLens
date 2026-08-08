from typing import Protocol


class LLMProvider(Protocol):
    model: str

    async def generate(self, messages: list[dict[str, str]], temperature: float = 0.2) -> str: ...
