"""
NovaCore - NovaCredit Models
Davranış Skoru & Vatandaşlık Ekonomisi
"""
from datetime import datetime
from enum import Enum

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class CreditTier(str, Enum):
    """
    Vatandaşlık tier'ları - NovaCredit'e göre belirlenir.
    
    GHOST   (0-199)    → Şüpheli, kısıtlı erişim
    GREY    (200-399)  → Yeni veya düşük aktivite
    SOLID   (400-699)  → Normal vatandaş
    ELITE   (700-899)  → Güvenilir, VIP erişim
    LEGEND  (900-1000) → Top tier, tam ayrıcalık
    """
    GHOST = "GHOST"
    GREY = "GREY"
    SOLID = "SOLID"
    ELITE = "ELITE"
    LEGEND = "LEGEND"


# Tier thresholds
TIER_THRESHOLDS = {
    CreditTier.GHOST: (0, 199),
    CreditTier.GREY: (200, 399),
    CreditTier.SOLID: (400, 699),
    CreditTier.ELITE: (700, 899),
    CreditTier.LEGEND: (900, 1000),
}


def calculate_tier(nova_credit: int) -> CreditTier:
    """Calculate tier from NovaCredit score."""
    for tier, (min_val, max_val) in TIER_THRESHOLDS.items():
        if min_val <= nova_credit <= max_val:
            return tier
    return CreditTier.GHOST


class CitizenScore(SQLModel, table=True):
    """
    Vatandaş davranış skoru.
    
    Her user'ın tek bir CitizenScore kaydı var.
    NovaCredit 0-1000 arası, başlangıç 500.
    """
    __tablename__ = "citizen_scores"

    # Primary key = user_id (1:1 ilişki)
    user_id: int = Field(foreign_key="users.id", primary_key=True, index=True)

    # Core NovaCredit score (0-1000)
    nova_credit: int = Field(default=500, ge=0, le=1000)

    # Calculated tier
    tier: CreditTier = Field(default=CreditTier.SOLID)

    # Risk score (0.0 - 1.0) - yüksek = riskli
    risk_score: float = Field(default=0.0, ge=0.0, le=1.0)

    # Reputation score (0.0 - 1.0) - yüksek = itibar
    reputation_score: float = Field(default=0.5, ge=0.0, le=1.0)

    # Activity metrics
    total_positive_events: int = Field(default=0)
    total_negative_events: int = Field(default=0)
    total_events: int = Field(default=0)

    # Streak tracking
    positive_streak: int = Field(default=0)  # Ardışık pozitif event
    negative_streak: int = Field(default=0)  # Ardışık negatif event

    # Volatility - skor ne kadar sallanıyor
    volatility: float = Field(default=0.0, ge=0.0, le=1.0)

    # Last activity
    last_event_at: datetime | None = Field(default=None)
    last_positive_at: datetime | None = Field(default=None)
    last_negative_at: datetime | None = Field(default=None)

    # Metadata (additional context)
    # Note: Python field is 'meta' to avoid SQLAlchemy reserved keyword conflict
    # DB column remains 'metadata' for backward compatibility
    meta: dict = Field(
        default_factory=dict,
        sa_column=Column("metadata", JSONB, default={}),
    )

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "nova_credit": 650,
                "tier": "SOLID",
                "risk_score": 0.15,
                "reputation_score": 0.72,
            }
        }


class ScoreChange(SQLModel, table=True):
    """
    NovaCredit değişim logu - immutable.
    
    Her davranış eventi bir ScoreChange kaydı oluşturur.
    Audit trail + analytics için kullanılır.
    """
    __tablename__ = "score_changes"

    id: int | None = Field(default=None, primary_key=True)

    # Citizen reference
    user_id: int = Field(foreign_key="users.id", index=True)

    # Event reference (events tablosundan)
    event_id: str | None = Field(default=None, index=True, max_length=100)
    event_type: str = Field(max_length=50, index=True)

    # Score change
    delta: int  # Pozitif veya negatif değişim
    old_score: int  # Önceki skor
    new_score: int  # Yeni skor

    # Category & reason
    category: str = Field(max_length=50, index=True)  # ECONOMIC, SOCIAL_POSITIVE, etc.
    reason: str = Field(max_length=255)

    # Source tracking
    source_app: str = Field(max_length=50, index=True)  # flirt, onlyvips, poker, aurora

    # Weight applied
    weight_applied: float = Field(default=1.0)
    base_delta: int = Field(default=0)  # Ağırlık öncesi delta

    # Context
    context: dict = Field(default_factory=dict, sa_column=Column(JSONB, default={}))

    # Timestamp
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "event_type": "TIP_SENT",
                "delta": 5,
                "old_score": 500,
                "new_score": 505,
                "category": "ECONOMIC",
                "reason": "FlirtMarket tip sent",
            }
        }


class RiskFlag(SQLModel, table=True):
    """
    Risk bayrakları - şüpheli davranış takibi.
    
    Fraud, abuse, manipulation tespiti için kullanılır.
    """
    __tablename__ = "risk_flags"

    id: int | None = Field(default=None, primary_key=True)

    user_id: int = Field(foreign_key="users.id", index=True)

    # Flag details
    flag_type: str = Field(max_length=50, index=True)  # FRAUD, ABUSE, MANIPULATION, SUSPICIOUS
    severity: str = Field(max_length=20)  # LOW, MEDIUM, HIGH, CRITICAL
    description: str = Field(max_length=500)

    # Related event
    event_id: str | None = Field(default=None, max_length=100)
    source_app: str = Field(max_length=50)

    # Status
    is_active: bool = Field(default=True)
    resolved_at: datetime | None = Field(default=None)
    resolved_by: int | None = Field(default=None)  # Admin user_id
    resolution_note: str | None = Field(default=None, max_length=500)

    # Context
    context: dict = Field(default_factory=dict, sa_column=Column(JSONB, default={}))

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 42,
                "flag_type": "SUSPICIOUS",
                "severity": "MEDIUM",
                "description": "Unusual transaction pattern detected",
            }
        }

