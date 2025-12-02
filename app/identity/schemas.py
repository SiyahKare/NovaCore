"""
NovaCore Identity Schemas - Request/Response Models
"""
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


# ============ Email Auth ============
class EmailLoginRequest(BaseModel):
    """Email login request."""
    
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")


class EmailRegisterRequest(BaseModel):
    """Email registration request."""
    
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    display_name: str | None = Field(None, max_length=255, description="Optional display name")


# ============ Telegram Auth ============
class TelegramAuthPayload(BaseModel):
    """
    Telegram WebApp initData payload.
    
    Gerçek implementasyonda Telegram imzasını verify edecek.
    Şimdilik dummy payload kabul ediyor.
    """

    telegram_id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    photo_url: str | None = None
    auth_date: int | None = None
    hash: str | None = None  # Telegram imzası


class AuthResponse(BaseModel):
    """Auth response with JWT token."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserResponse"


# ============ User ============
class UserResponse(BaseModel):
    """User response model."""

    id: int
    telegram_id: int | None
    email: str | None
    username: str | None
    display_name: str | None
    ton_wallet: str | None
    is_performer: bool
    is_agency_owner: bool
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """User update request."""

    display_name: str | None = Field(None, max_length=255)
    username: str | None = Field(None, max_length=255)
    ton_wallet: str | None = Field(None, max_length=255)


class UserCreate(BaseModel):
    """Internal user creation (from Telegram auth)."""

    telegram_id: int
    username: str | None = None
    display_name: str | None = None


# Fix forward reference
AuthResponse.model_rebuild()

