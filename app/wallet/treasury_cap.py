"""
Treasury Cap System
Günlük NCR dağıtım limitini kontrol eden ve yük oranına göre damping uygulayan sistem.
"""
from datetime import date, datetime
from typing import Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.config import settings
from app.wallet.models import DailyTreasuryStat


async def _get_or_create_today_stat(session: AsyncSession) -> DailyTreasuryStat:
    """Bugünün Treasury stat'ını getir veya oluştur."""
    today = date.today()
    
    result = await session.execute(
        select(DailyTreasuryStat).where(DailyTreasuryStat.day == today)
    )
    stat = result.scalar_one_or_none()
    
    if stat is None:
        stat = DailyTreasuryStat(
            day=today,
            limit_ncr=settings.TREASURY_DAILY_NCR_LIMIT,
            issued_ncr=0.0,
        )
        session.add(stat)
        await session.commit()
        await session.refresh(stat)
    
    return stat


def _get_damping_multiplier(load_ratio: float) -> float:
    """
    Load ratio'ya göre damping multiplier döner.
    
    Args:
        load_ratio: 0.0–∞ (issued / limit)
    
    Returns:
        Multiplier (0.0–1.0)
    """
    # Threshold'lar küçükten büyüğe sırala
    thresholds = sorted(settings.TREASURY_DAMPING_TABLE.items(), key=lambda x: x[0])
    
    for threshold, mult in thresholds:
        if load_ratio <= threshold:
            return mult
    
    # Her şeyden sonra taşmışsa: minimum ödeme
    return 0.05  # %5'lik can simidi


async def apply_treasury_cap(
    session: AsyncSession,
    pre_treasury_ncr: float,
) -> Tuple[float, dict]:
    """
    RewardEngine'den çıkan NCR'ı Treasury limitlerine göre keser.
    
    Args:
        session: Database session
        pre_treasury_ncr: Treasury öncesi NCR miktarı
    
    Returns:
        (adjusted_ncr, metadata)
    """
    if pre_treasury_ncr <= 0:
        return 0.0, {
            "treasury_applied": False,
            "reason": "non_positive_reward",
        }
    
    stat = await _get_or_create_today_stat(session)
    
    # Eğer limit 0 veya negatifse tüm dağıtım kapalıdır (panic mode)
    if stat.limit_ncr <= 0:
        return 0.0, {
            "treasury_applied": True,
            "reason": "zero_daily_limit",
            "load_ratio": 1.0,
            "multiplier": 0.0,
        }
    
    # Projected load ratio
    projected_issued = stat.issued_ncr + pre_treasury_ncr
    load_ratio = projected_issued / stat.limit_ncr
    
    # Get damping multiplier
    multiplier = _get_damping_multiplier(load_ratio)
    
    # Apply multiplier
    adjusted_ncr = round(pre_treasury_ncr * multiplier, 2)
    
    # Eğer multiplier çok düşükse, "simge ödül" gibi davranabilirsin
    if adjusted_ncr < 0.01:
        adjusted_ncr = 0.0
    
    # DB update
    stat.issued_ncr += adjusted_ncr
    stat.updated_at = datetime.utcnow()
    session.add(stat)
    await session.commit()
    await session.refresh(stat)
    
    meta = {
        "treasury_applied": True,
        "load_ratio": round(load_ratio, 4),
        "multiplier": multiplier,
        "pre_treasury_ncr": pre_treasury_ncr,
        "final_ncr": adjusted_ncr,
        "limit_ncr": stat.limit_ncr,
        "issued_ncr": stat.issued_ncr,
    }
    
    return adjusted_ncr, meta

