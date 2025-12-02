"""
NovaCore Treasury Service
Devletin Ekonomik Dolaşım Sistemi - İş Mantığı
"""
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy import func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.config import settings
from app.core.logging import get_logger
from app.treasury.models import SystemAccount, SystemAccountType, TreasuryFlow
from app.treasury.rules import POOL_ACCOUNT_TYPE_MAP, resolve_config
from app.treasury.schemas import (
    RevenueChartData,
    RouteRevenueRequest,
    SystemAccountOut,
    TreasuryFlowOut,
    TreasurySummary,
)
from app.wallet.models import Account, LedgerEntry, LedgerEntryType
from app.wallet.service import WalletService
from app.wallet.schemas import TransactionCreate

logger = get_logger("treasury")


class TreasuryService:
    """
    Treasury Service - Devletin ekonomik dolaşım sistemi.
    
    Her ekonomik işlemde:
    1. User → Performer net transfer
    2. Vergi → pool'lara dağılır (GROWTH, PERFORMER_POOL, DEV_FUND)
    3. Burn → token yakılır (supply düşer)
    4. TreasuryFlow log'u oluşturulur
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.wallet_service = WalletService(session)

    # ============ System Account Operations ============
    async def get_or_create_system_account(
        self, account_type: SystemAccountType, label: str, description: str | None = None
    ) -> SystemAccount:
        """Get or create system account."""
        result = await self.session.execute(
            select(SystemAccount).where(SystemAccount.account_type == account_type)
        )
        account = result.scalar_one_or_none()

        if not account:
            # Wallet account oluştur (system account için özel user_id)
            wallet_account = await self.wallet_service.get_or_create_account(
                settings.NCR_TREASURY_USER_ID, "NCR"
            )

            account = SystemAccount(
                account_type=account_type,
                wallet_account_id=wallet_account.id,
                label=label,
                description=description,
            )
            self.session.add(account)
            await self.session.flush()
            await self.session.refresh(account)

            logger.info(
                "system_account_created",
                account_type=account_type.value,
                label=label,
            )

        return account

    async def get_system_account_balance(
        self, account_type: SystemAccountType
    ) -> Decimal:
        """Get system account balance."""
        result = await self.session.execute(
            select(SystemAccount).where(SystemAccount.account_type == account_type)
        )
        account = result.scalar_one_or_none()

        if not account or not account.wallet_account_id:
            return Decimal("0")

        wallet_account_result = await self.session.execute(
            select(Account).where(Account.id == account.wallet_account_id)
        )
        wallet_account = wallet_account_result.scalar_one_or_none()

        return wallet_account.balance if wallet_account else Decimal("0")

    # ============ Revenue Routing ============
    async def route_revenue(self, request: RouteRevenueRequest) -> TreasuryFlowOut:
        """
        Ana revenue routing fonksiyonu.
        
        FlirtMarket, OnlyVips, PokerVerse → bu fonksiyonu çağırır.
        
        Flow:
        1. Config çöz (tax_rate + split)
        2. Tax hesapla
        3. User → Performer net transfer
        4. Tax → pool'lara dağıl
        5. Burn
        6. TreasuryFlow log'u oluştur
        
        Tüm işlemler tek composite transaction altında.
        """
        cfg = resolve_config(request.app, request.kind)

        # Hesaplamalar
        tax_amount = request.gross_amount * cfg.tax_rate
        net_to_performer = request.gross_amount - tax_amount

        # Pool dağılımları
        growth_amt = tax_amount * cfg.split["GROWTH"]
        perfpool_amt = tax_amount * cfg.split["PERFORMER_POOL"]
        dev_amt = tax_amount * cfg.split["DEV_FUND"]
        burn_amt = tax_amount * cfg.split["BURN"]

        # 1) User → Performer net transfer
        if request.performer_id:
            # User'dan çıkar
            await self.wallet_service.create_transaction(
                TransactionCreate(
                    user_id=request.user_id,
                    amount=request.gross_amount,
                    token="NCR",
                    type=LedgerEntryType.SPEND,
                    source_app=request.app.lower(),
                    performer_id=request.performer_id,
                    agency_id=request.agency_id,
                    reference_id=request.reference_id,
                    reference_type=request.reference_type,
                    metadata={
                        "kind": request.kind,
                        "gross_amount": str(request.gross_amount),
                        "tax_amount": str(tax_amount),
                        "net_to_performer": str(net_to_performer),
                        **request.metadata,
                    },
                )
            )

            # Performer'a ekle
            await self.wallet_service.create_transaction(
                TransactionCreate(
                    user_id=request.performer_id,
                    amount=net_to_performer,
                    token="NCR",
                    type=LedgerEntryType.EARN,
                    source_app=request.app.lower(),
                    related_user_id=request.user_id,
                    agency_id=request.agency_id,
                    reference_id=request.reference_id,
                    reference_type=request.reference_type,
                    metadata={
                        "kind": request.kind,
                        "from_user": request.user_id,
                        **request.metadata,
                    },
                )
            )

        # 2) Tax → pool'lara dağılır
        # GROWTH
        if growth_amt > 0:
            growth_account = await self.get_or_create_system_account(
                SystemAccountType.POOL_GROWTH,
                "Growth Fund",
                "Marketing ve büyüme kampanyaları için fon",
            )
            await self._credit_pool(
                growth_account,
                growth_amt,
                request.app,
                request.kind,
                request.user_id,
            )

        # PERFORMER_POOL
        if perfpool_amt > 0:
            perfpool_account = await self.get_or_create_system_account(
                SystemAccountType.POOL_PERFORMER,
                "Performer Bonus Pool",
                "Performer bonus dağıtımları için fon",
            )
            await self._credit_pool(
                perfpool_account,
                perfpool_amt,
                request.app,
                request.kind,
                request.user_id,
            )

        # DEV_FUND
        if dev_amt > 0:
            dev_account = await self.get_or_create_system_account(
                SystemAccountType.POOL_DEV,
                "Dev Fund",
                "Contributor ve developer ödemeleri için fon",
            )
            await self._credit_pool(
                dev_account,
                dev_amt,
                request.app,
                request.kind,
                request.user_id,
            )

        # 3) Burn
        if burn_amt > 0:
            await self._burn_tokens(
                burn_amt,
                request.app,
                request.kind,
                request.user_id,
            )

        # 4) TreasuryFlow log'u oluştur
        flow = TreasuryFlow(
            app=request.app.upper(),
            kind=request.kind.upper(),
            gross_amount=request.gross_amount,
            tax_amount=tax_amount,
            net_to_performer=net_to_performer,
            user_id=request.user_id,
            performer_id=request.performer_id,
            agency_id=request.agency_id,
            growth_amount=growth_amt,
            performer_pool_amount=perfpool_amt,
            dev_amount=dev_amt,
            burn_amount=burn_amt,
            reference_id=request.reference_id,
            reference_type=request.reference_type,
            metadata=request.metadata,
        )
        self.session.add(flow)
        await self.session.flush()
        await self.session.refresh(flow)

        logger.info(
            "revenue_routed",
            flow_id=flow.id,
            app=request.app,
            kind=request.kind,
            gross_amount=str(request.gross_amount),
            tax_amount=str(tax_amount),
            net_to_performer=str(net_to_performer),
            growth=str(growth_amt),
            perfpool=str(perfpool_amt),
            dev=str(dev_amt),
            burn=str(burn_amt),
        )

        return TreasuryFlowOut.model_validate(flow)

    async def _credit_pool(
        self,
        system_account: SystemAccount,
        amount: Decimal,
        app: str,
        kind: str,
        user_id: int,
    ) -> None:
        """Credit a pool account."""
        if not system_account.wallet_account_id:
            raise ValueError(f"System account {system_account.id} has no wallet account")

        # Treasury user_id'ye ekle (pool'lar treasury'de tutulur)
        await self.wallet_service.create_transaction(
            TransactionCreate(
                user_id=settings.NCR_TREASURY_USER_ID,
                amount=amount,
                token="NCR",
                type=LedgerEntryType.EARN,
                source_app=app.lower(),
                related_user_id=user_id,
                reference_id=system_account.id,
                reference_type="POOL_CREDIT",
                metadata={
                    "pool_type": system_account.account_type.value,
                    "kind": kind,
                },
            )
        )

    async def _burn_tokens(
        self, amount: Decimal, app: str, kind: str, user_id: int
    ) -> None:
        """Burn tokens (decrease total supply)."""
        # User'dan çıkar (burn)
        await self.wallet_service.create_transaction(
            TransactionCreate(
                user_id=user_id,
                amount=amount,
                token="NCR",
                type=LedgerEntryType.BURN,
                source_app=app.lower(),
                reference_type="TREASURY_BURN",
                metadata={
                    "kind": kind,
                    "burn_reason": "treasury_split",
                },
            )
        )

        logger.info(
            "tokens_burned",
            amount=str(amount),
            app=app,
            kind=kind,
            user_id=user_id,
        )

    # ============ Treasury Summary ============
    async def get_summary(self) -> TreasurySummary:
        """Get treasury summary for AuroraOS dashboard."""
        # Total treasury (tüm pool'ların toplamı)
        growth_balance = await self.get_system_account_balance(
            SystemAccountType.POOL_GROWTH
        )
        perfpool_balance = await self.get_system_account_balance(
            SystemAccountType.POOL_PERFORMER
        )
        dev_balance = await self.get_system_account_balance(SystemAccountType.POOL_DEV)

        total_treasury = growth_balance + perfpool_balance + dev_balance

        # Last 24h revenue
        yesterday = datetime.utcnow() - timedelta(days=1)
        revenue_24h_result = await self.session.execute(
            select(func.sum(TreasuryFlow.gross_amount)).where(
                TreasuryFlow.ts >= yesterday
            )
        )
        last_24h_revenue = revenue_24h_result.scalar() or Decimal("0")

        # Last 7d revenue
        week_ago = datetime.utcnow() - timedelta(days=7)
        revenue_7d_result = await self.session.execute(
            select(func.sum(TreasuryFlow.gross_amount)).where(
                TreasuryFlow.ts >= week_ago
            )
        )
        last_7d_revenue = revenue_7d_result.scalar() or Decimal("0")

        # Total burned
        burn_total_result = await self.session.execute(
            select(func.sum(TreasuryFlow.burn_amount))
        )
        total_burned = burn_total_result.scalar() or Decimal("0")

        # Revenue by app
        app_revenue_result = await self.session.execute(
            select(
                TreasuryFlow.app,
                func.sum(TreasuryFlow.gross_amount).label("total"),
            ).group_by(TreasuryFlow.app)
        )
        revenue_by_app = {
            row[0]: row[1] for row in app_revenue_result.all() if row[1]
        }

        # Revenue by kind
        kind_revenue_result = await self.session.execute(
            select(
                TreasuryFlow.kind,
                func.sum(TreasuryFlow.gross_amount).label("total"),
            ).group_by(TreasuryFlow.kind)
        )
        revenue_by_kind = {
            row[0]: row[1] for row in kind_revenue_result.all() if row[1]
        }

        return TreasurySummary(
            total_treasury=total_treasury,
            pools_balance={
                "POOL_GROWTH": growth_balance,
                "POOL_PERFORMER": perfpool_balance,
                "POOL_DEV": dev_balance,
            },
            last_24h_revenue=last_24h_revenue,
            last_7d_revenue=last_7d_revenue,
            total_burned=total_burned,
            revenue_by_app=revenue_by_app,
            revenue_by_kind=revenue_by_kind,
        )

    # ============ Flow History ============
    async def get_flows(
        self,
        range_str: str = "24h",
        app: str | None = None,
        kind: str | None = None,
        page: int = 1,
        per_page: int = 50,
    ) -> tuple[list[TreasuryFlowOut], int]:
        """Get treasury flows with filters."""
        query = select(TreasuryFlow)

        # Range filter
        if range_str == "24h":
            since = datetime.utcnow() - timedelta(days=1)
        elif range_str == "7d":
            since = datetime.utcnow() - timedelta(days=7)
        elif range_str == "30d":
            since = datetime.utcnow() - timedelta(days=30)
        else:
            since = None

        if since:
            query = query.where(TreasuryFlow.ts >= since)

        # App filter
        if app:
            query = query.where(TreasuryFlow.app == app.upper())

        # Kind filter
        if kind:
            query = query.where(TreasuryFlow.kind == kind.upper())

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.session.execute(count_query)).scalar() or 0

        # Fetch
        query = query.order_by(TreasuryFlow.ts.desc())
        query = query.offset((page - 1) * per_page).limit(per_page)

        result = await self.session.execute(query)
        flows = [TreasuryFlowOut.model_validate(f) for f in result.scalars().all()]

        return flows, total

