"""
Application configuration management.
"""
import os
from typing import Literal
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "Enterprise Purple Team Platform"
    APP_VERSION: str = "1.0.0"
    ENV: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = True
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://admin:password@localhost:5432/purple_team"
    DB_ECHO: bool = False
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # CORS
        CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173", "http://localhost:8000"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Security
    BCRYPT_LOG_ROUNDS: int = 12
    
    # API Keys (for integrations - Phase 7+)
    VIRUSTOTAL_API_KEY: str = ""
    ALIENVALUT_OTX_API_KEY: str = ""
    ABUSEIPDB_API_KEY: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def database_url_sync(self) -> str:
        """Return synchronous database URL for Alembic."""
        return self.DATABASE_URL.replace("asyncpg://", "postgresql://")


settings = Settings()
