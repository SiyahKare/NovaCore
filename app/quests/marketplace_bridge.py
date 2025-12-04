# app/quests/marketplace_bridge.py
"""
Marketplace Bridge - Quest → Marketplace Otomatik Gönderim

Vatandaş görevle üretim yapar → AI Score 70+ → Marketplace'e otomatik düşer
"""
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from .categories import QuestCategory, is_marketplace_eligible
from .models import UserQuest
from app.marketplace.service import MarketplaceService
from app.marketplace.catalog import (
    MarketplaceItemType,
    infer_item_type_from_quest_key,
    calculate_price,
    get_product_definition,
)


def _infer_category_from_quest(user_quest: UserQuest) -> QuestCategory:
    """
    Quest'ten kategori çıkar (key veya type'a göre).
    
    MVP Pack V1 görevleri için:
    - daily_micro_content → PRODUCTION
    - micro_value_action → PRODUCTION
    - skill_xp_log → LEARNING
    - vb.
    """
    key = user_quest.key.lower()
    
    # Produksiyon görevleri
    if any(x in key for x in ["content", "caption", "hook", "script", "translation", "description"]):
        return QuestCategory.PRODUCTION
    
    # Araştırma görevleri
    if any(x in key for x in ["research", "trend", "analysis", "discovery", "maps"]):
        return QuestCategory.RESEARCH
    
    # Temizlik görevleri
    if any(x in key for x in ["review", "spam", "toxic", "moderation"]):
        return QuestCategory.MODERATION
    
    # Topluluk görevleri
    if any(x in key for x in ["referral", "help", "friend", "community"]):
        return QuestCategory.COMMUNITY
    
    # Öğrenme görevleri
    if any(x in key for x in ["skill", "learning", "quiz", "education", "xp_log"]):
        return QuestCategory.LEARNING
    
    # Ritual görevleri
    if any(x in key for x in ["streak", "ritual", "report", "morning", "evening"]):
        return QuestCategory.RITUAL
    
    # Default: Produksiyon (en yaygın)
    return QuestCategory.PRODUCTION


async def check_and_send_to_marketplace(
    session: AsyncSession,
    user_quest: UserQuest,
    ai_score: float,
) -> Optional[int]:
    """
    Quest tamamlandığında marketplace'e gönderilebilir mi kontrol et.
    
    Args:
        session: Database session
        user_quest: Tamamlanan quest
        ai_score: AI kalite skoru (0-100)
    
    Returns:
        Marketplace item ID (eğer gönderildiyse) veya None
    """
    # Quest kategorisini belirle
    category = _infer_category_from_quest(user_quest)
    
    # Marketplace'e gönderilebilir mi?
    if not is_marketplace_eligible(category, ai_score):
        return None
    
    # Item tipini belirle (katalogdan)
    item_type = infer_item_type_from_quest_key(user_quest.key)
    
    # Fiyat hesapla (AI Score + Quest ödülü bazlı)
    base_quest_reward = user_quest.final_reward_ncr or user_quest.base_reward_ncr
    price_ncr = calculate_price(
        item_type=item_type,
        ai_score=ai_score,
        base_quest_reward=base_quest_reward,
    )
    
    # Tags oluştur (katalogdan)
    product_def = get_product_definition(item_type)
    tags = (product_def.tags.copy() if product_def and product_def.tags else [])
    tags.append("citizen_quest")
    tags.append(category.value.lower())
    
    # QuestProof'tan content'i al
    from sqlmodel import select
    from .proof_models import QuestProof
    
    proof_stmt = select(QuestProof).where(
        QuestProof.user_quest_id == user_quest.id
    ).order_by(QuestProof.created_at.desc())
    proof_result = await session.execute(proof_stmt)
    quest_proof = proof_result.scalar_one_or_none()
    
    content = quest_proof.content if quest_proof else None
    
    # Marketplace item oluştur
    marketplace_service = MarketplaceService(session)
    
    try:
        item = await marketplace_service.create_from_quest(
            creator_id=user_quest.user_id,
            source_quest_id=user_quest.id,
            title=user_quest.title,
            description=user_quest.description or user_quest.title,
            item_type=item_type.value,  # Enum'dan string'e çevir
            price_ncr=price_ncr,
            ai_score=ai_score,
            tags=tags,
            preview_text=user_quest.description[:200] if user_quest.description else None,
            content=content,  # QuestProof'tan gelen içerik
        )
        
        return item.id
    except Exception as e:
        # Hata durumunda logla ama quest'i bozma
        from app.core.logging import get_logger
        logger = get_logger("marketplace_bridge")
        logger.warning(
            "marketplace_item_creation_failed",
            quest_id=user_quest.id,
            error=str(e),
        )
        return None




def _infer_category_from_quest(user_quest: UserQuest) -> QuestCategory:
    """
    Quest'ten kategori çıkar (key veya type'a göre).
    
    MVP Pack V1 görevleri için:
    - daily_micro_content → PRODUCTION
    - micro_value_action → PRODUCTION
    - skill_xp_log → LEARNING
    - vb.
    """
    key = user_quest.key.lower()
    
    # Produksiyon görevleri
    if any(x in key for x in ["content", "caption", "hook", "script", "translation", "description"]):
        return QuestCategory.PRODUCTION
    
    # Araştırma görevleri
    if any(x in key for x in ["research", "trend", "analysis", "discovery", "maps"]):
        return QuestCategory.RESEARCH
    
    # Temizlik görevleri
    if any(x in key for x in ["review", "spam", "toxic", "moderation"]):
        return QuestCategory.MODERATION
    
    # Topluluk görevleri
    if any(x in key for x in ["referral", "help", "friend", "community"]):
        return QuestCategory.COMMUNITY
    
    # Öğrenme görevleri
    if any(x in key for x in ["skill", "learning", "quiz", "education", "xp_log"]):
        return QuestCategory.LEARNING
    
    # Ritual görevleri
    if any(x in key for x in ["streak", "ritual", "report", "morning", "evening"]):
        return QuestCategory.RITUAL
    
    # Default: Produksiyon (en yaygın)
    return QuestCategory.PRODUCTION


# =============================================================================
# MARKETPLACE ITEM CREATION (Placeholder)
# =============================================================================

async def create_marketplace_item(
    session: AsyncSession,
    quest: UserQuest,
    ai_score: float,
    category: QuestCategory,
) -> dict:
    """
    Marketplace item oluştur (placeholder).
    
    TODO: Marketplace modülü hazır olduğunda implement et.
    
    Returns:
        Marketplace item dict
    """
    # Placeholder - gerçek implementasyon marketplace modülünde olacak
    return {
        "id": "placeholder",
        "title": quest.title,
        "type": category.value,
        "price_ncr": quest.final_reward_ncr or quest.base_reward_ncr,
        "creator_id": quest.user_id,
        "ai_score": ai_score,
        "status": "pending",  # approved/pending/rejected
        "preview_text": quest.description[:200],  # İlk 200 karakter
        "created_at": datetime.utcnow(),
    }

