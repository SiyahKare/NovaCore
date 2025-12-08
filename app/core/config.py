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
    
    # Telethon (Aurora Contact User Bot)
    TELETHON_API_ID: str | None = None  # Telegram API ID (from https://my.telegram.org)
    TELETHON_API_HASH: str | None = None  # Telegram API Hash

    # Treasury
    NCR_TREASURY_USER_ID: int = 1
    
    # Treasury Cap System
    TREASURY_DAILY_NCR_LIMIT: float = 200_000.0
    
    # Treasury damping table (load_ratio -> multiplier)
    # Format: {max_load_ratio: multiplier}
    # Example: 0.70 means "up to 70% load = 1.0x multiplier"
    TREASURY_DAMPING_TABLE: dict[float, float] = {
        0.70: 1.00,  # %70'e kadar full ödeme
        0.85: 0.80,  # %70–85 arası %20 kesinti
        0.95: 0.60,  # %85–95 arası %40 kesinti
        1.00: 0.30,  # %95–100 arası %70 kesinti
        1.10: 0.10,  # %100–110 arası neredeyse yok
    }
    
    # NCR Pricing System
    # Teorik baz fiyat (örn: 1 NCR ≈ 1 TL başlangıç)
    NCR_BASE_PRICE_TRY: float = 1.0
    
    # Fiyatın inebileceği / çıkabileceği bantlar
    NCR_MIN_PRICE_TRY: float = 0.3
    NCR_MAX_PRICE_TRY: float = 3.0
    
    # Treasury coverage hedefi (ör: 1.2 = %120 teminat)
    NCR_TARGET_COVERAGE: float = 1.2
    
    # Coverage farkına duyarlılık katsayısı
    NCR_K_COVERAGE: float = 0.4  # ne kadar agresif tepki verelim?
    
    # Günlük net akıma duyarlılık
    NCR_K_FLOW: float = 0.2
    
    # Fiyat smoothing (0–1 arası, 1 = hiç smoothing yok)
    NCR_SMOOTHING_ALPHA: float = 0.3

    # Redis (opsiyonel)
    REDIS_URL: str = "redis://localhost:6379/0"

    # CORS
    # Default: localhost (dev)
    # Production: Cloudflare subdomain'leri (https://portal.siyahkare.com, https://app.siyahkare.com)
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    # Frontend URL (for bot deep links)
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Backend URL (for webhooks, etc.)
    BACKEND_URL: str = "http://localhost:8000"

    # Logging
    LOG_LEVEL: str = "INFO"
    
    # AI Scoring Service
    OPENAI_API_KEY: str | None = None  # OpenAI API key (from env: OPENAI_API_KEY)
    OPENAI_MODEL: str = "gpt-4o-mini"  # Model name (gpt-4o-mini, gpt-4-turbo-preview, vb.)

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


def get_settings() -> Settings:
    """Get settings instance."""
    # Note: Removed @lru_cache to allow .env changes to be picked up without restart
    return Settings()


settings = get_settings()

