"""
Application configuration using Pydantic Settings.
Simple, single-file configuration for all environments.
"""
from pydantic import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from .env file."""
    
    # Application Settings
    APP_NAME: str = "EduSportsConnect API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # Database Settings
    DATABASE_URL: str
    DATABASE_ECHO: bool = True
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_PRE_PING: bool = True
    DATABASE_POOL_RECYCLE: int = 3600
    
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
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()
