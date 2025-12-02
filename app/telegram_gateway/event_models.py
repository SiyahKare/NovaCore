"""
Telegram Gateway - Event & Ritual Models
Event katmanı: Nasip Friday, Quest War, Ritüeller
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from enum import Enum

from sqlalchemy import Column, UniqueConstraint, Index, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class EventType(str, Enum):
    """Event tipi."""
    NASIP_FRIDAY = "NASIP_FRIDAY"  # Haftalık ritüel
    QUEST_WAR = "QUEST_WAR"  # Yarışmalı event
    SEASONAL = "SEASONAL"  # Mevsimsel event
    RITUAL = "RITUAL"  # Özel ritüel
    ONBOARDING = "ONBOARDING"  # Onboarding event


class EventStatus(str, Enum):
    """Event durumu."""
    DRAFT = "DRAFT"  # Taslak
    ACTIVE = "ACTIVE"  # Aktif
    FINISHED = "FINISHED"  # Bitti
    CANCELLED = "CANCELLED"  # İptal edildi


class Event(SQLModel, table=True):
    """
    Event tanımı.
    
    Zaman kutusu + tema + kural seti.
    Task'lerin paketlenmiş, süreli ve buff'lı hali.
    """
    __tablename__ = "telegram_events"

    id: int | None = Field(default=None, primary_key=True)
    code: str = Field(index=True, unique=True, max_length=100)  # "nasip_friday_2025_12_05"
    name: str = Field(max_length=255)
    description: str | None = Field(default=None)
    
    # Event özellikleri
    event_type: EventType = Field(index=True)
    status: EventStatus = Field(default=EventStatus.DRAFT, index=True)
    
    # Zamanlama
    starts_at: datetime = Field(index=True)
    ends_at: datetime = Field(index=True)
    
    # Reward multipliers (global buff)
    reward_multiplier_xp: float = Field(default=1.0)
    reward_multiplier_ncr: float = Field(default=1.0)
    
    # Katılım kuralları
    max_participants: int | None = Field(default=None)
    min_level_required: int = Field(default=0)
    
    # Metadata
    event_metadata: dict = Field(
        default_factory=dict,
        sa_column=Column("metadata", JSONB, default={})
    )
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class EventTask(SQLModel, table=True):
    """
    Event ↔ Task çoktan çoğa bağlantı.
    
    Bir event birden fazla task içerebilir.
    Bir task birden fazla event'e bağlı olabilir.
    """
    __tablename__ = "telegram_event_tasks"

    id: int | None = Field(default=None, primary_key=True)
    event_id: int = Field(foreign_key="telegram_events.id", index=True)
    task_id: str = Field(foreign_key="telegram_tasks.id", index=True)
    
    # Event özelinde ekstra buff / override
    reward_multiplier_xp: float | None = Field(default=None)
    reward_multiplier_ncr: float | None = Field(default=None)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('event_id', 'task_id', name='uq_event_task'),
        Index('ix_event_tasks_event', 'event_id', 'task_id'),
    )


class EventParticipation(SQLModel, table=True):
    """
    Kullanıcının event katılımı ve skoru.
    
    Kimin hangi event'e girdiğini, ne zaman girdiğini, skorunu tutar.
    """
    __tablename__ = "telegram_event_participations"

    id: int | None = Field(default=None, primary_key=True)
    event_id: int = Field(foreign_key="telegram_events.id", index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    
    # Katılım
    joined_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    # Skor
    total_xp_earned: int = Field(default=0, index=True)
    total_ncr_earned: Decimal = Field(
        default=Decimal("0"),
        sa_column=Column(Numeric(18, 8), default=Decimal("0"))
    )
    tasks_completed: int = Field(default=0)
    
    # Sıralama (event bitince set edilir)
    rank: int | None = Field(default=None, index=True)
    is_winner: bool = Field(default=False)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('event_id', 'user_id', name='uq_event_participation'),
        Index('ix_event_participations_score', 'event_id', 'total_xp_earned', 'tasks_completed'),
    )


class EventReward(SQLModel, table=True):
    """
    Event sonrası toplu ödül / bonus log'u.
    
    Event bitince top 10'a, participation bonus'a vs. verilen ödüller.
    """
    __tablename__ = "telegram_event_rewards"

    id: int | None = Field(default=None, primary_key=True)
    event_id: int = Field(foreign_key="telegram_events.id", index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    
    # Bonus ödüller
    bonus_xp: int = Field(default=0)
    bonus_ncr: Decimal = Field(
        default=Decimal("0"),
        sa_column=Column(Numeric(18, 8), default=Decimal("0"))
    )
    reason: str | None = Field(default=None, max_length=100)  # "TOP_1", "TOP_10", "PARTICIPATION"
    
    # Transaction tracking
    wallet_tx_id: Optional[int] = Field(default=None, foreign_key="ledger_entries.id")
    xp_event_id: Optional[int] = Field(default=None, foreign_key="xp_events.id")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    __table_args__ = (
        UniqueConstraint('event_id', 'user_id', name='uq_event_reward'),
        Index('ix_event_rewards_reason', 'event_id', 'reason'),
    )

