"""
NovaCore - NovaCredit Service
Event → Delta → Score Update Engine
"""
from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.config import settings
from app.core.logging import get_logger
from app.nova_credit.models import (
    CitizenScore,
    CreditTier,
    RiskFlag,
    ScoreChange,
    calculate_tier,
    TIER_THRESHOLDS,
)
from app.nova_credit.rules import (
    CATEGORY_WEIGHTS,
    CREDIT_DEFAULT,
    CREDIT_MAX,
    CREDIT_MIN,
    EVENT_TYPE_MAPPINGS,
    EventCategory,
    TIER_PRIVILEGES,
    get_risk_level,
    get_streak_multiplier,
)
from app.nova_credit.schemas import (
    BehaviorEvent,
    CreditProfile,
    CreditProfileBrief,
    CreditStats,
    LeaderboardEntry,
    ProcessEventResult,
    RiskFlagCreate,
    RiskFlagOut,
    ScoreChangeOut,
    TierPrivileges,
)

logger = get_logger("nova_credit")


class NovaCreditService:
    """
    NovaCredit Engine - Davranış Skoru Motoru.
    
    Event → Delta hesaplama → Score güncelleme → Tier belirleme
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    # ============ Citizen Score CRUD ============
    async def get_citizen_score(self, user_id: int) -> CitizenScore | None:
        """Get citizen score by user_id."""
        result = await self.session.execute(
            select(CitizenScore).where(CitizenScore.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_or_create_citizen_score(self, user_id: int) -> CitizenScore:
        """Get or create citizen score."""
        score = await self.get_citizen_score(user_id)

        if not score:
            score = CitizenScore(
                user_id=user_id,
                nova_credit=CREDIT_DEFAULT,
                tier=calculate_tier(CREDIT_DEFAULT),
            )
            self.session.add(score)
            await self.session.flush()
            await self.session.refresh(score)

            logger.info("citizen_score_created", user_id=user_id)

        return score

    async def get_credit_profile(self, user_id: int) -> CreditProfile:
        """Get full credit profile with privileges."""
        score = await self.get_or_create_citizen_score(user_id)

        # Calculate progress to next tier
        next_tier = self._get_next_tier(score.tier)
        progress = 0.0
        credit_to_next = 0

        if next_tier:
            current_min, current_max = TIER_THRESHOLDS[score.tier]
            next_min, next_max = TIER_THRESHOLDS[next_tier]
            credit_to_next = next_min - score.nova_credit
            total_range = next_min - current_min
            if total_range > 0:
                progress = (score.nova_credit - current_min) / total_range
                progress = max(0.0, min(1.0, progress))

        # Get privileges
        privileges = TIER_PRIVILEGES.get(score.tier.value, TIER_PRIVILEGES["GREY"])

        return CreditProfile(
            user_id=score.user_id,
            nova_credit=score.nova_credit,
            tier=score.tier,
            risk_score=score.risk_score,
            reputation_score=score.reputation_score,
            total_events=score.total_events,
            positive_streak=score.positive_streak,
            negative_streak=score.negative_streak,
            risk_level=get_risk_level(score.risk_score),
            privileges=TierPrivileges(
                withdraw_limit_daily=privileges.withdraw_limit_daily,
                transfer_limit_daily=privileges.transfer_limit_daily,
                can_create_content=privileges.can_create_content,
                can_host_rooms=privileges.can_host_rooms,
                priority_support=privileges.priority_support,
                ai_model_tier=privileges.ai_model_tier,
                transaction_fee_discount=privileges.transaction_fee_discount,
            ),
            progress_to_next_tier=progress,
            next_tier=next_tier,
            credit_to_next_tier=max(0, credit_to_next),
            last_event_at=score.last_event_at,
            created_at=score.created_at,
            updated_at=score.updated_at,
        )

    async def get_credit_brief(self, user_id: int) -> CreditProfileBrief:
        """Get brief credit info."""
        score = await self.get_or_create_citizen_score(user_id)

        return CreditProfileBrief(
            user_id=score.user_id,
            nova_credit=score.nova_credit,
            tier=score.tier,
            risk_level=get_risk_level(score.risk_score),
        )

    def _get_next_tier(self, current_tier: CreditTier) -> CreditTier | None:
        """Get next tier if available."""
        tiers = list(CreditTier)
        try:
            current_index = tiers.index(current_tier)
            if current_index < len(tiers) - 1:
                return tiers[current_index + 1]
        except ValueError:
            pass
        return None

    # ============ Event Processing ============
    async def process_event(self, event: BehaviorEvent) -> ProcessEventResult:
        """
        Process a behavior event and update citizen score.
        
        This is the core engine method.
        """
        score = await self.get_or_create_citizen_score(event.actor_id)
        old_score = score.nova_credit
        old_tier = score.tier

        # Get category weight
        category_weight = CATEGORY_WEIGHTS.get(event.category)
        if not category_weight:
            logger.warning(
                "unknown_category",
                category=event.category,
                event_type=event.event_type,
            )
            category_weight = CATEGORY_WEIGHTS[EventCategory.ECONOMIC]

        # Apply streak bonus
        streak_multiplier = get_streak_multiplier(score.positive_streak)

        # Calculate final delta
        weight = category_weight.weight
        if weight > 0:
            # Pozitif eventlerde streak bonus uygula
            delta = int(event.base_delta * weight * streak_multiplier)
        else:
            # Negatif eventlerde streak bonus yok
            delta = int(event.base_delta * weight)

        # Update score
        new_score = max(CREDIT_MIN, min(CREDIT_MAX, score.nova_credit + delta))
        score.nova_credit = new_score

        # Update tier
        new_tier = calculate_tier(new_score)
        score.tier = new_tier
        tier_changed = old_tier != new_tier

        # Update risk & reputation
        risk_delta = category_weight.risk_impact
        reputation_delta = category_weight.reputation_impact

        score.risk_score = max(0.0, min(1.0, score.risk_score + risk_delta))
        score.reputation_score = max(0.0, min(1.0, score.reputation_score + reputation_delta))

        # Update streaks
        if delta > 0:
            score.positive_streak += 1
            score.negative_streak = 0
            score.total_positive_events += 1
            score.last_positive_at = datetime.utcnow()
        elif delta < 0:
            score.negative_streak += 1
            score.positive_streak = 0
            score.total_negative_events += 1
            score.last_negative_at = datetime.utcnow()

        # Update activity
        score.total_events += 1
        score.last_event_at = datetime.utcnow()
        score.updated_at = datetime.utcnow()

        self.session.add(score)

        # Create score change log
        change = ScoreChange(
            user_id=event.actor_id,
            event_id=event.event_id,
            event_type=event.event_type,
            delta=delta,
            old_score=old_score,
            new_score=new_score,
            category=event.category.value,
            reason=event.reason or event.event_type,
            source_app=event.source_app,
            weight_applied=weight * streak_multiplier if delta > 0 else weight,
            base_delta=event.base_delta,
            context=event.context,
        )
        self.session.add(change)

        await self.session.flush()

        # Log significant changes
        if tier_changed:
            logger.info(
                "tier_changed",
                user_id=event.actor_id,
                old_tier=old_tier.value,
                new_tier=new_tier.value,
                nova_credit=new_score,
            )

        logger.info(
            "credit_updated",
            user_id=event.actor_id,
            event_type=event.event_type,
            delta=delta,
            new_score=new_score,
            tier=new_tier.value,
        )

        # Build result
        message = None
        if tier_changed:
            if new_tier.value > old_tier.value:
                message = f"Tebrikler! {new_tier.value} tier'ına yükseldiniz!"
            else:
                message = f"Dikkat: {new_tier.value} tier'ına düştünüz."

        return ProcessEventResult(
            success=True,
            user_id=event.actor_id,
            event_type=event.event_type,
            delta=delta,
            old_score=old_score,
            new_score=new_score,
            old_tier=old_tier,
            new_tier=new_tier,
            tier_changed=tier_changed,
            risk_delta=risk_delta,
            reputation_delta=reputation_delta,
            message=message,
        )

    async def normalize_and_process(
        self,
        user_id: int,
        event_type: str,
        source_app: str,
        event_id: str | None = None,
        context: dict | None = None,
    ) -> ProcessEventResult:
        """
        Normalize event type to behavior event and process.
        
        Convenience method for common event types.
        """
        # Look up event type mapping
        mapping = EVENT_TYPE_MAPPINGS.get(event_type)

        if not mapping:
            logger.warning(
                "unmapped_event_type",
                event_type=event_type,
                source_app=source_app,
            )
            # Default to economic with small delta
            category = EventCategory.ECONOMIC
            base_delta = 1
        else:
            category, base_delta = mapping

        event = BehaviorEvent(
            event_id=event_id,
            actor_id=user_id,
            event_type=event_type,
            category=category,
            base_delta=base_delta,
            source_app=source_app,
            reason=f"{source_app}: {event_type}",
            context=context or {},
        )

        return await self.process_event(event)

    # ============ History ============
    async def get_score_history(
        self,
        user_id: int,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[ScoreChange], int]:
        """Get score change history."""
        query = select(ScoreChange).where(ScoreChange.user_id == user_id)

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.session.execute(count_query)).scalar() or 0

        # Fetch
        query = query.order_by(ScoreChange.created_at.desc())
        query = query.offset((page - 1) * per_page).limit(per_page)

        result = await self.session.execute(query)
        changes = list(result.scalars().all())

        return changes, total

    # ============ Risk Flags ============
    async def create_risk_flag(self, data: RiskFlagCreate) -> RiskFlagOut:
        """Create a risk flag for a user."""
        flag = RiskFlag(
            user_id=data.user_id,
            flag_type=data.flag_type,
            severity=data.severity,
            description=data.description,
            event_id=data.event_id,
            source_app=data.source_app,
            context=data.context,
        )
        self.session.add(flag)

        # Also process as negative event
        severity_delta = {
            "LOW": -5,
            "MEDIUM": -15,
            "HIGH": -30,
            "CRITICAL": -50,
        }

        event = BehaviorEvent(
            event_id=data.event_id,
            actor_id=data.user_id,
            event_type=f"RISK_FLAG_{data.flag_type}",
            category=EventCategory.RISK_NEGATIVE,
            base_delta=severity_delta.get(data.severity, -10),
            source_app=data.source_app,
            reason=data.description,
            context=data.context,
        )
        await self.process_event(event)

        await self.session.flush()
        await self.session.refresh(flag)

        logger.warning(
            "risk_flag_created",
            user_id=data.user_id,
            flag_type=data.flag_type,
            severity=data.severity,
        )

        return RiskFlagOut.model_validate(flag)

    async def get_active_risk_flags(self, user_id: int) -> list[RiskFlagOut]:
        """Get active risk flags for a user."""
        result = await self.session.execute(
            select(RiskFlag).where(
                RiskFlag.user_id == user_id,
                RiskFlag.is_active == True,
            )
        )
        flags = result.scalars().all()
        return [RiskFlagOut.model_validate(f) for f in flags]

    # ============ Stats ============
    async def get_stats(self) -> CreditStats:
        """Get credit system statistics."""
        # Total citizens
        total_result = await self.session.execute(
            select(func.count(CitizenScore.user_id))
        )
        total_citizens = total_result.scalar() or 0

        # Average credit
        avg_result = await self.session.execute(
            select(func.avg(CitizenScore.nova_credit))
        )
        average_credit = float(avg_result.scalar() or CREDIT_DEFAULT)

        # Tier distribution
        tier_query = (
            select(CitizenScore.tier, func.count(CitizenScore.user_id))
            .group_by(CitizenScore.tier)
        )
        tier_result = await self.session.execute(tier_query)
        tier_distribution = {row[0].value: row[1] for row in tier_result.all()}

        # Risk distribution
        risk_distribution = {
            "LOW": 0,
            "MEDIUM": 0,
            "HIGH": 0,
            "CRITICAL": 0,
        }
        # Simplified - in production would use proper ranges
        risk_query = await self.session.execute(
            select(CitizenScore.risk_score).where(CitizenScore.risk_score > 0)
        )
        for (risk_score,) in risk_query.all():
            level = get_risk_level(risk_score)
            risk_distribution[level] = risk_distribution.get(level, 0) + 1

        # Events in last 24h
        yesterday = datetime.utcnow() - timedelta(days=1)
        events_24h_result = await self.session.execute(
            select(func.count(ScoreChange.id)).where(
                ScoreChange.created_at >= yesterday
            )
        )
        events_24h = events_24h_result.scalar() or 0

        # Events in last 7d
        week_ago = datetime.utcnow() - timedelta(days=7)
        events_7d_result = await self.session.execute(
            select(func.count(ScoreChange.id)).where(
                ScoreChange.created_at >= week_ago
            )
        )
        events_7d = events_7d_result.scalar() or 0

        # At risk citizens
        at_risk_result = await self.session.execute(
            select(func.count(CitizenScore.user_id)).where(
                CitizenScore.risk_score > 0.6
            )
        )
        citizens_at_risk = at_risk_result.scalar() or 0

        # Ghost citizens
        ghost_result = await self.session.execute(
            select(func.count(CitizenScore.user_id)).where(
                CitizenScore.tier == CreditTier.GHOST
            )
        )
        citizens_in_ghost = ghost_result.scalar() or 0

        return CreditStats(
            total_citizens=total_citizens,
            average_credit=average_credit,
            median_credit=CREDIT_DEFAULT,  # TODO: calculate actual median
            tier_distribution=tier_distribution,
            risk_distribution=risk_distribution,
            events_last_24h=events_24h,
            events_last_7d=events_7d,
            citizens_at_risk=citizens_at_risk,
            citizens_in_ghost=citizens_in_ghost,
        )

    async def get_leaderboard(
        self,
        limit: int = 10,
        tier: CreditTier | None = None,
    ) -> list[LeaderboardEntry]:
        """Get credit leaderboard."""
        from app.identity.models import User

        query = (
            select(CitizenScore, User)
            .join(User, CitizenScore.user_id == User.id)
        )

        if tier:
            query = query.where(CitizenScore.tier == tier)

        query = query.order_by(CitizenScore.nova_credit.desc()).limit(limit)

        result = await self.session.execute(query)
        rows = result.all()

        entries = []
        for idx, (score, user) in enumerate(rows, start=1):
            entries.append(
                LeaderboardEntry(
                    rank=idx,
                    user_id=score.user_id,
                    username=user.username,
                    nova_credit=score.nova_credit,
                    tier=score.tier,
                    reputation_score=score.reputation_score,
                )
            )

        return entries

