from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=120)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    email: EmailStr
    full_name: str | None
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    user: UserRead


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    filename: str
    source: str | None
    author: str | None
    page_count: int
    chunk_count: int
    file_size: int
    status: str
    error_message: str | None
    created_at: datetime
    updated_at: datetime | None


class DocumentUpdate(BaseModel):
    filename: str | None = Field(default=None, min_length=1, max_length=512)
    source: str | None = None


class IngestResponse(BaseModel):
    document_id: str
    status: str
    message: str


class IngestRequest(BaseModel):
    document_id: str


class Citation(BaseModel):
    filename: str
    page_number: int
    chunk_number: int
    similarity: float


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    conversation_id: str | None = None
    stream: bool = False


class ChatResponse(BaseModel):
    conversation_id: str
    answer: str
    citations: list[Citation]


class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    role: str
    content: str
    citations: list[dict[str, Any]] | None
    created_at: datetime


class ConversationRead(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime | None
    messages: list[MessageRead] = []


class SettingsRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    chunk_size: int
    chunk_overlap: int
    top_k: int
    temperature: float
    llm_model: str
    embedding_model: str


class SettingsUpdate(BaseModel):
    chunk_size: int = Field(default=1000, ge=200, le=5000)
    chunk_overlap: int = Field(default=200, ge=0, le=1000)
    top_k: int = Field(default=5, ge=1, le=20)
    temperature: float = Field(default=0.2, ge=0, le=1)
    llm_model: str = Field(default="mistral-small-latest", min_length=1, max_length=120)
    embedding_model: str = Field(default="models/text-embedding-004", min_length=1, max_length=160)
