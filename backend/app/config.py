from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    PROJECT_NAME: str = "POPclub AI Core V2"
    API_V1_STR: str = "/api/v1"
    
    # AI Configs
    GEMINI_API_KEY: str
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    
    # Vector DB Configs
    CHROMA_PERSIST_DIR: str = str(Path(__file__).resolve().parent.parent / "chroma_db")
    CHROMA_COLLECTION_NAME: str = "popclub_knowledge"

    # Strict configuration setup for environment reading
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()