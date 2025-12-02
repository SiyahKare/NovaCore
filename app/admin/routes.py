"""
NovaCore Admin Routes - Health & Summary Endpoints
"""
from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import func, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.agency.models import Agency, Performer
from app.core.config import settings
from app.core.db import get_session
from app.core.security import get_admin_user
from app.identity.models import User
from app.wallet.models import Account, LedgerEntry
from app.xp_loyalty.models import UserLoyalty

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


# ============ Health Check ============
class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    environment: str
    timestamp: datetime
    database: str


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check system health status.",
)
async def health_check(
    session: AsyncSession = Depends(get_session),
) -> HealthResponse:
    """Health check endpoint."""
    # Test database connection
    db_status = "healthy"
    try:
        await session.execute(text("SELECT 1"))
    except Exception:
        db_status = "unhealthy"

    return HealthResponse(
        status="ok" if db_status == "healthy" else "degraded",
        version="0.1.0",
        environment=settings.ENV,
        timestamp=datetime.utcnow(),
        database=db_status,
    )


# ============ System Summary ============
class TopUser(BaseModel):
    """Top user entry."""

    user_id: int
    username: str | None
    display_name: str | None
    value: int  # XP or NCR


class TopPerformer(BaseModel):
    """Top performer entry."""

    performer_id: int
    display_name: str
    handle: str
    total_earnings: int
    agency_name: str | None


class SystemSummary(BaseModel):
    """System summary response."""

    # Users
    total_users: int
    active_users_24h: int  # placeholder

    # NCR Economy
    total_ncr_in_circulation: Decimal
    treasury_balance: Decimal
    total_transactions: int

    # XP/Loyalty
    total_xp_distributed: int
    average_level: float

    # Agencies
    total_agencies: int
    total_performers: int

    # Top lists
    top_users_by_xp: list[TopUser]
    top_users_by_ncr: list[TopUser]
    top_performers: list[TopPerformer]


@router.get(
    "/summary",
    response_model=SystemSummary,
    summary="System Summary",
    description="Get comprehensive system summary (admin only).",
)
async def get_summary(
    _admin: User = Depends(get_admin_user),
    session: AsyncSession = Depends(get_session),
) -> SystemSummary:
    """Get system summary."""

    # Total users
    users_result = await session.execute(select(func.count(User.id)))
    total_users = users_result.scalar() or 0

    # NCR in circulation (excluding treasury)
    circ_result = await session.execute(
        select(func.sum(Account.balance)).where(
            Account.token == "NCR",
            Account.user_id != settings.NCR_TREASURY_USER_ID,
        )
    )
    total_ncr = circ_result.scalar() or Decimal("0")

    # Treasury balance
    treasury_result = await session.execute(
        select(Account.balance).where(
            Account.user_id == settings.NCR_TREASURY_USER_ID,
            Account.token == "NCR",
        )
    )
    treasury_balance = treasury_result.scalar() or Decimal("0")

    # Total transactions
    tx_result = await session.execute(select(func.count(LedgerEntry.id)))
    total_transactions = tx_result.scalar() or 0

    # XP stats
    xp_result = await session.execute(select(func.sum(UserLoyalty.xp_total)))
    total_xp = xp_result.scalar() or 0

    avg_result = await session.execute(select(func.avg(UserLoyalty.level)))
    avg_level = float(avg_result.scalar() or 1.0)

    # Agencies
    agencies_result = await session.execute(
        select(func.count(Agency.id)).where(Agency.is_active == True)
    )
    total_agencies = agencies_result.scalar() or 0

    performers_result = await session.execute(
        select(func.count(Performer.id)).where(Performer.is_active == True)
    )
    total_performers = performers_result.scalar() or 0

    # Top users by XP
    top_xp_query = (
        select(UserLoyalty, User)
        .join(User, UserLoyalty.user_id == User.id)
        .order_by(UserLoyalty.xp_total.desc())
        .limit(5)
    )
    top_xp_result = await session.execute(top_xp_query)
    top_users_xp = [
        TopUser(
            user_id=loyalty.user_id,
            username=user.username,
            display_name=user.display_name,
            value=loyalty.xp_total,
        )
        for loyalty, user in top_xp_result.all()
    ]

    # Top users by NCR
    top_ncr_query = (
        select(Account, User)
        .join(User, Account.user_id == User.id)
        .where(Account.token == "NCR", Account.user_id != settings.NCR_TREASURY_USER_ID)
        .order_by(Account.balance.desc())
        .limit(5)
    )
    top_ncr_result = await session.execute(top_ncr_query)
    top_users_ncr = [
        TopUser(
            user_id=account.user_id,
            username=user.username,
            display_name=user.display_name,
            value=int(account.balance),
        )
        for account, user in top_ncr_result.all()
    ]

    # Top performers
    top_performers_query = (
        select(Performer, Agency)
        .join(Agency, Performer.agency_id == Agency.id)
        .where(Performer.is_active == True)
        .order_by(Performer.total_earnings.desc())
        .limit(5)
    )
    top_performers_result = await session.execute(top_performers_query)
    top_performers = [
        TopPerformer(
            performer_id=performer.id,
            display_name=performer.display_name,
            handle=performer.handle,
            total_earnings=performer.total_earnings,
            agency_name=agency.name,
        )
        for performer, agency in top_performers_result.all()
    ]

    return SystemSummary(
        total_users=total_users,
        active_users_24h=0,  # TODO: implement
        total_ncr_in_circulation=total_ncr,
        treasury_balance=treasury_balance,
        total_transactions=total_transactions,
        total_xp_distributed=total_xp,
        average_level=avg_level,
        total_agencies=total_agencies,
        total_performers=total_performers,
        top_users_by_xp=top_users_xp,
        top_users_by_ncr=top_users_ncr,
        top_performers=top_performers,
    )


# ============ Quick Stats ============
class QuickStats(BaseModel):
    """Quick stats for dashboard."""

    total_users: int
    total_ncr: Decimal
    treasury_ncr: Decimal
    total_performers: int


@router.get(
    "/stats",
    response_model=QuickStats,
    summary="Quick Stats",
    description="Get quick stats (no auth required for dashboard).",
)
async def get_quick_stats(
    session: AsyncSession = Depends(get_session),
) -> QuickStats:
    """Get quick stats."""
    from sqlmodel import select

    users = await session.execute(select(func.count(User.id)))
    total_users = users.scalar() or 0

    ncr = await session.execute(
        select(func.sum(Account.balance)).where(
            Account.token == "NCR",
            Account.user_id != settings.NCR_TREASURY_USER_ID,
        )
    )
    total_ncr = ncr.scalar() or Decimal("0")

    treasury = await session.execute(
        select(Account.balance).where(
            Account.user_id == settings.NCR_TREASURY_USER_ID,
            Account.token == "NCR",
        )
    )
    treasury_ncr = treasury.scalar() or Decimal("0")

    performers = await session.execute(
        select(func.count(Performer.id)).where(Performer.is_active == True)
    )
    total_performers = performers.scalar() or 0

    return QuickStats(
        total_users=total_users,
        total_ncr=total_ncr,
        treasury_ncr=treasury_ncr,
        total_performers=total_performers,
    )


# ============ NovaCredit Summary ============
class CreditSummary(BaseModel):
    """NovaCredit system summary."""

    total_citizens: int
    average_credit: float
    tier_distribution: dict[str, int]
    citizens_at_risk: int
    citizens_in_ghost: int
    events_last_24h: int


@router.get(
    "/credit/summary",
    response_model=CreditSummary,
    summary="Credit Summary",
    description="Get NovaCredit system summary (admin only).",
)
async def get_credit_summary(
    _admin: User = Depends(get_admin_user),
    session: AsyncSession = Depends(get_session),
) -> CreditSummary:
    """Get NovaCredit system summary."""
    from app.nova_credit.service import NovaCreditService

    service = NovaCreditService(session)
    stats = await service.get_stats()

    return CreditSummary(
        total_citizens=stats.total_citizens,
        average_credit=stats.average_credit,
        tier_distribution=stats.tier_distribution,
        citizens_at_risk=stats.citizens_at_risk,
        citizens_in_ghost=stats.citizens_in_ghost,
        events_last_24h=stats.events_last_24h,
    )


@router.get(
    "/credit/top",
    summary="Top Citizens by Credit",
    description="Get top citizens by NovaCredit score (admin only).",
)
async def get_credit_top(
    _admin: User = Depends(get_admin_user),
    session: AsyncSession = Depends(get_session),
):
    """Get top citizens by NovaCredit score."""
    from app.nova_credit.service import NovaCreditService

    service = NovaCreditService(session)
    return await service.get_top_citizens(limit=50)


# ============ Aurora Justice Stats ============
from app.admin.aurora_stats import AuroraStatsResponse, AuroraStatsService


@router.get(
    "/aurora/stats",
    response_model=AuroraStatsResponse,
    summary="Aurora Justice Stack Statistics",
    description="Get comprehensive Aurora Justice Stack statistics (admin only).",
)
async def get_aurora_stats(
    _admin: User = Depends(get_admin_user),
    session: AsyncSession = Depends(get_session),
) -> AuroraStatsResponse:
    """Get Aurora Justice Stack statistics."""
    service = AuroraStatsService(session)
    return await service.get_stats()


# ============ Aurora Violation Stream ============
from fastapi import Query
from sqlalchemy import and_
from sqlmodel import select, func
from datetime import datetime
from typing import Optional
from app.justice.models import ViolationLog, UserCpState
from app.justice.schemas import AdminViolationItem, AdminViolationListResponse
from app.justice.policy import regime_for_cp


@router.get(
    "/aurora/violations",
    response_model=AdminViolationListResponse,
    summary="Aurora Violation Stream",
    description="Get paginated violation stream with filters (admin only).",
)
async def list_violations(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    category: Optional[str] = Query(None, description="EKO, COM, SYS, TRUST"),
    severity_min: int = Query(1, ge=1, le=5),
    severity_max: int = Query(5, ge=1, le=5),
    since: Optional[datetime] = Query(None),
    _admin: User = Depends(get_admin_user),
    session: AsyncSession = Depends(get_session),
) -> AdminViolationListResponse:
    """Get paginated violation stream with filters."""
    filters = [
        ViolationLog.severity >= severity_min,
        ViolationLog.severity <= severity_max,
    ]

    if category:
        filters.append(ViolationLog.category == category)

    if since:
        filters.append(ViolationLog.created_at >= since)

    # Count total
    count_query = select(func.count()).select_from(
        select(ViolationLog.id).where(and_(*filters)).subquery()
    )
    total = (await session.execute(count_query)).scalar_one()

    # Fetch violations
    stmt = (
        select(ViolationLog)
        .where(and_(*filters))
        .order_by(ViolationLog.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await session.execute(stmt)
    rows = result.scalars().all()

    # Build response items
    items = []
    for v in rows:
        # Get user's CP state to determine regime_after
        cp_state_result = await session.execute(
            select(UserCpState).where(UserCpState.user_id == v.user_id)
        )
        cp_state = cp_state_result.scalar_one_or_none()
        regime_after = None
        if cp_state:
            # Get active policy to determine regime
            from app.justice.policy_service import PolicyService
            policy_service = PolicyService(session)
            policy = await policy_service.get_active_policy()
            regime_after = regime_for_cp(policy, cp_state.cp_value)

        # Extract message_preview from context if available
        message_preview = None
        if v.context and isinstance(v.context, dict):
            message_preview = v.context.get("message_preview")

        items.append(
            AdminViolationItem(
                id=str(v.id),
                user_id=v.user_id,
                category=v.category,
                code=v.code,
                severity=v.severity,
                cp_delta=float(v.cp_delta),
                regime_after=regime_after,
                source=v.source,
                message_preview=message_preview,
                meta=v.context or {},
                created_at=v.created_at,
            )
        )

    return AdminViolationListResponse(
        items=items, total=total, limit=limit, offset=offset
    )


# ============ Aurora Growth Metrics ============
from app.telemetry.schemas import GrowthMetricsResponse


@router.get(
    "/aurora/growth",
    response_model=GrowthMetricsResponse,
    summary="Aurora Growth Metrics",
    description="Get growth and education metrics (admin only).",
)
async def get_aurora_growth(
    _admin: User = Depends(get_admin_user),
    session: AsyncSession = Depends(get_session),
) -> GrowthMetricsResponse:
    """Get Aurora growth metrics."""
    from app.telemetry.router import get_growth_metrics
    return await get_growth_metrics(_admin, session)


async def get_top_citizens(
    _admin: User = Depends(get_admin_user),
    session: AsyncSession = Depends(get_session),
    tier: str | None = None,
    limit: int = 10,
):
    """Get top citizens by NovaCredit."""
    from app.nova_credit.models import CreditTier
    from app.nova_credit.service import NovaCreditService

    service = NovaCreditService(session)

    tier_filter = None
    if tier:
        try:
            tier_filter = CreditTier(tier)
        except ValueError:
            pass

    entries = await service.get_leaderboard(limit, tier_filter)

    return {
        "entries": [
            {
                "rank": e.rank,
                "user_id": e.user_id,
                "username": e.username,
                "nova_credit": e.nova_credit,
                "tier": e.tier.value,
                "reputation_score": e.reputation_score,
            }
            for e in entries
        ],
        "total": len(entries),
    }


# Import select for the summary queries
from sqlmodel import select
from typing import Optional
from fastapi import Query


# ============ User Management ============
class UserListItem(BaseModel):
    """User list item with consent and recall status."""
    user_id: str
    display_name: Optional[str] = None
    email: Optional[str] = None
    username: Optional[str] = None
    has_consent: bool
    consent_level: Optional[str] = None
    recall_state: str  # "NONE", "REQUESTED", "COMPLETED"
    recall_mode: Optional[str] = None
    recall_requested_at: Optional[datetime] = None
    recall_completed_at: Optional[datetime] = None
    cp_value: int = 0
    is_admin: bool = False
    created_at: datetime


class UserListResponse(BaseModel):
    """User list response."""
    users: list[UserListItem]
    total: int
    page: int
    limit: int


@router.get(
    "/aurora/users",
    response_model=UserListResponse,
    summary="List all users with consent and recall status",
    description="Get paginated list of all users with their consent and recall information (admin only).",
)
async def list_users(
    _admin: User = Depends(get_admin_user),
    session: AsyncSession = Depends(get_session),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=200, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by user_id, email, or display_name"),
    recall_filter: Optional[str] = Query(None, description="Filter by recall state: NONE, REQUESTED, COMPLETED"),
) -> UserListResponse:
    """List all users with consent and recall status."""
    from sqlalchemy import or_
    from app.consent.models import UserPrivacyProfile
    from app.justice.models import UserCpState
    
    # Base query for users
    query = select(User)
    
    # Apply search filter
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                User.id.cast(str).like(search_term),
                User.email.like(search_term) if User.email else False,
                User.display_name.like(search_term) if User.display_name else False,
                User.username.like(search_term) if User.username else False,
            )
        )
    
    # Get total count
    count_query = select(func.count(User.id))
    if search:
        search_term = f"%{search}%"
        count_query = count_query.where(
            or_(
                User.id.cast(str).like(search_term),
                User.email.like(search_term) if User.email else False,
                User.display_name.like(search_term) if User.display_name else False,
                User.username.like(search_term) if User.username else False,
            )
        )
    total_result = await session.execute(count_query)
    total = total_result.scalar() or 0
    
    # Apply pagination
    offset = (page - 1) * limit
    query = query.order_by(User.created_at.desc()).offset(offset).limit(limit)
    
    # Execute query
    result = await session.execute(query)
    users = result.scalars().all()
    
    # Get user IDs
    user_ids = [str(u.id) for u in users]
    
    # Get privacy profiles for these users
    profiles_query = select(UserPrivacyProfile).where(
        UserPrivacyProfile.user_id.in_(user_ids)
    )
    profiles_result = await session.execute(profiles_query)
    profiles = {p.user_id: p for p in profiles_result.scalars().all()}
    
    # Get CP states for these users
    cp_query = select(UserCpState).where(
        UserCpState.user_id.in_(user_ids)
    )
    cp_result = await session.execute(cp_query)
    cp_states = {c.user_id: c for c in cp_result.scalars().all()}
    
    # Build response
    user_items = []
    for user in users:
        user_id_str = str(user.id)
        profile = profiles.get(user_id_str)
        cp_state = cp_states.get(user_id_str)
        
        # Determine recall state
        recall_state = "NONE"
        if profile:
            if profile.recall_completed_at:
                recall_state = "COMPLETED"
            elif profile.recall_requested_at:
                recall_state = "REQUESTED"
        
        # Apply recall filter
        if recall_filter and recall_state != recall_filter:
            continue
        
        user_items.append(
            UserListItem(
                user_id=user_id_str,
                display_name=user.display_name,
                email=user.email,
                username=user.username,
                has_consent=profile is not None and profile.latest_consent_id is not None,
                consent_level=profile.consent_level if profile else None,
                recall_state=recall_state,
                recall_mode=profile.recall_mode if profile else None,
                recall_requested_at=profile.recall_requested_at if profile else None,
                recall_completed_at=profile.recall_completed_at if profile else None,
                cp_value=cp_state.cp_value if cp_state else 0,
                is_admin=user.is_admin,
                created_at=user.created_at,
            )
        )
    
    # Recalculate total if recall filter was applied
    if recall_filter:
        total = len(user_items)
    
    return UserListResponse(
        users=user_items,
        total=total,
        page=page,
        limit=limit,
    )


# ============ Admin Management ============
class SetAdminRequest(BaseModel):
    """Request to set admin status."""
    is_admin: bool


class SetAdminResponse(BaseModel):
    """Response after setting admin status."""
    user_id: str
    is_admin: bool
    message: str


@router.patch(
    "/aurora/users/{user_id}/admin",
    response_model=SetAdminResponse,
    summary="Set user admin status",
    description="Grant or revoke admin privileges for a user (admin only).",
)
async def set_user_admin(
    user_id: str,
    body: SetAdminRequest,
    _admin: User = Depends(get_admin_user),
    session: AsyncSession = Depends(get_session),
) -> SetAdminResponse:
    """Set admin status for a user."""
    from app.identity.service import IdentityService
    
    try:
        target_user_id = int(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID",
        )
    
    # Get target user
    result = await session.execute(select(User).where(User.id == target_user_id))
    target_user = result.scalar_one_or_none()
    
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Prevent self-demotion (admin cannot remove their own admin status)
    if _admin.id == target_user_id and not body.is_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove your own admin status",
        )
    
    # Update admin status
    target_user.is_admin = body.is_admin
    target_user.updated_at = datetime.utcnow()
    session.add(target_user)
    await session.commit()
    await session.refresh(target_user)
    
    action = "granted" if body.is_admin else "revoked"
    return SetAdminResponse(
        user_id=str(target_user.id),
        is_admin=target_user.is_admin,
        message=f"Admin privileges {action} successfully",
    )

