"""
NovaCore XP & Loyalty Schemas
"""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.xp_loyalty.models import LoyaltyTier


# ============ XP Event Schemas ============
class XpEventCreate(BaseModel):
    """Create XP event request."""

    user_id: int
    amount: int = Field(..., description="XP amount (can be negative)")
    event_type: str = Field(..., max_length=50, description="Event type identifier")
    source_app: Literal["flirt", "onlyvips", "poker", "aurora", "nasipquest", "marketplace"]

    # Optional tracking
    reference_id: str | None = None
    reference_type: str | None = None
    metadata: dict = Field(default_factory=dict)


class XpEventResponse(BaseModel):
    """XP event response."""

    id: int
    user_id: int
    amount: int
    event_type: str
    source_app: str
    xp_total_after: int | None
    level_after: int | None
    tier_after: str | None
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Loyalty Profile Schemas ============
class LoyaltyProfileResponse(BaseModel):
    """User loyalty profile response."""

    user_id: int
    xp_total: int
    level: int
    tier: LoyaltyTier
    total_events: int
    current_streak: int
    max_streak: int
    vip_priority: int
    ai_credits_bonus: float

    # Next level info
    xp_to_next_level: int
    xp_to_next_tier: int
    next_tier: LoyaltyTier | None

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LoyaltyProfileBrief(BaseModel):
    """Brief loyalty profile for Aurora routing."""

    user_id: int
    level: int
    tier: LoyaltyTier
    vip_priority: int
    ai_credits_bonus: float


# ============ Leaderboard ============
class LeaderboardEntry(BaseModel):
    """Leaderboard entry."""

    rank: int
    user_id: int
    username: str | None
    display_name: str | None
    xp_total: int
    level: int
    tier: LoyaltyTier


class LeaderboardResponse(BaseModel):
    """Leaderboard response."""

    entries: list[LeaderboardEntry]
    total_users: int
    period: str  # all_time, weekly, monthly


# ============ Stats ============
class LoyaltyStats(BaseModel):
    """Global loyalty stats."""

    total_users: int
    total_xp_distributed: int
    tier_distribution: dict[str, int]  # tier -> count
    average_level: float

