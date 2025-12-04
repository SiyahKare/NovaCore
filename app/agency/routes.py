"""
Agency Routes - Aurora Panel için Viral Asset API
"""
from typing import List, Optional
from decimal import Decimal

from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.db import get_session
from app.core.security import get_admin_user, get_current_user_optional
from app.core.logging import get_logger
from app.identity.models import User
from app.core.config import settings
from typing import Optional
from app.agency.models import CreatorAsset, CreatorAssetStatus, AssetMediaType
from app.agency.services.revenue_share_service import RevenueShareService

logger = get_logger("agency")

router = APIRouter(prefix="/api/v1/agency", tags=["agency"])


@router.get(
    "/assets/viral",
    response_model=List[CreatorAsset],
    summary="Ajans için seçilmiş viral içerik havuzunu getir",
)
async def list_viral_assets(
    limit: int = Query(50, ge=1, le=200),
    media_type: Optional[AssetMediaType] = Query(None),
    only_available: bool = Query(True, description="Kampanyada kullanılmamış olsun"),
    min_score: float = Query(90.0, ge=0.0, le=100.0, description="Minimum AI score"),
    session: AsyncSession = Depends(get_session),
    current_user: Optional[User] = Depends(get_current_user_optional),  # Optional auth for dev
):
    """
    AURORA CONTACT dashboard'u bu endpoint üzerinden:
    
    - Kullanıma hazır "ajanslık" içerikleri görür
    - Filtreleyip, kampanyaya atar
    
    Development mode'da token opsiyonel, production'da admin token gerekli.
    """
    # Production'da admin kontrolü
    if settings.is_prod and (not current_user or not current_user.is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    stmt = select(CreatorAsset).where(
        CreatorAsset.status.in_(
            [CreatorAssetStatus.CURATED, CreatorAssetStatus.APPROVED]
        )
    )
    
    if only_available:
        stmt = stmt.where(CreatorAsset.used_in_campaign == False)  # noqa: E712
    
    if media_type:
        stmt = stmt.where(CreatorAsset.media_type == media_type)
    
    stmt = stmt.where(CreatorAsset.ai_total_score >= min_score)
    
    stmt = stmt.order_by(CreatorAsset.ai_total_score.desc())
    stmt = stmt.limit(limit)
    
    result = await session.execute(stmt)
    assets = result.scalars().all()
    
    return list(assets)


@router.patch(
    "/assets/{asset_id}/use",
    response_model=CreatorAsset,
    summary="Asset'i kampanyada kullan",
)
async def use_asset_in_campaign(
    asset_id: int,
    client_id: Optional[int] = Query(None, description="Agency client ID"),
    session: AsyncSession = Depends(get_session),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Asset'i kampanyada kullanıldı olarak işaretle.
    
    Development mode'da token opsiyonel, production'da admin token gerekli.
    """
    # Production'da admin kontrolü
    if settings.is_prod and (not current_user or not current_user.is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    result = await session.execute(
        select(CreatorAsset).where(CreatorAsset.id == asset_id)
    )
    asset = result.scalar_one_or_none()
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found",
        )
    
    asset.used_in_campaign = True
    asset.status = CreatorAssetStatus.USED_IN_CAMPAIGN
    
    if client_id:
        asset.agency_client_id = client_id
    
    session.add(asset)
    await session.commit()
    await session.refresh(asset)
    
    return asset


@router.patch(
    "/assets/{asset_id}/approve",
    response_model=CreatorAsset,
    summary="Asset'i operatör onayından geçir",
)
async def approve_asset(
    asset_id: int,
    session: AsyncSession = Depends(get_session),
    _admin: User = Depends(get_admin_user),
):
    """Asset'i operatör onayından geçir."""
    result = await session.execute(
        select(CreatorAsset).where(CreatorAsset.id == asset_id)
    )
    asset = result.scalar_one_or_none()
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found",
        )
    
    asset.status = CreatorAssetStatus.APPROVED
    session.add(asset)
    await session.commit()
    await session.refresh(asset)
    
    return asset


@router.patch(
    "/assets/{asset_id}/feature",
    response_model=CreatorAsset,
    summary="Asset'i featured yap",
)
async def feature_asset(
    asset_id: int,
    is_featured: bool = Query(True),
    session: AsyncSession = Depends(get_session),
    _admin: User = Depends(get_admin_user),
):
    """Asset'i featured yap veya kaldır."""
    result = await session.execute(
        select(CreatorAsset).where(CreatorAsset.id == asset_id)
    )
    asset = result.scalar_one_or_none()
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found",
        )
    
    asset.is_featured = is_featured
    session.add(asset)
    await session.commit()
    await session.refresh(asset)
    
    return asset


class CampaignRevenueRequest(BaseModel):
    """Kampanya gelir kaydı request."""
    revenue: float = Field(gt=0, description="Toplam fiat geliri (TRY)")
    fiat_currency: str = Field(default="TRY", description="Para birimi")


class RevenueShareResponse(BaseModel):
    """Revenue share dağıtım sonucu."""
    success: bool
    message: str
    creator_ncr_paid: float
    creator_fiat_share: float
    treasury_fiat: float
    agency_operations_fiat: float
    total_fiat_processed: float
    ncr_price_try: float


@router.post(
    "/assets/{asset_id}/record-revenue",
    response_model=RevenueShareResponse,
    status_code=status.HTTP_200_OK,
    summary="Kampanya Gelirini Kaydet ve Paylaştır",
)
async def record_campaign_revenue(
    asset_id: int,
    payload: CampaignRevenueRequest,
    session: AsyncSession = Depends(get_session),
    _admin: User = Depends(get_admin_user),  # Admin yetkisi zorunlu
):
    """
    Belirli bir CreatorAsset'ten elde edilen fiat geliri kaydeder ve
    paylaşım kurallarına göre (20/40/40) Creator'a NCR ödemesi yapar.
    
    - Creator: %20 (NCR olarak)
    - Treasury: %40 (Fiat)
    - Agency Operations: %40 (Fiat)
    """
    if payload.revenue <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Gelir pozitif olmalıdır.",
        )
    
    try:
        share_service = RevenueShareService(session)
        results = await share_service.distribute_campaign_revenue(
            asset_id=asset_id,
            total_fiat_revenue=Decimal(str(payload.revenue)),
            fiat_currency=payload.fiat_currency,
        )
        
        return RevenueShareResponse(
            success=True,
            message="Gelir dağıtımı başarıyla tamamlandı.",
            creator_ncr_paid=float(results["creator_ncr"]),
            creator_fiat_share=float(results["creator_fiat"]),
            treasury_fiat=float(results["treasury_fiat"]),
            agency_operations_fiat=float(results["agency_operations_fiat"]),
            total_fiat_processed=float(results["total_fiat_processed"]),
            ncr_price_try=float(results["ncr_price_try"]),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger = get_logger("agency")
        logger.error(f"Revenue share error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gelir dağıtımı sırasında beklenmeyen hata.",
        )
