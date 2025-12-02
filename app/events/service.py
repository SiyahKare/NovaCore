"""
NovaCore Events Service - App Event Processing

Flow:
1. App (FlirtMarket/OnlyVips/Poker/Aurora) → POST /events/...
2. events modülü:
   - wallet.tx işler
   - xp_loyalty.event işler
   - nova_credit.process_event çağırır
3. nova_credit:
   - ΔNovaCredit hesaplar
   - CitizenScore günceller
"""
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.agency.service import AgencyService
from app.core.logging import get_logger
from app.events.schemas import (
    AuroraEvent,
    AuroraEventType,
    EventResult,
    FlirtEvent,
    FlirtEventType,
    OnlyVipsEvent,
    OnlyVipsEventType,
    PokerEvent,
    PokerEventType,
)
from app.nova_credit.service import NovaCreditService
from app.wallet.models import LedgerEntryType
from app.wallet.schemas import TransactionCreate
from app.wallet.service import WalletService
from app.xp_loyalty.schemas import XpEventCreate
from app.xp_loyalty.service import XpLoyaltyService

logger = get_logger("events")


class EventService:
    """Event processing service."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.wallet = WalletService(session)
        self.xp = XpLoyaltyService(session)
        self.agency = AgencyService(session)
        self.credit = NovaCreditService(session)  # NovaCredit engine

    # ============ FlirtMarket Events ============
    async def handle_flirt_event(self, event: FlirtEvent) -> EventResult:
        """Process FlirtMarket event."""
        ncr_change = Decimal("0")
        xp_change = 0
        revenue_split = None

        if event.event_type in [
            FlirtEventType.COIN_SPENT,
            FlirtEventType.SHOW_PURCHASED,
            FlirtEventType.TIP_SENT,
            FlirtEventType.GIFT_SENT,
        ]:
            # User spends NCR
            tx = await self.wallet.create_transaction(
                TransactionCreate(
                    user_id=event.user_id,
                    amount=event.amount,
                    type=LedgerEntryType.SPEND,
                    source_app="flirt",
                    performer_id=event.performer_id,
                    metadata={
                        "event_type": event.event_type.value,
                        **event.metadata,
                    },
                )
            )
            ncr_change = -event.amount

            # Revenue split if performer involved
            if event.performer_id:
                split = await self.agency.calculate_revenue_split(
                    event.performer_id, event.amount
                )
                revenue_split = {
                    "performer_amount": str(split.performer_amount),
                    "agency_amount": str(split.agency_amount),
                    "treasury_amount": str(split.treasury_amount),
                }

                # Record performer earnings
                await self.agency.record_performer_earnings(
                    event.performer_id, int(event.amount)
                )

            # XP bonus
            xp_amount = event.xp_bonus or self._calculate_flirt_xp(event)
            if xp_amount > 0:
                await self.xp.create_xp_event(
                    XpEventCreate(
                        user_id=event.user_id,
                        amount=xp_amount,
                        event_type=f"flirt_{event.event_type.value.lower()}",
                        source_app="flirt",
                        metadata=event.metadata,
                    )
                )
                xp_change = xp_amount

        elif event.event_type == FlirtEventType.BOOST_USED:
            # Boost is a smaller spend
            tx = await self.wallet.create_transaction(
                TransactionCreate(
                    user_id=event.user_id,
                    amount=event.amount,
                    type=LedgerEntryType.SPEND,
                    source_app="flirt",
                    metadata={"event_type": "BOOST_USED", **event.metadata},
                )
            )
            ncr_change = -event.amount

        # ====== NovaCredit Integration ======
        # Her event davranış skorunu etkiler
        credit_result = await self.credit.normalize_and_process(
            user_id=event.user_id,
            event_type=event.event_type.value,
            source_app="flirt",
            context={"performer_id": event.performer_id, **event.metadata},
        )

        # Get updated balance
        balance = await self.wallet.get_balance(event.user_id)
        loyalty = await self.xp.get_loyalty(event.user_id)

        logger.info(
            "flirt_event_processed",
            event_type=event.event_type.value,
            user_id=event.user_id,
            ncr_change=str(ncr_change),
            xp_change=xp_change,
            credit_delta=credit_result.delta,
        )

        return EventResult(
            success=True,
            event_type=event.event_type.value,
            user_id=event.user_id,
            ncr_change=ncr_change,
            xp_change=xp_change,
            new_ncr_balance=balance.balance,
            new_xp_total=loyalty.xp_total if loyalty else 0,
            revenue_split=revenue_split,
        )

    def _calculate_flirt_xp(self, event: FlirtEvent) -> int:
        """Calculate XP from FlirtMarket event."""
        # 1 XP per 10 NCR spent
        base_xp = int(event.amount / 10)

        # Bonus for specific events
        bonuses = {
            FlirtEventType.SHOW_PURCHASED: 50,
            FlirtEventType.TIP_SENT: 10,
            FlirtEventType.GIFT_SENT: 20,
        }

        return base_xp + bonuses.get(event.event_type, 0)

    # ============ OnlyVips Events ============
    async def handle_onlyvips_event(self, event: OnlyVipsEvent) -> EventResult:
        """Process OnlyVips event."""
        ncr_change = Decimal("0")
        xp_change = 0
        revenue_split = None

        if event.event_type in [
            OnlyVipsEventType.PREMIUM_PURCHASED,
            OnlyVipsEventType.CONTENT_UNLOCKED,
            OnlyVipsEventType.SUBSCRIPTION_RENEWED,
        ]:
            # User spends NCR
            if event.amount > 0:
                await self.wallet.create_transaction(
                    TransactionCreate(
                        user_id=event.user_id,
                        amount=event.amount,
                        type=LedgerEntryType.SPEND,
                        source_app="onlyvips",
                        performer_id=event.performer_id,
                        metadata={
                            "event_type": event.event_type.value,
                            **event.metadata,
                        },
                    )
                )
                ncr_change = -event.amount

                # Revenue split
                if event.performer_id:
                    split = await self.agency.calculate_revenue_split(
                        event.performer_id, event.amount
                    )
                    revenue_split = {
                        "performer_amount": str(split.performer_amount),
                        "agency_amount": str(split.agency_amount),
                        "treasury_amount": str(split.treasury_amount),
                    }
                    await self.agency.record_performer_earnings(
                        event.performer_id, int(event.amount)
                    )

        # XP events
        if event.xp_amount > 0 or event.event_type in [
            OnlyVipsEventType.QUEST_COMPLETED,
            OnlyVipsEventType.STREAK_BONUS,
        ]:
            xp_amount = event.xp_amount or self._calculate_onlyvips_xp(event)
            if xp_amount > 0:
                await self.xp.create_xp_event(
                    XpEventCreate(
                        user_id=event.user_id,
                        amount=xp_amount,
                        event_type=f"onlyvips_{event.event_type.value.lower()}",
                        source_app="onlyvips",
                        metadata=event.metadata,
                    )
                )
                xp_change = xp_amount

        # ====== NovaCredit Integration ======
        credit_result = await self.credit.normalize_and_process(
            user_id=event.user_id,
            event_type=event.event_type.value,
            source_app="onlyvips",
            context={"performer_id": event.performer_id, **event.metadata},
        )

        balance = await self.wallet.get_balance(event.user_id)
        loyalty = await self.xp.get_loyalty(event.user_id)

        logger.info(
            "onlyvips_event_processed",
            event_type=event.event_type.value,
            user_id=event.user_id,
            ncr_change=str(ncr_change),
            xp_change=xp_change,
            credit_delta=credit_result.delta,
        )

        return EventResult(
            success=True,
            event_type=event.event_type.value,
            user_id=event.user_id,
            ncr_change=ncr_change,
            xp_change=xp_change,
            new_ncr_balance=balance.balance,
            new_xp_total=loyalty.xp_total if loyalty else 0,
            revenue_split=revenue_split,
        )

    def _calculate_onlyvips_xp(self, event: OnlyVipsEvent) -> int:
        """Calculate XP from OnlyVips event."""
        xp_map = {
            OnlyVipsEventType.QUEST_COMPLETED: 100,
            OnlyVipsEventType.STREAK_BONUS: 50,
            OnlyVipsEventType.PREMIUM_PURCHASED: 25,
        }
        return xp_map.get(event.event_type, 0)

    # ============ PokerVerse Events ============
    async def handle_poker_event(self, event: PokerEvent) -> EventResult:
        """Process PokerVerse event."""
        ncr_change = Decimal("0")
        xp_change = 0

        if event.event_type == PokerEventType.BUY_IN:
            # User buys into table - escrow
            await self.wallet.create_transaction(
                TransactionCreate(
                    user_id=event.user_id,
                    amount=event.amount,
                    type=LedgerEntryType.SPEND,
                    source_app="poker",
                    reference_id=event.table_id,
                    reference_type="table_buy_in",
                    metadata={
                        "event_type": "BUY_IN",
                        "table_id": event.table_id,
                        **event.metadata,
                    },
                )
            )
            ncr_change = -event.amount

        elif event.event_type == PokerEventType.CASH_OUT:
            # User cashes out
            await self.wallet.create_transaction(
                TransactionCreate(
                    user_id=event.user_id,
                    amount=event.amount,
                    type=LedgerEntryType.EARN,
                    source_app="poker",
                    reference_id=event.table_id,
                    reference_type="table_cash_out",
                    metadata={
                        "event_type": "CASH_OUT",
                        "table_id": event.table_id,
                        **event.metadata,
                    },
                )
            )
            ncr_change = event.amount

            # XP for profitable session
            if event.amount > 0:
                xp_amount = min(100, int(event.amount / 10))
                await self.xp.create_xp_event(
                    XpEventCreate(
                        user_id=event.user_id,
                        amount=xp_amount,
                        event_type="poker_profit",
                        source_app="poker",
                        metadata=event.metadata,
                    )
                )
                xp_change = xp_amount

        elif event.event_type == PokerEventType.RAKE:
            # Rake goes to treasury
            await self.wallet.create_transaction(
                TransactionCreate(
                    user_id=event.user_id,
                    amount=event.amount,
                    type=LedgerEntryType.RAKE,
                    source_app="poker",
                    reference_id=event.hand_id,
                    reference_type="hand_rake",
                    metadata={
                        "event_type": "RAKE",
                        "hand_id": event.hand_id,
                        "table_id": event.table_id,
                        **event.metadata,
                    },
                )
            )
            ncr_change = -event.amount

        elif event.event_type == PokerEventType.TOURNAMENT_BUY_IN:
            await self.wallet.create_transaction(
                TransactionCreate(
                    user_id=event.user_id,
                    amount=event.amount,
                    type=LedgerEntryType.SPEND,
                    source_app="poker",
                    reference_type="tournament_buy_in",
                    metadata={"event_type": "TOURNAMENT_BUY_IN", **event.metadata},
                )
            )
            ncr_change = -event.amount

        elif event.event_type == PokerEventType.TOURNAMENT_PRIZE:
            await self.wallet.create_transaction(
                TransactionCreate(
                    user_id=event.user_id,
                    amount=event.amount,
                    type=LedgerEntryType.EARN,
                    source_app="poker",
                    reference_type="tournament_prize",
                    metadata={"event_type": "TOURNAMENT_PRIZE", **event.metadata},
                )
            )
            ncr_change = event.amount

            # Big XP for tournament win
            xp_amount = 200
            await self.xp.create_xp_event(
                XpEventCreate(
                    user_id=event.user_id,
                    amount=xp_amount,
                    event_type="poker_tournament_prize",
                    source_app="poker",
                    metadata=event.metadata,
                )
            )
            xp_change = xp_amount

        # ====== NovaCredit Integration ======
        credit_result = await self.credit.normalize_and_process(
            user_id=event.user_id,
            event_type=event.event_type.value,
            source_app="poker",
            context={"table_id": event.table_id, "hand_id": event.hand_id, **event.metadata},
        )

        balance = await self.wallet.get_balance(event.user_id)
        loyalty = await self.xp.get_loyalty(event.user_id)

        logger.info(
            "poker_event_processed",
            event_type=event.event_type.value,
            user_id=event.user_id,
            ncr_change=str(ncr_change),
            credit_delta=credit_result.delta,
        )

        return EventResult(
            success=True,
            event_type=event.event_type.value,
            user_id=event.user_id,
            ncr_change=ncr_change,
            xp_change=xp_change,
            new_ncr_balance=balance.balance,
            new_xp_total=loyalty.xp_total if loyalty else 0,
        )

    # ============ Aurora Events ============
    async def handle_aurora_event(self, event: AuroraEvent) -> EventResult:
        """Process Aurora AI event."""
        ncr_change = Decimal("0")
        xp_change = 0
        revenue_split = None

        if event.event_type in [
            AuroraEventType.AI_CHAT_SESSION,
            AuroraEventType.AI_IMAGE_GENERATED,
            AuroraEventType.AI_VOICE_MESSAGE,
            AuroraEventType.TOKEN_BURN,
        ]:
            # Burn NCR for AI usage
            if event.amount > 0:
                await self.wallet.create_transaction(
                    TransactionCreate(
                        user_id=event.user_id,
                        amount=event.amount,
                        type=LedgerEntryType.BURN,
                        source_app="aurora",
                        performer_id=event.performer_id,
                        metadata={
                            "event_type": event.event_type.value,
                            "ai_profile_id": event.ai_profile_id,
                            "tokens_used": event.tokens_used,
                            **event.metadata,
                        },
                    )
                )
                ncr_change = -event.amount

            # AI performer revenue split
            if event.performer_id and event.amount > 0:
                split = await self.agency.calculate_revenue_split(
                    event.performer_id, event.amount
                )
                revenue_split = {
                    "performer_amount": str(split.performer_amount),
                    "agency_amount": str(split.agency_amount),
                    "treasury_amount": str(split.treasury_amount),
                }

            # XP for AI usage
            xp_amount = min(50, event.tokens_used // 100)  # 1 XP per 100 tokens
            if xp_amount > 0:
                await self.xp.create_xp_event(
                    XpEventCreate(
                        user_id=event.user_id,
                        amount=xp_amount,
                        event_type=f"aurora_{event.event_type.value.lower()}",
                        source_app="aurora",
                        metadata=event.metadata,
                    )
                )
                xp_change = xp_amount

        # ====== NovaCredit Integration ======
        credit_result = await self.credit.normalize_and_process(
            user_id=event.user_id,
            event_type=event.event_type.value,
            source_app="aurora",
            context={
                "performer_id": event.performer_id,
                "ai_profile_id": event.ai_profile_id,
                "tokens_used": event.tokens_used,
                **event.metadata,
            },
        )

        balance = await self.wallet.get_balance(event.user_id)
        loyalty = await self.xp.get_loyalty(event.user_id)

        logger.info(
            "aurora_event_processed",
            event_type=event.event_type.value,
            user_id=event.user_id,
            ncr_change=str(ncr_change),
            tokens_used=event.tokens_used,
            credit_delta=credit_result.delta,
        )

        return EventResult(
            success=True,
            event_type=event.event_type.value,
            user_id=event.user_id,
            ncr_change=ncr_change,
            xp_change=xp_change,
            new_ncr_balance=balance.balance,
            new_xp_total=loyalty.xp_total if loyalty else 0,
            revenue_split=revenue_split,
        )

