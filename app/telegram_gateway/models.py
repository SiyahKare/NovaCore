"""
Telegram Gateway Models
Telegram bot ↔ NovaCore bridge için veri modelleri
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class TelegramAccount(SQLModel, table=True):
    """
    Telegram kullanıcısı ↔ NovaCore User eşlemesi.
    
    Her Telegram kullanıcısı bir User ile bağlıdır.
    İlk bot etkileşiminde otomatik oluşturulur.
    """
    __tablename__ = "telegram_accounts"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True, unique=True)
    telegram_user_id: int = Field(index=True, unique=True)
    username: str | None = Field(default=None, index=True, max_length=255)
    first_name: str | None = Field(default=None, max_length=255)
    last_name: str | None = Field(default=None, max_length=255)
    
    # Bot interaction tracking
    first_seen_at: datetime = Field(default_factory=datetime.utcnow)
    last_seen_at: datetime = Field(default_factory=datetime.utcnow)
    last_command: str | None = Field(default=None, max_length=100)
    
    # MiniApp / WebApp integration
    webapp_init_data: dict | None = Field(
        default=None,
        sa_column=Column(JSONB, default={})
    )  # Telegram WebApp initData (encrypted)
    
    # Metadata
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

