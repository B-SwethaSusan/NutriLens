SYSTEM_PROMPT = """You are a careful nutrition expert.
Answer ONLY using the retrieved context below. Do not use outside knowledge.
If the answer is unavailable in the context, respond exactly:
\"I could not find enough information in the uploaded documents.\"
Be clear and appropriately cautious. Always cite filename and page number after every paragraph using [filename, p. N].
This is educational information, not a diagnosis or individualized medical advice.
"""


def build_context(chunks) -> str:
    return "\n\n".join(
        f"SOURCE {index}: {chunk.filename}, page {chunk.page_number}\n{chunk.text}"
        for index, chunk in enumerate(chunks, 1)
    )


def build_messages(question: str, chunks, history: list[dict[str, str]]) -> list[dict[str, str]]:
    context = build_context(chunks)
    user_message = f"Retrieved context:\n{context or '(no relevant context)'}\n\nQuestion: {question}"
    return [{"role": "system", "content": SYSTEM_PROMPT}, *history[-10:], {"role": "user", "content": user_message}]
