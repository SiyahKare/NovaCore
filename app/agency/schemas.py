"""
NovaCore Agency Schemas
"""
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.agency.models import OperatorRole, PerformerType


# ============ Agency Schemas ============
class AgencyCreate(BaseModel):
    """Create agency request."""

    name: str = Field(..., max_length=255)
    slug: str = Field(..., max_length=100, pattern=r"^[a-z0-9_-]+$")
    description: str | None = Field(None, max_length=1000)
    default_performer_share: int = Field(50, ge=0, le=100)
    default_agency_share: int = Field(30, ge=0, le=100)
    default_treasury_share: int = Field(20, ge=0, le=100)


class AgencyUpdate(BaseModel):
    """Update agency request."""

    name: str | None = Field(None, max_length=255)
    description: str | None = Field(None, max_length=1000)
    default_performer_share: int | None = Field(None, ge=0, le=100)
    default_agency_share: int | None = Field(None, ge=0, le=100)
    default_treasury_share: int | None = Field(None, ge=0, le=100)


class AgencyResponse(BaseModel):
    """Agency response."""

    id: int
    name: str
    slug: str
    description: str | None
    owner_user_id: int
    is_active: bool
    is_verified: bool
    default_performer_share: int
    default_agency_share: int
    default_treasury_share: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AgencyWithStats(AgencyResponse):
    """Agency with stats."""

    performer_count: int
    total_earnings: Decimal


# ============ Operator Schemas ============
class OperatorAdd(BaseModel):
    """Add operator to agency."""

    user_id: int
    role: OperatorRole = OperatorRole.OPERATOR
    custom_share: int | None = Field(None, ge=0, le=100)


class OperatorUpdate(BaseModel):
    """Update operator."""

    role: OperatorRole | None = None
    is_active: bool | None = None
    custom_share: int | None = Field(None, ge=0, le=100)


class OperatorResponse(BaseModel):
    """Operator response."""

    id: int
    agency_id: int
    user_id: int
    role: OperatorRole
    is_active: bool
    custom_share: int | None
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Performer Schemas ============
class PerformerCreate(BaseModel):
    """Create performer request."""

    display_name: str = Field(..., max_length=255)
    handle: str = Field(..., max_length=100, pattern=r"^[a-z0-9_]+$")
    bio: str | None = Field(None, max_length=2000)
    avatar_url: str | None = Field(None, max_length=500)

    type: PerformerType = PerformerType.HUMAN
    user_id: int | None = None  # Optional link to real user

    # Revenue sharing
    share_performer: int = Field(50, ge=0, le=100)
    share_agency: int = Field(30, ge=0, le=100)
    share_treasury: int = Field(20, ge=0, le=100)

    # AI
    ai_profile_id: str | None = None

    # Metadata
    tags: list[str] = Field(default_factory=list)
    is_test: bool = False


class PerformerUpdate(BaseModel):
    """Update performer request."""

    display_name: str | None = Field(None, max_length=255)
    bio: str | None = Field(None, max_length=2000)
    avatar_url: str | None = Field(None, max_length=500)

    share_performer: int | None = Field(None, ge=0, le=100)
    share_agency: int | None = Field(None, ge=0, le=100)
    share_treasury: int | None = Field(None, ge=0, le=100)

    ai_profile_id: str | None = None
    is_active: bool | None = None
    is_featured: bool | None = None
    tags: list[str] | None = None


class PerformerResponse(BaseModel):
    """Performer response."""

    id: int
    agency_id: int
    user_id: int | None
    display_name: str
    handle: str
    bio: str | None
    avatar_url: str | None
    type: PerformerType
    is_test: bool
    share_performer: int
    share_agency: int
    share_treasury: int
    ai_profile_id: str | None
    is_active: bool
    is_featured: bool
    total_earnings: int
    total_shows: int
    tags: list[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PerformerBrief(BaseModel):
    """Brief performer info for listing."""

    id: int
    display_name: str
    handle: str
    avatar_url: str | None
    type: PerformerType
    is_active: bool
    is_featured: bool

    class Config:
        from_attributes = True


# ============ Revenue Split ============
class RevenueSplit(BaseModel):
    """Revenue split calculation."""

    total_amount: Decimal
    performer_amount: Decimal
    agency_amount: Decimal
    treasury_amount: Decimal
    performer_id: int
    agency_id: int

