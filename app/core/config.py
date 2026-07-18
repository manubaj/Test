"""
Application configuration loaded from environment variables / .env.

LLM provider can be switched between Ollama (default, local/open-source)
and OpenAI via ``LLM_PROVIDER`` without changing application code.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central typed settings object (injected across the app)."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "AI Sales Intelligence Platform"
    app_env: str = "development"
    debug: bool = True
    api_prefix: str = "/api/v1"
    secret_key: str = Field(
        default="dev-only-secret-key-change-in-production-32chars",
        min_length=32,
    )
    access_token_expire_minutes: int = 60
    api_key_header: str = "X-API-Key"
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # Database
    database_url: str = (
        "postgresql+asyncpg://aisales:aisales_secret@localhost:5432/aisales"
    )
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "aisales"
    postgres_password: str = "aisales_secret"
    postgres_db: str = "aisales"

    # LLM
    llm_provider: Literal["ollama", "openai"] = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"

    # Embeddings / NLP
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    faiss_index_path: str = "./data/faiss/index"
    spacy_model: str = "en_core_web_sm"

    # Crawler
    crawler_max_pages: int = 8
    crawler_timeout_seconds: int = 30
    crawler_user_agent: str = "AISalesIntelligenceBot/1.0 (+https://localhost)"

    # Rate limiting
    rate_limit_requests: int = 120
    rate_limit_window_seconds: int = 60

    # Bootstrap admin
    bootstrap_admin_email: str = "admin@example.com"
    bootstrap_admin_username: str = "admin"
    bootstrap_admin_password: str = "Admin123!"
    bootstrap_admin_api_key: str = "dev-api-key-change-me"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def strip_origins(cls, value: str) -> str:
        return value.strip() if isinstance(value, str) else value

    @property
    def cors_origin_list(self) -> list[str]:
        """Parse comma-separated CORS origins into a list."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_development(self) -> bool:
        return self.app_env.lower() in {"development", "dev", "local"}


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton for dependency injection."""
    return Settings()
