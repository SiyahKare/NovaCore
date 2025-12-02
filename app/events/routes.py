"""
NovaCore Events Routes - App Event Ingest Endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.events.schemas import (
    AuroraEvent,
    EventResult,
    FlirtEvent,
    OnlyVipsEvent,
    PokerEvent,
)
from app.events.service import EventService

router = APIRouter(prefix="/api/v1/events", tags=["events"])


@router.post(
    "/flirt",
    response_model=EventResult,
    summary="FlirtMarket Event",
    description="Process FlirtMarket event (coin spent, show purchase, tip, gift).",
)
async def handle_flirt_event(
    event: FlirtEvent,
    session: AsyncSession = Depends(get_session),
) -> EventResult:
    """
    Process FlirtMarket event.
    
    Event types:
    - COIN_SPENT: User spent coins on performer
    - SHOW_PURCHASED: Private show purchased
    - BOOST_USED: User used boost
    - TIP_SENT: User tipped performer
    - GIFT_SENT: Virtual gift sent
    
    Effects:
    - Deducts NCR from user wallet
    - Awards XP to user
    - Calculates revenue split (performer/agency/treasury)
    - Records performer earnings
    """
    service = EventService(session)
    return await service.handle_flirt_event(event)


@router.post(
    "/onlyvips",
    response_model=EventResult,
    summary="OnlyVips Event",
    description="Process OnlyVips event (premium, content, quest, streak).",
)
async def handle_onlyvips_event(
    event: OnlyVipsEvent,
    session: AsyncSession = Depends(get_session),
) -> EventResult:
    """
    Process OnlyVips event.
    
    Event types:
    - PREMIUM_PURCHASED: Premium content purchased
    - CONTENT_UNLOCKED: Content unlocked
    - SUBSCRIPTION_RENEWED: Subscription renewed
    - QUEST_COMPLETED: Quest completed
    - STREAK_BONUS: Daily streak bonus
    
    Effects:
    - Deducts NCR for purchases
    - Awards XP for activity
    - Calculates revenue split for performer content
    """
    service = EventService(session)
    return await service.handle_onlyvips_event(event)


@router.post(
    "/poker",
    response_model=EventResult,
    summary="PokerVerse Event",
    description="Process PokerVerse event (buy-in, cash-out, rake, tournament).",
)
async def handle_poker_event(
    event: PokerEvent,
    session: AsyncSession = Depends(get_session),
) -> EventResult:
    """
    Process PokerVerse event.
    
    Event types:
    - BUY_IN: User buys into table
    - CASH_OUT: User cashes out from table
    - RAKE: Rake taken from pot
    - TOURNAMENT_BUY_IN: Tournament buy-in
    - TOURNAMENT_PRIZE: Tournament prize payout
    
    Effects:
    - Manages NCR for poker operations
    - Rake goes to treasury
    - Awards XP for profitable sessions
    """
    service = EventService(session)
    return await service.handle_poker_event(event)


@router.post(
    "/aurora",
    response_model=EventResult,
    summary="Aurora AI Event",
    description="Process Aurora AI event (chat, image, voice, token burn).",
)
async def handle_aurora_event(
    event: AuroraEvent,
    session: AsyncSession = Depends(get_session),
) -> EventResult:
    """
    Process Aurora AI event.
    
    Event types:
    - AI_CHAT_SESSION: AI chat session
    - AI_IMAGE_GENERATED: AI image generated
    - AI_VOICE_MESSAGE: AI voice message
    - TOKEN_BURN: Token burn for AI usage
    
    Effects:
    - Burns NCR for AI usage
    - Awards XP based on tokens used
    - Calculates revenue split for AI performers
    """
    service = EventService(session)
    return await service.handle_aurora_event(event)

