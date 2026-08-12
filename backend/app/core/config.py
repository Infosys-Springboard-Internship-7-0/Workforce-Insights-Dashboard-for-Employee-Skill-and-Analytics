"""Centralized backend configuration, loaded from environment variables."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore")

    # App
    app_name: str = Field(default="AI Workforce Assistant Platform")
    app_env: str = Field(default="development")
    log_level: str = Field(default="INFO")
    cors_origins: str = Field(default="http://localhost:5173")

    # LLM (Groq)
    groq_api_key: str = Field(default="")
    groq_model: str = Field(default="openai/gpt-oss-20b")

    # Embeddings
    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")

    # ChromaDB
    chroma_persist_dir: str = Field(default="./data/chroma_db")
    chroma_collection_name: str = Field(default="workforce_documents")

    # RAG tuning
    chunk_size: int = Field(default=800)
    chunk_overlap: int = Field(default=120)
    top_k_chunks: int = Field(default=5)

    # Storage
    documents_dir: str = Field(default="./data/documents")
    datasets_dir: str = Field(default="./data/datasets")

    # Database
    database_url: str = Field(default="sqlite:///./data/platform.db")

    # Security
    jwt_secret_key: str = Field(default="dev-only-insecure-secret-change-me")
    jwt_algorithm: str = Field(default="HS256")
    jwt_expire_minutes: int = Field(default=120)

    # Initial admin seed
    initial_admin_email: str = Field(default="info@gu-saurabh.site")
    initial_admin_password: str = Field(default="change_this_password")
    initial_admin_name: str = Field(default="Platform Admin")

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
