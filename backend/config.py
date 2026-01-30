"""
Configuration for the Phishing Awareness Training application.
Uses environment variables with sensible defaults for development.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings - can override with environment variables."""
    
    # JWT secret key - MUST be changed in production and kept secret!
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    
    # Algorithm used for JWT signing
    ALGORITHM: str = "HS256"
    
    # How long access tokens are valid (in minutes)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # SQLite database URL (file-based, no server needed)
    DATABASE_URL: str = "sqlite:///./phishing_training.db"
    
    # Allow CORS from frontend (adjust for your frontend URL)
    CORS_ORIGINS: list = ["http://localhost:5500", "http://127.0.0.1:5500", "http://localhost:8000", "*"]
    
    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance - only loads once."""
    return Settings()
