# novacore/app/nova_score/schemas.py
"""
NovaScore v1.0 – Schemas

5 Bileşenli Vatandaşlık Skoru:
- ActivityScore (0-25): Düzen ve süreklilik
- QualityScore (0-25): Üretilen işin kalitesi
- EthicsScore (0-25): RiskScore'un tersinden
- ContributionScore (0-15): Tribe'e katkı
- EconomicScore (0-10): NCR stake / kullanım
"""
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum

from .models import NovaScoreBreakdown


# =============================================================================
# LEGACY SCHEMAS (Backward Compatibility)
# =============================================================================

class ComponentScore(BaseModel):
    """Legacy component score for backward compatibility."""
    value: float = Field(..., ge=0, le=100)
    confidence: float = Field(..., ge=0.0, le=1.0)


class NovaScoreComponents(BaseModel):
    """Legacy components for backward compatibility."""
    ECO: ComponentScore
    REL: ComponentScore
    SOC: ComponentScore
    ID: ComponentScore
    CON: ComponentScore


class NovaScoreResponse(BaseModel):
    """Legacy response for backward compatibility."""
    user_id: str
    nova_score: int = Field(..., ge=0, le=1000)
    components: NovaScoreComponents
    cp: int = Field(..., description="Ceza puanı (Adalet modülünden)")
    confidence_overall: float = Field(
        ..., ge=0.0, le=1.0, description="Feature coverage'a göre genel güven"
    )
    explanation: Optional[str] = Field(
        None,
        description="Kısa açıklama: düşük veri / recall / kısıtlanmış policy vs.",
    )


# =============================================================================
# NOVA SCORE v1.0 SCHEMAS
# =============================================================================

from ..core.citizenship import CitizenLevel as CitizenLevelEnum


# NovaScoreBreakdownV1 artık NovaScoreBreakdown'ı alias olarak kullanıyor
NovaScoreBreakdownV1 = NovaScoreBreakdown  # Backward compatibility


class NovaScoreResponseV1(BaseModel):
    """
    NovaScore v1.0 API response.
    
    Yeni 5 bileşenli sistem ile.
    """
    user_id: str
    nova_score: float = Field(ge=0.0, le=100.0, description="NovaScore (0-100)")
    level: CitizenLevelEnum = Field(description="Vatandaşlık seviyesi")
    level_name: str = Field(description="Seviye adı (Ghost, Resident, etc.)")
    level_description: str = Field(description="Seviye açıklaması")
    breakdown: NovaScoreBreakdownV1 = Field(description="Skor bileşenleri")
    
    # Seviye hakları
    task_multiplier: float = Field(description="Görev ödül çarpanı")
    withdraw_limit_daily: float = Field(description="Günlük withdraw limiti (NCR)")
    can_validate: bool = Field(description="DAO validator olabilir mi")
    can_refer: bool = Field(description="Referral yapabilir mi")
    
    # Risk entegrasyonu
    risk_score: Optional[float] = Field(None, ge=0.0, le=10.0, description="AbuseGuard RiskScore")
    
    class Config:
        use_enum_values = True


# =============================================================================
# INPUT SCHEMAS (API Request)
# =============================================================================

class NovaScoreInputData(BaseModel):
    """
    NovaScore hesaplama için gerekli veriler (API input).
    
    Bu veriler normalde backend'den otomatik toplanır.
    Admin/test için manuel input.
    """
    # Activity metricleri
    streak_days: int = Field(default=0, ge=0, le=365, description="Üst üste aktif gün sayısı")
    weekly_completed_tasks: int = Field(default=0, ge=0, description="Son 7 günde tamamlanan görev")
    
    # Quality metricleri
    siyah_score_avg: float = Field(default=50.0, ge=0.0, le=100.0, description="Son 20 görev kalite ortalaması")
    
    # Ethics metricleri (otomatik çekilir)
    risk_score: float = Field(default=0.0, ge=0.0, le=10.0, description="AbuseGuard RiskScore")
    
    # Contribution metricleri
    valid_referrals: int = Field(default=0, ge=0, description="Aktif referral sayısı")
    dao_votes: int = Field(default=0, ge=0, description="Son 30 gün DAO/validator katkısı")
    
    # Economic metricleri
    ncr_staked: float = Field(default=0.0, ge=0.0, description="Aktif stake (NCR)")
    usage_volume_30d: float = Field(default=0.0, ge=0.0, description="30 günde harcanan NCR")
