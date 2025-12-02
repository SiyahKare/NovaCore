"""
NovaCore Agency Models - NovaAgency, Performers
"""
from datetime import datetime
from enum import Enum

from sqlalchemy import Column
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

