# app/justice/nasipcourt_models.py
# NasipCourt DAO v1.0 - Justice Stack Veri Modelleri

from datetime import datetime
from enum import Enum
from typing import Optional, List
import uuid

from sqlalchemy import Column, Index, Integer
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlmodel import Field, SQLModel


class JusticeEventType(str, Enum):
    """Justice Event Tipleri - AbuseEventType'dan genişletilmiştir."""
    SPAM = "spam"
    TOXIC = "toxic"
    EXPLOIT = "exploit"
    FRAUD = "fraud"
    NCR_RESET = "ncr_reset"
    KEY_SUSPEND = "key_suspend"
    COMMUNITY_ATTACK = "community_attack"
    LOW_QUALITY_BURST = "low_quality_burst"
    DUPLICATE_PROOF = "duplicate_proof"
    TOO_FAST_COMPLETION = "too_fast_completion"
    AUTO_REJECT = "auto_reject"
    APPEAL_REJECTED = "appeal_rejected"
    MANUAL_FLAG = "manual_flag"


class RiskEvent(SQLModel, table=True):
    """
    3.1. RiskEvent: Bir davranışı veya ihlali kaydeder.
    
    NovaCore'un AI scoring'i ve Validator çoğunluk skorunu tutar.
    """
    __tablename__ = "justice_risk_events"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    event_uuid: str = Field(
        default_factory=lambda: uuid.uuid4().hex,
        index=True,
        unique=True,
        max_length=64
    )
    user_id: int = Field(index=True, foreign_key="users.id")
    
    # AI Scoring (NovaCore tarafından üretilir)
    score_ai: float = Field(
        ge=0.0,
        le=100.0,
        description="NovaCore'un Ürettiği AI Risk Skoru (0-100)"
    )
    
    # Human Scoring (Validator çoğunluk skoru)
    score_human: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=100.0,
        description="Validator Çoğunluk Skoru"
    )
    
    event_type: JusticeEventType = Field(
        index=True,
        description="İhlal tipi"
    )
    
    status: str = Field(
        default="pending",
        index=True,
        description="pending, hitl, appealed, resolved"
    )
    
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    meta: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSONB),
        description="Ek metadata (submission_id, quest_id, proof_ref, etc.)"
    )
    
    # Source tracking
    source: Optional[str] = Field(
        default=None,
        description="Olayı raporlayan modül: 'nasipquest', 'abuse_guard', 'moderator', etc."
    )
    
    __table_args__ = (
        Index('ix_risk_events_user_status', 'user_id', 'status'),
        Index('ix_risk_events_score_ai', 'score_ai'),
        Index('ix_risk_events_timestamp', 'timestamp'),
    )


class JusticeCase(SQLModel, table=True):
    """
    3.2. Case (Yargı Dosyası): Karar verme sürecini ve DAO oylamasını tutar.
    
    HITL süreci: 5 Validator, %60 çoğunluk kararı.
    """
    __tablename__ = "justice_cases"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: int = Field(foreign_key="justice_risk_events.id", index=True, unique=True)
    
    # HITL / DAO Süreci
    validators: List[int] = Field(
        default_factory=list,
        sa_column=Column(ARRAY(Integer)),
        description="Görevli validator'ların ID'leri (max 5)"
    )
    
    validator_votes: dict = Field(
        default_factory=dict,
        sa_column=Column(JSONB),
        description="Validator oyları: {validator_id: 'APPROVE' | 'REJECT'}"
    )
    
    decision: Optional[str] = Field(
        default=None,
        index=True,
        description="approved / rejected / suspended (çoğunluk kararı)"
    )
    
    consensus_reached: bool = Field(
        default=False,
        description="%60 çoğunluk sağlandı mı?"
    )
    
    consensus_at: Optional[datetime] = None
    
    # Appeal Süreci
    appeal_allowed: bool = Field(default=True)
    appeal_fee_paid: bool = Field(default=False)
    appeal_id: Optional[int] = Field(default=None, foreign_key="justice_task_appeals.id")
    
    # Resolution
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[int] = Field(default=None, foreign_key="users.id")
    
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    __table_args__ = (
        Index('ix_justice_cases_status', 'decision'),
        Index('ix_justice_cases_consensus', 'consensus_reached'),
    )


class JusticePenalty(SQLModel, table=True):
    """
    3.3. Penalty (Ceza Kaydı): Uygulanan nihai cezayı loglar.
    
    Ceza tipleri:
    - NCR_RESET: NCR bakiyesi sıfırlanır
    - NASIP_BURN: NASIP token yakılır
    - KEY_SUSPEND: Key (NFT) askıya alınır
    - RISK_SCORE_PENALTY: RiskScore'a ceza eklenir
    """
    __tablename__ = "justice_penalties"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, foreign_key="users.id")
    case_id: int = Field(foreign_key="justice_cases.id", index=True)
    event_id: int = Field(foreign_key="justice_risk_events.id", index=True)
    
    penalty_type: str = Field(
        index=True,
        description="NCR_RESET / NASIP_BURN / KEY_SUSPEND / RISK_SCORE_PENALTY"
    )
    
    amount: Optional[float] = Field(
        default=None,
        description="NCR veya NASIP miktarı (burn/reset için)"
    )
    
    duration_days: Optional[int] = Field(
        default=None,
        description="Key suspend süresi (gün)"
    )
    
    risk_score_delta: Optional[float] = Field(
        default=None,
        description="RiskScore'a eklenen ceza (+2.0 gibi)"
    )
    
    reason: str = Field(description="Ceza gerekçesi")
    
    applied_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    applied_by: Optional[int] = Field(default=None, foreign_key="users.id")
    
    # Execution metadata
    execution_metadata: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSONB),
        description="Ceza uygulama detayları (wallet_tx_id, nft_update_hash, etc.)"
    )
    
    __table_args__ = (
        Index('ix_justice_penalties_user', 'user_id'),
        Index('ix_justice_penalties_type', 'penalty_type'),
    )

