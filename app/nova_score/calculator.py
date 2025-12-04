# app/nova_score/calculator.py
"""
NovaScore v1.0 – Vatandaşlık Skoru Formülü

Amaç: "Bu adam sisteme yararlı mı, güvenilir mi, stabil mi?" sorusuna tek rakamla cevap.
0-100 arası, 60+ = güvenilir, 80+ = çekirdek citizen.

5 Bileşen:
1. ActivityScore (0-25): Düzen ve süreklilik
2. QualityScore (0-25): Üretilen işin kalitesi (SiyahScore)
3. EthicsScore (0-25): RiskScore'un tersinden
4. ContributionScore (0-15): Tribe'e katkı (referral, DAO, validator)
5. EconomicScore (0-10): NCR stake / kullanım
"""
from dataclasses import dataclass
from typing import Optional
from pydantic import BaseModel, Field

from ..core.citizenship import CitizenLevel, nova_score_to_level, CITIZEN_LEVEL_INFO
from .models import NovaScoreBreakdown


# =============================================================================
# NOVA SCORE BREAKDOWN (Pydantic Model)
# =============================================================================

# NovaScoreBreakdown artık app/nova_score/models.py'den import ediliyor


class NovaScoreResult(BaseModel):
    """NovaScore hesaplama sonucu."""
    user_id: str
    value: float = Field(ge=0.0, le=100.0, description="NovaScore (0-100)")
    level: CitizenLevel
    level_name: str
    level_description: str
    breakdown: NovaScoreBreakdown
    task_multiplier: float = Field(description="Görev ödül çarpanı")
    withdraw_limit_daily: float = Field(description="Günlük withdraw limiti (NCR)")
    can_validate: bool = Field(description="DAO validator olabilir mi")
    can_refer: bool = Field(description="Referral yapabilir mi")


# =============================================================================
# INPUT DATA (Hesaplama için gerekli veriler)
# =============================================================================

@dataclass
class NovaScoreInput:
    """NovaScore hesaplama için gerekli kullanıcı verileri."""
    user_id: str
    
    # Activity metricleri
    streak_days: int = 0                # Üst üste aktif gün sayısı (max 30)
    weekly_completed_tasks: int = 0     # Son 7 günde tamamlanan görev (0-50)
    
    # Quality metricleri
    siyah_score_avg: float = 50.0       # Son 20 görev kalite ortalaması (0-100)
    
    # Ethics metricleri
    risk_score: float = 0.0             # AbuseGuard RiskScore (0-10)
    
    # Contribution metricleri
    valid_referrals: int = 0            # Aktif referral sayısı (limit 20)
    dao_votes: int = 0                  # Son 30 gün DAO/validator katkısı (limit 20)
    
    # Economic metricleri
    ncr_staked: float = 0.0             # Aktif stake (NCR)
    usage_volume_30d: float = 0.0       # 30 günde harcanan NCR


# =============================================================================
# NOVA SCORE CALCULATOR v1.0
# =============================================================================

class NovaScoreCalculator:
    """
    NovaScore v1.0 Hesaplayıcı.
    
    5 bileşenli formül:
    NovaScore = ActivityScore + QualityScore + EthicsScore + ContributionScore + EconomicScore
    """
    
    # Normalização sabitleri
    MAX_STREAK_DAYS = 30
    MAX_WEEKLY_TASKS = 50
    MAX_REFERRALS = 20
    MAX_DAO_VOTES = 20
    MAX_NCR_STAKED = 10_000.0  # 10k NCR üstü full puan
    MAX_USAGE_VOLUME = 2_000.0  # 2k NCR üstü full puan
    
    @staticmethod
    def _normalize(value: float, max_value: float) -> float:
        """Değeri 0-1 aralığına normalize et."""
        if max_value <= 0:
            return 0.0
        return min(1.0, max(0.0, value / max_value))
    
    @classmethod
    def compute_activity_score(cls, streak_days: int, weekly_completed: int) -> float:
        """
        ActivityScore (0-25): Düzen ve süreklilik.
        
        activity = (
            min(streak_days, 30) / 30 * 15  # max 15
            + min(weekly_completed, 50) / 50 * 10  # max 10
        )
        """
        streak_component = cls._normalize(streak_days, cls.MAX_STREAK_DAYS) * 15.0
        weekly_component = cls._normalize(weekly_completed, cls.MAX_WEEKLY_TASKS) * 10.0
        return round(streak_component + weekly_component, 2)
    
    @classmethod
    def compute_quality_score(cls, siyah_score_avg: float) -> float:
        """
        QualityScore (0-25): Üretilen işin kalitesi.
        
        quality = (siyah_avg / 100) * 25
        """
        normalized = cls._normalize(siyah_score_avg, 100.0)
        return round(normalized * 25.0, 2)
    
    @classmethod
    def compute_ethics_score(cls, risk_score: float) -> float:
        """
        EthicsScore (0-25): RiskScore'un tersinden.
        
        0 risk → full 25
        10 risk → 0
        
        ethics = max(0.0, 25 * (1 - risk_score / 10))
        """
        ethics = max(0.0, 25.0 * (1.0 - risk_score / 10.0))
        return round(ethics, 2)
    
    @classmethod
    def compute_contribution_score(cls, valid_referrals: int, dao_votes: int) -> float:
        """
        ContributionScore (0-15): Tribe'e katkı.
        
        contrib = (
            min(valid_referrals, 20) / 20 * 8   # max 8
            + min(dao_votes, 20) / 20 * 7       # max 7
        )
        """
        referral_component = cls._normalize(valid_referrals, cls.MAX_REFERRALS) * 8.0
        dao_component = cls._normalize(dao_votes, cls.MAX_DAO_VOTES) * 7.0
        return round(referral_component + dao_component, 2)
    
    @classmethod
    def compute_economic_score(cls, ncr_staked: float, usage_volume: float) -> float:
        """
        EconomicScore (0-10): NCR stake / kullanım.
        
        stake_component = min(ncr_staked / 10_000, 1.0) * 6  # 10k NCR üstü full
        usage_component = min(usage_volume / 2_000, 1.0) * 4 # 2k NCR üstü full
        
        economic = stake_component + usage_component
        """
        stake_component = cls._normalize(ncr_staked, cls.MAX_NCR_STAKED) * 6.0
        usage_component = cls._normalize(usage_volume, cls.MAX_USAGE_VOLUME) * 4.0
        return round(stake_component + usage_component, 2)
    
    @classmethod
    def calculate(cls, input_data: NovaScoreInput) -> NovaScoreResult:
        """
        NovaScore hesapla.
        
        NovaScore = activity + quality + ethics + contrib + economic
        """
        # Her bileşeni hesapla
        activity = cls.compute_activity_score(
            input_data.streak_days,
            input_data.weekly_completed_tasks
        )
        quality = cls.compute_quality_score(input_data.siyah_score_avg)
        ethics = cls.compute_ethics_score(input_data.risk_score)
        contribution = cls.compute_contribution_score(
            input_data.valid_referrals,
            input_data.dao_votes
        )
        economic = cls.compute_economic_score(
            input_data.ncr_staked,
            input_data.usage_volume_30d
        )
        
        # Toplam skor
        total = activity + quality + ethics + contribution + economic
        nova_score = round(min(100.0, max(0.0, total)), 1)
        
        # Level belirle
        level = nova_score_to_level(nova_score)
        level_info = CITIZEN_LEVEL_INFO[level]
        
        return NovaScoreResult(
            user_id=input_data.user_id,
            value=nova_score,
            level=level,
            level_name=level_info["name"],
            level_description=level_info["description"],
            breakdown=NovaScoreBreakdown(
                activity=activity,
                quality=quality,
                ethics=ethics,
                contribution=contribution,
                economic=economic,
            ),
            task_multiplier=level_info["task_multiplier"],
            withdraw_limit_daily=level_info["withdraw_limit_daily"],
            can_validate=level_info["can_validate"],
            can_refer=level_info["can_refer"],
        )


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def recompute_nova_score(
    user_id: str,
    streak_days: int,
    weekly_completed_tasks: int,
    siyah_score_avg: float,
    risk_score: float,
    valid_referrals: int,
    dao_votes: int,
    ncr_staked: float,
    usage_volume_30d: float,
) -> NovaScoreResult:
    """
    NovaScore'u yeniden hesapla.
    
    Bu fonksiyon periyodik olarak (örn. günlük) çağrılır
    veya önemli eventlerde (görev tamamlama, referral onayı, vs.) tetiklenir.
    """
    input_data = NovaScoreInput(
        user_id=user_id,
        streak_days=streak_days,
        weekly_completed_tasks=weekly_completed_tasks,
        siyah_score_avg=siyah_score_avg,
        risk_score=risk_score,
        valid_referrals=valid_referrals,
        dao_votes=dao_votes,
        ncr_staked=ncr_staked,
        usage_volume_30d=usage_volume_30d,
    )
    return NovaScoreCalculator.calculate(input_data)


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    # Örnek hesaplama
    example_input = NovaScoreInput(
        user_id="user_123",
        streak_days=15,              # 15 gün aktif
        weekly_completed_tasks=20,   # Haftada 20 görev
        siyah_score_avg=75.0,        # %75 kalite
        risk_score=1.0,              # Düşük risk
        valid_referrals=5,           # 5 aktif referral
        dao_votes=3,                 # 3 DAO katkısı
        ncr_staked=1000.0,           # 1000 NCR stake
        usage_volume_30d=500.0,      # 500 NCR harcama
    )
    
    result = NovaScoreCalculator.calculate(example_input)
    
    print(f"NovaScore: {result.value}")
    print(f"Level: {result.level_name}")
    print(f"Breakdown:")
    print(f"  Activity: {result.breakdown.activity}/25")
    print(f"  Quality: {result.breakdown.quality}/25")
    print(f"  Ethics: {result.breakdown.ethics}/25")
    print(f"  Contribution: {result.breakdown.contribution}/15")
    print(f"  Economic: {result.breakdown.economic}/10")
    print(f"Task Multiplier: {result.task_multiplier}x")
    print(f"Can Validate: {result.can_validate}")

