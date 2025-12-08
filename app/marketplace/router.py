# app/marketplace/router.py
"""
Marketplace Router - FastAPI Endpoints

KOBİ / Dashboard erişimi için API.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.marketplace.models import MarketplaceItem, MarketplacePurchase
from app.marketplace.service import MarketplaceService
from app.core.db import get_session
from app.consent.router import get_current_user_id
from app.identity.models import User
from app.core.security import get_current_user
from app.core.logging import get_logger
from app.telegram_gateway.router import get_telegram_account, verify_bridge_token
from sqlmodel import select

logger = get_logger("marketplace")


router = APIRouter(prefix="/api/v1/marketplace", tags=["marketplace"])


def get_marketplace_service(
    session: AsyncSession = Depends(get_session),
) -> MarketplaceService:
    """Marketplace service dependency."""
    return MarketplaceService(session)


@router.get(
    "/items",
    response_model=List[MarketplaceItem],
    summary="Marketplace item'lerini listele",
)
async def list_items(
    item_type: Optional[str] = Query(None, description="Item tipi filtresi"),
    limit: int = Query(20, ge=1, le=100, description="Sayfa boyutu"),
    offset: int = Query(0, ge=0, description="Sayfa offset'i"),
    status: Optional[str] = Query(None, description="Durum filtresi (default: active)"),
    service: MarketplaceService = Depends(get_marketplace_service),
):
    """
    Marketplace item'lerini listele.
    
    KOBİ / Creator dashboard için kullanılır.
    """
    try:
        return await service.list_items(
            item_type=item_type,
            limit=limit,
            offset=offset,
            status=status,
        )
    except Exception as e:
        # Database hatası veya tablo yoksa boş liste döndür
        logger = get_logger("marketplace")
        logger.error("marketplace_list_items_error", error=str(e))
        return []


@router.get(
    "/items/{item_id}",
    response_model=MarketplaceItem,
    summary="Tek bir marketplace item getir",
)
async def get_item(
    item_id: int,
    service: MarketplaceService = Depends(get_marketplace_service),
):
    """
    Tek bir marketplace item detayını getir.
    """
    try:
        return await service.get_item(item_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


async def get_user_from_telegram_or_auth(
    telegram_user_id: Optional[int] = Query(None, description="Telegram user ID (for bot)"),
    current_user: Optional[User] = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> User:
    """
    Telegram user ID varsa Telegram account'tan user'ı çek,
    yoksa authenticated user'ı kullan.
    """
    if telegram_user_id:
        account = await get_telegram_account(telegram_user_id, session)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Telegram account not found. Call /api/v1/telegram/link first.",
            )
        result = await session.execute(
            select(User).where(User.id == account.user_id)
        )
        return result.scalar_one()
    
    if current_user:
        return current_user
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
    )


@router.post(
    "/items/{item_id}/purchase",
    response_model=MarketplacePurchase,
    summary="Marketplace item satın al",
)
async def purchase_item(
    item_id: int,
    user: User = Depends(get_user_from_telegram_or_auth),
    service: MarketplaceService = Depends(get_marketplace_service),
):
    """
    Marketplace item satın al.
    
    Satın alma akışı:
    1. Item kontrolü
    2. Bakiye kontrolü
    3. NCR transfer (buyer → creator & treasury)
    4. Purchase kaydı oluştur
    
    Telegram bot için: ?telegram_user_id=123456
    Web için: JWT token ile authentication
    """
    try:
        return await service.purchase_item(
            buyer_id=user.id,
            item_id=item_id,
        )
    except ValueError as e:
        error_msg = str(e)
        # Duplicate purchase kontrolü
        if "zaten daha önce satın aldınız" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_msg,
            )
        # Yetersiz bakiye kontrolü
        elif "yetersiz bakiye" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=error_msg,
            )
        # Diğer hatalar
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        )


async def get_user_id_from_telegram_or_auth(
    telegram_user_id: Optional[int] = Query(None, description="Telegram user ID (for bot)"),
    current_user_id: Optional[int] = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> int:
    """Telegram user ID varsa account'tan user_id çek, yoksa authenticated user_id kullan."""
    if telegram_user_id:
        account = await get_telegram_account(telegram_user_id, session)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Telegram account not found. Call /api/v1/telegram/link first.",
            )
        return account.user_id
    
    if current_user_id:
        return current_user_id
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
    )


@router.get(
    "/my-items",
    response_model=List[MarketplaceItem],
    summary="Kendi item'lerimi getir",
)
async def get_my_items(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_id: int = Depends(get_user_id_from_telegram_or_auth),
    service: MarketplaceService = Depends(get_marketplace_service),
):
    """
    Giriş yapan kullanıcının marketplace item'lerini getir.
    
    Telegram bot için: ?telegram_user_id=123456
    Web için: JWT token ile authentication
    """
    return await service.get_creator_items(
        creator_id=user_id,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/my-sales",
    summary="Satış istatistiklerimi getir",
)
async def get_my_sales(
    user_id: int = Depends(get_user_id_from_telegram_or_auth),
    service: MarketplaceService = Depends(get_marketplace_service),
):
    """
    Giriş yapan kullanıcının satış istatistiklerini getir.
    
    Telegram bot için: ?telegram_user_id=123456
    Web için: JWT token ile authentication
    
    Returns:
        {
            "creator_id": int,
            "total_sales": int,
            "total_revenue_ncr": float,
            "purchases": List[MarketplacePurchase]
        }
    """
    return await service.get_creator_sales(creator_id=user_id)

