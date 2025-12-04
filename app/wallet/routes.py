"""
NovaCore Wallet Routes - NCR Ledger Endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.security import get_admin_user, get_current_user
from app.identity.models import User
from app.wallet.models import LedgerEntryType
from app.wallet.schemas import (
    BalanceResponse,
    TransactionCreate,
    TransactionListResponse,
    TransactionResponse,
    TransferRequest,
    TransferResponse,
    TreasurySummary,
)
from app.wallet.service import WalletService

router = APIRouter(prefix="/api/v1/wallet", tags=["wallet"])


# ============ Balance Endpoints ============
@router.get(
    "/me",
    response_model=BalanceResponse,
    summary="Get My Balance",
    description="Get the current user's NCR balance.",
)
async def get_my_balance(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    token: str = Query("NCR", description="Token symbol"),
) -> BalanceResponse:
    """Get current user's balance."""
    service = WalletService(session)
    return await service.get_balance(current_user.id, token)


@router.get(
    "/balance/{user_id}",
    response_model=BalanceResponse,
    summary="Get User Balance",
    description="Get a specific user's balance (internal use).",
)
async def get_user_balance(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    token: str = Query("NCR", description="Token symbol"),
) -> BalanceResponse:
    """Get user's balance by ID."""
    service = WalletService(session)
    return await service.get_balance(user_id, token)


# ============ Transaction Endpoints ============
@router.post(
    "/tx",
    response_model=TransactionResponse,
    summary="Create Transaction",
    description="Create a new ledger entry (used by FlirtMarket, OnlyVips, PokerVerse, Aurora).",
)
async def create_transaction(
    tx: TransactionCreate,
    session: AsyncSession = Depends(get_session),
) -> TransactionResponse:
    """
    Create a ledger transaction.
    
    This is the primary endpoint for all apps to record NCR movements:
    - FlirtMarket: SPEND for coin purchases, EARN for performer tips
    - OnlyVips: SPEND for premium content
    - PokerVerse: RAKE for poker rake
    - Aurora: BURN for AI usage
    """
    service = WalletService(session)
    return await service.create_transaction(tx)


@router.get(
    "/me/transactions",
    response_model=TransactionListResponse,
    summary="My Transaction History",
    description="Get current user's transaction history.",
)
async def get_my_transactions(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    token: str | None = Query(None, description="Filter by token"),
    type: LedgerEntryType | None = Query(None, description="Filter by type"),
) -> TransactionListResponse:
    """Get current user's transaction history."""
    service = WalletService(session)
    entries, total = await service.get_transactions(
        current_user.id, page, per_page, token, type
    )

    return TransactionListResponse(
        transactions=[TransactionResponse.model_validate(e) for e in entries],
        total=total,
        page=page,
        per_page=per_page,
    )


# ============ Transfer Endpoint ============
@router.post(
    "/transfer",
    response_model=TransferResponse,
    summary="Transfer NCR",
    description="Transfer NCR to another user.",
)
async def transfer(
    request: TransferRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> TransferResponse:
    """
    Transfer NCR to another user.
    
    **Enforcement:** This action is checked against the user's CP regime.
    RESTRICTED and LOCKDOWN users cannot transfer funds.
    """
    # Aurora Justice Enforcement Check
    from app.justice.router import JusticeService
    from app.justice.enforcement import check_action_allowed
    from app.justice.policy import Action
    
    justice_service = JusticeService(session)
    cp_state = await justice_service.get_cp(str(current_user.id))
    check_action_allowed(cp_state, Action.WITHDRAW_FUNDS)
    
    service = WalletService(session)
    return await service.transfer(current_user.id, request)


# ============ Treasury (Admin) ============
@router.get(
    "/treasury",
    response_model=TreasurySummary,
    summary="Treasury Summary",
    description="Get treasury summary (admin only).",
)
async def get_treasury_summary(
    _admin: User = Depends(get_admin_user),
    session: AsyncSession = Depends(get_session),
) -> TreasurySummary:
    """Get treasury summary - admin only."""
    service = WalletService(session)
    return await service.get_treasury_summary()

