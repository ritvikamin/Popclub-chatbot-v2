from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "POPclub AI Core V2"
    API_V1_STR: str = "/api/v1"

    # AI configs
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-2.5-flash"
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"

    # Vector DB configs
    CHROMA_PERSIST_DIR: str = str(Path(__file__).resolve().parent.parent / "chroma_db")
    CHROMA_COLLECTION_NAME: str = "popclub_knowledge"

    # RAG tuning knobs
    TOP_K: int = 3                    # chunks retrieved per question
    MIN_RELEVANCE_SCORE: float = 0.25  # cosine similarity below this = "not in the docs"
    MAX_HISTORY_MESSAGES: int = 6      # recent chat messages used for follow-ups
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    MAX_UPLOAD_BYTES: int = 1_000_000

    # Protects the admin (upload) endpoint. Empty = admin endpoints disabled.
    ADMIN_API_KEY: str = ""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()
