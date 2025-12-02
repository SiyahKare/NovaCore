"""
Telegram Gateway - Event Schemas
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


class EventResponse(BaseModel):
    """Event response."""
    id: int
    code: str
    name: str
    description: Optional[str] = None
    event_type: str
    status: str
    starts_at: datetime
    ends_at: datetime
    reward_multiplier_xp: float
    reward_multiplier_ncr: float
    max_participants: Optional[int] = None
    min_level_required: int
    is_joined: bool = False
    user_rank: Optional[int] = None
    user_score: Optional[dict] = None


class ActiveEventsResponse(BaseModel):
    """Aktif event'ler response."""
    events: list[EventResponse]
    total_active: int


class EventJoinResponse(BaseModel):
    """Event join response."""
    success: bool
    message: str
    event_id: int
    event_name: str


class EventLeaderboardEntry(BaseModel):
    """Leaderboard entry."""
    rank: int
    user_id: int
    telegram_user_id: int
    username: Optional[str] = None
    display_name: Optional[str] = None
    total_xp_earned: int
    total_ncr_earned: str
    tasks_completed: int


class EventLeaderboardResponse(BaseModel):
    """Event leaderboard response."""
    event_id: int
    event_name: str
    entries: list[EventLeaderboardEntry]
    total_participants: int
    updated_at: datetime

