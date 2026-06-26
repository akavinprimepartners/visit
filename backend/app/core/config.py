"""
Configuration Management
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings"""
    
    # Environment
    ENV: str = "development"
    DEBUG: bool = True
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    LOGS_DIR: Path = BASE_DIR / "logs"
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/akavin.db"
    REDIS_URL: str = "redis://localhost:6379"
    ELASTICSEARCH_URL: str = "http://localhost:9200"
    
    # API
    API_VERSION: str = "v1"
    API_PREFIX: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # OCR
    OCR_ENGINE: str = "paddleocr"  # paddleocr, tesseract, easyocr
    OCR_LANGUAGE: str = "en"
    
    # AI
    AI_MODEL: str = "llama2"
    AI_BASE_URL: str = "http://localhost:11434"
    
    # Storage
    STORAGE_TYPE: str = "local"  # local, s3, gcs
    STORAGE_PATH: Path = DATA_DIR / "storage"
    
    # Search
    SEARCH_ENGINE: str = "elasticsearch"  # elasticsearch, postgres
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings"""
    return Settings()

settings = get_settings()

# Create directories
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.LOGS_DIR.mkdir(parents=True, exist_ok=True)
settings.STORAGE_PATH.mkdir(parents=True, exist_ok=True)
