"""
NovaCore - NovaCredit Schemas
Request/Response Models
"""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.nova_credit.models import CreditTier
from app.nova_credit.rules import EventCategory


# ============ Behavior Event (Internal) ============
class BehaviorEvent(BaseModel):
    """
    Normalized behavior event.
    
    Events modülünden gelen raw event → bu formata dönüştürülür.
    NovaCredit engine bu formatı işler.
    """
    event_id: str | None = None
    actor_id: int  # user_id
    event_type: str  # TIP_SENT, QUEST_COMPLETED, etc.
    category: EventCategory
    base_delta: int  # Ağırlık öncesi temel delta
    source_app: Literal["flirt", "onlyvips", "poker", "aurora", "system"]
    reason: str | None = None
    context: dict = Field(default_factory=dict)


# ============ Credit Profile ============
class CreditProfile(BaseModel):
    """User's full credit profile."""
    user_id: int
    nova_credit: int
    tier: CreditTier
    risk_score: float
    reputation_score: float

    # Activity
    total_events: int
    positive_streak: int
    negative_streak: int

    # Risk level
    risk_level: str

    # Privileges
    privileges: "TierPrivileges"

    # Progress
    progress_to_next_tier: float  # 0.0 - 1.0
    next_tier: CreditTier | None
    credit_to_next_tier: int

    # Timestamps
    last_event_at: datetime | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CreditProfileBrief(BaseModel):
    """Brief credit info for quick lookups."""
    user_id: int
    nova_credit: int
    tier: CreditTier
    risk_level: str


class TierPrivileges(BaseModel):
    """Tier-based privileges."""
    withdraw_limit_daily: int
    transfer_limit_daily: int
    can_create_content: bool
    can_host_rooms: bool
    priority_support: bool
    ai_model_tier: str
    transaction_fee_discount: float


# Fix forward reference
CreditProfile.model_rebuild()


# ============ Score Change ============
class ScoreChangeOut(BaseModel):
    """Score change response."""
    id: int
    user_id: int
    event_type: str
    delta: int
    old_score: int
    new_score: int
    category: str
    reason: str
    source_app: str
    created_at: datetime

    class Config:
        from_attributes = True


class ScoreChangeHistory(BaseModel):
    """Score change history response."""
    changes: list[ScoreChangeOut]
    total: int
    page: int
    per_page: int


# ============ Process Result ============
class ProcessEventResult(BaseModel):
    """Result of processing a behavior event."""
    success: bool
    user_id: int
    event_type: str
    
    # Score changes
    delta: int
    old_score: int
    new_score: int
    
    # New tier if changed
    old_tier: CreditTier
    new_tier: CreditTier
    tier_changed: bool
    
    # Risk/reputation changes
    risk_delta: float
    reputation_delta: float
    
    message: str | None = None


# ============ Risk Flag ============
class RiskFlagCreate(BaseModel):
    """Create risk flag."""
    user_id: int
    flag_type: Literal["FRAUD", "ABUSE", "MANIPULATION", "SUSPICIOUS"]
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    description: str = Field(..., max_length=500)
    event_id: str | None = None
    source_app: str
    context: dict = Field(default_factory=dict)


class RiskFlagOut(BaseModel):
    """Risk flag response."""
    id: int
    user_id: int
    flag_type: str
    severity: str
    description: str
    is_active: bool
    created_at: datetime
    resolved_at: datetime | None

    class Config:
        from_attributes = True


# ============ Admin Stats ============
class CreditStats(BaseModel):
    """Credit system stats."""
    total_citizens: int
    average_credit: float
    median_credit: int

    # Distribution
    tier_distribution: dict[str, int]
    risk_distribution: dict[str, int]

    # Activity
    events_last_24h: int
    events_last_7d: int

    # Health
    citizens_at_risk: int  # risk_score > 0.6
    citizens_in_ghost: int  # tier = GHOST


class CreditLeaderboard(BaseModel):
    """Credit leaderboard."""
    entries: list["LeaderboardEntry"]
    total: int


class LeaderboardEntry(BaseModel):
    """Leaderboard entry."""
    rank: int
    user_id: int
    username: str | None
    nova_credit: int
    tier: CreditTier
    reputation_score: float


CreditLeaderboard.model_rebuild()

