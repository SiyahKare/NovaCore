"""
NovaCore XP & Loyalty Routes
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.security import get_current_user
from app.identity.models import User
from app.xp_loyalty.schemas import (
    LeaderboardResponse,
    LoyaltyProfileBrief,
    LoyaltyProfileResponse,
    LoyaltyStats,
    XpEventCreate,
    XpEventResponse,
)
from app.xp_loyalty.service import XpLoyaltyService

router = APIRouter(prefix="/api/v1/loyalty", tags=["xp_loyalty"])


# ============ Profile Endpoints ============
@router.get(
    "/me",
    response_model=LoyaltyProfileResponse,
    summary="My Loyalty Profile",
    description="Get current user's loyalty profile with XP, level, tier.",
)
async def get_my_loyalty(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> LoyaltyProfileResponse:
    """Get current user's loyalty profile."""
    service = XpLoyaltyService(session)
    return await service.get_loyalty_profile(current_user.id)


@router.get(
    "/profile/{user_id}",
    response_model=LoyaltyProfileResponse,
    summary="Get Loyalty Profile",
    description="Get a user's loyalty profile by ID.",
)
async def get_loyalty_profile(
    user_id: int,
    session: AsyncSession = Depends(get_session),
) -> LoyaltyProfileResponse:
    """Get user's loyalty profile."""
    service = XpLoyaltyService(session)
    return await service.get_loyalty_profile(user_id)


@router.get(
    "/brief/{user_id}",
    response_model=LoyaltyProfileBrief,
    summary="Get Loyalty Brief",
    description="Get brief loyalty info for Aurora routing.",
)
async def get_loyalty_brief(
    user_id: int,
    session: AsyncSession = Depends(get_session),
) -> LoyaltyProfileBrief:
    """Get brief loyalty profile for routing decisions."""
    service = XpLoyaltyService(session)
    return await service.get_loyalty_brief(user_id)


# ============ XP Event Endpoint ============
@router.post(
    "/event",
    response_model=XpEventResponse,
    summary="Create XP Event",
    description="Create an XP event (used by FlirtMarket, OnlyVips, PokerVerse, Aurora).",
)
async def create_xp_event(
    event: XpEventCreate,
    session: AsyncSession = Depends(get_session),
) -> XpEventResponse:
    """
    Create XP event from app.
    
    Event types:
    - quest_complete: Quest tamamlandı
    - streak: Günlük giriş streak
    - whale_bonus: Yüksek harcama bonusu
    - referral: Referral bonusu
    - poker_win: Poker kazancı
    - ai_usage: Aurora kullanımı
    """
    service = XpLoyaltyService(session)
    return await service.create_xp_event(event)


# ============ Leaderboard ============
@router.get(
    "/leaderboard",
    response_model=LeaderboardResponse,
    summary="XP Leaderboard",
    description="Get the XP leaderboard.",
)
async def get_leaderboard(
    session: AsyncSession = Depends(get_session),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> LeaderboardResponse:
    """Get XP leaderboard."""
    service = XpLoyaltyService(session)
    return await service.get_leaderboard(limit, offset)


# ============ Stats ============
@router.get(
    "/stats",
    response_model=LoyaltyStats,
    summary="Loyalty Stats",
    description="Get global loyalty statistics.",
)
async def get_stats(
    session: AsyncSession = Depends(get_session),
) -> LoyaltyStats:
    """Get global loyalty stats."""
    service = XpLoyaltyService(session)
    return await service.get_stats()

