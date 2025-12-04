# app/justice/constitution.py
"""
AuroraOS "Adalet" Modülü – Anayasa v1.0

SiyahKare devletinin otomatik ceza motoru.
Prensipler:
- P1: Otomatik Adalet, İnsan Onayı (kritik eşiklerde HITL/Ombudsman)
- P2: Ekonomik Ceza, Aşağılama Yok (NCR/XP/erişim üzerinden)
- P3: Şeffaflık (RuleID + Sebep + Süre görülür)
- P4: Tersine Çevrilebilirlik (çoğu ceza zaman + düzgün davranış ile silinir)
- P5: "Ahlaklı House Edge" Uyumu (ödül motoru ile ceza motoru aynı sinyalleri kullanır)
"""
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, NamedTuple
from dataclasses import dataclass

from pydantic import BaseModel, Field

from ..core.citizenship import CitizenLevel, nova_score_to_level, CITIZEN_LEVEL_INFO


# =============================================================================
# SANCTION TYPES (Ceza Tipleri)
# =============================================================================

class SanctionType(str, Enum):
    """
    Ceza tipleri - P2 prensibi: Ekonomik Ceza, Aşağılama Yok.
    """
    W1_WARNING = "W1"           # Uyarı: UI banner + log. Ekonomiye dokunmaz.
    E1_REWARD_PENALTY = "E1"    # Ödül Düşürme: reward_multiplier düşürülür
    C1_COOLDOWN = "C1"          # Cooldown: görev/withdraw kapatılır
    L1_LIMIT = "L1"             # Limit: günlük max NCR/görev sayısı düşürülür
    S1_SHADOW_FREEZE = "S1"     # Shadow Freeze: görev vermez, "sistem yoğun" görünür
    H1_HUMAN_REVIEW = "H1"      # Human Review: zorunlu DAO/Ombudsman incelemesi


# =============================================================================
# RULE DEFINITIONS (Kanun Tablosu v1.0)
# =============================================================================

class RuleID(str, Enum):
    """Adalet kuralları."""
    R01_FAST_COMPLETION = "R01"    # Hızlı Tamamlama / Emek Hırsızlığı
    R02_LOW_QUALITY_SPAM = "R02"   # Düşük Kalite Serisi / Spam
    R03_MULTI_ACCOUNT = "R03"      # Multi Account / Sybil Denemesi
    R04_TOXICITY = "R04"           # Toxicity & Taciz
    R05_ECONOMIC_MANIP = "R05"     # Ekonomik Manipülasyon (Pump & Dump / Referral Abuse)
    R06_SYSTEM_EXPLOIT = "R06"     # Sistem Exploit / Bug Abuse


@dataclass
class JusticeRule:
    """
    Kanun tanımı.
    
    Her kural için:
    - trigger koşulları
    - base cooldown (saat)
    - reward_multiplier (ceza sonrası)
    - risk_delta (RiskScore artışı)
    - requires_human (HITL zorunlu mu)
    """
    rule_id: RuleID
    name: str
    description: str
    base_cooldown_hours: int
    reward_multiplier: float  # 0.0-1.0 arası
    risk_delta: float
    requires_human: bool
    sanction_types: list[SanctionType]


# Kanun Tablosu v1.0
RULE_SET: dict[RuleID, JusticeRule] = {
    # R01 – Hızlı Tamamlama / Emek Hırsızlığı
    RuleID.R01_FAST_COMPLETION: JusticeRule(
        rule_id=RuleID.R01_FAST_COMPLETION,
        name="Hızlı Tamamlama / Emek Hırsızlığı",
        description="completion_time < min_expected_time VEYA TOO_FAST_COMPLETION 3x/24h",
        base_cooldown_hours=12,
        reward_multiplier=0.0,  # o görev ödülü = 0
        risk_delta=1.0,
        requires_human=False,
        sanction_types=[SanctionType.E1_REWARD_PENALTY, SanctionType.C1_COOLDOWN],
    ),
    
    # R02 – Düşük Kalite Serisi / Spam
    RuleID.R02_LOW_QUALITY_SPAM: JusticeRule(
        rule_id=RuleID.R02_LOW_QUALITY_SPAM,
        name="Düşük Kalite Serisi / Spam",
        description="Son 10 görevde siyah_score_avg < 50 VEYA LOW_QUALITY_BURST flag",
        base_cooldown_hours=0,  # cooldown yok, sadece limit
        reward_multiplier=0.7,
        risk_delta=0.5,
        requires_human=False,
        sanction_types=[SanctionType.E1_REWARD_PENALTY, SanctionType.L1_LIMIT],
    ),
    
    # R03 – Multi Account / Sybil Denemesi
    RuleID.R03_MULTI_ACCOUNT: JusticeRule(
        rule_id=RuleID.R03_MULTI_ACCOUNT,
        name="Multi Account / Sybil Denemesi",
        description="Aynı cihaz/IP/numara → 3+ account, ortak referral zinciri",
        base_cooldown_hours=168,  # 7 gün withdraw freeze
        reward_multiplier=0.0,
        risk_delta=3.0,
        requires_human=True,  # Ombudsman incelemesi zorunlu
        sanction_types=[SanctionType.S1_SHADOW_FREEZE, SanctionType.C1_COOLDOWN, SanctionType.H1_HUMAN_REVIEW],
    ),
    
    # R04 – Toxicity & Taciz
    RuleID.R04_TOXICITY: JusticeRule(
        rule_id=RuleID.R04_TOXICITY,
        name="Toxicity & Taciz",
        description="toxicity_score > 0.8 VEYA NSFW/illegal içerik",
        base_cooldown_hours=48,  # 24-72 saat chat ban
        reward_multiplier=0.5,
        risk_delta=2.0,
        requires_human=False,  # tekrarı için insan gerekir
        sanction_types=[SanctionType.C1_COOLDOWN, SanctionType.E1_REWARD_PENALTY],
    ),
    
    # R05 – Ekonomik Manipülasyon
    RuleID.R05_ECONOMIC_MANIP: JusticeRule(
        rule_id=RuleID.R05_ECONOMIC_MANIP,
        name="Ekonomik Manipülasyon (Pump & Dump / Referral Abuse)",
        description="Referral'dan gelen hesapların 70%+ ban/risk8+ VEYA wash trading",
        base_cooldown_hours=168,  # 7-30 gün withdraw freeze
        reward_multiplier=0.0,  # referans bonusları iptal
        risk_delta=3.0,
        requires_human=True,  # DAO/ops incelemesi
        sanction_types=[SanctionType.C1_COOLDOWN, SanctionType.H1_HUMAN_REVIEW],
    ),
    
    # R06 – Sistem Exploit / Bug Abuse
    RuleID.R06_SYSTEM_EXPLOIT: JusticeRule(
        rule_id=RuleID.R06_SYSTEM_EXPLOIT,
        name="Sistem Exploit / Bug Abuse",
        description="Anormal API istekleri, negatif bakiye, double-claim pattern",
        base_cooldown_hours=9999,  # Kalıcı (full account freeze)
        reward_multiplier=0.0,
        risk_delta=5.0,
        requires_human=True,  # Ombudsman/DevOps zorunlu
        sanction_types=[SanctionType.C1_COOLDOWN, SanctionType.H1_HUMAN_REVIEW],
    ),
}


# =============================================================================
# SANCTION MODEL (Ceza Kararı)
# =============================================================================

class Sanction(BaseModel):
    """
    Ceza kararı - P3 prensibi: Şeffaflık.
    
    Her cezanın yanında RuleID + Sebep + Süre görülür.
    """
    rule_id: RuleID
    sanction_types: list[str]  # SanctionType enum değerleri string olarak
    cooldown_hours: int
    cooldown_until: Optional[datetime] = None
    reward_multiplier: float = Field(ge=0.0, le=1.0)
    risk_delta: float
    requires_human: bool
    daily_task_limit: Optional[int] = None  # L1 için
    daily_ncr_limit: Optional[float] = None  # L1 için
    reason: str
    recovery_hint: Optional[str] = None  # P4: Nasıl düzelir?
    
    class Config:
        use_enum_values = True


# =============================================================================
# JUSTICE ENGINE (Ceza Hesaplayıcı)
# =============================================================================

class JusticeEngine:
    """
    Adalet motoru - Anayasa v1.0.
    
    NovaScore'u merhamet katsayısı olarak kullanır:
    - Yüksek NovaScore → biraz daha hafif ceza
    - Düşük NovaScore → ceza ağırlaşır
    """
    
    @staticmethod
    def detect_rule(
        cooldown_flags: list[str],
        siyah_score_avg: Optional[float] = None,
        toxicity_score: Optional[float] = None,
        multi_device_score: Optional[float] = None,
        fraud_flags: Optional[list[str]] = None,
    ) -> Optional[RuleID]:
        """
        Event'ten hangi kuralın tetiklendiğini belirle.
        
        Args:
            cooldown_flags: TOO_FAST_COMPLETION, LOW_QUALITY_BURST, MULTI_ACCOUNT
            siyah_score_avg: Son görevlerin kalite ortalaması
            toxicity_score: Mesaj/media toxicity skoru (0-1)
            multi_device_score: Aynı IP/cihaz şişirme skoru (0-1)
            fraud_flags: REFERRAL_ABUSE, WASH_TRADING, SYSTEM_EXPLOIT, etc.
        """
        fraud_flags = fraud_flags or []
        
        # R01 - Hızlı Tamamlama
        if "TOO_FAST_COMPLETION" in cooldown_flags:
            return RuleID.R01_FAST_COMPLETION
        
        # R02 - Düşük Kalite Serisi
        if "LOW_QUALITY_BURST" in cooldown_flags or (siyah_score_avg and siyah_score_avg < 50):
            return RuleID.R02_LOW_QUALITY_SPAM
        
        # R03 - Multi Account
        if "MULTI_ACCOUNT" in cooldown_flags or (multi_device_score and multi_device_score > 0.7):
            return RuleID.R03_MULTI_ACCOUNT
        
        # R04 - Toxicity
        if toxicity_score and toxicity_score > 0.8:
            return RuleID.R04_TOXICITY
        
        # R05 - Ekonomik Manipülasyon
        if "REFERRAL_ABUSE" in fraud_flags or "WASH_TRADING" in fraud_flags:
            return RuleID.R05_ECONOMIC_MANIP
        
        # R06 - Sistem Exploit
        if "SYSTEM_EXPLOIT" in fraud_flags or "DOUBLE_CLAIM" in fraud_flags or "NEGATIVE_BALANCE" in fraud_flags:
            return RuleID.R06_SYSTEM_EXPLOIT
        
        return None
    
    @staticmethod
    def compute_mercy_factor(nova_score: float) -> float:
        """
        NovaScore'dan merhamet katsayısı hesapla.
        
        NovaScore 100 → mercy = 0.5 (ceza %50 hafifler)
        NovaScore 0 → mercy = 1.0 (ceza tam uygulanır)
        """
        return 1.0 - (nova_score / 200.0)
    
    @staticmethod
    def apply_justice(
        rule_id: RuleID,
        risk_score: float,
        nova_score: float,
        repeat_count: int = 0,
    ) -> Sanction:
        """
        Ceza hesapla.
        
        Args:
            rule_id: Tetiklenen kural
            risk_score: Kullanıcının mevcut risk skoru (0-10)
            nova_score: Kullanıcının NovaScore'u (0-100)
            repeat_count: Bu kuralın tekrar sayısı (7 gün içinde)
        
        Returns:
            Sanction kararı
        """
        rule = RULE_SET[rule_id]
        mercy = JusticeEngine.compute_mercy_factor(nova_score)
        
        # Cooldown hesapla
        base_cooldown = rule.base_cooldown_hours
        # Risk yükseldikçe cooldown artar
        risk_multiplier = 1.0 + (risk_score / 5.0)
        # Tekrarlarda cooldown katlanır
        repeat_multiplier = 1.0 + (repeat_count * 0.5)
        
        cooldown_hours = int(base_cooldown * risk_multiplier * repeat_multiplier * mercy)
        cooldown_until = datetime.utcnow() + timedelta(hours=cooldown_hours) if cooldown_hours > 0 else None
        
        # Reward multiplier: tekrarlarda daha düşük
        reward_mult = rule.reward_multiplier
        if repeat_count > 0:
            reward_mult = max(0.0, reward_mult - 0.1 * repeat_count)
        
        # Daily limits (L1 için)
        daily_task_limit = None
        daily_ncr_limit = None
        if SanctionType.L1_LIMIT in rule.sanction_types:
            daily_task_limit = max(2, 10 - repeat_count * 2)
            daily_ncr_limit = max(10.0, 100.0 - repeat_count * 20.0)
        
        # Recovery hint (P4: Tersine Çevrilebilirlik)
        recovery_hints = {
            RuleID.R01_FAST_COMPLETION: "7 gün içinde 5 görevi düzgün tamamlarsan ceza kalkar.",
            RuleID.R02_LOW_QUALITY_SPAM: "Üst üste 5 görevi siyah_score >= 70 ile tamamlarsan ceza kalkar.",
            RuleID.R03_MULTI_ACCOUNT: "Ombudsman incelemesini bekle. Temiz çıkarsan ceza kaldırılır.",
            RuleID.R04_TOXICITY: "24 saat boyunca saygılı ol. 3 ihlal/30 gün → insan incelemesi.",
            RuleID.R05_ECONOMIC_MANIP: "DAO incelemesi zorunlu. Ekonomik manipülasyon ciddi suçtur.",
            RuleID.R06_SYSTEM_EXPLOIT: "DevOps ile iletişime geç. Bug report ise ödül alabilirsin.",
        }
        
        return Sanction(
            rule_id=rule_id,
            sanction_types=rule.sanction_types,
            cooldown_hours=cooldown_hours,
            cooldown_until=cooldown_until,
            reward_multiplier=reward_mult,
            risk_delta=rule.risk_delta,
            requires_human=rule.requires_human,
            daily_task_limit=daily_task_limit,
            daily_ncr_limit=daily_ncr_limit,
            reason=f"{rule.name}: {rule.description}",
            recovery_hint=recovery_hints.get(rule_id),
        )


# =============================================================================
# JUSTICE SIGNALS (Sinyal Modeli)
# =============================================================================

class JusticeSignals(BaseModel):
    """
    Adalet modülü giriş sinyalleri.
    
    Bu metrikler ödül motoru ile paylaşılır (P5: Ahlaklı House Edge Uyumu).
    """
    risk_score: float = Field(ge=0.0, le=10.0, description="AbuseGuard'dan (0-10)")
    siyah_score: float = Field(ge=0.0, le=100.0, description="İçerik kalitesi (0-100)")
    cooldown_flags: list[str] = Field(default_factory=list, description="TOO_FAST_COMPLETION, LOW_QUALITY_BURST, MULTI_ACCOUNT")
    toxicity_score: float = Field(ge=0.0, le=1.0, default=0.0, description="Mesaj & media analizi (0-1)")
    multi_device_score: float = Field(ge=0.0, le=1.0, default=0.0, description="Aynı IP/cihaz/numara şişirme (0-1)")
    fraud_flags: list[str] = Field(default_factory=list, description="REFERRAL_ABUSE, WASH_TRADING, SYSTEM_EXPLOIT, etc.")


# =============================================================================
# VATANDAŞLIK SEVİYELERİ (NovaScore → Level)
# =============================================================================
# Artık app/core/citizenship.py'den import ediliyor

