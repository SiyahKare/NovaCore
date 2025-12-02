"""
Telegram Gateway - Leaderboard Schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class LeaderboardEntry(BaseModel):
    """Leaderboard entry."""
    rank: int
    user_id: int
    telegram_user_id: int
    username: Optional[str] = None
    display_name: Optional[str] = None
    xp_total: int
    level: int
    tier: str
    tasks_completed: int
    referrals_count: int


class LeaderboardResponse(BaseModel):
    """Leaderboard response."""
    entries: list[LeaderboardEntry]
    total_users: int
    period: str  # "daily", "weekly", "all_time"
    updated_at: datetime


class ProfileCardResponse(BaseModel):
    """Profil kartı response."""
    user_id: int
    telegram_user_id: int
    username: Optional[str] = None
    display_name: Optional[str] = None
    
    # Stats
    xp_total: int
    level: int
    tier: str
    tasks_completed: int
    referrals_count: int
    rank_all_time: Optional[int] = None
    rank_weekly: Optional[int] = None
    
    # Achievements
    achievements: list[str] = Field(default_factory=list)
    
    # Timestamps
    first_seen_at: datetime
    last_seen_at: datetime

