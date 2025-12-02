"""
NovaCore Wallet Schemas - Request/Response Models
"""
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

from app.wallet.models import LedgerEntryType


# ============ Account Schemas ============
class AccountResponse(BaseModel):
    """Account balance response."""

    id: int
    user_id: int
    token: str
    balance: Decimal
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BalanceResponse(BaseModel):
    """Simple balance response."""

    user_id: int
    token: str
    balance: Decimal


class MultiBalanceResponse(BaseModel):
    """Multiple token balances."""

    user_id: int
    balances: dict[str, Decimal]  # token -> balance


# ============ Transaction Schemas ============
class TransactionCreate(BaseModel):
    """Create a new ledger transaction."""

    user_id: int
    amount: Decimal = Field(..., gt=0, description="Positive amount")
    type: LedgerEntryType
    source_app: Literal["flirt", "onlyvips", "poker", "aurora", "admin"]
    token: str = "NCR"

    # Optional tracking
    related_user_id: int | None = None
    performer_id: int | None = None
    agency_id: int | None = None
    reference_id: str | None = None
    reference_type: str | None = None
    metadata: dict = Field(default_factory=dict)


class TransactionResponse(BaseModel):
    """Transaction response."""

    id: int
    user_id: int | None
    amount: Decimal
    token: str
    type: LedgerEntryType
    source_app: str
    balance_after: Decimal | None
    created_at: datetime

    class Config:
        from_attributes = True


class TransactionListResponse(BaseModel):
    """List of transactions."""

    transactions: list[TransactionResponse]
    total: int
    page: int
    per_page: int


# ============ Transfer Schema ============
class TransferRequest(BaseModel):
    """Transfer between users."""

    to_user_id: int
    amount: Decimal = Field(..., gt=0)
    token: str = "NCR"
    note: str | None = None


class TransferResponse(BaseModel):
    """Transfer result."""

    from_user_id: int
    to_user_id: int
    amount: Decimal
    token: str
    from_balance_after: Decimal
    to_balance_after: Decimal
    created_at: datetime


# ============ Treasury Schemas ============
class TreasuryBalance(BaseModel):
    """Treasury balance summary."""

    token: str
    balance: Decimal
    total_rake: Decimal
    total_fees: Decimal
    total_burns: Decimal


class TreasurySummary(BaseModel):
    """Full treasury summary."""

    balances: list[TreasuryBalance]
    total_ncr_in_circulation: Decimal
    total_users_with_balance: int

