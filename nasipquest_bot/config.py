"""
NasipQuest Bot Configuration
"""
import os
from pathlib import Path
from dotenv import load_dotenv


# .env dosyasını yükle (NovaCore root dizininden)
def load_env():
    """NovaCore root dizinindeki .env dosyasını yükle."""
    current = Path(__file__).resolve()
    # nasipquest_bot/config.py -> NovaCore/.env
    root = current.parent.parent
    env_file = root / ".env"
    if env_file.exists():
        load_dotenv(env_file, override=False)
    else:
        # Fallback: mevcut dizinde ara
        load_dotenv(".env", override=False)


# .env dosyasını yükle
load_env()


class BotConfig:
    """Bot configuration from environment variables."""
    
    # Telegram Bot Token (BotFather'dan alınır)
    BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    
    # NovaCore API URL
    NOVACORE_URL: str = os.getenv("NOVACORE_URL", "http://localhost:8000")
    
    # Frontend URL (Citizen Portal)
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # StoryQuest Engine URL (Film Motoru API)
    STORYQUEST_URL: str = os.getenv("STORYQUEST_URL", "https://storyquest.siyahkare.com")
    
    # Bridge Token (NovaCore .env'deki TELEGRAM_BRIDGE_TOKEN ile aynı olmalı)
    BRIDGE_TOKEN: str = os.getenv("TELEGRAM_BRIDGE_TOKEN", "")
    
    # Bot settings
    DEBUG: bool = os.getenv("BOT_DEBUG", "false").lower() == "true"
    
    # Broadcast settings (grup/kanal yayını için)
    BROADCAST_CHANNEL_ID: str = os.getenv("BROADCAST_CHANNEL_ID", "")  # @seferverse veya -100xxx
    BROADCAST_GROUP_ID: str = os.getenv("BROADCAST_GROUP_ID", "")  # Grup ID'si
    
    # Admin groups (botun admin olduğu gruplar - virgülle ayrılmış)
    # Örnek: ADMIN_GROUPS=-1001234567890,-1009876543210
    ADMIN_GROUPS: str = os.getenv("ADMIN_GROUPS", "")  # Grup ID'leri (virgülle ayrılmış)
    
    # Admin groups (botun admin olduğu gruplar - virgülle ayrılmış)
    # Örnek: ADMIN_GROUPS=-1001234567890,-1009876543210
    ADMIN_GROUPS: str = os.getenv("ADMIN_GROUPS", "")  # Grup ID'leri (virgülle ayrılmış)


config = BotConfig()
