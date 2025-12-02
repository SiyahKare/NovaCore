"""
NovaCore Identity Service - User & Auth Logic
"""
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.config import settings
from app.core.logging import get_logger
from app.core.security import create_access_token
from app.identity.models import User
from app.identity.schemas import AuthResponse, TelegramAuthPayload, UserResponse, UserUpdate

logger = get_logger("identity")


class IdentityService:
    """Identity service for user management and authentication."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_id(self, user_id: int) -> User | None:
        """Get user by internal ID."""
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_user_by_telegram_id(self, telegram_id: int) -> User | None:
        """Get user by Telegram ID."""
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def create_user(
        self,
        telegram_id: int | None = None,
        email: str | None = None,
        password_hash: str | None = None,
        username: str | None = None,
        display_name: str | None = None,
        telegram_data: dict | None = None,
    ) -> User:
        """Create a new user."""
        user = User(
            telegram_id=telegram_id,
            email=email,
            password_hash=password_hash,
            username=username,
            display_name=display_name or username or (email.split("@")[0] if email else None),
            telegram_data=telegram_data or {},
        )
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)

        logger.info(
            "user_created",
            user_id=user.id,
            telegram_id=telegram_id,
            email=email,
            username=username,
        )

        return user

    async def update_user(self, user: User, update_data: UserUpdate) -> User:
        """Update user fields."""
        update_dict = update_data.model_dump(exclude_unset=True)

        for field, value in update_dict.items():
            setattr(user, field, value)

        user.updated_at = datetime.utcnow()
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)

        logger.info("user_updated", user_id=user.id, fields=list(update_dict.keys()))

        return user

    async def get_or_create_user(
        self,
        telegram_id: int,
        username: str | None = None,
        display_name: str | None = None,
        telegram_data: dict | None = None,
    ) -> tuple[User, bool]:
        """Get existing user or create new one. Returns (user, created)."""
        user = await self.get_user_by_telegram_id(telegram_id)

        if user:
            # Update username/display_name if changed
            updated = False
            if username and user.username != username:
                user.username = username
                updated = True
            if display_name and user.display_name != display_name:
                user.display_name = display_name
                updated = True
            if telegram_data:
                user.telegram_data = telegram_data
                updated = True

            if updated:
                user.updated_at = datetime.utcnow()
                self.session.add(user)
                await self.session.flush()

            return user, False

        # Create new user
        user = await self.create_user(
            telegram_id=telegram_id,
            username=username,
            display_name=display_name,
            telegram_data=telegram_data,
        )
        return user, True

    async def authenticate_telegram(self, payload: TelegramAuthPayload) -> AuthResponse:
        """
        Authenticate user via Telegram WebApp initData.
        
        TODO: v0.2'de gerçek Telegram imza doğrulaması eklenecek.
        Şimdilik payload'daki telegram_id ile user oluştur/getir.
        """
        # TODO: Verify Telegram hash signature
        # verify_telegram_signature(payload, settings.TELEGRAM_BOT_TOKEN)

        # Get display name from Telegram data
        display_name = payload.first_name
        if payload.last_name:
            display_name = f"{payload.first_name} {payload.last_name}"

        # Get or create user
        user, created = await self.get_or_create_user(
            telegram_id=payload.telegram_id,
            username=payload.username,
            display_name=display_name,
            telegram_data={
                "photo_url": payload.photo_url,
                "auth_date": payload.auth_date,
            },
        )

        # Create JWT token
        access_token = create_access_token(user_id=user.id)

        logger.info(
            "telegram_auth",
            user_id=user.id,
            telegram_id=payload.telegram_id,
            created=created,
        )

        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.JWT_EXPIRE_MINUTES * 60,
            user=UserResponse.model_validate(user),
        )

