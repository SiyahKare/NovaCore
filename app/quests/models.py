"""
Quest Models - Production-Ready Quest Engine
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Enum as SQLEnum, Index
from sqlmodel import Field, SQLModel

from .enums import QuestType, QuestStatus


class UserQuest(SQLModel, table=True):
    """
    Kullanıcıya atanan ve AbuseGuard + HouseEdge ile ödüllendirilen görev kaydı.
    
    QuestFactory'nin runtime çıktısının kalıcı DB karşılığı.
    """
    __tablename__ = "user_quests"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Kimlik
    user_id: int = Field(index=True, foreign_key="users.id", description="NovaCore internal user_id")
    quest_uuid: str = Field(index=True, max_length=100, description="QuestFactory runtime UUID")
    quest_type: QuestType = Field(
        sa_column=Column(SQLEnum(QuestType, name="quest_type_enum")),
        description="Görevin tipik kategorisi (meme, quiz, reflection, vs.)",
    )
    key: str = Field(index=True, max_length=255, description="Logical key (ex: 'EMEK_HIRSIZLIGI_PROOF')")
    
    # Copy
    title: str = Field(max_length=255)
    description: str = Field(default="")

    # Ekonomi (Base + Final)
    base_reward_ncr: float = Field(description="QuestFactory default NCR reward (ör: 10.0)")
    base_reward_xp: int = Field(description="QuestFactory default XP reward (ör: 25)")

    # Final (House Edge + AbuseGuard sonrası)
    final_reward_ncr: Optional[float] = Field(default=None)
    final_reward_xp: Optional[int] = Field(default=None)
    final_score: Optional[float] = Field(
        default=None, description="AI scoring / quality score (0-100)"
    )

    # Durum
    status: QuestStatus = Field(
        default=QuestStatus.ASSIGNED,
        sa_column=Column(SQLEnum(QuestStatus, name="quest_status_enum"), index=True),
    )

    # Süreler
    assigned_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    expires_at: datetime = Field(index=True)
    submitted_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    # Proof meta (raw payload başka tabloda da olabilir; MVP için burada minimal)
    proof_type: Optional[str] = Field(
        default=None,
        max_length=50,
        description="text | photo | link | mixed (MVP için string; sonra Enum'a alınır)"
    )
    proof_payload_ref: Optional[str] = Field(
        default=None,
        max_length=500,
        description="S3/Telegram file id / JSON key vs. ağır veriye pointer"
    )

    # Audit / AbuseGuard entegrasyonu
    abuse_risk_snapshot: Optional[float] = Field(
        default=None, description="Görev tamamlama anındaki RiskScore"
    )
    house_edge_snapshot: Optional[float] = Field(
        default=None,
        description="House Edge multiplier / efektif çarpanı loglamak için (örn: 0.8)",
    )

    __table_args__ = (
        Index('ix_user_quests_user_status', 'user_id', 'status'),
        Index('ix_user_quests_user_expires', 'user_id', 'expires_at'),
    )

