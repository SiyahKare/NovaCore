"""
Chat Manager - AI/Human Hybrid Chat Service
Aurora Contact Telegram conversation yönetimi
"""
from typing import Optional, Dict, List, Tuple
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.agency.models import AgencyClient, PipelineStage
from app.core.logging import get_logger

logger = get_logger("chat_manager")


class IntentClassifier:
    """Basit intent classification (ileride daha sofistike olabilir)."""
    
    OPERATIONAL_KEYWORDS = [
        "bakiye", "balance", "fiyat", "price", "demo", "randevu", "schedule",
        "ticket", "destek", "support", "create", "oluştur", "kayıt", "register"
    ]
    
    CASUAL_KEYWORDS = [
        "merhaba", "hello", "nasılsın", "how are you", "günaydın", "good morning",
        "şaka", "joke", "mizah", "humor", "eğlenceli", "funny"
    ]
    
    @staticmethod
    def analyze(text: str) -> str:
        """Mesajın intent'ini analiz et."""
        text_lower = text.lower()
        
        # Operational intent kontrolü
        if any(keyword in text_lower for keyword in IntentClassifier.OPERATIONAL_KEYWORDS):
            if "demo" in text_lower or "randevu" in text_lower or "schedule" in text_lower:
                return "schedule_demo"
            elif "bakiye" in text_lower or "balance" in text_lower:
                return "check_balance"
            elif "ticket" in text_lower or "destek" in text_lower or "support" in text_lower:
                return "create_ticket"
            else:
                return "operational"
        
        # Casual intent kontrolü
        if any(keyword in text_lower for keyword in IntentClassifier.CASUAL_KEYWORDS):
            if "şaka" in text_lower or "joke" in text_lower or "mizah" in text_lower:
                return "joke_request"
            else:
                return "casual_chat"
        
        return "general_faq"


class GrokProxy:
    """Grok proxy - Hızlı yanıt ve tonlama için."""
    
    @staticmethod
    async def get_quick_response(text: str, context: Optional[Dict] = None) -> str:
        """
        Grok'a yönlendir (şimdilik mock, ileride gerçek Grok API entegrasyonu).
        
        Grok'un felsefesi: Agresif, mizahi, direkt, sınırları zorlayan.
        """
        # TODO: Gerçek Grok API entegrasyonu
        # Şimdilik basit bir mock response
        
        text_lower = text.lower()
        
        if "merhaba" in text_lower or "hello" in text_lower:
            return "Merhaba! Aurora Contact'a hoş geldin. WhatsApp otomasyonu hakkında bilgi almak ister misin? 🚀"
        
        if "fiyat" in text_lower or "price" in text_lower:
            return "Fiyatlandırma konusunda detaylı bilgi vermek için önce işletmenizin mesaj hacmini bilmem gerekiyor. Hangi sektördesiniz? 💼"
        
        if "demo" in text_lower or "randevu" in text_lower:
            return "Harika! Demo için yarın saat 14:00'te uygun musun? Yoksa başka bir zaman tercih eder misin? 📅"
        
        # Default Grok-style response
        return "Anladım! WhatsApp otomasyonu konusunda sana yardımcı olabilirim. Hangi konuda bilgi almak istersin? 💬"


class GPTRouter:
    """GPT router - Tool calling ve complex orchestration için."""
    
    @staticmethod
    async def route_with_tools(
        text: str,
        pipeline_stage: PipelineStage,
        context: Optional[Dict] = None
    ) -> Tuple[str, Optional[List[Dict]]]:
        """
        GPT'ye yönlendir (tool calling ile).
        
        Returns:
            (reply, tool_calls)
        """
        # TODO: Gerçek GPT API entegrasyonu (OpenAI/Anthropic)
        # Şimdilik mock response
        
        text_lower = text.lower()
        tool_calls = []
        
        if "demo" in text_lower or "randevu" in text_lower:
            tool_calls.append({
                "function": "schedule_demo",
                "arguments": {
                    "lead_id": context.get("lead_id") if context else None,
                    "preferred_time": "tomorrow_14:00"
                }
            })
            reply = "Demo randevusu oluşturuluyor. Yarın saat 14:00'te görüşelim! 📅"
        
        elif "bakiye" in text_lower or "balance" in text_lower:
            tool_calls.append({
                "function": "check_balance",
                "arguments": {
                    "lead_id": context.get("lead_id") if context else None
                }
            })
            reply = "Bakiye bilgisi kontrol ediliyor..."
        
        else:
            reply = "Anladım. Bu konuda sana yardımcı olabilirim. Detaylı bilgi için demo randevusu almak ister misin?"
        
        return reply, tool_calls if tool_calls else None


class ChatManager:
    """Aurora Contact chat yönetimi - AI/Human hybrid."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.intent_classifier = IntentClassifier()
        self.grok_proxy = GrokProxy()
        self.gpt_router = GPTRouter()
    
    async def get_or_create_agency_client(
        self,
        telegram_user_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
    ) -> AgencyClient:
        """Telegram user'dan AgencyClient oluştur veya getir."""
        # Önce mevcut client'ı ara (telegram_user_id'ye göre)
        # Şimdilik basit bir mapping (ileride AgencyClient'a telegram_user_id field'ı eklenebilir)
        
        # TODO: AgencyClient modeline telegram_user_id ekle
        # Şimdilik name'e göre arama yapıyoruz (geçici)
        
        stmt = select(AgencyClient).where(
            AgencyClient.name.ilike(f"%{username or first_name or 'Unknown'}%")
        ).limit(1)
        
        result = await self.session.execute(stmt)
        client = result.scalar_one_or_none()
        
        if not client:
            # Yeni client oluştur
            client = AgencyClient(
                name=first_name or username or f"Telegram User {telegram_user_id}",
                pipeline_stage=PipelineStage.LEAD,
            )
            self.session.add(client)
            await self.session.commit()
            await self.session.refresh(client)
        
        return client
    
    async def process_hybrid_chat(
        self,
        sender_id: int,
        incoming_text: str,
        pipeline_stage: PipelineStage,
        context: Optional[Dict] = None,
    ) -> Tuple[str, Optional[List[Dict]]]:
        """
        Hybrid chat işleme - Grok/GPT routing.
        
        Returns:
            (reply, tool_calls)
        """
        # 1. Intent analizi
        intent = self.intent_classifier.analyze(incoming_text)
        
        logger.info(
            "chat_intent_analyzed",
            sender_id=sender_id,
            intent=intent,
            text_preview=incoming_text[:50],
        )
        
        # 2. Model yönlendirme
        if intent in ["schedule_demo", "check_balance", "create_ticket", "operational"]:
            # GPT'ye yönlendir (tool calling)
            reply, tool_calls = await self.gpt_router.route_with_tools(
                incoming_text,
                pipeline_stage,
                context=context or {},
            )
        elif intent in ["casual_chat", "joke_request", "general_faq"]:
            # Grok'a yönlendir (hızlı yanıt)
            reply = await self.grok_proxy.get_quick_response(
                incoming_text,
                context=context,
            )
            tool_calls = None
        else:
            # Default
            reply = "Üzgünüm, şu an bu konuyu anlayamadım. WhatsApp otomasyonu hakkında bilgi almak ister misin?"
            tool_calls = None
        
        return reply, tool_calls
    
    async def log_conversation(
        self,
        sender_id: int,
        incoming_text: str,
        reply: str,
        tool_calls: Optional[List[Dict]] = None,
    ) -> None:
        """Konuşmayı logla (ileride Conversation model'e kaydedilebilir)."""
        logger.info(
            "conversation_logged",
            sender_id=sender_id,
            incoming_preview=incoming_text[:100],
            reply_preview=reply[:100],
            tool_calls=tool_calls,
        )
        # TODO: Conversation model'e kaydet
    
    async def trigger_human_handoff(
        self,
        sender_id: int,
        reason: str,
    ) -> None:
        """Human handoff tetikle."""
        logger.warning(
            "human_handoff_triggered",
            sender_id=sender_id,
            reason=reason,
        )
        # TODO: Human handoff queue'ya ekle

