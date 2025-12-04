# app/economy/constitution.py
"""
SiyahKare NCR Ekonomi Anayasası v1.0

Temel İlkeler:
- Madde 1: NCR tek resmî dijital para birimi
- Madde 2: Emek İlkesi - "Emek yoksa, NCR de yoktur"
- Madde 3: NCR Kazanma Mekanizması
- Madde 4: NCR Harcama Alanları
- Madde 5: Enflasyon Kontrolü ve Burn
- Madde 6: Emek Dışı Kazancın Geçersizliği
- Madde 7: Vatandaşın Hakkı
"""
from enum import Enum
from typing import Optional
from dataclasses import dataclass
from datetime import datetime

from pydantic import BaseModel, Field


# =============================================================================
# ECONOMY MODES (Madde 9)
# =============================================================================

class EconomyMode(str, Enum):
    """
    Ekonomik modlar - Neural Governor tarafından belirlenir.
    """
    NORMAL = "normal"           # Standart kurallar
    GROWTH = "growth"           # Yeni vatandaş odaklı, yüksek emission
    STABILIZATION = "stabilization"  # Enflasyon kontrolü, düşük emission
    RECOVERY = "recovery"       # Kriz modu, acil önlemler


# =============================================================================
# ECONOMIC CONSTANTS
# =============================================================================

class EconomyConstants:
    """
    Ekonomi sabitleri - DAO tarafından güncellenebilir.
    """
    # Madde 3: RewardMultiplier sınırları
    MIN_REWARD_MULTIPLIER: float = 0.1
    MAX_REWARD_MULTIPLIER: float = 2.0
    
    # Madde 3: Streak Factor
    MAX_STREAK_DAYS: int = 30
    STREAK_BONUS_PER_DAY: float = 0.01  # Her gün için +%1
    
    # Madde 3: SiyahScore Factor
    SIYAH_SCORE_BASE: float = 0.7
    SIYAH_SCORE_MAX_BONUS: float = 0.5
    
    # Madde 3: Citizen Level Multipliers
    # Artık app/core/citizenship.py'den get_citizen_level_multiplier() kullanılıyor
    
    # Madde 5: Burn oranları
    MARKET_FEE_RATE: float = 0.05        # %5 market fee
    OFF_RAMP_FEE_RATE: float = 0.10      # %10 off-ramp fee
    BURN_RATIO: float = 0.5              # Fee'nin %50'si yakılır
    
    # Madde 5: Inactivity
    INACTIVITY_THRESHOLD_DAYS: int = 90   # 90 gün inaktivite → freeze
    
    # Madde 6: Fraud Risk Deltas
    FRAUD_RISK_DELTAS: dict = {
        "FRAUD_BOT": 3.0,
        "FRAUD_SYBIL": 5.0,
        "FRAUD_EXPLOIT": 5.0,
        "FRAUD_COPY": 2.0,
    }
    
    # Madde 6: Fraud Cooldown (saat)
    FRAUD_COOLDOWN_HOURS: dict = {
        "FRAUD_BOT": 168,      # 7 gün
        "FRAUD_SYBIL": 9999,   # Kalıcı (tüm hesaplar)
        "FRAUD_EXPLOIT": 9999, # Kalıcı (inceleme ile)
        "FRAUD_COPY": 72,      # 3 gün
    }


ECONOMY_CONSTANTS = EconomyConstants()


# =============================================================================
# FRAUD TYPES (Madde 6)
# =============================================================================

class FraudType(str, Enum):
    """
    Emek dışı kazanç türleri - Madde 6.
    """
    BOT = "FRAUD_BOT"           # Bot/script spam
    SYBIL = "FRAUD_SYBIL"       # Multi-account
    EXPLOIT = "FRAUD_EXPLOIT"   # Bug abuse
    COPY = "FRAUD_COPY"         # Plagiarism


# =============================================================================
# RESULT MODELS
# =============================================================================

class RewardMultiplierResult(BaseModel):
    """
    RewardMultiplier hesaplama sonucu - Madde 3.
    """
    user_id: str
    base_ncr: float = Field(description="Görevin base NCR değeri")
    final_ncr: float = Field(description="Hesaplanan final NCR")
    multiplier: float = Field(ge=0.1, le=2.0, description="Final çarpan")
    
    # Bileşenler (şeffaflık için - Madde 7)
    streak_factor: float = Field(description="Streak çarpanı (1.0-1.3)")
    siyah_factor: float = Field(description="Kalite çarpanı (0.7-1.2)")
    risk_factor: float = Field(description="Risk çarpanı (0.0-1.0)")
    nova_factor: float = Field(description="Vatandaşlık çarpanı (0.5-1.5)")
    
    # Context
    streak_days: int
    siyah_score_avg: float
    risk_score: float
    citizen_level: str


class BurnResult(BaseModel):
    """
    Burn işlemi sonucu - Madde 5.
    """
    transaction_id: str
    user_id: str
    gross_amount: float = Field(description="İşlem brüt tutarı")
    fee_amount: float = Field(description="Alınan fee")
    burn_amount: float = Field(description="Yakılan NCR")
    net_amount: float = Field(description="Kullanıcıya kalan")
    fee_type: str = Field(description="market | off_ramp | other")
    burned_at: datetime


class ClawbackResult(BaseModel):
    """
    Geri alma (clawback) sonucu - Madde 6.
    """
    user_id: str
    fraud_type: FraudType
    clawed_amount: float = Field(description="Geri alınan NCR")
    risk_delta: float = Field(description="RiskScore artışı")
    cooldown_hours: int = Field(description="Uygulanan cooldown")
    reason: str
    clawed_at: datetime


# =============================================================================
# USER CONTEXT (RewardMultiplier hesaplama için)
# =============================================================================

@dataclass
class UserEconomyContext:
    """
    Kullanıcı ekonomi context'i - RewardMultiplier hesaplama için.
    """
    user_id: str
    streak_days: int = 0
    siyah_score_avg: float = 50.0
    risk_score: float = 0.0
    citizen_level: str = "resident"
    ncr_balance: float = 0.0
    last_activity_at: Optional[datetime] = None


# =============================================================================
# ECONOMY RIGHTS (Madde 7)
# =============================================================================

class CitizenEconomyRights(BaseModel):
    """
    Vatandaşın ekonomik hakları - Madde 7.
    """
    # Tasarruf hakkı
    can_spend: bool = True
    can_transfer: bool = True
    can_stake: bool = True
    can_withdraw: bool = True
    
    # Şeffaflık hakkı
    can_view_earnings: bool = True
    can_view_deductions: bool = True
    can_view_nova_score: bool = True
    can_view_risk_score: bool = True
    
    # İtiraz hakkı
    can_appeal_clawback: bool = True
    can_appeal_sanction: bool = True
    can_appeal_burn: bool = True
    
    # Limitler (seviyeye göre)
    daily_withdraw_limit: float = 200.0
    daily_transfer_limit: float = 500.0
    
    @classmethod
    def for_level(cls, citizen_level: str) -> "CitizenEconomyRights":
        """Vatandaşlık seviyesine göre haklar."""
        limits = {
            "ghost": {"daily_withdraw_limit": 50.0, "daily_transfer_limit": 100.0, "can_stake": False},
            "resident": {"daily_withdraw_limit": 200.0, "daily_transfer_limit": 500.0},
            "core_citizen": {"daily_withdraw_limit": 500.0, "daily_transfer_limit": 1000.0},
            "sovereign": {"daily_withdraw_limit": 1000.0, "daily_transfer_limit": 2000.0},
            "prime": {"daily_withdraw_limit": 2000.0, "daily_transfer_limit": 5000.0},
        }
        level_config = limits.get(citizen_level, limits["resident"])
        return cls(**level_config)


# =============================================================================
# ECONOMY GUARANTEES (Madde 8)
# =============================================================================

ECONOMY_GUARANTEES = {
    "emek_kazanc": "Çalışan kazanır, çalışmayan kazanamaz",
    "seffaf_kurallar": "Tüm formüller açık ve denetlenebilir",
    "adil_dagilim": "Ahlaklı vatandaş daha çok kazanır",
    "enflasyon_kontrolu": "Burn + Limit ile değer koruması",
    "tasarruf_guvenligi": "Haksız el koyma yok",
}

ECONOMY_PROHIBITIONS = {
    "sebepsiz_basim": "Sebepsiz NCR yaratma yasak (emeksiz basım)",
    "keyfi_silme": "Keyfi bakiye silme yasak (şeffaf kural olmadan)",
    "gizli_fee": "Gizli fee uygulama yasak (tüm kesintiler görünür)",
    "habersiz_degisiklik": "Vatandaşı bilgilendirmeden kural değiştirme yasak",
}

