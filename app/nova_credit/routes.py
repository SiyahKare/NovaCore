"""
NovaCore - NovaCredit Routes
API Endpoints for Credit System
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.security import get_admin_user, get_current_user
from app.identity.models import User
from app.nova_credit.models import CreditTier
from app.nova_credit.schemas import (
    BehaviorEvent,
    CreditLeaderboard,
    CreditProfile,
    CreditProfileBrief,
    CreditStats,
    LeaderboardEntry,
    ProcessEventResult,
    RiskFlagCreate,
    RiskFlagOut,
    ScoreChangeHistory,
    ScoreChangeOut,
)
from app.nova_credit.service import NovaCreditService

router = APIRouter(prefix="/api/v1/credit", tags=["nova_credit"])


# ============ Profile Endpoints ============
@router.get(
    "/me",
    response_model=CreditProfile,
    summary="My Credit Profile",
    description="Get current user's full credit profile with privileges.",
)
async def get_my_credit(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> CreditProfile:
    """Get current user's credit profile."""
    service = NovaCreditService(session)
    return await service.get_credit_profile(current_user.id)


@router.get(
    "/profile/{user_id}",
    response_model=CreditProfile,
    summary="Get Credit Profile",
    description="Get a user's credit profile by ID.",
)
async def get_credit_profile(
    user_id: int,
    session: AsyncSession = Depends(get_session),
) -> CreditProfile:
    """Get user's credit profile."""
    service = NovaCreditService(session)
    return await service.get_credit_profile(user_id)


@router.get(
    "/brief/{user_id}",
    response_model=CreditProfileBrief,
    summary="Get Credit Brief",
    description="Get brief credit info for quick lookups (Aurora routing, etc).",
)
async def get_credit_brief(
    user_id: int,
    session: AsyncSession = Depends(get_session),
) -> CreditProfileBrief:
    """Get brief credit profile."""
    service = NovaCreditService(session)
    return await service.get_credit_brief(user_id)


# ============ History ============
@router.get(
    "/me/history",
    response_model=ScoreChangeHistory,
    summary="My Credit History",
    description="Get current user's credit score change history.",
)
async def get_my_history(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
) -> ScoreChangeHistory:
    """Get current user's score change history."""
    service = NovaCreditService(session)
    changes, total = await service.get_score_history(
        current_user.id, page, per_page
    )

    return ScoreChangeHistory(
        changes=[ScoreChangeOut.model_validate(c) for c in changes],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get(
    "/{user_id}/history",
    response_model=ScoreChangeHistory,
    summary="Get Credit History",
    description="Get a user's credit score change history.",
)
async def get_history(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
) -> ScoreChangeHistory:
    """Get user's score change history."""
    service = NovaCreditService(session)
    changes, total = await service.get_score_history(user_id, page, per_page)

    return ScoreChangeHistory(
        changes=[ScoreChangeOut.model_validate(c) for c in changes],
        total=total,
        page=page,
        per_page=per_page,
    )


# ============ Event Processing (Internal) ============
@router.post(
    "/process",
    response_model=ProcessEventResult,
    summary="Process Behavior Event",
    description="Process a behavior event and update credit score (internal use).",
)
async def process_event(
    event: BehaviorEvent,
    session: AsyncSession = Depends(get_session),
) -> ProcessEventResult:
    """
    Process a behavior event.
    
    This endpoint is used by other modules (events, wallet) to
    report behavior events that affect credit score.
    """
    service = NovaCreditService(session)
    return await service.process_event(event)


# ============ Risk Flags ============
@router.get(
    "/me/risks",
    response_model=list[RiskFlagOut],
    summary="My Risk Flags",
    description="Get current user's active risk flags.",
)
async def get_my_risks(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[RiskFlagOut]:
    """Get current user's risk flags."""
    service = NovaCreditService(session)
    return await service.get_active_risk_flags(current_user.id)


@router.post(
    "/risks",
    response_model=RiskFlagOut,
    summary="Create Risk Flag",
    description="Create a risk flag for a user (admin/system only).",
)
async def create_risk_flag(
    data: RiskFlagCreate,
    _admin: User = Depends(get_admin_user),
    session: AsyncSession = Depends(get_session),
) -> RiskFlagOut:
    """Create a risk flag."""
    service = NovaCreditService(session)
    return await service.create_risk_flag(data)


# ============ Leaderboard ============
@router.get(
    "/leaderboard",
    response_model=CreditLeaderboard,
    summary="Credit Leaderboard",
    description="Get top citizens by credit score.",
)
async def get_leaderboard(
    session: AsyncSession = Depends(get_session),
    limit: int = Query(10, ge=1, le=100),
    tier: CreditTier | None = Query(None, description="Filter by tier"),
) -> CreditLeaderboard:
    """Get credit leaderboard."""
    service = NovaCreditService(session)
    entries = await service.get_leaderboard(limit, tier)

    return CreditLeaderboard(
        entries=entries,
        total=len(entries),
    )


# ============ Stats (Admin) ============
@router.get(
    "/stats",
    response_model=CreditStats,
    summary="Credit Statistics",
    description="Get credit system statistics (admin only).",
)
async def get_stats(
    _admin: User = Depends(get_admin_user),
    session: AsyncSession = Depends(get_session),
) -> CreditStats:
    """Get credit system statistics."""
    service = NovaCreditService(session)
    return await service.get_stats()


# ============ Admin Endpoints ============
@router.get(
    "/admin/risky",
    response_model=list[CreditProfileBrief],
    summary="Risky Citizens",
    description="Get citizens with high risk scores (admin only).",
)
async def get_risky_citizens(
    _admin: User = Depends(get_admin_user),
    session: AsyncSession = Depends(get_session),
    limit: int = Query(20, ge=1, le=100),
) -> list[CreditProfileBrief]:
    """Get citizens with high risk scores."""
    from sqlmodel import select
    from app.nova_credit.models import CitizenScore

    result = await session.execute(
        select(CitizenScore)
        .where(CitizenScore.risk_score > 0.5)
        .order_by(CitizenScore.risk_score.desc())
        .limit(limit)
    )
    scores = result.scalars().all()

    from app.nova_credit.rules import get_risk_level

    return [
        CreditProfileBrief(
            user_id=s.user_id,
            nova_credit=s.nova_credit,
            tier=s.tier,
            risk_level=get_risk_level(s.risk_score),
        )
        for s in scores
    ]


@router.get(
    "/admin/ghosts",
    response_model=list[CreditProfileBrief],
    summary="Ghost Citizens",
    description="Get citizens in GHOST tier (admin only).",
)
async def get_ghost_citizens(
    _admin: User = Depends(get_admin_user),
    session: AsyncSession = Depends(get_session),
    limit: int = Query(20, ge=1, le=100),
) -> list[CreditProfileBrief]:
    """Get citizens in GHOST tier."""
    from sqlmodel import select
    from app.nova_credit.models import CitizenScore

    result = await session.execute(
        select(CitizenScore)
        .where(CitizenScore.tier == CreditTier.GHOST)
        .order_by(CitizenScore.nova_credit.asc())
        .limit(limit)
    )
    scores = result.scalars().all()

    from app.nova_credit.rules import get_risk_level

    return [
        CreditProfileBrief(
            user_id=s.user_id,
            nova_credit=s.nova_credit,
            tier=s.tier,
            risk_level=get_risk_level(s.risk_score),
        )
        for s in scores
    ]

