"""
NasipQuest Bot Configuration
"""
import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


# Bot dizinindeki .env dosyasını manuel oku
BOT_DIR = Path(__file__).parent
ENV_FILE = BOT_DIR / ".env"

# .env dosyasını manuel olarak oku
if ENV_FILE.exists():
    with open(ENV_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                # Environment variable olarak set et (eğer zaten set edilmemişse)
                if key not in os.environ:
                    os.environ[key] = value


class BotConfig(BaseSettings):
    """Bot configuration from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=None,  # Manuel okuduk, buraya gerek yok
        case_sensitive=False,
        extra="ignore",
    )
    
    # Telegram Bot Token (BotFather'dan alınır)
    BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    
    # NovaCore API URL
    NOVACORE_URL: str = os.getenv("NOVACORE_URL", "http://localhost:8000")
    
    # Bridge Token (NovaCore .env'deki TELEGRAM_BRIDGE_TOKEN ile aynı olmalı)
    BRIDGE_TOKEN: str = os.getenv("TELEGRAM_BRIDGE_TOKEN", "")
    
    # Bot settings
    DEBUG: bool = os.getenv("BOT_DEBUG", "false").lower() == "true"


config = BotConfig()
