import logging
from collections.abc import AsyncIterator
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.llm.base import LLMProvider
from app.models import Conversation, Message, User
from app.prompts.nutrition import build_messages
from app.services.retrieval import RetrievedChunk, RetrievalService

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(self, retrieval_factory, llm_factory):
        self.retrieval_factory = retrieval_factory
        self.llm_factory = llm_factory

    def _conversation(self, db: Session, user: User | None, conversation_id: str | None) -> Conversation | None:
        if not user:
            return None
        conversation = None
        if conversation_id:
            conversation = db.scalar(select(Conversation).where(Conversation.id == conversation_id, Conversation.owner_id == user.id))
        if not conversation:
            conversation = Conversation(owner_id=user.id, title="New conversation")
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
        return conversation

    async def answer(self, db: Session, user: User | None, question: str, conversation_id: str | None, top_k: int, temperature: float,
                     embedding_model: str | None = None, llm_model: str | None = None):
        conversation = self._conversation(db, user, conversation_id)
        history = [{"role": message.role, "content": message.content} for message in conversation.messages] if conversation else []
        chunks = await self.retrieval_factory(embedding_model).search(db, user.id if user else None, question, top_k)
        messages = build_messages(question, chunks, history)
        answer = await self.llm_factory(llm_model).generate(messages, temperature)
        if conversation:
            user_message = Message(conversation_id=conversation.id, role="user", content=question)
            assistant_message = Message(conversation_id=conversation.id, role="assistant", content=answer, citations=[self.citation(item) for item in chunks])
            db.add_all([user_message, assistant_message])
            conversation.title = question[:80]
            db.commit()
        logger.info("Generated answer conversation=%s citations=%s", conversation.id if conversation else "guest", len(chunks))
        return conversation.id if conversation else (conversation_id or str(uuid4())), answer, chunks

    @staticmethod
    def citation(chunk: RetrievedChunk) -> dict:
        return {"filename": chunk.filename, "page_number": chunk.page_number, "chunk_number": chunk.chunk_number, "similarity": chunk.similarity}

    async def stream_answer(self, answer: str) -> AsyncIterator[str]:
        for word in answer.split(" "):
            yield f"data: {word} \n\n"
        yield "data: [DONE]\n\n"
