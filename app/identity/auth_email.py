"""
Email-based Authentication for Aurora
"""
from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
import bcrypt

from app.core.security import create_access_token
from app.identity.models import User
from app.identity.schemas import AuthResponse, UserResponse


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


async def authenticate_email(
    session: AsyncSession,
    email: str,
    password: str,
) -> AuthResponse:
    """
    Authenticate user with email and password.
    
    Returns AuthResponse with JWT token if credentials are valid.
    Raises HTTPException if authentication fails.
    """
    # Find user by email
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email account not set up. Please register first.",
        )

    # Verify password
    if not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Create JWT token
    from app.core.config import settings
    access_token = create_access_token(user_id=user.id)

    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user),
    )


async def register_email(
    session: AsyncSession,
    email: str,
    password: str,
    display_name: Optional[str] = None,
) -> AuthResponse:
    """
    Register a new user with email and password.
    
    Returns AuthResponse with JWT token.
    Raises HTTPException if email already exists.
    """
    # Check if email already exists
    result = await session.execute(select(User).where(User.email == email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Generate synthetic telegram_id for web users (900M+ range)
    # Only if telegram_id is not already set (for email users)
    import hashlib
    import time
    email_hash = int(hashlib.md5(email.encode()).hexdigest()[:8], 16) % 1000000000
    telegram_id = 900000000 + (email_hash % 100000000)

    # Check for collision and retry if needed
    max_retries = 5
    for attempt in range(max_retries):
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        if not result.scalar_one_or_none():
            break
        # Add attempt number and timestamp to make it more unique
        telegram_id = 900000000 + ((email_hash + int(time.time() * 1000) + attempt) % 100000000)

    # Create new user
    user = User(
        telegram_id=telegram_id,
        email=email,
        password_hash=hash_password(password),
        display_name=display_name or email.split("@")[0],
        telegram_data={"source": "email", "email": email},
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    # Create JWT token
    from app.core.config import settings
    access_token = create_access_token(user_id=user.id)

    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user),
    )

