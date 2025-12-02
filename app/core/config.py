"""
NovaCore Configuration
"""
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """NovaCore settings from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Environment
    ENV: Literal["dev", "staging", "prod"] = "dev"

    # Database
    # Note: Docker container uses port 5433 externally (5432 is used by other services)
    DATABASE_URL: str = "postgresql+asyncpg://novacore:novacore@localhost:5433/novacore"
    DATABASE_URL_SYNC: str = "postgresql://novacore:novacore@localhost:5433/novacore"

    # JWT
    JWT_SECRET: str = "dev-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 10080  # 7 days

    # Telegram (v0.2)
    TELEGRAM_BOT_TOKEN: str = "placeholder"
    TELEGRAM_BRIDGE_TOKEN: str | None = None  # Bot ↔ NovaCore servis token
    TELEGRAM_LINK_SECRET: str | None = None  # Start param HMAC secret (defaults to JWT_SECRET)

    # Treasury
    NCR_TREASURY_USER_ID: int = 1

    # Redis (opsiyonel)
    REDIS_URL: str = "redis://localhost:6379/0"

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    # Logging
    LOG_LEVEL: str = "INFO"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins string to list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def is_dev(self) -> bool:
        return self.ENV == "dev"

    @property
    def is_prod(self) -> bool:
        return self.ENV == "prod"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()

