"""
Dev-only Identity endpoints (synthetic users & tokens)
"""
import hashlib

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_session
from app.core.logging import get_logger
from app.core.security import create_access_token
from app.identity.service import IdentityService

router = APIRouter(prefix="/api/v1/dev", tags=["dev"])
logger = get_logger("dev_identity")


def _synthetic_telegram_id(seed: str) -> int:
    """Produce deterministic 900M+ telegram_id for web/dev users."""
    digest = hashlib.md5(seed.encode("utf-8")).hexdigest()
    return 900_000_000 + (int(digest[:8], 16) % 100_000_000)


def _normalize_username(seed: str) -> str:
    """Lowercase + trim username to fit DB constraints."""
    slug = seed.strip().lower().replace(" ", "_")
    return slug[:255] if slug else "dev_user"


@router.post(
    "/token",
    summary="Dev mode token oluştur",
)
async def create_dev_token(
    user_id: str = Query(..., min_length=3, max_length=255, description="Synthetic user identifier"),
    session: AsyncSession = Depends(get_session),
):
    """Return a JWT for synthetic dev/testing users."""
    if not settings.is_dev:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Dev token endpoint disabled outside dev environment",
        )

    telegram_id = _synthetic_telegram_id(user_id)
    display_name = user_id[:255]
    username = _normalize_username(user_id)

    service = IdentityService(session)
    user, created = await service.get_or_create_user(
        telegram_id=telegram_id,
        username=username,
        display_name=display_name,
        telegram_data={"source": "web_dev", "user_id": user_id},
    )
    await session.commit()
    await session.refresh(user)

    token = create_access_token(user_id=user.id)
    logger.info(
        "dev_token_issued",
        user_id=user.id,
        telegram_id=telegram_id,
        synthetic_user_id=user_id,
        created=created,
    )

    return {
        "token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "telegram_id": user.telegram_id,
        "display_name": user.display_name,
        "created": created,
    }


@router.post(
    "/token/telegram",
    summary="Telegram user_id ile token oluştur (dev mode)",
)
async def create_token_for_telegram_user(
    telegram_user_id: int = Query(..., description="Telegram user ID"),
    session: AsyncSession = Depends(get_session),
):
    """
    Telegram user_id'si ile token oluştur.
    
    Bu endpoint, Telegram'da quest tamamlayan kullanıcının web panelinde
    aynı user_id ile giriş yapabilmesi için kullanılır.
    """
    if not settings.is_dev:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Dev token endpoint disabled outside dev environment",
        )
    
    # TelegramAccount üzerinden User'ı bul
    from app.telegram_gateway.models import TelegramAccount
    from app.identity.models import User
    from sqlmodel import select
    
    account_stmt = select(TelegramAccount).where(
        TelegramAccount.telegram_user_id == telegram_user_id
    )
    account_result = await session.execute(account_stmt)
    account = account_result.scalar_one_or_none()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Telegram account not found for telegram_user_id: {telegram_user_id}. Call /api/v1/telegram/link first.",
        )
    
    # User'ı çek
    user_stmt = select(User).where(User.id == account.user_id)
    user_result = await session.execute(user_stmt)
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found for account.user_id: {account.user_id}",
        )
    
    token = create_access_token(user_id=user.id)
    logger.info(
        "dev_telegram_token_issued",
        user_id=user.id,
        telegram_user_id=telegram_user_id,
        telegram_account_id=account.id,
    )
    
    return {
        "token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "telegram_id": user.telegram_id,
        "telegram_user_id": telegram_user_id,
        "display_name": user.display_name,
        "username": user.username,
    }

