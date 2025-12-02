"""
NovaCore Identity Models - User & SSO
"""
from datetime import datetime

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """
    User model - tek doğruluk kaynağı.
    
    Telegram ID → internal user_id mapping.
    Tüm uygulamalar (FlirtMarket, OnlyVips, PokerVerse, Aurora) bu user_id'yi kullanır.
    """

    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    telegram_id: int | None = Field(default=None, index=True, unique=True)
    email: str | None = Field(default=None, index=True, unique=True, max_length=255)
    password_hash: str | None = Field(default=None)  # bcrypt hash for email auth
    username: str | None = Field(default=None, index=True, max_length=255)
    display_name: str | None = Field(default=None, max_length=255)

    # TON wallet for NCR payout
    ton_wallet: str | None = Field(default=None, max_length=255)

    # Role flags
    is_performer: bool = Field(default=False)
    is_agency_owner: bool = Field(default=False)
    is_admin: bool = Field(default=False)

    # Metadata
    telegram_data: dict = Field(default_factory=dict, sa_column=Column(JSONB, default={}))

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "telegram_id": 123456789,
                "username": "johndoe",
                "display_name": "John Doe",
                "is_performer": False,
                "is_agency_owner": False,
                "is_admin": False,
            }
        }

