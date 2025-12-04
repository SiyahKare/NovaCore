# app/quests/categories.py
"""
Citizen Quest Engine - 6 Ana Kategori

Baron'un Devlet Ajandası:
1. Citizen Quest Engine (Görevleri dağıt → ekonomi çalışsın)
2. Marketplace Core (vatandaşın ürettiği değer satılabilsin)
3. SiyahKare Viral Agency (optimize → paketle → sat)
4. NCR / Fiat Bridge (gelir çekilebilsin)
5. Aurora Contact B2B (hunter → KOBİ → MRR)
"""
from enum import Enum
from typing import Optional


class QuestCategory(str, Enum):
    """
    6 Ana Görev Kategorisi - Gerçek Ekonomi İçin
    
    Her kategori farklı bir üretim alanını hedefler.
    """
    PRODUCTION = "production"      # A. Produksiyon Görevleri - Gerçek ekonomik değer
    RESEARCH = "research"          # B. Araştırma Görevleri - Trend/niche analizi
    MODERATION = "moderation"      # C. Temizlik Görevleri - HITL içerik inceleme
    COMMUNITY = "community"        # D. Topluluk Görevleri - Referral/yardım
    LEARNING = "learning"          # E. Öğrenme Görevleri - Eğitim modülleri
    RITUAL = "ritual"              # F. Ritual Görevleri - Streak/rapor


class ProductionQuestType(str, Enum):
    """Produksiyon görevleri alt tipleri."""
    MINI_CONTENT_HOOK = "mini_content_hook"          # Hook cümlesi
    SEO_SENTENCE = "seo_sentence"                    # SEO cümlesi
    PRODUCT_DESCRIPTION = "product_description"      # Ürün açıklaması
    VIRAL_SHORT_SCRIPT = "viral_short_script"        # Viral short script
    PHOTO_CAPTION = "photo_caption"                  # Foto caption (Flirt/Dating)
    MICRO_TRANSLATION = "micro_translation"          # Mikro çeviri


class ResearchQuestType(str, Enum):
    """Araştırma görevleri alt tipleri."""
    TREND_ANALYSIS = "trend_analysis"                # Trend analizi
    TIKTOK_DISCOVERY = "tiktok_discovery"            # TikTok keşfet tarama
    LOCAL_NICHE = "local_niche"                      # Local niche araştırması
    MAPS_SCRAPING = "maps_scraping"                  # Google Maps scraping (manuel proof)


class ModerationQuestType(str, Enum):
    """Temizlik görevleri alt tipleri."""
    CONTENT_REVIEW = "content_review"                 # Kötü içerik inceleme (HITL)
    SPAM_DETECTION = "spam_detection"                 # Spam tespiti
    TOXIC_REPORT = "toxic_report"                    # Toxic comment raporlama


class CommunityQuestType(str, Enum):
    """Topluluk görevleri alt tipleri."""
    REFERRAL = "referral"                            # 1 referral
    HELP_MESSAGES = "help_messages"                  # 3 mesaj yardım
    DISCORD_HELP = "discord_help"                    # Discord'da yardım
    ONBOARDING_HELP = "onboarding_help"              # Yeni vatandaş onboarding


class LearningQuestType(str, Enum):
    """Öğrenme görevleri alt tipleri."""
    AI_BASICS = "ai_basics"                          # Basic AI eğitim modülü
    CRYPTO_BASICS = "crypto_basics"                   # Crypto basics quiz
    NOVACORE_ONBOARDING = "novacore_onboarding"      # NovaCore onboarding


class RitualQuestType(str, Enum):
    """Ritual görevleri alt tipleri."""
    MORNING_MODE = "morning_mode"                    # Sabah modu
    EVENING_CLOSE = "evening_close"                  # Akşam kapanış
    FRIDAY_REPORT = "friday_report"                  # Cuma Raporu
    STREAK_TASK = "streak_task"                      # Streak Task


# =============================================================================
# CATEGORY METADATA
# =============================================================================

CATEGORY_INFO = {
    QuestCategory.PRODUCTION: {
        "name": "Produksiyon",
        "description": "Gerçek ekonomik değer üreten işler",
        "base_ncr_range": (8.0, 20.0),
        "base_xp_range": (30, 75),
        "marketplace_eligible": True,  # Marketplace'e otomatik gönderilebilir
        "min_ai_score_for_marketplace": 70.0,
    },
    QuestCategory.RESEARCH: {
        "name": "Araştırma",
        "description": "Trend analizi ve niche araştırması",
        "base_ncr_range": (10.0, 25.0),
        "base_xp_range": (40, 80),
        "marketplace_eligible": True,
        "min_ai_score_for_marketplace": 70.0,
    },
    QuestCategory.MODERATION: {
        "name": "Temizlik",
        "description": "Kötü içerik inceleme ve spam tespiti",
        "base_ncr_range": (5.0, 15.0),
        "base_xp_range": (20, 50),
        "marketplace_eligible": False,  # HITL görevleri marketplace'e gitmez
        "requires_hitl": True,
    },
    QuestCategory.COMMUNITY: {
        "name": "Topluluk",
        "description": "Referral ve yardım görevleri",
        "base_ncr_range": (3.0, 12.0),
        "base_xp_range": (15, 40),
        "marketplace_eligible": False,
    },
    QuestCategory.LEARNING: {
        "name": "Öğrenme",
        "description": "Eğitim modülleri ve quiz'ler",
        "base_ncr_range": (5.0, 15.0),
        "base_xp_range": (25, 60),
        "marketplace_eligible": False,
    },
    QuestCategory.RITUAL: {
        "name": "Ritual",
        "description": "Streak ve rapor görevleri",
        "base_ncr_range": (2.0, 8.0),
        "base_xp_range": (10, 30),
        "marketplace_eligible": False,
    },
}


def get_category_info(category: QuestCategory) -> dict:
    """Kategori bilgilerini getir."""
    return CATEGORY_INFO.get(category, {})


def is_marketplace_eligible(category: QuestCategory, ai_score: float) -> bool:
    """
    Bu kategori marketplace'e gönderilebilir mi?
    
    Args:
        category: Quest kategorisi
        ai_score: AI kalite skoru (0-100)
    
    Returns:
        True if eligible
    """
    info = get_category_info(category)
    
    if not info.get("marketplace_eligible", False):
        return False
    
    min_score = info.get("min_ai_score_for_marketplace", 70.0)
    return ai_score >= min_score

