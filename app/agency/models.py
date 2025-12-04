"""
NovaCore Agency Models - NovaAgency, Performers
"""
from datetime import datetime
from enum import Enum

from typing import Optional

from sqlalchemy import Column, Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class Agency(SQLModel, table=True):
    """
    Agency model - Betül'ün NovaAgency'si gibi.
    
    Bir Agency birden fazla Performer yönetebilir.
    """

    __tablename__ = "agencies"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=255, index=True)
    slug: str = Field(max_length=100, unique=True, index=True)
    description: str | None = Field(default=None, max_length=1000)

    # Owner user
    owner_user_id: int = Field(foreign_key="users.id", index=True)

    # Status
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)

    # Revenue sharing defaults
    default_performer_share: int = Field(default=50)  # %
    default_agency_share: int = Field(default=30)  # %
    default_treasury_share: int = Field(default=20)  # %

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


class OperatorRole(str, Enum):
    """Operator roles within an agency."""

    PATRONICE = "PATRONICE"  # Betül - full control
    OPERATOR = "OPERATOR"  # Standard operator
    MANAGER = "MANAGER"  # Can manage performers
    VIEWER = "VIEWER"  # Read-only


class AgencyOperator(SQLModel, table=True):
    """
    Agency operator - people who work for the agency.
    
    Patronice (Betül) vs regular operators.
    """

    __tablename__ = "agency_operators"

    id: int | None = Field(default=None, primary_key=True)
    agency_id: int = Field(foreign_key="agencies.id", index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    role: OperatorRole = Field(default=OperatorRole.OPERATOR)
    is_active: bool = Field(default=True)

    # Custom revenue share override (optional)
    custom_share: int | None = Field(default=None)  # Override default

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PerformerType(str, Enum):
    """Performer types."""

    HUMAN = "HUMAN"  # Real person
    AI = "AI"  # Pure AI (Aurora)
    HYBRID = "HYBRID"  # Human assisted by AI


class Performer(SQLModel, table=True):
    """
    Performer model - models managed by agencies.
    
    Can be human, AI, or hybrid.
    """

    __tablename__ = "performers"

    id: int | None = Field(default=None, primary_key=True)
    agency_id: int = Field(foreign_key="agencies.id", index=True)

    # Optional link to a real user (for human performers)
    user_id: int | None = Field(default=None, foreign_key="users.id", index=True)

    # Display info
    display_name: str = Field(max_length=255)
    handle: str = Field(max_length=100, unique=True, index=True)
    bio: str | None = Field(default=None, max_length=2000)
    avatar_url: str | None = Field(default=None, max_length=500)

    # Type
    type: PerformerType = Field(default=PerformerType.HUMAN)
    is_test: bool = Field(default=False)  # Test performer

    # Revenue sharing (overrides agency defaults)
    share_performer: int = Field(default=50)  # % to performer
    share_agency: int = Field(default=30)  # % to agency
    share_treasury: int = Field(default=20)  # % to treasury

    # AI integration (for AI/HYBRID types)
    ai_profile_id: str | None = Field(default=None, max_length=100)  # Aurora profile ID

    # Status
    is_active: bool = Field(default=True)
    is_featured: bool = Field(default=False)

    # Stats (denormalized for performance)
    total_earnings: int = Field(default=0)  # Total NCR earned
    total_shows: int = Field(default=0)  # Total shows/sessions

    # Metadata (additional context)
    # Note: Python field is 'meta' to avoid SQLAlchemy reserved keyword conflict
    # DB column remains 'metadata' for backward compatibility
    tags: list[str] = Field(default_factory=list, sa_column=Column(JSONB, default=[]))
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
                "id": 1,
                "agency_id": 1,
                "display_name": "Luna",
                "handle": "luna_star",
                "type": "HUMAN",
                "share_performer": 50,
                "share_agency": 30,
                "share_treasury": 20,
            }
        }


class CreatorAssetStatus(str, Enum):
    """CreatorAsset durumu."""
    DRAFT = "DRAFT"  # oluştu ama daha review edilmedi
    CURATED = "CURATED"  # sistem tarafından "ajanslık" diye işaretlendi
    APPROVED = "APPROVED"  # human/operatör onayı
    USED_IN_CAMPAIGN = "USED_IN_CAMPAIGN"


class AssetMediaType(str, Enum):
    """Asset medya tipi."""
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    TEXT = "TEXT"
    MIXED = "MIXED"


class PipelineStage(str, Enum):
    """Agency client pipeline stage."""
    LEAD = "LEAD"
    CONTACTED = "CONTACTED"
    DEMO_DONE = "DEMO_DONE"
    NEGOTIATION = "NEGOTIATION"
    WON = "WON"
    LOST = "LOST"


class AgencyClient(SQLModel, table=True):
    """
    Ajans müşterisi (KOBİ veya marka).
    """
    __tablename__ = "agency_clients"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=255)
    contact_person: Optional[str] = Field(default=None, max_length=255)
    contact_phone: Optional[str] = Field(default=None, max_length=50)
    contact_email: Optional[str] = Field(default=None, max_length=255)

    pipeline_stage: PipelineStage = Field(
        default=PipelineStage.LEAD,
        sa_column=Column(SQLEnum(PipelineStage, name="pipeline_stage_enum")),
    )

    monthly_mrr_try: float = Field(default=0.0, description="Aktif abonelik varsa")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CreatorAsset(SQLModel, table=True):
    """
    NasipQuest görevlerinden süzülen, ajansın kullanacağı "viral potansiyelli" içerik.

    Bu varlık:
    - Bir kullanıcıya ait
    - Bir task_submission kaynağına bağlı
    - Ajans tarafında paketlere/dosyalara dönüşür
    """
    __tablename__ = "creator_assets"

    id: Optional[int] = Field(default=None, primary_key=True)

    user_id: int = Field(index=True, foreign_key="users.id", description="NasipQuest user")
    task_id: str = Field(index=True, max_length=100, description="Görevin ID'si")
    submission_id: int = Field(index=True, foreign_key="telegram_task_submissions.id", description="TaskSubmission ID'si")

    media_type: AssetMediaType = Field(
        default=AssetMediaType.IMAGE,
        sa_column=Column(SQLEnum(AssetMediaType, name="asset_media_type_enum")),
    )
    media_url: str = Field(max_length=1000, description="S3 / CDN / Telegram file URL")
    caption: Optional[str] = Field(default=None, max_length=2000, description="Aurora optimize caption")
    hook_script: Optional[str] = Field(
        default=None,
        max_length=500,
        description="İlk 3–5 saniyelik hook metni"
    )
    platform_hint: Optional[str] = Field(
        default=None,
        max_length=50,
        description="tiktok / reels / shorts / youtube / story vb."
    )

    # AI / Scoring snapshot
    ai_total_score: float = Field(index=True, description="AI total score (0-100)")
    ai_creativity_score: float = Field(default=0.0, description="AI creativity score")
    ai_aesthetic_score: float = Field(default=0.0, description="AI aesthetic score")
    ai_algo_fit_score: float = Field(default=0.0, description="AI algorithm fit score")

    siyah_score_snapshot: float = Field(default=0.0, description="O anki SiyahScore")
    risk_score_snapshot: float = Field(default=0.0, description="O anki RiskScore")

    tags: Optional[str] = Field(
        default=None,
        max_length=500,
        description="virality, meme, boss_whatsapp, hook, loop, glitch vb. comma-separated"
    )

    status: CreatorAssetStatus = Field(
        default=CreatorAssetStatus.CURATED,
        sa_column=Column(SQLEnum(CreatorAssetStatus, name="creator_asset_status_enum")),
    )

    is_featured: bool = Field(default=False, index=True)
    used_in_campaign: bool = Field(default=False, index=True)

    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # İleri seviye: client_id, campaign_id vs. eklenebilir
    agency_client_id: Optional[int] = Field(default=None, foreign_key="agency_clients.id")

    __table_args__ = (
        Index('ix_creator_assets_user_status', 'user_id', 'status'),
        Index('ix_creator_assets_ai_score', 'ai_total_score'),
        Index('ix_creator_assets_status', 'status'),
    )

