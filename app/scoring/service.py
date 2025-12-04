# app/scoring/service.py
"""
AI Scoring Service V1 - Quest Kalite Filtresi

Vatandaş → Üretir → AI Score → Marketplace'e düşer (70+)
"""
import json
import os
from typing import Optional

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    AsyncOpenAI = None

from app.core.config import settings
from app.core.logging import get_logger
from .models import QuestScoringInput, QuestScoringOutput

logger = get_logger("scoring")


class ScoringService:
    """
    AI Scoring Service - Quest kalite filtresi.
    
    Provider: OpenAI (gpt-4o-mini veya gpt-4-turbo-preview)
    Cost: Düşük (küçük model)
    """
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize scoring service.
        
        Args:
            api_key: OpenAI API key (default: OPENAI_API_KEY env var)
            model: Model name (default: gpt-4o-mini)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY") or (getattr(settings, "OPENAI_API_KEY", None) if hasattr(settings, "OPENAI_API_KEY") else None)
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        
        if not OPENAI_AVAILABLE:
            logger.warning("openai package not installed, scoring will use fallback")
            self.client = None
        elif not self.api_key:
            logger.warning("OPENAI_API_KEY not set, scoring will use fallback")
            self.client = None
        else:
            self.client = AsyncOpenAI(api_key=self.api_key)
    
    async def score_quest(self, input_data: QuestScoringInput) -> QuestScoringOutput:
        """
        Quest'i AI ile puanla.
        
        Args:
            input_data: Quest scoring input
        
        Returns:
            QuestScoringOutput
        
        Raises:
            ValueError: Scoring failed
        """
        # PRODUCTION ve RESEARCH için full scoring
        # Diğerleri için basit kontrol
        if input_data.category not in ["PRODUCTION", "RESEARCH"]:
            return self._basic_scoring(input_data)
        
        # OpenAI client yoksa fallback
        if not self.client:
            return self._fallback_scoring(input_data)
        
        try:
            return await self._ai_scoring(input_data)
        except Exception as e:
            logger.error("ai_scoring_failed", error=str(e), quest_key=input_data.quest_key)
            # Fallback'e düş
            return self._fallback_scoring(input_data)
    
    async def _ai_scoring(self, input_data: QuestScoringInput) -> QuestScoringOutput:
        """OpenAI ile AI scoring."""
        
        # Prompt oluştur
        system_prompt = self._get_system_prompt()
        user_prompt = self._get_user_prompt(input_data)
        
        # API çağrısı
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,  # Daha tutarlı sonuçlar için düşük temperature
        )
        
        # Response parse et
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Empty response from OpenAI")
        
        data = json.loads(content)
        
        # Output oluştur
        return QuestScoringOutput(
            score=float(data.get("score", 70.0)),
            reasoning=data.get("reasoning", "AI scoring completed"),
            flags=data.get("flags", []),
            suggested_tags=data.get("suggested_tags", []),
        )
    
    def _get_system_prompt(self) -> str:
        """System prompt."""
        return """Sen bir "Citizen Quest Judge"sın.

Görevin: Vatandaşın ürettiği içeriği 0-100 arası puanlamak.

Kriterlerin:
- 40 altı: Çöp / spam / alakasız / çok kısa
- 40-69: Orta, geliştirilebilir
- 70-84: Marketplace'e gidebilir, kaliteli
- 85-100: Premium, viral potansiyelli, çok değerli

Ek kontroller:
- NSFW, nefret, scam, kumar tespit edersen "nsfw_or_toxic" flag'i ata
- Çok kısa veya boş içerik ise "low_quality" flag'i ata
- Çok klişe, boş motivational ise "cliche" flag'i ata
- Spam pattern'i varsa "spam" flag'i ata

OUTPUT:
Sadece JSON dön:
{
  "score": <0-100 float>,
  "reasoning": "<kısa açıklama, Türkçe>",
  "flags": ["flag1", "flag2", ...],
  "suggested_tags": ["tag1", "tag2", ...]
}"""
    
    def _get_user_prompt(self, input_data: QuestScoringInput) -> str:
        """User prompt."""
        return f"""Quest Key: {input_data.quest_key}
Kategori: {input_data.category}
Proof Type: {input_data.proof_type}
Dil: {input_data.lang}

İçerik:
{input_data.proof_payload[:2000]}  # Max 2000 karakter

Bu içeriği puanla ve JSON döndür."""
    
    def _basic_scoring(self, input_data: QuestScoringInput) -> QuestScoringOutput:
        """
        MODERATION / COMMUNITY / LEARNING / RITUAL için basit scoring.
        
        Model çağrısı yapmaz, sadece temel kontroller.
        """
        proof_len = len(input_data.proof_payload)
        
        # Çok kısa kontrolü
        if proof_len < 10:
            return QuestScoringOutput(
                score=30.0,
                reasoning="auto_pass_non_commercial_too_short",
                flags=["low_quality"],
                suggested_tags=[],
            )
        
        # Spam kontrolü (basit)
        if proof_len > 5000:  # Çok uzun spam olabilir
            return QuestScoringOutput(
                score=50.0,
                reasoning="auto_pass_non_commercial_too_long",
                flags=["spam"],
                suggested_tags=[],
            )
        
        # Default: Orta skor
        return QuestScoringOutput(
            score=70.0,
            reasoning="auto_pass_non_commercial",
            flags=[],
            suggested_tags=[],
        )
    
    def _fallback_scoring(self, input_data: QuestScoringInput) -> QuestScoringOutput:
        """
        OpenAI çağrısı başarısız olursa fallback scoring.
        
        Basit heuristikler kullanır.
        """
        proof_len = len(input_data.proof_payload)
        
        # Uzunluk bazlı scoring
        if proof_len < 20:
            score = 40.0
            flags = ["low_quality"]
        elif proof_len < 100:
            score = 60.0
            flags = []
        elif proof_len < 500:
            score = 75.0
            flags = []
        else:
            score = 80.0
            flags = []
        
        return QuestScoringOutput(
            score=score,
            reasoning=f"fallback_scoring_length_based_{proof_len}",
            flags=flags,
            suggested_tags=[input_data.category.lower()],
        )


# Global service instance
_scoring_service: Optional[ScoringService] = None


def get_scoring_service() -> ScoringService:
    """Get global scoring service instance."""
    global _scoring_service
    if _scoring_service is None:
        _scoring_service = ScoringService()
    return _scoring_service


async def score_quest(input_data: QuestScoringInput) -> QuestScoringOutput:
    """
    Quest'i puanla (convenience function).
    
    Args:
        input_data: Quest scoring input
    
    Returns:
        QuestScoringOutput
    """
    service = get_scoring_service()
    return await service.score_quest(input_data)

