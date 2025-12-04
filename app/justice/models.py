# app/justice/models.py

from datetime import datetime

from typing import Optional

from sqlmodel import SQLModel, Field, Column, JSON

from sqlalchemy.dialects.postgresql import UUID

import uuid





class ViolationLog(SQLModel, table=True):

    __tablename__ = "justice_violations"



    id: uuid.UUID = Field(

        default_factory=uuid.uuid4,

        sa_column=Column(UUID(as_uuid=True), primary_key=True, index=True),

    )



    user_id: str = Field(index=True)



    category: str = Field(

        index=True

    )  # "EKO" | "COM" | "SYS" | "TRUST"

    code: str = Field(index=True, max_length=64)  # "EKO_NO_SHOW", "COM_TOXIC", vs.

    severity: int = Field(default=1)  # 1–5



    cp_delta: int = Field(

        default=0, description="Bu violation'ın CP'ye katkısı (pozitif)"

    )



    source: Optional[str] = Field(

        default=None,

        description="Olayı raporlayan modül: 'nova-core', 'moderation-bot', vb.",

    )

    context: Optional[dict] = Field(

        default=None,

        sa_column=Column(JSON),

    )



    created_at: datetime = Field(default_factory=datetime.utcnow)





class UserCpState(SQLModel, table=True):

    __tablename__ = "justice_cp_state"



    user_id: str = Field(primary_key=True)

    cp_value: int = Field(default=0, index=True)

    regime: str = Field(default="NORMAL", index=True)  # NORMAL | SOFT_FLAG | PROBATION | RESTRICTED | LOCKDOWN

    last_updated_at: datetime = Field(default_factory=datetime.utcnow)


class TaskAppeal(SQLModel, table=True):
    """
    Task submission appeal model.
    
    Kullanıcılar reddedilen görevler için itiraz edebilir.
    Appeal fee (5 NCR) ödenir ve görev Ethics Appeal Queue'ya alınır.
    """
    __tablename__ = "justice_task_appeals"
    
    id: int | None = Field(default=None, primary_key=True)
    submission_id: int = Field(index=True, description="Task submission ID")
    user_id: str = Field(index=True, description="User ID who submitted the appeal")
    
    reason: str = Field(max_length=500, description="Appeal reason")
    status: str = Field(default="pending", index=True)  # "pending", "approved", "rejected"
    
    appeal_fee_paid: bool = Field(default=False, description="Whether appeal fee (5 NCR) was paid")
    appeal_fee_tx_id: Optional[int] = Field(default=None, description="Wallet transaction ID for appeal fee")
    
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[int] = Field(default=None, foreign_key="users.id", description="Admin/DAO delegate who reviewed")
    review_notes: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)


class JusticeSanctionLog(SQLModel, table=True):
    """
    Sanction (ceza) kaydı - Anayasa v1.0.
    
    Her ceza kararı burada loglanır.
    P3 Prensibi: Şeffaflık - RuleID + Sebep + Süre görülür.
    """
    __tablename__ = "justice_sanctions"
    
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(UUID(as_uuid=True), primary_key=True, index=True),
    )
    
    user_id: str = Field(index=True)
    
    # Kural bilgisi (R01-R06)
    rule_id: str = Field(index=True, max_length=10)  # "R01", "R02", etc.
    rule_name: str = Field(max_length=100)
    reason: str = Field(max_length=500)
    
    # Ceza detayları
    sanction_types: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="Applied sanction types, e.g. ['W1','E1','C1']"
    )
    cooldown_hours: int = Field(default=0)
    cooldown_until: Optional[datetime] = None
    reward_multiplier: float = Field(default=1.0, ge=0.0, le=1.0)
    daily_task_limit: Optional[int] = None
    daily_ncr_limit: Optional[float] = None
    
    # Risk impact
    risk_delta: float = Field(default=0.0)
    requires_human: bool = Field(default=False)
    
    # Context
    nova_score_at_time: Optional[float] = None
    risk_score_at_time: Optional[float] = None
    mercy_factor: Optional[float] = None
    
    # Recovery
    recovery_hint: Optional[str] = None
    recovered_at: Optional[datetime] = None
    recovered_reason: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    # Status
    is_active: bool = Field(default=True, index=True)  # P4: Ceza sonlandırıldığında False

