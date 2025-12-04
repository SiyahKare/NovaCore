"""
Admin Economy Dashboard Routes
NasipQuest Economy Dashboard API endpoints
"""
from datetime import datetime, timedelta, date
from typing import Optional
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import func, and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from pydantic import BaseModel

from app.core.db import get_session
from app.core.security import get_admin_user
from app.identity.models import User
from app.wallet.models import DailyTreasuryStat, NCRMarketState, Account, LedgerEntry, LedgerEntryType
from app.abuse.models import UserRiskProfile
from app.wallet.pricing import get_current_ncr_price


router = APIRouter(prefix="/api/v1/admin/economy", tags=["admin", "economy"])


class TreasuryDailyStat(BaseModel):
    """Günlük Treasury istatistiği."""
    day: date
    limit_ncr: float
    issued_ncr: float
    load_ratio: float
    remaining_ncr: float


class NCRPriceHistory(BaseModel):
    """NCR fiyat geçmişi."""
    timestamp: datetime
    price_try: float
    ema_coverage: float
    ema_flow_index: float


class EconomySummary(BaseModel):
    """Ekonomi özeti."""
    # NCR Market
    current_price_try: float
    price_change_24h: float
    price_change_7d: float
    
    # Treasury
    treasury_reserves_fiat: float  # Placeholder - gerçek değer başka yerden gelecek
    ncr_outstanding: float
    coverage_ratio: float
    
    # Daily Stats
    daily_limit_ncr: float
    daily_issued_ncr: float
    daily_load_ratio: float
    
    # Flow (24h)
    net_mint_24h: float
    net_burn_24h: float
    net_redemption_24h: float
    
    # Risk Distribution
    risk_score_distribution: dict[str, int]
    
    # User Stats
    total_users: int
    active_users_24h: int


@router.get(
    "/summary",
    response_model=EconomySummary,
    summary="Ekonomi özeti (Dashboard ana ekranı)",
    dependencies=[Depends(get_admin_user)],
)
async def get_economy_summary(
    session: AsyncSession = Depends(get_session),
):
    """
    Dashboard için ekonomi özeti.
    
    Tüm kritik metrikleri tek response'da döner.
    """
    # NCR Price
    current_price = await get_current_ncr_price(session)
    
    # Treasury Daily Stat
    today = date.today()
    result = await session.execute(
        select(DailyTreasuryStat).where(DailyTreasuryStat.day == today)
    )
    daily_stat = result.scalar_one_or_none()
    
    if not daily_stat:
        daily_limit = 200_000.0  # Default
        daily_issued = 0.0
    else:
        daily_limit = daily_stat.limit_ncr
        daily_issued = daily_stat.issued_ncr
    
    daily_load = (daily_issued / daily_limit) if daily_limit > 0 else 0.0
    
    # NCR Outstanding (total balance in all accounts)
    accounts_result = await session.execute(
        select(func.sum(Account.balance)).where(Account.token == "NCR")
    )
    ncr_outstanding = float(accounts_result.scalar_one() or 0)
    
    # Flow (24h)
    since_24h = datetime.utcnow() - timedelta(hours=24)
    
    mint_result = await session.execute(
        select(func.sum(LedgerEntry.amount)).where(
            and_(
                LedgerEntry.type == LedgerEntryType.EARN,
                LedgerEntry.source_app == "telegram_task",
                LedgerEntry.created_at >= since_24h,
            )
        )
    )
    net_mint_24h = float(mint_result.scalar_one() or 0)
    
    burn_result = await session.execute(
        select(func.sum(LedgerEntry.amount)).where(
            and_(
                LedgerEntry.type == LedgerEntryType.BURN,
                LedgerEntry.created_at >= since_24h,
            )
        )
    )
    net_burn_24h = float(burn_result.scalar_one() or 0)
    
    # Redemption (withdrawals) - placeholder
    net_redemption_24h = 0.0
    
    # Coverage (placeholder - gerçek değer başka yerden gelecek)
    treasury_reserves_fiat = 300_000.0  # Placeholder
    coverage_ratio = (treasury_reserves_fiat / (ncr_outstanding * current_price)) if (ncr_outstanding * current_price) > 0 else 2.0
    
    # Risk Distribution
    risk_profiles_result = await session.execute(select(UserRiskProfile))
    profiles = risk_profiles_result.scalars().all()
    
    risk_dist = {
        "0-2": 0,
        "3-5": 0,
        "6-8": 0,
        "9-10": 0,
    }
    for profile in profiles:
        score = profile.risk_score
        if score <= 2.0:
            risk_dist["0-2"] += 1
        elif score <= 5.0:
            risk_dist["3-5"] += 1
        elif score <= 8.0:
            risk_dist["6-8"] += 1
        else:
            risk_dist["9-10"] += 1
    
    # User Stats (placeholder)
    total_users = len(profiles)  # Simplified
    active_users_24h = total_users  # Placeholder
    
    # Price changes (placeholder - gerçek değer history'den gelecek)
    price_change_24h = 0.0
    price_change_7d = 0.0
    
    return EconomySummary(
        current_price_try=current_price,
        price_change_24h=price_change_24h,
        price_change_7d=price_change_7d,
        treasury_reserves_fiat=treasury_reserves_fiat,
        ncr_outstanding=ncr_outstanding,
        coverage_ratio=coverage_ratio,
        daily_limit_ncr=daily_limit,
        daily_issued_ncr=daily_issued,
        daily_load_ratio=daily_load,
        net_mint_24h=net_mint_24h,
        net_burn_24h=net_burn_24h,
        net_redemption_24h=net_redemption_24h,
        risk_score_distribution=risk_dist,
        total_users=total_users,
        active_users_24h=active_users_24h,
    )


@router.get(
    "/treasury/daily",
    response_model=list[TreasuryDailyStat],
    summary="Günlük Treasury istatistikleri (son N gün)",
    dependencies=[Depends(get_admin_user)],
)
async def get_treasury_daily_stats(
    days: int = Query(30, ge=1, le=365, description="Son N gün"),
    session: AsyncSession = Depends(get_session),
):
    """
    Günlük Treasury istatistikleri.
    
    Dashboard'da grafik için kullanılır.
    """
    since = date.today() - timedelta(days=days)
    
    result = await session.execute(
        select(DailyTreasuryStat)
        .where(DailyTreasuryStat.day >= since)
        .order_by(DailyTreasuryStat.day.desc())
    )
    stats = result.scalars().all()
    
    daily_stats = []
    for stat in stats:
        load_ratio = (stat.issued_ncr / stat.limit_ncr) if stat.limit_ncr > 0 else 0.0
        daily_stats.append(
            TreasuryDailyStat(
                day=stat.day,
                limit_ncr=stat.limit_ncr,
                issued_ncr=stat.issued_ncr,
                load_ratio=load_ratio,
                remaining_ncr=stat.limit_ncr - stat.issued_ncr,
            )
        )
    
    return daily_stats


@router.get(
    "/ncr/price-history",
    response_model=list[NCRPriceHistory],
    summary="NCR fiyat geçmişi",
    dependencies=[Depends(get_admin_user)],
)
async def get_ncr_price_history(
    days: int = Query(30, ge=1, le=365, description="Son N gün"),
    session: AsyncSession = Depends(get_session),
):
    """
    NCR fiyat geçmişi.
    
    Not: Şu an sadece mevcut state döner. 
    Gelecekte price history tablosu eklendiğinde bu endpoint genişletilecek.
    """
    # Placeholder - gerçek implementasyonda price_history tablosu olacak
    result = await session.execute(select(NCRMarketState).limit(1))
    state = result.scalar_one_or_none()
    
    if not state:
        return []
    
    # Şimdilik sadece mevcut state'i döndür
    return [
        NCRPriceHistory(
            timestamp=state.last_updated_at,
            price_try=state.current_price_try,
            ema_coverage=state.ema_coverage,
            ema_flow_index=state.ema_flow_index,
        )
    ]


@router.get(
    "/ncr/current",
    summary="Mevcut NCR fiyatı ve metrikleri",
    dependencies=[Depends(get_admin_user)],
)
async def get_ncr_current(
    session: AsyncSession = Depends(get_session),
):
    """Mevcut NCR fiyatı ve market state."""
    result = await session.execute(select(NCRMarketState).limit(1))
    state = result.scalar_one_or_none()
    
    if not state:
        current_price = await get_current_ncr_price(session)
        return {
            "current_price_try": current_price,
            "last_price_try": current_price,
            "ema_coverage": 1.0,
            "ema_flow_index": 0.0,
            "last_updated_at": datetime.utcnow().isoformat(),
        }
    
    return {
        "current_price_try": state.current_price_try,
        "last_price_try": state.last_price_try,
        "ema_coverage": state.ema_coverage,
        "ema_flow_index": state.ema_flow_index,
        "last_updated_at": state.last_updated_at.isoformat(),
    }

