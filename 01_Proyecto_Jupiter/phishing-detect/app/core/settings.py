from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Carga y valida la configuración de la app desde variables de entorno.
    Define defaults y un punto único de acceso a los settings.
    """

    log_file: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4.1"

    # Postgres
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/phishing_detect"
    db_echo: bool = False

    # Localización
    default_timezone: str = "Europe/Madrid"

    # Proveedores de repuracion (CU-02)
    virustotal_api_key: str | None = None

    # SMTP para envío de alertas por email
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_from: str = ""

    # Redis (Celery broker + backend)
    redis_url: str = "redis://localhost:6379/0"

    # Qdrant (vector store RAG CU-04)
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "phishing_docs"

    # Google Gemini (LLM + embeddings RAG CU-04)
    google_api_key: str = ""
    cu04_similarity_top_k: int = 5
    cu04_chunk_size: int = 1200
    cu04_chunk_overlap: int = 200
    cu04_auto_ingest: bool = True


settings = Settings()
