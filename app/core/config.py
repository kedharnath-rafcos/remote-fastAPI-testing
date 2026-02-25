"""
Application configuration using Pydantic Settings.
Simple, single-file configuration for all environments.
"""
import os
from pydantic import BaseSettings, root_validator, validator
from typing import Optional


def _resolve_environment() -> str:
    """Resolve active app environment from process env."""
    return os.getenv("ENVIRONMENT", "development").strip().lower()


def _resolve_env_file() -> str:
    """Resolve env file path from active environment."""
    environment = _resolve_environment()
    env_map = {
        "development": ".env.development",
        "staging": ".env.staging",
        "production": ".env.production",
    }
    return env_map.get(environment, ".env.development")


class Settings(BaseSettings):
    """Application settings loaded from environment-specific .env files."""
    
    # Application Settings
    APP_NAME: str = "EduSportsConnect API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Database Settings
    DATABASE_URL: str
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_PRE_PING: bool = True
    DATABASE_POOL_RECYCLE: int = 3600
    DB_INIT_ON_STARTUP: bool = True
    DB_REQUIRED_ON_STARTUP: bool = True
    
    # CORS Settings
    ALLOWED_ORIGINS: str = "*"
    
    # Security Settings
    SECRET_KEY: Optional[str] = None
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AWS S3 Settings
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "eu-north-1"
    AWS_S3_BUCKET_NAME: str = "sports-images-test"
    AWS_S3_MAX_FILE_SIZE: int = 10485760  # 10MB in bytes
    AWS_S3_ALLOWED_EXTENSIONS: str = "jpg,jpeg,png,gif,webp"

    @validator("ENVIRONMENT")
    def validate_environment(cls, value: str) -> str:
        """Normalize and validate environment value."""
        normalized = value.strip().lower()
        allowed = {"development", "staging", "production"}
        if normalized not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of: {', '.join(sorted(allowed))}")
        return normalized

    @root_validator
    def validate_production_safety(cls, values: dict) -> dict:
        """Enforce secure settings when running in production."""
        environment = values.get("ENVIRONMENT", "development")
        if environment != "production":
            return values

        if values.get("DEBUG"):
            raise ValueError("DEBUG must be False in production")

        secret_key = (values.get("SECRET_KEY") or "").strip()
        if not secret_key or "change-in-production" in secret_key:
            raise ValueError("SECRET_KEY must be set to a strong value in production")

        allowed_origins = (values.get("ALLOWED_ORIGINS") or "").strip()
        if not allowed_origins or allowed_origins == "*":
            raise ValueError("ALLOWED_ORIGINS must be explicitly configured in production")

        return values
    
    @property
    def cors_origins(self) -> list[str]:
        """Get CORS origins as a list."""
        if self.ALLOWED_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    @property
    def s3_allowed_extensions(self) -> list[str]:
        """Get allowed file extensions as a list."""
        return [ext.strip() for ext in self.AWS_S3_ALLOWED_EXTENSIONS.split(",")]
    
    class Config:
        """Pydantic config."""
        env_file = _resolve_env_file()
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()
