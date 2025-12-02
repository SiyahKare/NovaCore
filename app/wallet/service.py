"""
NovaCore Wallet Service - NCR Ledger Logic
"""
from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.config import settings
from app.core.logging import get_logger
from app.wallet.models import Account, LedgerEntry, LedgerEntryType
from app.wallet.schemas import (
    BalanceResponse,
    TransactionCreate,
    TransactionResponse,
    TransferRequest,
    TransferResponse,
    TreasuryBalance,
    TreasurySummary,
)

logger = get_logger("wallet")


class WalletService:
    """Wallet service for NCR ledger operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ============ Account Operations ============
    async def get_account(self, user_id: int, token: str = "NCR") -> Account | None:
        """Get user account for a specific token."""
        result = await self.session.execute(
            select(Account).where(Account.user_id == user_id, Account.token == token)
        )
        return result.scalar_one_or_none()

    async def get_or_create_account(self, user_id: int, token: str = "NCR") -> Account:
        """Get existing account or create new one with zero balance."""
        account = await self.get_account(user_id, token)

        if not account:
            account = Account(user_id=user_id, token=token, balance=Decimal("0"))
            self.session.add(account)
            await self.session.flush()
            await self.session.refresh(account)

            logger.info("account_created", user_id=user_id, token=token)

        return account

    async def get_balance(self, user_id: int, token: str = "NCR") -> BalanceResponse:
        """Get user's balance for a token."""
        account = await self.get_or_create_account(user_id, token)
        return BalanceResponse(
            user_id=user_id,
            token=token,
            balance=account.balance,
        )

    # ============ Transaction Operations ============
    async def create_transaction(self, tx: TransactionCreate) -> TransactionResponse:
        """
        Create a ledger entry and update account balance.
        
        This is the core transaction method used by all apps.
        """
        account = await self.get_or_create_account(tx.user_id, tx.token)

        # Calculate new balance based on type
        if tx.type in [LedgerEntryType.EARN, LedgerEntryType.DEPOSIT, LedgerEntryType.REWARD]:
            # Increase balance
            new_balance = account.balance + tx.amount
        elif tx.type in [
            LedgerEntryType.SPEND,
            LedgerEntryType.WITHDRAW,
            LedgerEntryType.BURN,
            LedgerEntryType.FEE,
            LedgerEntryType.RAKE,
        ]:
            # Decrease balance
            if account.balance < tx.amount:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient balance. Current: {account.balance}, Required: {tx.amount}",
                )
            new_balance = account.balance - tx.amount
        elif tx.type == LedgerEntryType.TRANSFER:
            # Transfer out - decrease balance
            if account.balance < tx.amount:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient balance for transfer. Current: {account.balance}",
                )
            new_balance = account.balance - tx.amount
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown transaction type: {tx.type}",
            )

        # Create ledger entry
        entry = LedgerEntry(
            user_id=tx.user_id,
            amount=tx.amount,
            token=tx.token,
            type=tx.type,
            source_app=tx.source_app,
            related_user_id=tx.related_user_id,
            performer_id=tx.performer_id,
            agency_id=tx.agency_id,
            reference_id=tx.reference_id,
            reference_type=tx.reference_type,
            meta=tx.metadata,  # Schema uses 'metadata', model uses 'meta'
            balance_after=new_balance,
        )
        self.session.add(entry)

        # Update account balance
        account.balance = new_balance
        account.updated_at = datetime.utcnow()
        self.session.add(account)

        await self.session.flush()
        await self.session.refresh(entry)

        logger.info(
            "transaction_created",
            entry_id=entry.id,
            user_id=tx.user_id,
            type=tx.type.value,
            amount=str(tx.amount),
            source_app=tx.source_app,
            balance_after=str(new_balance),
        )

        # Handle treasury operations for RAKE/FEE/BURN
        if tx.type in [LedgerEntryType.RAKE, LedgerEntryType.FEE, LedgerEntryType.BURN]:
            await self._credit_treasury(tx.amount, tx.type, tx.source_app, tx.metadata)  # Schema field name

        return TransactionResponse.model_validate(entry)

    async def _credit_treasury(
        self,
        amount: Decimal,
        entry_type: LedgerEntryType,
        source_app: str,
        metadata: dict,
    ) -> None:
        """Credit treasury account with rake/fee/burn."""
        treasury_account = await self.get_or_create_account(
            settings.NCR_TREASURY_USER_ID, "NCR"
        )

        treasury_entry = LedgerEntry(
            user_id=settings.NCR_TREASURY_USER_ID,
            amount=amount,
            token="NCR",
            type=LedgerEntryType.EARN,  # Treasury "earns" the rake/fee
            source_app=source_app,
            meta={
                "original_type": entry_type.value,
                **metadata,
            },
            balance_after=treasury_account.balance + amount,
        )
        self.session.add(treasury_entry)

        treasury_account.balance += amount
        treasury_account.updated_at = datetime.utcnow()
        self.session.add(treasury_account)

        await self.session.flush()

        logger.info(
            "treasury_credited",
            amount=str(amount),
            type=entry_type.value,
            source_app=source_app,
            new_balance=str(treasury_account.balance),
        )

    # ============ Transfer Operations ============
    async def transfer(
        self,
        from_user_id: int,
        request: TransferRequest,
    ) -> TransferResponse:
        """Transfer tokens between users."""
        if from_user_id == request.to_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot transfer to yourself",
            )

        # Get both accounts
        from_account = await self.get_or_create_account(from_user_id, request.token)
        to_account = await self.get_or_create_account(request.to_user_id, request.token)

        # Check balance
        if from_account.balance < request.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient balance. Current: {from_account.balance}",
            )

        # Create entries
        now = datetime.utcnow()

        from_entry = LedgerEntry(
            user_id=from_user_id,
            amount=request.amount,
            token=request.token,
            type=LedgerEntryType.TRANSFER,
            source_app="wallet",
            related_user_id=request.to_user_id,
            meta={"note": request.note, "direction": "out"},
            balance_after=from_account.balance - request.amount,
        )

        to_entry = LedgerEntry(
            user_id=request.to_user_id,
            amount=request.amount,
            token=request.token,
            type=LedgerEntryType.EARN,  # Receiving is an earn
            source_app="wallet",
            related_user_id=from_user_id,
            meta={"note": request.note, "direction": "in", "is_transfer": True},
            balance_after=to_account.balance + request.amount,
        )

        self.session.add(from_entry)
        self.session.add(to_entry)

        # Update balances
        from_account.balance -= request.amount
        from_account.updated_at = now
        to_account.balance += request.amount
        to_account.updated_at = now

        self.session.add(from_account)
        self.session.add(to_account)

        await self.session.flush()

        logger.info(
            "transfer_completed",
            from_user_id=from_user_id,
            to_user_id=request.to_user_id,
            amount=str(request.amount),
            token=request.token,
        )

        return TransferResponse(
            from_user_id=from_user_id,
            to_user_id=request.to_user_id,
            amount=request.amount,
            token=request.token,
            from_balance_after=from_account.balance,
            to_balance_after=to_account.balance,
            created_at=now,
        )

    # ============ History ============
    async def get_transactions(
        self,
        user_id: int,
        page: int = 1,
        per_page: int = 20,
        token: str | None = None,
        entry_type: LedgerEntryType | None = None,
    ) -> tuple[list[LedgerEntry], int]:
        """Get user's transaction history."""
        query = select(LedgerEntry).where(LedgerEntry.user_id == user_id)

        if token:
            query = query.where(LedgerEntry.token == token)
        if entry_type:
            query = query.where(LedgerEntry.type == entry_type)

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.session.execute(count_query)).scalar() or 0

        # Fetch
        query = query.order_by(LedgerEntry.created_at.desc())
        query = query.offset((page - 1) * per_page).limit(per_page)

        result = await self.session.execute(query)
        entries = list(result.scalars().all())

        return entries, total

    # ============ Treasury ============
    async def get_treasury_summary(self) -> TreasurySummary:
        """Get treasury summary."""
        treasury_account = await self.get_or_create_account(
            settings.NCR_TREASURY_USER_ID, "NCR"
        )

        # Calculate totals from ledger
        rake_result = await self.session.execute(
            select(func.sum(LedgerEntry.amount)).where(
                LedgerEntry.user_id == settings.NCR_TREASURY_USER_ID,
                LedgerEntry.meta["original_type"].astext == "rake",  # DB column is 'metadata', Python field is 'meta'
            )
        )
        total_rake = rake_result.scalar() or Decimal("0")

        fee_result = await self.session.execute(
            select(func.sum(LedgerEntry.amount)).where(
                LedgerEntry.user_id == settings.NCR_TREASURY_USER_ID,
                LedgerEntry.meta["original_type"].astext == "fee",  # DB column is 'metadata', Python field is 'meta'
            )
        )
        total_fees = fee_result.scalar() or Decimal("0")

        burn_result = await self.session.execute(
            select(func.sum(LedgerEntry.amount)).where(
                LedgerEntry.user_id == settings.NCR_TREASURY_USER_ID,
                LedgerEntry.meta["original_type"].astext == "burn",  # DB column is 'metadata', Python field is 'meta'
            )
        )
        total_burns = burn_result.scalar() or Decimal("0")

        # Total NCR in circulation
        circ_result = await self.session.execute(
            select(func.sum(Account.balance)).where(
                Account.token == "NCR",
                Account.user_id != settings.NCR_TREASURY_USER_ID,
            )
        )
        total_circulation = circ_result.scalar() or Decimal("0")

        # Users with balance
        users_result = await self.session.execute(
            select(func.count(Account.id)).where(
                Account.token == "NCR",
                Account.balance > 0,
            )
        )
        users_with_balance = users_result.scalar() or 0

        return TreasurySummary(
            balances=[
                TreasuryBalance(
                    token="NCR",
                    balance=treasury_account.balance,
                    total_rake=total_rake,
                    total_fees=total_fees,
                    total_burns=total_burns,
                )
            ],
            total_ncr_in_circulation=total_circulation,
            total_users_with_balance=users_with_balance,
        )

