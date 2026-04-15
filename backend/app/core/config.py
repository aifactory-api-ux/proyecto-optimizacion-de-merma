"""
Application Configuration

Centralized configuration management using environment variables.
Loads and validates all application settings with pydantic-settings.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables.
    
    All sensitive configuration should be provided via environment variables.
    The application will fail to start if required variables are missing.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application Settings
    APP_NAME: str = Field(
        default="Merma Optimization API",
        description="Application name"
    )
    APP_VERSION: str = Field(
        default="1.0.0",
        description="Application version"
    )
    DEBUG: bool = Field(
        default=False,
        description="Enable debug mode"
    )
    API_PREFIX: str = Field(
        default="/api/v1",
        description="API prefix for all routes"
    )
    
    # Database Settings
    POSTGRES_HOST: str = Field(
        description="PostgreSQL database host"
    )
    POSTGRES_PORT: int = Field(
        default=5432,
        description="PostgreSQL database port"
    )
    POSTGRES_USER: str = Field(
        description="PostgreSQL database user"
    )
    POSTGRES_PASSWORD: str = Field(
        description="PostgreSQL database password"
    )
    POSTGRES_DB: str = Field(
        description="PostgreSQL database name"
    )
    
    @property
    def DATABASE_URL(self) -> str:
        """Generate async database URL for SQLAlchemy."""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    @property
    def DATABASE_URL_SYNC(self) -> str:
        """Generate sync database URL for SQLAlchemy (for migrations)."""
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    # Database Pool Settings
    DB_POOL_SIZE: int = Field(
        default=10,
        description="Database connection pool size"
    )
    DB_MAX_OVERFLOW: int = Field(
        default=20,
        description="Maximum overflow connections"
    )
    DB_POOL_TIMEOUT: int = Field(
        default=30,
        description="Pool connection timeout in seconds"
    )
    
    # Redis Settings
    REDIS_HOST: str = Field(
        description="Redis cache host"
    )
    REDIS_PORT: int = Field(
        default=6379,
        description="Redis cache port"
    )
    REDIS_PASSWORD: Optional[str] = Field(
        default=None,
        description="Redis password (if required)"
    )
    REDIS_DB: int = Field(
        default=0,
        description="Redis database number"
    )
    REDIS_DECODE_RESPONSES: bool = Field(
        default=True,
        description="Decode Redis responses to Python types"
    )
    CACHE_DEFAULT_TTL: int = Field(
        default=300,
        description="Default cache TTL in seconds"
    )
    
    @property
    def REDIS_URL(self) -> str:
        """Generate Redis connection URL."""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # JWT Settings
    JWT_SECRET_KEY: str = Field(
        description="Secret key for JWT token generation"
    )
    JWT_ALGORITHM: str = Field(
        default="HS256",
        description="Algorithm for JWT token signing"
    )
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="JWT token expiration in minutes"
    )
    
    # AWS Settings
    AWS_REGION: str = Field(
        default="us-east-1",
        description="AWS region for services"
    )
    AWS_ACCESS_KEY_ID: Optional[str] = Field(
        default=None,
        description="AWS access key for S3"
    )
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(
        default=None,
        description="AWS secret key for S3"
    )
    AWS_S3_BUCKET: Optional[str] = Field(
        default=None,
        description="S3 bucket name for data storage"
    )
    
    # CORS Settings
    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins"
    )
    
    # Logging Settings
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level"
    )
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format"
    )
    
    # Business Settings
    PILOT_STORES: list[int] = Field(
        default=[1, 2, 3],
        description="List of pilot store IDs"
    )
    DEFAULT_WASTE_THRESHOLD_PERCENT: float = Field(
        default=5.0,
        description="Default waste threshold percentage"
    )
    DEMAND_PREDICTION_DAYS: int = Field(
        default=7,
        description="Number of days to predict demand"
    )


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings instance.
    
    Returns:
        Settings: Application settings configuration
    """
    return settings
