"""
Telegram Gateway - Task & Submission Models
Görev sistemi ve abuse koruması için veri modelleri
"""
from datetime import datetime
from typing import Optional
from enum import Enum

from sqlalchemy import Column, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class TaskDifficulty(str, Enum):
    """Görev zorluk seviyesi."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class TaskType(str, Enum):
    """Görev tipi."""
    ONCHAIN = "onchain"  # Blockchain işlemi
    SOCIAL = "social"  # Sosyal medya paylaşımı
    MICROTASK = "microtask"  # Küçük görev
    QUIZ = "quiz"  # Quiz/soru
    STREAK = "streak"  # Streak görevi
    REFERRAL = "referral"  # Referral görevi


class ProofType(str, Enum):
    """Kanıt tipi."""
    NONE = "none"  # Kanıt gerekmez
    SCREENSHOT = "screenshot"  # Ekran görüntüsü
    LINK = "link"  # Link paylaşımı
    TEXT = "text"  # Metin açıklama
    QUIZ_ANSWER = "quiz_answer"  # Quiz cevabı
    ONCHAIN_TX = "onchain_tx"  # Blockchain transaction hash


class TaskStatus(str, Enum):
    """Görev durumu."""
    DRAFT = "draft"  # Taslak
    ACTIVE = "active"  # Aktif
    PAUSED = "paused"  # Duraklatılmış
    ARCHIVED = "archived"  # Arşivlenmiş


class SubmissionStatus(str, Enum):
    """Görev submit durumu."""
    PENDING = "pending"  # Beklemede
    APPROVED = "approved"  # Onaylandı
    REJECTED = "rejected"  # Reddedildi
    REWARDED = "rewarded"  # Ödül verildi


class Task(SQLModel, table=True):
    """
    Görev tanımı.
    
    Her görev bir kez tanımlanır, kullanıcılara atanır.
    """
    __tablename__ = "telegram_tasks"

    id: str = Field(primary_key=True, max_length=100)  # "daily_login", "refer_friend"
    title: str = Field(max_length=255)
    description: str = Field(default="")
    
    # Görev özellikleri
    category: str = Field(index=True, max_length=50)  # "daily", "weekly", "special"
    difficulty: TaskDifficulty = Field(default=TaskDifficulty.EASY)
    task_type: TaskType = Field(default=TaskType.MICROTASK)
    proof_type: ProofType = Field(default=ProofType.NONE)
    
    # Ödüller
    reward_xp: int = Field(default=0)
    reward_ncr: str = Field(default="0")
    
    # Zamanlama
    cooldown_seconds: int = Field(default=0, description="Tekrar yapılabilme süresi (saniye)")
    expires_at: Optional[datetime] = Field(default=None, index=True)
    streak_required: int = Field(default=0, description="Kaç gün streak gerekiyor")
    
    # Durum
    status: TaskStatus = Field(default=TaskStatus.ACTIVE, index=True)
    max_completions_per_user: int = Field(default=1, description="Kullanıcı başına max tamamlama sayısı")
    
    # Metadata
    task_metadata: dict = Field(
        default_factory=dict,
        sa_column=Column("metadata", JSONB, default={})
    )
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TaskAssignment(SQLModel, table=True):
    """
    Kullanıcıya atanan görev.
    
    Her kullanıcı için hangi görevlerin aktif olduğunu tutar.
    """
    __tablename__ = "telegram_task_assignments"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    task_id: str = Field(foreign_key="telegram_tasks.id", index=True)
    
    # Assignment metadata
    assigned_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(default=None, index=True)
    is_active: bool = Field(default=True, index=True)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('user_id', 'task_id', name='uq_user_task_assignment'),
        Index('ix_task_assignments_user_active', 'user_id', 'is_active'),
    )


class TaskSubmission(SQLModel, table=True):
    """
    Görev tamamlama kaydı.
    
    Idempotency için: (user_id, task_id) unique constraint.
    """
    __tablename__ = "telegram_task_submissions"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    task_id: str = Field(foreign_key="telegram_tasks.id", index=True)
    
    # Submission data
    proof: Optional[str] = Field(default=None, description="Screenshot URL, link, text, etc.")
    proof_metadata: dict = Field(default_factory=dict, sa_column=Column(JSONB, default={}))
    
    # Status
    status: SubmissionStatus = Field(default=SubmissionStatus.PENDING, index=True)
    reviewed_by: Optional[int] = Field(default=None, foreign_key="users.id")
    reviewed_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    
    # Idempotency
    external_id: Optional[str] = Field(default=None, unique=True, index=True, description="External submission ID for idempotency")
    
    # Timestamps
    submitted_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('user_id', 'task_id', name='uq_user_task_submission'),
        Index('ix_task_submissions_status', 'status', 'submitted_at'),
    )


class TaskReward(SQLModel, table=True):
    """
    Görev ödülü kaydı.
    
    Her ödül verildiğinde buraya log düşer (audit trail).
    """
    __tablename__ = "telegram_task_rewards"

    id: int | None = Field(default=None, primary_key=True)
    submission_id: int = Field(foreign_key="telegram_task_submissions.id", index=True, unique=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    task_id: str = Field(foreign_key="telegram_tasks.id", index=True)
    
    # Rewards
    xp_amount: int = Field(default=0)
    ncr_amount: str = Field(default="0")
    
    # Transaction tracking
    wallet_tx_id: Optional[int] = Field(default=None, foreign_key="ledger_entries.id")
    xp_event_id: Optional[int] = Field(default=None, foreign_key="xp_events.id")
    
    # Timestamps
    rewarded_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ReferralReward(SQLModel, table=True):
    """
    Referral ödülü kaydı.
    
    Self-referral koruması için: (referrer_user_id, referred_user_id) unique.
    """
    __tablename__ = "telegram_referral_rewards"

    id: int | None = Field(default=None, primary_key=True)
    referrer_user_id: int = Field(foreign_key="users.id", index=True)
    referred_user_id: int = Field(foreign_key="users.id", index=True)
    referral_code: str = Field(index=True, max_length=50)
    
    # Rewards
    xp_amount: int = Field(default=0)
    ncr_amount: str = Field(default="0")
    
    # Transaction tracking
    wallet_tx_id: Optional[int] = Field(default=None, foreign_key="ledger_entries.id")
    xp_event_id: Optional[int] = Field(default=None, foreign_key="xp_events.id")
    
    # Metadata
    reward_metadata: dict = Field(
        default_factory=dict,
        sa_column=Column("metadata", JSONB, default={})
    )
    
    # Timestamps
    rewarded_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('referrer_user_id', 'referred_user_id', name='uq_referral_pair'),
        Index('ix_referral_rewards_code', 'referral_code', 'rewarded_at'),
    )

