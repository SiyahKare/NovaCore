"""
NovaCore XP & Loyalty Models
"""
from datetime import datetime
from enum import Enum

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class LoyaltyTier(str, Enum):
    """User loyalty tiers."""

    BRONZE = "BRONZE"
    SILVER = "SILVER"
    GOLD = "GOLD"
    DIAMOND = "DIAMOND"


# Tier thresholds (XP required)
TIER_THRESHOLDS = {
    LoyaltyTier.BRONZE: 0,
    LoyaltyTier.SILVER: 1000,
    LoyaltyTier.GOLD: 5000,
    LoyaltyTier.DIAMOND: 25000,
}

# Level XP requirements (level -> XP needed)
def get_level_xp_requirement(level: int) -> int:
    """Get XP required for a level. Exponential curve."""
    # Level 1: 0 XP, Level 2: 100 XP, Level 3: 200 XP, etc.
    # Simple linear for now, can be adjusted
    return (level - 1) * 100


class XpEvent(SQLModel, table=True):
    """
    XP Event log - immutable.
    
    Her XP kazanımı/kaybı burada loglanır.
    """

    __tablename__ = "xp_events"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)

    # XP details
    amount: int  # Can be negative for XP loss
    event_type: str = Field(index=True, max_length=50)  # quest_complete, streak, whale_bonus, etc.
    source_app: str = Field(index=True, max_length=50)  # flirt, onlyvips, poker, aurora

    # Optional references
    reference_id: str | None = Field(default=None, max_length=100)
    reference_type: str | None = Field(default=None, max_length=50)

    # Metadata (event details, etc.)
    # Note: Python field is 'meta' to avoid SQLAlchemy reserved keyword conflict
    # DB column remains 'metadata' for backward compatibility
    meta: dict = Field(
        default_factory=dict,
        sa_column=Column("metadata", JSONB, default={}),
    )

    # XP totals after this event
    xp_total_after: int | None = None
    level_after: int | None = None
    tier_after: str | None = None

    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserLoyalty(SQLModel, table=True):
    """
    User loyalty profile - cached/computed.
    
    Aurora routing, VIP masa, priority vs. için kullanılır.
    """

    __tablename__ = "user_loyalty"

    user_id: int = Field(foreign_key="users.id", primary_key=True)

    # XP & Level
    xp_total: int = Field(default=0)
    level: int = Field(default=1)
    tier: LoyaltyTier = Field(default=LoyaltyTier.BRONZE)

    # Stats
    total_events: int = Field(default=0)

    # Streaks (opsiyonel, v0.2)
    current_streak: int = Field(default=0)
    max_streak: int = Field(default=0)
    last_activity_date: datetime | None = None

    # VIP benefits (Aurora/Betül routing için)
    vip_priority: int = Field(default=0)  # 0-100, higher = better routing
    ai_credits_bonus: float = Field(default=0.0)  # Bonus AI credits multiplier

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "xp_total": 5500,
                "level": 12,
                "tier": "GOLD",
                "vip_priority": 75,
            }
        }

