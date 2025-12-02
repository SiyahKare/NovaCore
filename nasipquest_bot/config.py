"""
NasipQuest Bot Configuration
"""
import os
from typing import Optional

from pydantic_settings import BaseSettings


class BotConfig(BaseSettings):
    """Bot configuration from environment variables."""
    
    # Telegram Bot Token (BotFather'dan alınır)
    BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    
    # NovaCore API URL
    NOVACORE_URL: str = os.getenv("NOVACORE_URL", "http://localhost:8000")
    
    # Bridge Token (NovaCore .env'deki TELEGRAM_BRIDGE_TOKEN ile aynı olmalı)
    BRIDGE_TOKEN: str = os.getenv("TELEGRAM_BRIDGE_TOKEN", "")
    
    # Bot settings
    DEBUG: bool = os.getenv("BOT_DEBUG", "false").lower() == "true"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


config = BotConfig()

