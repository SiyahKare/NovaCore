"""
NovaCore - NovaCredit Rules & Weights
Davranış Kategorileri & Ağırlık Sistemi

Bu dosya "devletin anayasası" gibi.
Değiştirmek kolay - kanun değişikliği gibi.
"""
from enum import Enum
from typing import NamedTuple


# ============ Skor Sınırları ============
CREDIT_MIN = 0
CREDIT_MAX = 1000
CREDIT_DEFAULT = 500


# ============ Event Kategorileri ============
class EventCategory(str, Enum):
    """
    Davranış kategorileri.
    
    Her event bir kategoriye aittir.
    Kategori, ağırlığı ve risk skorunu belirler.
    """
    # Pozitif Davranışlar
    ECONOMIC = "ECONOMIC"  # Para harcama, transaction
    SOCIAL_POSITIVE = "SOCIAL_POSITIVE"  # Tip, gift, positive interaction
    CONTRIBUTION = "CONTRIBUTION"  # Content creation, community contribution
    LOYALTY = "LOYALTY"  # Streak, daily login, retention
    VERIFICATION = "VERIFICATION"  # Identity verify, KYC

    # Negatif Davranışlar
    RISK_NEGATIVE = "RISK_NEGATIVE"  # Fraud attempt, abuse
    SOCIAL_NEGATIVE = "SOCIAL_NEGATIVE"  # Report, block, harassment
    ABANDONMENT = "ABANDONMENT"  # Uzun süre inactive, terk
    VIOLATION = "VIOLATION"  # TOS violation, ban


# ============ Kategori Ağırlıkları ============
class CategoryWeight(NamedTuple):
    """Kategori ağırlık bilgisi."""
    weight: float  # Delta çarpanı
    risk_impact: float  # Risk skoruna etkisi (-1 to 1)
    reputation_impact: float  # Reputation'a etkisi (-1 to 1)


CATEGORY_WEIGHTS: dict[EventCategory, CategoryWeight] = {
    # Pozitif kategoriler
    EventCategory.ECONOMIC: CategoryWeight(
        weight=1.0,
        risk_impact=-0.01,  # Ekonomik aktivite riski azaltır
        reputation_impact=0.02,
    ),
    EventCategory.SOCIAL_POSITIVE: CategoryWeight(
        weight=1.5,
        risk_impact=-0.02,
        reputation_impact=0.05,  # Sosyal pozitiflik reputation'ı artırır
    ),
    EventCategory.CONTRIBUTION: CategoryWeight(
        weight=2.0,  # En yüksek pozitif ağırlık
        risk_impact=-0.03,
        reputation_impact=0.08,
    ),
    EventCategory.LOYALTY: CategoryWeight(
        weight=0.8,
        risk_impact=-0.01,
        reputation_impact=0.02,
    ),
    EventCategory.VERIFICATION: CategoryWeight(
        weight=3.0,  # Doğrulama çok değerli
        risk_impact=-0.1,  # Riski ciddi düşürür
        reputation_impact=0.15,
    ),

    # Negatif kategoriler
    EventCategory.RISK_NEGATIVE: CategoryWeight(
        weight=-3.0,  # En ağır ceza
        risk_impact=0.15,  # Riski ciddi artırır
        reputation_impact=-0.2,
    ),
    EventCategory.SOCIAL_NEGATIVE: CategoryWeight(
        weight=-2.0,
        risk_impact=0.08,
        reputation_impact=-0.15,
    ),
    EventCategory.ABANDONMENT: CategoryWeight(
        weight=-0.5,  # Hafif ceza
        risk_impact=0.02,
        reputation_impact=-0.03,
    ),
    EventCategory.VIOLATION: CategoryWeight(
        weight=-5.0,  # En ağır
        risk_impact=0.25,
        reputation_impact=-0.3,
    ),
}


# ============ Event Type → Category Mapping ============
EVENT_TYPE_MAPPINGS: dict[str, tuple[EventCategory, int]] = {
    # FlirtMarket Events
    "COIN_SPENT": (EventCategory.ECONOMIC, 2),
    "SHOW_PURCHASED": (EventCategory.ECONOMIC, 5),
    "BOOST_USED": (EventCategory.ECONOMIC, 1),
    "TIP_SENT": (EventCategory.SOCIAL_POSITIVE, 3),
    "GIFT_SENT": (EventCategory.SOCIAL_POSITIVE, 4),
    "MESSAGE_SENT": (EventCategory.SOCIAL_POSITIVE, 1),
    "PROFILE_REPORTED": (EventCategory.SOCIAL_NEGATIVE, -5),

    # OnlyVips Events
    "PREMIUM_PURCHASED": (EventCategory.ECONOMIC, 8),
    "CONTENT_UNLOCKED": (EventCategory.ECONOMIC, 3),
    "SUBSCRIPTION_RENEWED": (EventCategory.LOYALTY, 10),
    "QUEST_COMPLETED": (EventCategory.CONTRIBUTION, 5),
    "STREAK_BONUS": (EventCategory.LOYALTY, 3),
    "CONTENT_CREATED": (EventCategory.CONTRIBUTION, 15),

    # PokerVerse Events
    "BUY_IN": (EventCategory.ECONOMIC, 2),
    "CASH_OUT": (EventCategory.ECONOMIC, 1),
    "RAKE": (EventCategory.ECONOMIC, 1),
    "TOURNAMENT_BUY_IN": (EventCategory.ECONOMIC, 5),
    "TOURNAMENT_PRIZE": (EventCategory.CONTRIBUTION, 10),
    "HAND_PLAYED": (EventCategory.LOYALTY, 1),
    "CHIP_DUMP_DETECTED": (EventCategory.RISK_NEGATIVE, -20),

    # Aurora Events
    "AI_CHAT_SESSION": (EventCategory.ECONOMIC, 2),
    "AI_IMAGE_GENERATED": (EventCategory.ECONOMIC, 3),
    "AI_VOICE_MESSAGE": (EventCategory.ECONOMIC, 2),
    "TOKEN_BURN": (EventCategory.ECONOMIC, 1),
    "AI_FEEDBACK_POSITIVE": (EventCategory.CONTRIBUTION, 5),
    "AI_FEEDBACK_NEGATIVE": (EventCategory.SOCIAL_NEGATIVE, -2),

    # System Events
    "DAILY_LOGIN": (EventCategory.LOYALTY, 2),
    "REFERRAL_SIGNUP": (EventCategory.CONTRIBUTION, 20),
    "REFERRAL_ACTIVE": (EventCategory.CONTRIBUTION, 30),
    "KYC_VERIFIED": (EventCategory.VERIFICATION, 50),
    "TELEGRAM_VERIFIED": (EventCategory.VERIFICATION, 20),
    "TON_WALLET_CONNECTED": (EventCategory.VERIFICATION, 15),

    # Risk Events
    "FRAUD_ATTEMPT": (EventCategory.RISK_NEGATIVE, -50),
    "ABUSE_REPORTED": (EventCategory.RISK_NEGATIVE, -30),
    "TOS_VIOLATION": (EventCategory.VIOLATION, -100),
    "ACCOUNT_WARNING": (EventCategory.VIOLATION, -20),
    "TEMPORARY_BAN": (EventCategory.VIOLATION, -150),
    "PERMANENT_BAN": (EventCategory.VIOLATION, -500),

    # Abandonment
    "INACTIVE_7_DAYS": (EventCategory.ABANDONMENT, -5),
    "INACTIVE_30_DAYS": (EventCategory.ABANDONMENT, -15),
    "INACTIVE_90_DAYS": (EventCategory.ABANDONMENT, -30),
}


# ============ Tier Privileges ============
class TierPrivilege(NamedTuple):
    """Tier'a göre ayrıcalıklar."""
    withdraw_limit_daily: int  # NCR
    transfer_limit_daily: int  # NCR
    can_create_content: bool
    can_host_rooms: bool
    priority_support: bool
    ai_model_tier: str
    transaction_fee_discount: float  # 0.0 - 1.0


TIER_PRIVILEGES = {
    "GHOST": TierPrivilege(
        withdraw_limit_daily=0,  # Çekim yok
        transfer_limit_daily=100,
        can_create_content=False,
        can_host_rooms=False,
        priority_support=False,
        ai_model_tier="basic",
        transaction_fee_discount=0.0,
    ),
    "GREY": TierPrivilege(
        withdraw_limit_daily=500,
        transfer_limit_daily=1000,
        can_create_content=False,
        can_host_rooms=False,
        priority_support=False,
        ai_model_tier="basic",
        transaction_fee_discount=0.0,
    ),
    "SOLID": TierPrivilege(
        withdraw_limit_daily=5000,
        transfer_limit_daily=10000,
        can_create_content=True,
        can_host_rooms=True,
        priority_support=False,
        ai_model_tier="standard",
        transaction_fee_discount=0.1,
    ),
    "ELITE": TierPrivilege(
        withdraw_limit_daily=50000,
        transfer_limit_daily=100000,
        can_create_content=True,
        can_host_rooms=True,
        priority_support=True,
        ai_model_tier="premium",
        transaction_fee_discount=0.25,
    ),
    "LEGEND": TierPrivilege(
        withdraw_limit_daily=500000,  # Neredeyse sınırsız
        transfer_limit_daily=1000000,
        can_create_content=True,
        can_host_rooms=True,
        priority_support=True,
        ai_model_tier="elite",
        transaction_fee_discount=0.5,
    ),
}


# ============ Risk Thresholds ============
RISK_THRESHOLDS = {
    "LOW": (0.0, 0.3),
    "MEDIUM": (0.3, 0.6),
    "HIGH": (0.6, 0.8),
    "CRITICAL": (0.8, 1.0),
}


def get_risk_level(risk_score: float) -> str:
    """Get risk level from score."""
    for level, (min_val, max_val) in RISK_THRESHOLDS.items():
        if min_val <= risk_score < max_val:
            return level
    return "CRITICAL"


# ============ Decay Rules ============
# Inactive kullanıcıların skorları zamanla düşer
DECAY_RULES = {
    "inactive_7_days_decay": -1,  # Günlük düşüş
    "inactive_30_days_decay": -2,
    "inactive_90_days_decay": -5,
    "max_decay_per_day": -10,  # Maksimum günlük düşüş
}


# ============ Bonus Rules ============
# Streak ve özel durumlar için bonus
STREAK_BONUSES = {
    3: 1.1,  # 3 gün streak → %10 bonus
    7: 1.25,  # 7 gün streak → %25 bonus
    14: 1.5,  # 14 gün streak → %50 bonus
    30: 2.0,  # 30 gün streak → %100 bonus
}


def get_streak_multiplier(streak_days: int) -> float:
    """Get bonus multiplier for streak."""
    multiplier = 1.0
    for days, bonus in sorted(STREAK_BONUSES.items()):
        if streak_days >= days:
            multiplier = bonus
    return multiplier

