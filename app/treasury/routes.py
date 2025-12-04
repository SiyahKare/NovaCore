"""
NovaCore Treasury Routes
SiyahKare Nation Console için Treasury API endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.logging import get_logger
from app.treasury.schemas import (
    RevenueChartData,
    SystemAccountOut,
    TreasuryFlowOut,
    TreasuryFlowQuery,
    TreasurySummary,
)
from app.treasury.service import TreasuryService

logger = get_logger("treasury.routes")

router = APIRouter(prefix="/api/v1/treasury", tags=["Treasury"])


async def get_treasury_service(
    session: AsyncSession = Depends(get_session),
) -> TreasuryService:
    """Dependency for TreasuryService."""
    return TreasuryService(session)


@router.get("/summary", response_model=TreasurySummary)
async def get_treasury_summary(
    service: TreasuryService = Depends(get_treasury_service),
):
    """
    Treasury summary for NovaCore dashboard.
    
    Returns:
        - total_treasury: Tüm pool'ların toplam bakiyesi
        - pools_balance: Her pool'un bakiyesi
        - last_24h_revenue: Son 24 saatteki gelir
        - last_7d_revenue: Son 7 gündeki gelir
        - total_burned: Toplam yakılan token
        - revenue_by_app: Uygulama bazlı gelir breakdown
        - revenue_by_kind: Event tipi bazlı gelir breakdown
    """
    return await service.get_summary()


@router.get("/flows", response_model=list[TreasuryFlowOut])
async def get_treasury_flows(
    range: str = Query(default="24h", description="24h, 7d, 30d, all"),
    app: str | None = Query(default=None, description="Filter by app"),
    kind: str | None = Query(default=None, description="Filter by kind"),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=50, ge=1, le=100),
    service: TreasuryService = Depends(get_treasury_service),
):
    """
    Get treasury flows with filters.
    
    Returns paginated list of treasury flows.
    """
    flows, total = await service.get_flows(range, app, kind, page, per_page)
    return flows


@router.get("/pools", response_model=dict[str, SystemAccountOut])
async def get_treasury_pools(
    service: TreasuryService = Depends(get_treasury_service),
):
    """
    Get all treasury pool accounts with balances.
    
    Returns:
        {
            "POOL_GROWTH": {...},
            "POOL_PERFORMER": {...},
            "POOL_DEV": {...}
        }
    """
    from app.treasury.models import SystemAccount, SystemAccountType
    from sqlmodel import select

    pools = {}
    for pool_type in [
        SystemAccountType.POOL_GROWTH,
        SystemAccountType.POOL_PERFORMER,
        SystemAccountType.POOL_DEV,
    ]:
        result = await service.session.execute(
            select(SystemAccount).where(SystemAccount.account_type == pool_type)
        )
        account = result.scalar_one_or_none()
        if account:
            balance = await service.get_system_account_balance(pool_type)
            pool_out = SystemAccountOut.model_validate(account)
            pool_out.balance = balance
            pools[pool_type.value] = pool_out

    return pools


@router.get("/charts/revenue-by-app", response_model=RevenueChartData)
async def get_revenue_by_app_chart(
    range: str = Query(default="7d", description="7d, 30d"),
    service: TreasuryService = Depends(get_treasury_service),
):
    """
    Revenue chart data by app for NovaCore.
    
    Returns time series data for revenue breakdown by app.
    """
    from datetime import timedelta, datetime
    from decimal import Decimal
    from sqlalchemy import func, cast, Date
    from sqlmodel import select
    from app.treasury.models import TreasuryFlow

    # Range
    if range == "7d":
        since = datetime.utcnow() - timedelta(days=7)
    else:  # 30d
        since = datetime.utcnow() - timedelta(days=30)

    # Query: group by date and app
    query = (
        select(
            cast(TreasuryFlow.ts, Date).label("date"),
            TreasuryFlow.app,
            func.sum(TreasuryFlow.gross_amount).label("revenue"),
        )
        .where(TreasuryFlow.ts >= since)
        .group_by(cast(TreasuryFlow.ts, Date), TreasuryFlow.app)
        .order_by(cast(TreasuryFlow.ts, Date))
    )

    result = await service.session.execute(query)
    rows = result.all()

    # Organize data
    dates = sorted(set(row[0] for row in rows))
    apps = sorted(set(row[1] for row in rows))

    revenue_by_app = {app: [Decimal("0")] * len(dates) for app in apps}
    total_revenue = [Decimal("0")] * len(dates)

    for date, app, revenue in rows:
        date_idx = dates.index(date)
        revenue_by_app[app][date_idx] = revenue
        total_revenue[date_idx] += revenue

    return RevenueChartData(
        labels=[d.strftime("%Y-%m-%d") for d in dates],
        revenue=total_revenue,
        app_breakdown=revenue_by_app,
    )


@router.get("/charts/revenue-by-kind", response_model=RevenueChartData)
async def get_revenue_by_kind_chart(
    range: str = Query(default="7d", description="7d, 30d"),
    service: TreasuryService = Depends(get_treasury_service),
):
    """
    Revenue chart data by kind (event type) for NovaCore.
    
    Returns time series data for revenue breakdown by event kind.
    """
    from datetime import timedelta, datetime
    from decimal import Decimal
    from sqlalchemy import func, cast, Date
    from sqlmodel import select
    from app.treasury.models import TreasuryFlow

    # Range
    if range == "7d":
        since = datetime.utcnow() - timedelta(days=7)
    else:  # 30d
        since = datetime.utcnow() - timedelta(days=30)

    # Query: group by date and kind
    query = (
        select(
            cast(TreasuryFlow.ts, Date).label("date"),
            TreasuryFlow.kind,
            func.sum(TreasuryFlow.gross_amount).label("revenue"),
        )
        .where(TreasuryFlow.ts >= since)
        .group_by(cast(TreasuryFlow.ts, Date), TreasuryFlow.kind)
        .order_by(cast(TreasuryFlow.ts, Date))
    )

    result = await service.session.execute(query)
    rows = result.all()

    # Organize data
    dates = sorted(set(row[0] for row in rows))
    kinds = sorted(set(row[1] for row in rows))

    revenue_by_kind = {kind: [Decimal("0")] * len(dates) for kind in kinds}
    total_revenue = [Decimal("0")] * len(dates)

    for date, kind, revenue in rows:
        date_idx = dates.index(date)
        revenue_by_kind[kind][date_idx] = revenue
        total_revenue[date_idx] += revenue

    return RevenueChartData(
        labels=[d.strftime("%Y-%m-%d") for d in dates],
        revenue=total_revenue,
        app_breakdown=revenue_by_kind,
    )

