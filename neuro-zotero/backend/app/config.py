from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "NeuroZotero"
    DEBUG: bool = True
    API_PREFIX: str = "/api"
    VERSION: str = "0.1.0"
    
    # Database
    DATABASE_URL: str = "sqlite:///./neurozotero.db"
    
    # Ollama Configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama2"
    OLLAMA_TIMEOUT: int = 120
    
    # GGUF Model Configuration
    GGUF_MODEL_PATH: str = "./models"
    GGUF_DEFAULT_MODEL: str = "llama-2-7b-chat.Q4_K_M.gguf"
    GGUF_N_CTX: int = 4096
    GGUF_N_GPU_LAYERS: int = 35
    GGUF_N_THREADS: int = 8
    
    # Vector Database for Semantic Search
    VECTOR_DB_TYPE: str = "chroma"  # Options: chroma, qdrant
    VECTOR_DB_PATH: str = "./vector_db"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
    # File Storage
    UPLOAD_DIR: str = "./uploads"
    PDF_CACHE_DIR: str = "./pdf_cache"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    # Celery (for background tasks)
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Create necessary directories
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.PDF_CACHE_DIR, exist_ok=True)
os.makedirs(settings.GGUF_MODEL_PATH, exist_ok=True)
os.makedirs(settings.VECTOR_DB_PATH, exist_ok=True)
