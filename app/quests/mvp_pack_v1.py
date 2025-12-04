# app/quests/mvp_pack_v1.py
"""
MVP Citizen Quest Pack V1

Her gün vatandaşa 3 slot görev:
1. MONEY - Ekonomi/üretim/iş
2. SKILL - Öğrenme/üretim/beceri
3. INTEGRITY - Ahlak/şeffaflık/tribe

Her görev NovaScore komponentlerine sinyal verir ve AbuseGuard uyumludur.
"""
from dataclasses import dataclass
from typing import Optional, Literal
from enum import Enum

from .enums import QuestType


class QuestSlot(str, Enum):
    """Günlük görev slotları."""
    MONEY = "money"      # Ekonomi/üretim/iş
    SKILL = "skill"      # Öğrenme/üretim/beceri
    INTEGRITY = "integrity"  # Ahlak/şeffaflık/tribe


class ProofType(str, Enum):
    """Proof tipi."""
    TEXT = "text"
    PHOTO = "photo"
    LINK = "link"
    MIXED = "mixed"


@dataclass
class QuestDefinition:
    """
    Quest tanımı - kodlanabilir format.
    
    Her görev:
    - NovaScore komponentlerine sinyal verir
    - AbuseGuard kurallarına uyumludur
    - Auto-review kurallarına sahiptir
    """
    # Kimlik
    quest_id: str  # Unique ID (ex: "daily_income_snapshot")
    slot: QuestSlot  # Hangi slot'ta gösterilecek
    quest_type: QuestType  # Quest tipi
    
    # Copy
    title: str
    description: str
    instructions: str  # Kullanıcıya gösterilecek talimat
    
    # Ekonomi
    base_ncr: float
    base_xp: int
    
    # Proof gereksinimleri
    proof_type: ProofType
    min_length: Optional[int] = None  # Text için minimum karakter
    max_length: Optional[int] = None  # Text için maksimum karakter
    requires_hitl: bool = False  # Her zaman HITL gerekli mi?
    
    # Tek seferlik görev mi?
    one_time_only: bool = False
    
    # NovaScore sinyalleri (hangi komponentlere katkı yapar)
    nova_signals: dict[str, float] = None  # {"ECO": 0.3, "REL": 0.2, ...}
    
    # AbuseGuard kuralları
    abuse_rules: dict[str, any] = None  # {"min_quality_score": 50, "spam_detection": True}
    
    # AI scoring kuralları
    ai_scoring: dict[str, any] = None  # {"min_score": 40, "originality_weight": 0.5}
    
    # Özel kurallar
    special_rules: Optional[str] = None  # Özel açıklama


# =============================================================================
# BASE QUEST DEFINITIONS - MVP Pack V1
# =============================================================================

BASE_QUEST_DEFS: list[QuestDefinition] = [
    # ========================================================================
    # MONEY SLOT
    # ========================================================================
    
    QuestDefinition(
        quest_id="daily_income_snapshot",
        slot=QuestSlot.MONEY,
        quest_type=QuestType.REFLECTION,
        title="Günün Para Raporu",
        description="Bugün cebine giren/çıkan parayı tek cümleyle yaz",
        instructions=(
            "Bugün cebine giren/çıkana dair **tek bir cümle** yaz:\n"
            "Örn: 'Bugün 200 TL kahve+ulaşım yaktım, 0 TL kazandım.'"
        ),
        base_ncr=5.0,
        base_xp=15,
        proof_type=ProofType.TEXT,
        min_length=10,  # 10 karakterden kısa → reject
        max_length=200,
        requires_hitl=False,
        one_time_only=False,
        nova_signals={
            "ECO": 0.3,  # Ekonomik farkındalık
            "REL": 0.2,  # Düzenlilik sinyali
        },
        abuse_rules={
            "min_quality_score": 30,  # Çok düşük kalite → reject
            "spam_detection": True,  # "asd, ???" tarzı spam kontrolü
            "duplicate_check": True,  # Aynı proof tekrar kontrolü
        },
        ai_scoring={
            "min_score": 30,
            "coherence_weight": 0.7,  # Tutarlılık ağırlığı
            "meaning_weight": 0.3,  # Anlam ağırlığı
        },
    ),
    
    QuestDefinition(
        quest_id="micro_value_action",
        slot=QuestSlot.MONEY,
        quest_type=QuestType.REFLECTION,
        title="Küçük Ticari Hamle",
        description="Bugün yaptığın küçük ama gerçek bir değer hareketini yaz",
        instructions=(
            "Bugün yaptığın **küçük ama gerçek** bir değer hareketini yaz:\n"
            "Birine ücretsiz yardım, iş ilanına başvuru, CV güncelleme, müşteri mesajı vs.\n\n"
            "**Not:** 'hiç yok' yazarsan → dürüstlük → düşük NCR ama Integrity sinyali +"
        ),
        base_ncr=8.0,
        base_xp=25,
        proof_type=ProofType.TEXT,
        min_length=10,
        max_length=300,
        requires_hitl=False,
        one_time_only=False,
        nova_signals={
            "ECO": 0.4,  # Ekonomik aktivite
            "CON": 0.3,  # Katkı sinyali
            "ID": 0.2,  # Kimlik/kişisel gelişim
        },
        abuse_rules={
            "min_quality_score": 40,
            "spam_detection": True,
            "honesty_bonus": True,  # "hiç yok" yazarsa → Integrity bonus
        },
        ai_scoring={
            "min_score": 40,
            "concreteness_weight": 0.6,  # Somutluk (SQL join öğrendim vs.)
            "value_weight": 0.4,  # Değer yaratma
        },
        special_rules=(
            "Eğer kullanıcı 'hiç yok' veya benzeri dürüst cevap verirse:\n"
            "- NCR düşük (2.0) ama Integrity sinyali +0.5 artar\n"
            "- Bu dürüstlük kaydı NovaScore'a pozitif etki eder"
        ),
    ),
    
    # ========================================================================
    # SKILL SLOT
    # ========================================================================
    
    QuestDefinition(
        quest_id="daily_micro_content",
        slot=QuestSlot.SKILL,
        quest_type=QuestType.MEME,
        title="1 Dakika Nasip Üretimi",
        description="Nasip/Rızık/Gerçek temalı 1 cümlelik söz yaz",
        instructions=(
            "Bugün 'Nasip / Rızık / Gerçek' temalı **1 cümlelik** kısa bir cümle yaz.\n"
            "Bu cümle ileride short/meme altyazısı olarak kullanılacak."
        ),
        base_ncr=10.0,
        base_xp=30,
        proof_type=ProofType.TEXT,
        min_length=15,
        max_length=150,
        requires_hitl=False,
        one_time_only=False,
        nova_signals={
            "CON": 0.5,  # Üretim katkısı
            "SOC": 0.3,  # Sosyal içerik
        },
        abuse_rules={
            "min_quality_score": 50,
            "spam_detection": True,
            "originality_check": True,  # Orijinallik kontrolü
        },
        ai_scoring={
            "min_score": 50,
            "originality_weight": 0.5,  # Orijinallik
            "meaning_weight": 0.3,  # Anlam
            "vibe_weight": 0.2,  # Vibe/ton
        },
        special_rules=(
            "AI Score 80+ ise → CreatorAsset pipeline'a girebilir (ileride)\n"
            "Bu içerik Viral Agency tarafına da bağlanabilir"
        ),
    ),
    
    QuestDefinition(
        quest_id="skill_xp_log",
        slot=QuestSlot.SKILL,
        quest_type=QuestType.REFLECTION,
        title="Skill XP (Mikro Öğrenme Log'u)",
        description="Bugün kendine yatırım olarak ne öğrendin?",
        instructions=(
            "Bugün kendine yatırım olarak ne öğrendin?\n"
            "1 cümle: kurs, video, kitap, pratik, kod, vs.\n\n"
            "**Not:** 'hiçbir şey' yazarsan → NCR yok ama kayıt var"
        ),
        base_ncr=6.0,
        base_xp=20,
        proof_type=ProofType.TEXT,
        min_length=10,
        max_length=200,
        requires_hitl=False,
        one_time_only=False,
        nova_signals={
            "REL": 0.4,  # Düzenli öğrenme = güvenilirlik
            "CON": 0.3,  # Kendine yatırım = katkı
        },
        abuse_rules={
            "min_quality_score": 35,
            "spam_detection": True,
            "concreteness_check": True,  # Somut şeyler daha yüksek score
        },
        ai_scoring={
            "min_score": 35,
            "concreteness_weight": 0.7,  # "SQL join öğrendim" gibi somut
            "learning_value_weight": 0.3,  # Öğrenme değeri
        },
        special_rules=(
            "Somut şeyler (örn: 'SQL join öğrendim') daha yüksek score alır\n"
            "'hiçbir şey' → NCR 0 ama kayıt tutulur (dürüstlük sinyali)"
        ),
    ),
    
    # ========================================================================
    # INTEGRITY SLOT
    # ========================================================================
    
    QuestDefinition(
        quest_id="swamp_story_v1",
        slot=QuestSlot.INTEGRITY,
        quest_type=QuestType.REFLECTION,
        title="Bataklık Kaydı",
        description="Seni en çok ezen anını 3-5 cümlede anlat",
        instructions=(
            "Kendini en çok **ezilmiş, sömürülmüş veya kullanılmış** hissettiğin\n"
            "bir anı 3–5 cümleyle yaz.\n"
            "Bu senin 'Bataklık Kaydın'. Sistem seni buradan yukarı çekecek."
        ),
        base_ncr=15.0,  # Yüksek ödül (duygusal emek)
        base_xp=50,
        proof_type=ProofType.TEXT,
        min_length=50,  # En az 3-5 cümle
        max_length=500,
        requires_hitl=True,  # Her zaman HITL (etik kuyruğu)
        one_time_only=True,  # Tek seferlik (onboarding'de bir kere)
        nova_signals={
            "ID": 0.5,  # Kimlik/kişisel hikaye
            "REL": 0.3,  # Güvenilirlik (açıklık)
            "SOC": 0.2,  # Empati/sosyal bağlantı
        },
        abuse_rules={
            "min_quality_score": 40,
            "spam_detection": True,
            "emotional_depth_check": True,  # Duygusal derinlik kontrolü
        },
        ai_scoring={
            "min_score": 40,
            "emotional_weight": 0.4,  # Duygusal derinlik
            "coherence_weight": 0.3,  # Tutarlılık
            "authenticity_weight": 0.3,  # Otantiklik
        },
        special_rules=(
            "**Her zaman HITL** (insan moderasyon/etik kuyruğu)\n"
            "AI = sadece scoring, etik değil\n"
            "Bu görev onboarding'de bir kere çıkar"
        ),
    ),
    
    QuestDefinition(
        quest_id="nasip_oath_v1",
        slot=QuestSlot.INTEGRITY,
        quest_type=QuestType.REFLECTION,
        title="Nasip Yemin Kartı",
        description="3 maddeden hepsini kabul ediyorsan 'Kabul ediyorum' yaz",
        instructions=(
            "Aşağıdaki 3 maddeden **hepsini kabul ediyorsan** 'Kabul ediyorum' yaz.\n\n"
            "1. Sistemden çalmayacağım.\n"
            "2. Başkasının emeğiyle övünmeyeceğim.\n"
            "3. Yalan kanıt üretmeyeceğim."
        ),
        base_ncr=5.0,
        base_xp=20,
        proof_type=ProofType.TEXT,
        min_length=10,
        max_length=50,
        requires_hitl=False,
        one_time_only=True,  # Tek seferlik
        nova_signals={
            "ID": 0.6,  # Kimlik/taahhüt
        },
        abuse_rules={
            "exact_match_check": True,  # "Kabul ediyorum" dışında → flag
            "oath_violation_tracking": True,  # Yemin sonrası ihlal → RiskScore bonus artış
        },
        ai_scoring={
            "min_score": 80,  # "Kabul ediyorum" yazarsa → 100
            "exact_match_bonus": True,  # Tam eşleşme bonusu
        },
        special_rules=(
            "**AbuseGuard:** Yemin edip sonra spam/proof hilesi yaparsa → RiskScore bonus artış\n"
            "Bu görev IntegrityScore, CP tavanı, NovaScore ceiling'i etkiler"
        ),
    ),
    
    QuestDefinition(
        quest_id="trusted_friend_refer",
        slot=QuestSlot.INTEGRITY,
        quest_type=QuestType.REFLECTION,
        title="Tribe Ping",
        description="Hayatında gerçekten güvendiğin 1 kişinin adını yaz",
        instructions=(
            "Hayatında **gerçekten güvendiğin** 1 kişinin adını (veya rumuzunu) yaz.\n"
            "Onu sisteme davet etmek zorunda değilsin.\n"
            "Sadece 'kim' senin için güven demek, onu gör."
        ),
        base_ncr=3.0,  # Düşük ödül (psikolojik sinyal)
        base_xp=15,
        proof_type=ProofType.TEXT,
        min_length=2,
        max_length=50,
        requires_hitl=False,
        one_time_only=False,
        nova_signals={
            "ID": 0.3,  # Kimlik/güven ilişkileri
            "SOC": 0.2,  # Sosyal bağlantı
        },
        abuse_rules={
            "min_quality_score": 20,
            "spam_detection": True,
        },
        ai_scoring={
            "min_score": 20,
            "meaning_weight": 0.5,  # Anlamlı isim mi?
            "authenticity_weight": 0.5,  # Otantiklik
        },
        special_rules=(
            "Sistem bunu *hemen* referral'a çevirmez, sadece psikolojik & identity sinyali\n"
            "İleride: Bu isim sisteme gelirse → referral bağlantısı kurulabilir"
        ),
    ),
]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_quest_by_id(quest_id: str) -> Optional[QuestDefinition]:
    """Quest ID'ye göre tanım getir."""
    for quest in BASE_QUEST_DEFS:
        if quest.quest_id == quest_id:
            return quest
    return None


def get_quests_by_slot(slot: QuestSlot) -> list[QuestDefinition]:
    """Slot'a göre quest'leri getir."""
    return [q for q in BASE_QUEST_DEFS if q.slot == slot]


def get_daily_quest_set(
    user_id: int,
    completed_one_time_quests: list[str] = None,
) -> dict[QuestSlot, QuestDefinition]:
    """
    Kullanıcı için günlük quest seti oluştur.
    
    Her slot'tan 1 görev seçer:
    - MONEY slot → daily_income_snapshot veya micro_value_action
    - SKILL slot → daily_micro_content veya skill_xp_log
    - INTEGRITY slot → swamp_story_v1 (tek seferlik), nasip_oath_v1 (tek seferlik), veya trusted_friend_refer
    
    Args:
        user_id: Kullanıcı ID
        completed_one_time_quests: Tamamlanmış tek seferlik görev ID'leri
    
    Returns:
        {slot: QuestDefinition} dict
    """
    completed_one_time_quests = completed_one_time_quests or []
    
    daily_set = {}
    
    # MONEY slot - rastgele birini seç
    money_quests = [q for q in get_quests_by_slot(QuestSlot.MONEY) if not q.one_time_only or q.quest_id not in completed_one_time_quests]
    if money_quests:
        import random
        daily_set[QuestSlot.MONEY] = random.choice(money_quests)
    
    # SKILL slot - rastgele birini seç
    skill_quests = [q for q in get_quests_by_slot(QuestSlot.SKILL) if not q.one_time_only or q.quest_id not in completed_one_time_quests]
    if skill_quests:
        import random
        daily_set[QuestSlot.SKILL] = random.choice(skill_quests)
    
    # INTEGRITY slot - önce tek seferlikleri kontrol et
    integrity_quests = [q for q in get_quests_by_slot(QuestSlot.INTEGRITY) if not q.one_time_only or q.quest_id not in completed_one_time_quests]
    if integrity_quests:
        import random
        daily_set[QuestSlot.INTEGRITY] = random.choice(integrity_quests)
    
    return daily_set


# =============================================================================
# EXPORT
# =============================================================================

__all__ = [
    "QuestSlot",
    "ProofType",
    "QuestDefinition",
    "BASE_QUEST_DEFS",
    "get_quest_by_id",
    "get_quests_by_slot",
    "get_daily_quest_set",
]

