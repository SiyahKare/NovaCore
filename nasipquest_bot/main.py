"""
NasipQuest Telegram Bot - Main Entry Point
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from .config import config
from .handlers import router
from .handlers_marketplace import router as marketplace_router
from .handlers_quest_proof import router as quest_proof_router
from .api_client import api_client

# Logging setup
logging.basicConfig(
    level=logging.DEBUG if config.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    """Bot'u başlat."""
    # Config kontrolü
    if not config.BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN environment variable is required!")
        return
    
    if not config.BRIDGE_TOKEN:
        logger.warning("TELEGRAM_BRIDGE_TOKEN not set. Some features may not work.")
    
    logger.info(f"Starting NasipQuest Bot...")
    logger.info(f"NovaCore URL: {config.NOVACORE_URL}")
    logger.info(f"StoryQuest URL: {config.STORYQUEST_URL}")
    logger.info(f"Debug mode: {config.DEBUG}")
    
    # Bot ve Dispatcher oluştur
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )
    dp = Dispatcher()
    
    # Router'ları ekle (sıra önemli - daha spesifik handler'lar önce)
    dp.include_router(quest_proof_router)  # Text handler - command'lerden önce
    dp.include_router(marketplace_router)
    dp.include_router(router)  # Command handler'lar
    
    try:
        # Bot'u başlat
        logger.info("Bot is running...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.error(f"Bot error: {e}", exc_info=True)
    finally:
        # Cleanup
        await api_client.close()
        await bot.session.close()
        logger.info("Bot stopped.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")

