from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    GEMINI_API_KEY: str = "dummy_key_for_testing"
    MODEL_NAME: str = "models/gemini-2.5-flash"
    EMBEDDING_MODEL: str = "models/gemini-embedding-001"
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50
    COLLECTION_NAME: str = "ai_reports"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

