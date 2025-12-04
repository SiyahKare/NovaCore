"""
Quest Enums
"""
from enum import Enum


class QuestType(str, Enum):
    """Quest tipi."""
    MEME = "meme"  # Meme üretimi
    QUIZ = "quiz"  # Quiz/soru
    REFLECTION = "reflection"  # Düşünce/reflection
    SOCIAL = "social"  # Sosyal medya paylaşımı
    ONCHAIN = "onchain"  # Blockchain işlemi
    MICROTASK = "microtask"  # Küçük görev
    STREAK = "streak"  # Streak görevi
    REFERRAL = "referral"  # Referral görevi
    MONEY = "money"  # Ekonomi/üretim/iş görevi (MVP Pack V1)
    SKILL = "skill"  # Öğrenme/üretim/beceri görevi (MVP Pack V1)
    INTEGRITY = "integrity"  # Ahlak/şeffaflık/tribe görevi (MVP Pack V1)


class QuestStatus(str, Enum):
    """Quest durumu."""
    ASSIGNED = "assigned"  # Kullanıcıya verildi, henüz dokunmadı
    SUBMITTED = "submitted"  # Kullanıcı proof gönderdi, AI/HITL bekliyor
    UNDER_REVIEW = "under_review"  # DAO / HITL kuyruğunda
    APPROVED = "approved"  # Ödül dağıtıldı
    REJECTED = "rejected"  # Red / itiraz mümkün
    EXPIRED = "expired"  # Süresi geçmiş

