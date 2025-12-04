"""
NCR Pricing System
Fiyat stabilizasyon algoritması - Coverage + Flow bazlı fiyat ayarlama
"""
from datetime import datetime
from typing import Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.config import settings
from app.wallet.models import NCRMarketState


async def _get_or_init_market_state(session: AsyncSession) -> NCRMarketState:
    """Market state'i getir veya oluştur."""
    result = await session.execute(
        select(NCRMarketState).order_by(NCRMarketState.id).limit(1)
    )
    state = result.scalar_one_or_none()
    
    if state is None:
        state = NCRMarketState(
            current_price_try=settings.NCR_BASE_PRICE_TRY,
            last_price_try=settings.NCR_BASE_PRICE_TRY,
            ema_coverage=1.0,
            ema_flow_index=0.0,
        )
        session.add(state)
        await session.commit()
        await session.refresh(state)
    
    return state


def _ema(prev: float, new: float, alpha: float) -> float:
    """Exponential Moving Average."""
    return (alpha * new) + ((1 - alpha) * prev)


def compute_coverage_ratio(
    *,
    treasury_reserves_fiat: float,
    ncr_outstanding: float,
    reference_price: float,
) -> float:
    """
    Coverage ratio hesapla.
    
    coverage = (kasa / (yükümlülük))
    yükümlülük ≈ ncr_outstanding * reference_price
    """
    if ncr_outstanding <= 0 or reference_price <= 0:
        # NCR yoksa coverage sonsuz gibi, ama pratikte 2.0 gibi yüksek bir rakam verebiliriz
        return 2.0
    
    liability = ncr_outstanding * reference_price
    if liability <= 0:
        return 2.0
    
    return treasury_reserves_fiat / liability


def compute_flow_index(
    *,
    net_mint_24h: float,
    net_burn_24h: float,
    net_redemption_24h: float,
    anchor: float = 100_000.0,  # sistem hacmine göre tune edilir
) -> float:
    """
    Flow index hesapla.
    
    Pozitif değer = sistem için baskı (daha çok ödeme yükü)
    Negatif değer = rahatlama (yakım vs.)
    """
    if anchor <= 0:
        anchor = 1.0
    net_out = net_mint_24h - net_burn_24h - net_redemption_24h
    return net_out / anchor


async def update_ncr_price(
    session: AsyncSession,
    *,
    treasury_reserves_fiat: float,
    ncr_outstanding: float,
    net_mint_24h: float,
    net_burn_24h: float,
    net_redemption_24h: float,
) -> Tuple[float, dict]:
    """
    NCR fiyatını Treasury ve akıma göre günceller.
    
    Bu fonksiyon günde 1 kere cron'la tetiklenebilir.
    
    Args:
        session: Database session
        treasury_reserves_fiat: Kasadaki fiat / stablecoin
        ncr_outstanding: Tüm cüzdanlardaki toplam NCR (liability)
        net_mint_24h: Son 24 saatte basılan NCR
        net_burn_24h: Son 24 saatte yakılan NCR
        net_redemption_24h: Son 24 saatte fiata çevrilen NCR
    
    Returns:
        (new_price, metadata)
    """
    state = await _get_or_init_market_state(session)
    
    base_price = settings.NCR_BASE_PRICE_TRY
    
    # 1) Coverage ve Flow hesapla
    raw_coverage = compute_coverage_ratio(
        treasury_reserves_fiat=treasury_reserves_fiat,
        ncr_outstanding=ncr_outstanding,
        reference_price=state.current_price_try or base_price,
    )
    
    raw_flow = compute_flow_index(
        net_mint_24h=net_mint_24h,
        net_burn_24h=net_burn_24h,
        net_redemption_24h=net_redemption_24h,
    )
    
    # 2) EMA smoothing
    alpha = settings.NCR_SMOOTHING_ALPHA
    ema_cov = _ema(state.ema_coverage, raw_coverage, alpha)
    ema_flow = _ema(state.ema_flow_index, raw_flow, alpha)
    
    # 3) Coverage bazlı düzeltme
    target = settings.NCR_TARGET_COVERAGE
    cov_diff = ema_cov - target  # pozitif = fazla teminat, negatif = zayıf
    
    cov_adjust = settings.NCR_K_COVERAGE * cov_diff
    # Örn: coverage 1.4, target 1.2, diff 0.2 → +0.08 (~%8 artış baskısı)
    
    # 4) Flow bazlı düzeltme
    # Pozitif flow_index → daha çok NCR yükümlülüğü → fiyatı hafif bastır
    flow_adjust = -settings.NCR_K_FLOW * ema_flow
    
    # 5) Kombine ayarlama
    total_adjust = cov_adjust + flow_adjust
    
    # Hard clamp: bir günde belli bir %'den fazla oynama olmasın
    max_daily_change = 0.15  # ±%15
    if total_adjust > max_daily_change:
        total_adjust = max_daily_change
    elif total_adjust < -max_daily_change:
        total_adjust = -max_daily_change
    
    # 6) Yeni fiyat
    proposed_price = state.current_price_try * (1 + total_adjust)
    
    # Fiyat bantlarını uygula
    min_p = settings.NCR_MIN_PRICE_TRY
    max_p = settings.NCR_MAX_PRICE_TRY
    new_price = max(min_p, min(max_p, proposed_price))
    
    # 7) State güncelle
    state.last_price_try = state.current_price_try
    state.current_price_try = round(new_price, 4)
    state.ema_coverage = round(ema_cov, 4)
    state.ema_flow_index = round(ema_flow, 6)
    state.last_updated_at = datetime.utcnow()
    
    session.add(state)
    await session.commit()
    await session.refresh(state)
    
    meta = {
        "old_price": state.last_price_try,
        "new_price": state.current_price_try,
        "raw_coverage": raw_coverage,
        "ema_coverage": ema_cov,
        "raw_flow": raw_flow,
        "ema_flow": ema_flow,
        "cov_adjust": cov_adjust,
        "flow_adjust": flow_adjust,
        "total_adjust": total_adjust,
    }
    
    return state.current_price_try, meta


async def get_current_ncr_price(session: AsyncSession) -> float:
    """Mevcut NCR fiyatını getir."""
    state = await _get_or_init_market_state(session)
    return state.current_price_try

