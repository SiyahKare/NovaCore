"""
NovaCore Wallet Models - NCR Ledger
"""
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import Column, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class Account(SQLModel, table=True):
    """
    User account for token balances.
    
    Her user'ın NCR hesabı var.
    Gelecekte farklı token'lar da eklenebilir (şimdilik sadece NCR).
    """

    __tablename__ = "accounts"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    token: str = Field(default="NCR", index=True, max_length=10)
    balance: Decimal = Field(
        default=Decimal("0"),
        sa_column=Column(Numeric(precision=18, scale=8), nullable=False, default=0),
    )

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class DailyTreasuryStat(SQLModel, table=True):
    """
    Günlük Treasury istatistiği.
    
    Her gün için:
    - O günün limit'i (snapshot)
    - Şu ana kadar dağıtılan toplam NCR
    """
    __tablename__ = "daily_treasury_stats"
    
    id: int | None = Field(default=None, primary_key=True)
    day: date = Field(index=True, unique=True)
    
    # O gün için hedef/limit (snapshot)
    limit_ncr: float = Field(default=0.0)
    # Şu ana kadar dağıtılan toplam NCR
    issued_ncr: float = Field(default=0.0)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class NCRMarketState(SQLModel, table=True):
    """
    NCR fiyatı ve piyasa metrikleri.
    
    Tek satırlık global bir kayıt (id=1).
    """
    __tablename__ = "ncr_market_state"
    
    id: int | None = Field(default=None, primary_key=True)
    
    current_price_try: float = Field(default=1.0)
    last_price_try: float = Field(default=1.0)
    
    ema_coverage: float = Field(default=1.0)  # 1.0 = %100 teminat
    ema_flow_index: float = Field(default=0.0)  # pozitif = sistemden fazla çıkış / baskı
    
    # Basit telemetri
    last_updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "token": "NCR",
                "balance": "1000.00000000",
            }
        }


class LedgerEntryType(str, Enum):
    """Types of ledger entries."""

    EARN = "earn"  # Kazanç (quest, referral, vs.)
    SPEND = "spend"  # Harcama (coin satın alma, show, vs.)
    TRANSFER = "transfer"  # User arası transfer
    RAKE = "rake"  # Poker rake (treasury'e)
    FEE = "fee"  # Platform fee (treasury'e)
    BURN = "burn"  # Aurora AI usage burn
    DEPOSIT = "deposit"  # Dışarıdan yatırma
    WITHDRAW = "withdraw"  # Dışarı çekme
    REWARD = "reward"  # Bonus, airdrop, vs.


class LedgerEntry(SQLModel, table=True):
    """
    NCR Ledger Entry - her işlem burada.
    
    Immutable log - hiçbir zaman güncellenmez veya silinmez.
    Balance hesaplaması Account tablosunda tutulur (performance için).
    """

    __tablename__ = "ledger_entries"

    id: int | None = Field(default=None, primary_key=True)

    # User (None for treasury operations)
    user_id: int | None = Field(default=None, foreign_key="users.id", index=True)

    # Transaction details
    amount: Decimal = Field(
        sa_column=Column(Numeric(precision=18, scale=8), nullable=False)
    )
    token: str = Field(default="NCR", max_length=10)
    type: LedgerEntryType = Field(index=True)

    # Source tracking
    source_app: str = Field(index=True, max_length=50)  # flirt, onlyvips, poker, aurora

    # Related entities (for tracking)
    related_user_id: int | None = Field(default=None, index=True)  # Transfer için karşı taraf
    performer_id: int | None = Field(default=None, index=True)  # Performer için
    agency_id: int | None = Field(default=None, index=True)  # Agency için

    # Reference tracking
    reference_id: str | None = Field(default=None, index=True, max_length=100)
    reference_type: str | None = Field(default=None, max_length=50)

    # Metadata (event details, etc.)
    # Note: Python field is 'meta' to avoid SQLAlchemy reserved keyword conflict
    # DB column remains 'metadata' for backward compatibility
    meta: dict = Field(
        default_factory=dict,
        sa_column=Column("metadata", JSONB, default={}),
    )

    # Balance after this transaction (for audit trail)
    balance_after: Decimal | None = Field(
        default=None,
        sa_column=Column(Numeric(precision=18, scale=8), nullable=True),
    )

    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "amount": "100.00000000",
                "token": "NCR",
                "type": "earn",
                "source_app": "flirt",
                "meta": {"event_type": "quest_complete"},  # Python field name
            }
        }

