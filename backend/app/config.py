from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Nutrition RAG Agent"
    environment: Literal["development", "test", "production"] = "development"
    debug: bool = False
    api_prefix: str = "/api"
    secret_key: str = Field(default="change-me-in-production", min_length=16)
    access_token_expire_minutes: int = 60 * 24
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    database_url: str = "sqlite:///./nutrition_rag.db"
    supabase_url: str = ""
    supabase_key: str = ""
    supabase_service_key: str = ""
    supabase_storage_bucket: str = "nutrition-pdfs"

    mistral_api_key: str = ""
    mistral_model: str = "mistral-small-latest"
    mistral_base_url: str = "https://api.mistral.ai/v1"
    gemini_api_key: str = ""
    embedding_model: str = "models/text-embedding-004"
    embedding_dimensions: int = 768

    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k: int = 5
    temperature: float = 0.2
    max_upload_size_mb: int = 100
    rate_limit_per_minute: int = 60
    redis_url: str = ""

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def allowed_origins(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]

    @field_validator("chunk_overlap")
    @classmethod
    def overlap_smaller_than_chunk(cls, value: int, info):
        chunk_size = info.data.get("chunk_size", 1000)
        if value >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
