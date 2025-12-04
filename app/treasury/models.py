"""
NovaCore Treasury Models
Devletin Ekonomik Dolaşım Sistemi - Modeller
"""
from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import uuid4

from sqlalchemy import Column, Numeric, String, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class SystemAccountType(str, Enum):
    """
    Sistem hesap tipleri - devletin farklı kasaları.
    
    USER            → normal vatandaş
    PERFORMER       → şovcu / creator
    AGENCY_TREASURY → ajansın iç kasası (Betül Agency vs)
    STATE_TREASURY  → devlet ana hazinesi
    POOL_GROWTH     → Growth / marketing fonu
    POOL_PERFORMER  → Performer bonus fonu
    POOL_DEV        → Contributor / Dev fonu
    POOL_BURN       → Yakılan tutar log'u (cüzdan değil, muhasebe)
    """
    USER = "USER"
    PERFORMER = "PERFORMER"
    AGENCY_TREASURY = "AGENCY_TREASURY"
    STATE_TREASURY = "STATE_TREASURY"
    POOL_GROWTH = "POOL_GROWTH"
    POOL_PERFORMER = "POOL_PERFORMER"
    POOL_DEV = "POOL_DEV"
    POOL_BURN = "POOL_BURN"


class SystemAccount(SQLModel, table=True):
    """
    Sistem hesabı - devletin özel kasaları.
    
    Her sistem hesabı bir wallet Account'a bağlıdır.
    Treasury modülü bu hesapları özel olarak yönetir.
    """
    __tablename__ = "system_accounts"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    account_type: SystemAccountType = Field(index=True)
    
    # Wallet Account referansı
    wallet_account_id: int | None = Field(
        default=None,
        foreign_key="accounts.id",
        unique=True,
        index=True
    )
    
    # Metadata
    label: str = Field(max_length=255)  # "Growth Fund", "Dev Pool", vs.
    description: str | None = Field(default=None, max_length=1000)
    
    # Agency referansı (eğer AGENCY_TREASURY ise)
    agency_id: int | None = Field(default=None, foreign_key="agencies.id", index=True)
    
    # Metadata (additional context)
    # Note: Python field is 'meta' to avoid SQLAlchemy reserved keyword conflict
    # DB column remains 'metadata' for backward compatibility
    meta: dict = Field(
        default_factory=dict,
        sa_column=Column("metadata", JSONB, default={}),
    )
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "account_type": "POOL_GROWTH",
                "wallet_account_id": 1,
                "label": "Growth Fund",
                "description": "Marketing ve büyüme kampanyaları için fon",
            }
        }


class TreasuryFlow(SQLModel, table=True):
    """
    Treasury akış logu - her ekonomik işlem burada.
    
    Bu tablo → NovaCore'da Treasury heatmap / kaynak breakdown'ı besler.
    """
    __tablename__ = "treasury_flows"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    ts: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    # Event bilgileri
    app: str = Field(index=True, max_length=50)  # FLIRTMARKET, ONLYVIPS, POKER, AURORA
    kind: str = Field(index=True, max_length=50)  # TIP, MESSAGE, SUBSCRIPTION, RAKE, etc.
    
    # Tutarlar
    gross_amount: Decimal = Field(
        sa_column=Column(Numeric(precision=18, scale=8), nullable=False)
    )
    tax_amount: Decimal = Field(
        sa_column=Column(Numeric(precision=18, scale=8), nullable=False)
    )
    net_to_performer: Decimal = Field(
        sa_column=Column(Numeric(precision=18, scale=8), nullable=False)
    )
    
    # İlgili kullanıcılar
    user_id: int | None = Field(default=None, foreign_key="users.id", index=True)
    performer_id: int | None = Field(default=None, foreign_key="users.id", index=True)
    agency_id: int | None = Field(default=None, foreign_key="agencies.id", index=True)
    
    # Pool dağılımları
    growth_amount: Decimal = Field(
        default=Decimal("0"),
        sa_column=Column(Numeric(precision=18, scale=8), nullable=False)
    )
    performer_pool_amount: Decimal = Field(
        default=Decimal("0"),
        sa_column=Column(Numeric(precision=18, scale=8), nullable=False)
    )
    dev_amount: Decimal = Field(
        default=Decimal("0"),
        sa_column=Column(Numeric(precision=18, scale=8), nullable=False)
    )
    burn_amount: Decimal = Field(
        default=Decimal("0"),
        sa_column=Column(Numeric(precision=18, scale=8), nullable=False)
    )
    
    # Metadata (additional context)
    # Note: Python field is 'meta' to avoid SQLAlchemy reserved keyword conflict
    # DB column remains 'metadata' for backward compatibility
    meta: dict = Field(
        default_factory=dict,
        sa_column=Column("metadata", JSONB, default={}),
    )
    
    # Reference tracking
    reference_id: str | None = Field(default=None, index=True, max_length=100)
    reference_type: str | None = Field(default=None, max_length=50)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "app": "FLIRTMARKET",
                "kind": "TIP",
                "gross_amount": "100.00000000",
                "tax_amount": "20.00000000",
                "net_to_performer": "80.00000000",
                "growth_amount": "8.00000000",
                "performer_pool_amount": "6.00000000",
                "dev_amount": "4.00000000",
                "burn_amount": "2.00000000",
            }
        }

