class LocalLLMProvider:
    model = "local-development-model"

    async def generate(self, messages: list[dict[str, str]], temperature: float = 0.2) -> str:
        context = next((item["content"] for item in messages if item["role"] == "user"), "")
        question = context.split("Question:", 1)[-1].strip().split("\n", 1)[0]
        return (
            "I could not call the configured language model in local mode. "
            f"Your question was: {question}. Configure MISTRAL_API_KEY to generate an answer from the retrieved context."
        )
