"""
Identity Routes - User Management & Authentication
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.db import get_session
from app.core.security import get_current_user, create_access_token
from app.identity.models import User
from app.identity.service import IdentityService
from app.identity.schemas import (
    UserResponse,
    AuthResponse,
    EmailLoginRequest,
    EmailRegisterRequest,
    TelegramAuthPayload,
)
from app.telegram_gateway.models import TelegramAccount

router = APIRouter(prefix="/api/v1/identity", tags=["identity"])


# ============ Authentication ============

@router.post(
    "/register",
    response_model=AuthResponse,
    summary="Email ile kayıt ol",
)
async def register(
    payload: EmailRegisterRequest,
    session: AsyncSession = Depends(get_session),
) -> AuthResponse:
    """Email ve şifre ile yeni kullanıcı oluştur."""
    service = IdentityService(session)
    return await service.register_email(payload)


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Email ile giriş yap",
)
async def login(
    payload: EmailLoginRequest,
    session: AsyncSession = Depends(get_session),
) -> AuthResponse:
    """Email ve şifre ile giriş yap."""
    service = IdentityService(session)
    return await service.login_email(payload)


@router.post(
    "/telegram/auth",
    response_model=AuthResponse,
    summary="Telegram WebApp ile giriş yap",
)
async def telegram_auth(
    payload: TelegramAuthPayload,
    session: AsyncSession = Depends(get_session),
) -> AuthResponse:
    """
    Telegram WebApp initData ile giriş yap.
    
    Telegram MiniApp'ten gelen initData ile kullanıcı doğrulanır.
    """
    service = IdentityService(session)
    return await service.authenticate_telegram(payload)


# ============ User Profile ============

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Giriş yapan kullanıcının profil bilgisi",
)
async def get_me(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> UserResponse:
    """Giriş yapan kullanıcının profil bilgisi."""
    return UserResponse.model_validate(current_user)


# ============ Telegram Linking ============

@router.post(
    "/telegram/link",
    response_model=UserResponse,
    summary="Mevcut web kullanıcısını Telegram hesabı ile bağla",
)
async def link_telegram_account(
    telegram_user_id: int = Query(..., description="Telegram user ID"),
    telegram_username: str | None = Query(None, description="Telegram username"),
    telegram_first_name: str | None = Query(None, description="Telegram first name"),
    telegram_last_name: str | None = Query(None, description="Telegram last name"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> UserResponse:
    """
    Mevcut web kullanıcısını Telegram hesabı ile bağla.
    
    Bu endpoint web'den authenticated kullanıcının Telegram hesabını bağlamak için kullanılır.
    Telegram MiniApp'ten gelen bilgilerle mevcut user'ın telegram_id'si güncellenir.
    """
    # Check if telegram_user_id is already linked to another user
    existing_account = await session.execute(
        select(TelegramAccount).where(
            TelegramAccount.telegram_user_id == telegram_user_id
        )
    )
    existing_account_obj = existing_account.scalar_one_or_none()
    
    if existing_account_obj:
        if existing_account_obj.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bu Telegram hesabı başka bir kullanıcıya bağlı",
            )
        # Already linked to this user, just update
        existing_account_obj.username = telegram_username
        existing_account_obj.first_name = telegram_first_name
        existing_account_obj.last_name = telegram_last_name
        existing_account_obj.last_seen_at = datetime.utcnow()
        session.add(existing_account_obj)
    else:
        # Create new TelegramAccount
        telegram_account = TelegramAccount(
            user_id=current_user.id,
            telegram_user_id=telegram_user_id,
            username=telegram_username,
            first_name=telegram_first_name,
            last_name=telegram_last_name,
        )
        session.add(telegram_account)
    
    # Update user's telegram_id
    current_user.telegram_id = telegram_user_id
    if telegram_username and not current_user.username:
        current_user.username = telegram_username
    if telegram_first_name and not current_user.display_name:
        current_user.display_name = telegram_first_name
    
    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)
    
    return UserResponse.model_validate(current_user)


@router.get(
    "/telegram/status",
    summary="Telegram hesabı bağlantı durumu",
)
async def get_telegram_status(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Kullanıcının Telegram hesabı bağlantı durumunu kontrol et.
    """
    telegram_account = await session.execute(
        select(TelegramAccount).where(
            TelegramAccount.user_id == current_user.id
        )
    )
    account = telegram_account.scalar_one_or_none()
    
    return {
        "is_linked": account is not None,
        "telegram_user_id": current_user.telegram_id,
        "telegram_username": account.username if account else None,
        "telegram_display_name": f"{account.first_name or ''} {account.last_name or ''}".strip() if account else None,
    }
