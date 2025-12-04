"""
Telethon Client - Aurora Contact Telegram User Bot
Business Hunter için Telegram mesaj yönetimi
"""
import asyncio
import logging
from typing import Optional

from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError

from app.core.config import settings
from app.core.logging import get_logger
from app.core.db import get_session
from app.agency.services.chat_manager import ChatManager

logger = get_logger("telethon")

# Telethon configuration
API_ID = getattr(settings, 'TELETHON_API_ID', None)
API_HASH = getattr(settings, 'TELETHON_API_HASH', None)
SESSION_NAME = 'aurora_contact_session'

# Global client instance
client: Optional[TelegramClient] = None


async def initialize_telethon_client() -> Optional[TelegramClient]:
    """Telethon client'ı başlat."""
    if not API_ID or not API_HASH:
        logger.warning("TELETHON_API_ID or TELETHON_API_HASH not set. Telethon client disabled.")
        return None
    
    try:
        global client
        client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
        await client.start()
        
        # 2FA kontrolü
        if not await client.is_user_authorized():
            logger.error("Telethon client not authorized. Please login first.")
            return None
        
        logger.info("Telethon client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Telethon client: {e}", exc_info=True)
        return None


@events.register(events.NewMessage(incoming=True, private=True))
async def handle_incoming_lead_message(event):
    """
    AURORA CONTACT'a gelen her yeni özel mesajı yakalar.
    """
    sender_id = event.sender_id
    incoming_text = event.text or ""
    sender = await event.get_sender()
    username = getattr(sender, 'username', None)
    first_name = getattr(sender, 'first_name', None)
    
    logger.info(
        "incoming_message_received",
        sender_id=sender_id,
        username=username,
        text_preview=incoming_text[:100],
    )
    
    try:
        # Database session al
        async for session in get_session():
            chat_manager = ChatManager(session)
            
            # 1. Göndericiyi NovaCore'da bul / Lead verisini çek
            client_lead = await chat_manager.get_or_create_agency_client(
                telegram_user_id=sender_id,
                username=username,
                first_name=first_name,
            )
            
            # 2. Hybrid chat işle
            reply, tool_calls = await chat_manager.process_hybrid_chat(
                sender_id=sender_id,
                incoming_text=incoming_text,
                pipeline_stage=client_lead.pipeline_stage,
                context={
                    "lead_id": client_lead.id,
                    "pipeline_stage": client_lead.pipeline_stage.value,
                },
            )
            
            # 3. Tool calls varsa işle (ileride tool executor eklenecek)
            if tool_calls:
                logger.info(
                    "tool_calls_detected",
                    sender_id=sender_id,
                    tool_calls=tool_calls,
                )
                # TODO: Tool executor entegrasyonu
                # await tools_executor.run(tool_calls)
            
            # 4. Yanıtı gönder
            await client.send_message(sender_id, reply)
            
            # 5. Konuşmayı logla
            await chat_manager.log_conversation(
                sender_id=sender_id,
                incoming_text=incoming_text,
                reply=reply,
                tool_calls=tool_calls,
            )
            
            break  # Session context manager'dan çık
    
    except Exception as e:
        logger.error(f"Error handling incoming message: {e}", exc_info=True)
        
        # Human handoff tetikle
        try:
            async for session in get_session():
                chat_manager = ChatManager(session)
                await chat_manager.trigger_human_handoff(sender_id, f"LLM Error: {str(e)}")
                break
        except Exception as handoff_error:
            logger.error(f"Human handoff error: {handoff_error}", exc_info=True)
        
        # Kullanıcıya hata mesajı gönder
        try:
            await client.send_message(
                sender_id,
                "Üzgünüm, şu an teknik bir sorun yaşıyorum. İnsan operatöre devrediyorum. Lütfen kısa süre içinde tekrar deneyin."
            )
        except Exception as send_error:
            logger.error(f"Failed to send error message: {send_error}", exc_info=True)


async def start_telethon_client():
    """Telethon client'ı başlat ve event handler'ları kaydet."""
    global client
    
    client = await initialize_telethon_client()
    if not client:
        return
    
    # Event handler'ı kaydet
    client.add_event_handler(handle_incoming_lead_message)
    
    logger.info("Telethon client started and listening for messages")
    
    # Client'ı çalışır durumda tut (arka planda)
    # Not: Bu fonksiyon FastAPI lifespan'ında çağrılacak


async def stop_telethon_client():
    """Telethon client'ı durdur."""
    global client
    if client:
        await client.disconnect()
        logger.info("Telethon client stopped")
        client = None


# Background task için
async def run_telethon_background():
    """Background task olarak Telethon client'ı çalıştır."""
    client = await initialize_telethon_client()
    if not client:
        return
    
    client.add_event_handler(handle_incoming_lead_message)
    
    try:
        await client.run_until_disconnected()
    except Exception as e:
        logger.error(f"Telethon background task error: {e}", exc_info=True)
    finally:
        await client.disconnect()

