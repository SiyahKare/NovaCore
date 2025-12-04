"""
AbuseGuard - RiskScore & Abuse Event Models
NasipQuest ekonomisini koruyan risk motoru veri modelleri
"""
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Column, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class AbuseEventType(str, Enum):
    """Abuse event tipleri."""
    LOW_QUALITY_BURST = "low_quality_burst"       # Aynı gün 5+ low score
    DUPLICATE_PROOF = "duplicate_proof"           # Aynı medya/kanıt tekrar
    TOO_FAST_COMPLETION = "too_fast_completion"   # < N saniye
    AUTO_REJECT = "auto_reject"                   # AI score < threshold
    APPEAL_REJECTED = "appeal_rejected"           # İtiraz reddedildi
    MANUAL_FLAG = "manual_flag"                   # Mod/DAO flag'i
    TOXIC_CONTENT = "toxic_content"               # NSFW/toxic içerik (AI scoring flag)


class UserRiskProfile(SQLModel, table=True):
    """
    Kullanıcı risk profili.
    
    Her kullanıcının RiskScore'u burada tutulur.
    """
    __tablename__ = "abuse_user_risk_profiles"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", unique=True, index=True)
    
    # Risk score (0.0 - 10.0)
    risk_score: float = Field(default=0.0, ge=0.0, le=10.0, index=True)
    
    # Metadata
    risk_metadata: dict = Field(
        default_factory=dict,
        sa_column=Column("risk_metadata", JSONB, default={})
    )
    
    # Timestamps
    last_event_at: Optional[datetime] = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    __table_args__ = (
        Index('ix_risk_profiles_score', 'risk_score'),
        Index('ix_risk_profiles_last_event', 'last_event_at'),
    )


class AbuseEvent(SQLModel, table=True):
    """
    Abuse event kaydı.
    
    Her risk event'i buraya loglanır (audit trail).
    """
    __tablename__ = "abuse_events"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    
    # Event details
    event_type: AbuseEventType = Field(index=True)
    delta: float = Field(description="RiskScore'a eklenen değer")
    
    # Metadata
    meta: dict = Field(
        default_factory=dict,
        sa_column=Column("meta", JSONB, default={})
    )
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index('ix_abuse_events_user_type', 'user_id', 'event_type'),
        Index('ix_abuse_events_created', 'created_at'),
    )

