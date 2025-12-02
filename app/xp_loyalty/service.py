"""
NovaCore XP & Loyalty Service
"""
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.logging import get_logger
from app.xp_loyalty.models import (
    LoyaltyTier,
    TIER_THRESHOLDS,
    UserLoyalty,
    XpEvent,
    get_level_xp_requirement,
)
from app.xp_loyalty.schemas import (
    LeaderboardEntry,
    LeaderboardResponse,
    LoyaltyProfileBrief,
    LoyaltyProfileResponse,
    LoyaltyStats,
    XpEventCreate,
    XpEventResponse,
)

logger = get_logger("xp_loyalty")


class XpLoyaltyService:
    """XP & Loyalty service."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ============ Loyalty Profile ============
    async def get_loyalty(self, user_id: int) -> UserLoyalty | None:
        """Get user's loyalty profile."""
        result = await self.session.execute(
            select(UserLoyalty).where(UserLoyalty.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_or_create_loyalty(self, user_id: int) -> UserLoyalty:
        """Get or create loyalty profile."""
        loyalty = await self.get_loyalty(user_id)

        if not loyalty:
            loyalty = UserLoyalty(user_id=user_id)
            self.session.add(loyalty)
            await self.session.flush()
            await self.session.refresh(loyalty)

            logger.info("loyalty_created", user_id=user_id)

        return loyalty

    async def get_loyalty_profile(self, user_id: int) -> LoyaltyProfileResponse:
        """Get full loyalty profile with computed fields."""
        loyalty = await self.get_or_create_loyalty(user_id)

        # Calculate XP to next level
        current_level_xp = get_level_xp_requirement(loyalty.level)
        next_level_xp = get_level_xp_requirement(loyalty.level + 1)
        xp_to_next_level = max(0, next_level_xp - loyalty.xp_total)

        # Calculate XP to next tier
        next_tier = self._get_next_tier(loyalty.tier)
        xp_to_next_tier = 0
        if next_tier:
            xp_to_next_tier = max(0, TIER_THRESHOLDS[next_tier] - loyalty.xp_total)

        return LoyaltyProfileResponse(
            user_id=loyalty.user_id,
            xp_total=loyalty.xp_total,
            level=loyalty.level,
            tier=loyalty.tier,
            total_events=loyalty.total_events,
            current_streak=loyalty.current_streak,
            max_streak=loyalty.max_streak,
            vip_priority=loyalty.vip_priority,
            ai_credits_bonus=loyalty.ai_credits_bonus,
            xp_to_next_level=xp_to_next_level,
            xp_to_next_tier=xp_to_next_tier,
            next_tier=next_tier,
            created_at=loyalty.created_at,
            updated_at=loyalty.updated_at,
        )

    async def get_loyalty_brief(self, user_id: int) -> LoyaltyProfileBrief:
        """Get brief loyalty profile for Aurora routing."""
        loyalty = await self.get_or_create_loyalty(user_id)

        return LoyaltyProfileBrief(
            user_id=loyalty.user_id,
            level=loyalty.level,
            tier=loyalty.tier,
            vip_priority=loyalty.vip_priority,
            ai_credits_bonus=loyalty.ai_credits_bonus,
        )

    def _get_next_tier(self, current_tier: LoyaltyTier) -> LoyaltyTier | None:
        """Get next tier if available."""
        tiers = list(LoyaltyTier)
        current_index = tiers.index(current_tier)

        if current_index < len(tiers) - 1:
            return tiers[current_index + 1]
        return None

    # ============ XP Events ============
    async def create_xp_event(self, event: XpEventCreate) -> XpEventResponse:
        """Create XP event and update loyalty profile."""
        loyalty = await self.get_or_create_loyalty(event.user_id)

        # Update XP
        old_xp = loyalty.xp_total
        loyalty.xp_total = max(0, loyalty.xp_total + event.amount)  # Don't go below 0

        # Update level
        old_level = loyalty.level
        loyalty.level = self._calculate_level(loyalty.xp_total)

        # Update tier
        old_tier = loyalty.tier
        loyalty.tier = self._calculate_tier(loyalty.xp_total)

        # Update VIP priority based on tier
        loyalty.vip_priority = self._calculate_vip_priority(loyalty.tier, loyalty.level)

        # Update AI credits bonus based on tier
        loyalty.ai_credits_bonus = self._calculate_ai_bonus(loyalty.tier)

        # Update stats
        loyalty.total_events += 1
        loyalty.updated_at = datetime.utcnow()
        loyalty.last_activity_date = datetime.utcnow()

        self.session.add(loyalty)

        # Create event log
        xp_event = XpEvent(
            user_id=event.user_id,
            amount=event.amount,
            event_type=event.event_type,
            source_app=event.source_app,
            reference_id=event.reference_id,
            reference_type=event.reference_type,
            meta=event.metadata,  # Schema uses 'metadata', model uses 'meta'
            xp_total_after=loyalty.xp_total,
            level_after=loyalty.level,
            tier_after=loyalty.tier.value,
        )
        self.session.add(xp_event)

        await self.session.flush()
        await self.session.refresh(xp_event)

        # Log level/tier changes
        if old_level != loyalty.level:
            logger.info(
                "level_up",
                user_id=event.user_id,
                old_level=old_level,
                new_level=loyalty.level,
            )

        if old_tier != loyalty.tier:
            logger.info(
                "tier_up",
                user_id=event.user_id,
                old_tier=old_tier.value,
                new_tier=loyalty.tier.value,
            )

        logger.info(
            "xp_event_created",
            event_id=xp_event.id,
            user_id=event.user_id,
            amount=event.amount,
            event_type=event.event_type,
            xp_total=loyalty.xp_total,
        )

        return XpEventResponse.model_validate(xp_event)

    def _calculate_level(self, xp: int) -> int:
        """Calculate level from XP."""
        # Simple linear: 100 XP per level
        level = (xp // 100) + 1
        return max(1, level)

    def _calculate_tier(self, xp: int) -> LoyaltyTier:
        """Calculate tier from XP."""
        for tier in reversed(list(LoyaltyTier)):
            if xp >= TIER_THRESHOLDS[tier]:
                return tier
        return LoyaltyTier.BRONZE

    def _calculate_vip_priority(self, tier: LoyaltyTier, level: int) -> int:
        """Calculate VIP priority (0-100)."""
        tier_base = {
            LoyaltyTier.BRONZE: 0,
            LoyaltyTier.SILVER: 25,
            LoyaltyTier.GOLD: 50,
            LoyaltyTier.DIAMOND: 75,
        }

        # Base from tier + level bonus (max +25)
        priority = tier_base[tier] + min(25, level)
        return min(100, priority)

    def _calculate_ai_bonus(self, tier: LoyaltyTier) -> float:
        """Calculate AI credits bonus multiplier."""
        bonuses = {
            LoyaltyTier.BRONZE: 0.0,
            LoyaltyTier.SILVER: 0.1,  # +10%
            LoyaltyTier.GOLD: 0.25,  # +25%
            LoyaltyTier.DIAMOND: 0.5,  # +50%
        }
        return bonuses[tier]

    # ============ Leaderboard ============
    async def get_leaderboard(
        self,
        limit: int = 10,
        offset: int = 0,
    ) -> LeaderboardResponse:
        """Get XP leaderboard."""
        from app.identity.models import User

        # Query with join to get user info
        query = (
            select(UserLoyalty, User)
            .join(User, UserLoyalty.user_id == User.id)
            .order_by(UserLoyalty.xp_total.desc())
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(query)
        rows = result.all()

        entries = []
        for idx, (loyalty, user) in enumerate(rows, start=offset + 1):
            entries.append(
                LeaderboardEntry(
                    rank=idx,
                    user_id=loyalty.user_id,
                    username=user.username,
                    display_name=user.display_name,
                    xp_total=loyalty.xp_total,
                    level=loyalty.level,
                    tier=loyalty.tier,
                )
            )

        # Total count
        count_result = await self.session.execute(
            select(func.count(UserLoyalty.user_id))
        )
        total = count_result.scalar() or 0

        return LeaderboardResponse(
            entries=entries,
            total_users=total,
            period="all_time",
        )

    # ============ Stats ============
    async def get_stats(self) -> LoyaltyStats:
        """Get global loyalty stats."""
        # Total users
        users_result = await self.session.execute(
            select(func.count(UserLoyalty.user_id))
        )
        total_users = users_result.scalar() or 0

        # Total XP distributed
        xp_result = await self.session.execute(
            select(func.sum(UserLoyalty.xp_total))
        )
        total_xp = xp_result.scalar() or 0

        # Tier distribution
        tier_query = (
            select(UserLoyalty.tier, func.count(UserLoyalty.user_id))
            .group_by(UserLoyalty.tier)
        )
        tier_result = await self.session.execute(tier_query)
        tier_distribution = {row[0].value: row[1] for row in tier_result.all()}

        # Average level
        avg_result = await self.session.execute(
            select(func.avg(UserLoyalty.level))
        )
        average_level = float(avg_result.scalar() or 1.0)

        return LoyaltyStats(
            total_users=total_users,
            total_xp_distributed=total_xp,
            tier_distribution=tier_distribution,
            average_level=average_level,
        )

