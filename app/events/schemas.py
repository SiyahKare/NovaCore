"""
NovaCore Events Schemas - App Event Ingest
"""
from decimal import Decimal
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


# ============ FlirtMarket Events ============
class FlirtEventType(str, Enum):
    COIN_SPENT = "COIN_SPENT"  # User spent coins on performer
    SHOW_PURCHASED = "SHOW_PURCHASED"  # Private show purchased
    BOOST_USED = "BOOST_USED"  # User used boost
    TIP_SENT = "TIP_SENT"  # User tipped performer
    GIFT_SENT = "GIFT_SENT"  # Virtual gift sent


class FlirtEvent(BaseModel):
    """FlirtMarket event payload."""

    event_type: FlirtEventType
    user_id: int
    performer_id: int | None = None
    amount: Decimal = Field(..., gt=0)
    metadata: dict = Field(default_factory=dict)

    # XP bonus (optional)
    xp_bonus: int | None = None


# ============ OnlyVips Events ============
class OnlyVipsEventType(str, Enum):
    PREMIUM_PURCHASED = "PREMIUM_PURCHASED"
    CONTENT_UNLOCKED = "CONTENT_UNLOCKED"
    SUBSCRIPTION_RENEWED = "SUBSCRIPTION_RENEWED"
    QUEST_COMPLETED = "QUEST_COMPLETED"
    STREAK_BONUS = "STREAK_BONUS"


class OnlyVipsEvent(BaseModel):
    """OnlyVips event payload."""

    event_type: OnlyVipsEventType
    user_id: int
    performer_id: int | None = None
    amount: Decimal = Field(default=Decimal("0"))
    metadata: dict = Field(default_factory=dict)

    # XP
    xp_amount: int = Field(default=0)


# ============ PokerVerse Events ============
class PokerEventType(str, Enum):
    BUY_IN = "BUY_IN"  # Masaya oturma
    CASH_OUT = "CASH_OUT"  # Masadan kalkma
    RAKE = "RAKE"  # Pot rake
    TOURNAMENT_BUY_IN = "TOURNAMENT_BUY_IN"
    TOURNAMENT_PRIZE = "TOURNAMENT_PRIZE"


class PokerEvent(BaseModel):
    """PokerVerse event payload."""

    event_type: PokerEventType
    user_id: int
    amount: Decimal = Field(..., gt=0)
    table_id: str | None = None
    hand_id: str | None = None
    metadata: dict = Field(default_factory=dict)


# ============ Aurora Events ============
class AuroraEventType(str, Enum):
    AI_CHAT_SESSION = "AI_CHAT_SESSION"
    AI_IMAGE_GENERATED = "AI_IMAGE_GENERATED"
    AI_VOICE_MESSAGE = "AI_VOICE_MESSAGE"
    TOKEN_BURN = "TOKEN_BURN"


class AuroraEvent(BaseModel):
    """Aurora AI event payload."""

    event_type: AuroraEventType
    user_id: int
    performer_id: int | None = None  # AI performer
    amount: Decimal = Field(..., ge=0)  # Burn amount
    ai_profile_id: str | None = None
    tokens_used: int = Field(default=0)
    metadata: dict = Field(default_factory=dict)


# ============ Generic Event Result ============
class EventResult(BaseModel):
    """Event processing result."""

    success: bool
    event_type: str
    user_id: int
    ncr_change: Decimal
    xp_change: int
    new_ncr_balance: Decimal | None = None
    new_xp_total: int | None = None
    revenue_split: dict | None = None  # performer/agency/treasury split
    message: str | None = None

