"""
Aurora Justice Stack - Statistics & Metrics
"""
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
from sqlalchemy import func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.consent.models import ConsentRecord, UserPrivacyProfile
from app.justice.models import ViolationLog, UserCpState, TaskAppeal
from app.justice.nasipcourt_models import RiskEvent
from app.wallet.models import LedgerEntry, LedgerEntryType


class RegimeDistribution(BaseModel):
    """Regime distribution stats."""
    NORMAL: int = 0
    SOFT_FLAG: int = 0
    PROBATION: int = 0
    RESTRICTED: int = 0
    LOCKDOWN: int = 0


class ViolationBreakdown(BaseModel):
    """Violation category breakdown."""
    EKO: int = 0
    COM: int = 0
    SYS: int = 0
    TRUST: int = 0


class AppealStats(BaseModel):
    """Appeal statistics."""
    total_appeals: int = 0
    approved_count: int = 0
    rejected_count: int = 0
    pending_count: int = 0
    approval_rate: float = 0.0  # approved / (approved + rejected)
    rejection_rate: float = 0.0  # rejected / (approved + rejected)


class JusticeOverviewMetrics(BaseModel):
    """Justice Overview specific metrics for monitoring."""
    pending_hitl_count: int = 0  # Pending HITL violations (Gri Alan)
    appeal_stats: AppealStats
    ncr_burn_total: float = 0.0  # Total NCR burned (AbuseGuard enforcement)
    ncr_burn_last_24h: float = 0.0  # NCR burned in last 24h


class AuroraStatsResponse(BaseModel):
    """Aurora Justice Stack statistics."""
    # Consent & Privacy
    total_consent_records: int
    total_privacy_profiles: int
    recall_requests_count: int
    recall_requests_last_24h: int
    consent_signatures_last_24h: int
    
    # Justice & CP
    total_violations: int
    violations_last_24h: int
    violations_last_7d: int
    violation_breakdown: ViolationBreakdown
    average_cp: float
    regime_distribution: RegimeDistribution
    lockdown_users_count: int
    
    # Justice Overview Metrics (NasipCourt DAO v1.0)
    justice_overview: JusticeOverviewMetrics
    
    # NovaScore (if available)
    users_with_nova_score: Optional[int] = None
    
    # Timestamps
    generated_at: datetime


class AuroraStatsService:
    """Service for calculating Aurora statistics."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_stats(self) -> AuroraStatsResponse:
        """Get comprehensive Aurora statistics."""
        now = datetime.utcnow()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        
        # Consent & Privacy Stats
        consent_count_result = await self.session.execute(
            select(func.count(ConsentRecord.id))
        )
        total_consent_records = consent_count_result.scalar() or 0
        
        profile_count_result = await self.session.execute(
            select(func.count(UserPrivacyProfile.user_id))
        )
        total_privacy_profiles = profile_count_result.scalar() or 0
        
        recall_count_result = await self.session.execute(
            select(func.count(UserPrivacyProfile.user_id)).where(
                UserPrivacyProfile.recall_requested_at.isnot(None)
            )
        )
        recall_requests_count = recall_count_result.scalar() or 0
        
        recall_24h_result = await self.session.execute(
            select(func.count(UserPrivacyProfile.user_id)).where(
                and_(
                    UserPrivacyProfile.recall_requested_at.isnot(None),
                    UserPrivacyProfile.recall_requested_at >= last_24h
                )
            )
        )
        recall_requests_last_24h = recall_24h_result.scalar() or 0
        
        consent_24h_result = await self.session.execute(
            select(func.count(ConsentRecord.id)).where(
                ConsentRecord.signed_at >= last_24h
            )
        )
        consent_signatures_last_24h = consent_24h_result.scalar() or 0
        
        # Justice & CP Stats
        violation_count_result = await self.session.execute(
            select(func.count(ViolationLog.id))
        )
        total_violations = violation_count_result.scalar() or 0
        
        violation_24h_result = await self.session.execute(
            select(func.count(ViolationLog.id)).where(
                ViolationLog.created_at >= last_24h
            )
        )
        violations_last_24h = violation_24h_result.scalar() or 0
        
        violation_7d_result = await self.session.execute(
            select(func.count(ViolationLog.id)).where(
                ViolationLog.created_at >= last_7d
            )
        )
        violations_last_7d = violation_7d_result.scalar() or 0
        
        # Violation breakdown by category
        violation_breakdown_result = await self.session.execute(
            select(
                ViolationLog.category,
                func.count(ViolationLog.id).label("count")
            ).group_by(ViolationLog.category)
        )
        breakdown_dict = {row.category: row.count for row in violation_breakdown_result.all()}
        violation_breakdown = ViolationBreakdown(
            EKO=breakdown_dict.get("EKO", 0),
            COM=breakdown_dict.get("COM", 0),
            SYS=breakdown_dict.get("SYS", 0),
            TRUST=breakdown_dict.get("TRUST", 0),
        )
        
        # CP Stats
        cp_avg_result = await self.session.execute(
            select(func.avg(UserCpState.cp_value))
        )
        average_cp = float(cp_avg_result.scalar() or 0.0)
        
        # Regime distribution
        regime_dist_result = await self.session.execute(
            select(
                UserCpState.regime,
                func.count(UserCpState.user_id).label("count")
            ).group_by(UserCpState.regime)
        )
        regime_dict = {row.regime: row.count for row in regime_dist_result.all()}
        regime_distribution = RegimeDistribution(
            NORMAL=regime_dict.get("NORMAL", 0),
            SOFT_FLAG=regime_dict.get("SOFT_FLAG", 0),
            PROBATION=regime_dict.get("PROBATION", 0),
            RESTRICTED=regime_dict.get("RESTRICTED", 0),
            LOCKDOWN=regime_dict.get("LOCKDOWN", 0),
        )
        
        lockdown_count_result = await self.session.execute(
            select(func.count(UserCpState.user_id)).where(
                UserCpState.regime == "LOCKDOWN"
            )
        )
        lockdown_users_count = lockdown_count_result.scalar() or 0
        
        # ============ Justice Overview Metrics ============
        # 1. Pending HITL Count (Gri Alan: score_ai 40-69, status=hitl)
        pending_hitl_result = await self.session.execute(
            select(func.count(RiskEvent.id)).where(
                and_(
                    RiskEvent.status == "hitl",
                    RiskEvent.score_ai >= 40.0,
                    RiskEvent.score_ai < 70.0
                )
            )
        )
        pending_hitl_count = pending_hitl_result.scalar() or 0
        
        # 2. Appeal Statistics
        appeal_total_result = await self.session.execute(
            select(func.count(TaskAppeal.id))
        )
        total_appeals = appeal_total_result.scalar() or 0
        
        appeal_approved_result = await self.session.execute(
            select(func.count(TaskAppeal.id)).where(
                TaskAppeal.status == "approved"
            )
        )
        approved_count = appeal_approved_result.scalar() or 0
        
        appeal_rejected_result = await self.session.execute(
            select(func.count(TaskAppeal.id)).where(
                TaskAppeal.status == "rejected"
            )
        )
        rejected_count = appeal_rejected_result.scalar() or 0
        
        appeal_pending_result = await self.session.execute(
            select(func.count(TaskAppeal.id)).where(
                TaskAppeal.status == "pending"
            )
        )
        pending_count = appeal_pending_result.scalar() or 0
        
        # Calculate approval/rejection rates
        total_decided = approved_count + rejected_count
        approval_rate = (approved_count / total_decided * 100.0) if total_decided > 0 else 0.0
        rejection_rate = (rejected_count / total_decided * 100.0) if total_decided > 0 else 0.0
        
        appeal_stats = AppealStats(
            total_appeals=total_appeals,
            approved_count=approved_count,
            rejected_count=rejected_count,
            pending_count=pending_count,
            approval_rate=round(approval_rate, 2),
            rejection_rate=round(rejection_rate, 2),
        )
        
        # 3. NCR Burn Statistics (AbuseGuard enforcement)
        # Total burn (all time)
        burn_total_result = await self.session.execute(
            select(func.sum(LedgerEntry.amount)).where(
                LedgerEntry.type == LedgerEntryType.BURN
            )
        )
        burn_total = burn_total_result.scalar()
        ncr_burn_total = float(burn_total) if burn_total else 0.0
        
        # Burn in last 24h
        burn_24h_result = await self.session.execute(
            select(func.sum(LedgerEntry.amount)).where(
                and_(
                    LedgerEntry.type == LedgerEntryType.BURN,
                    LedgerEntry.created_at >= last_24h
                )
            )
        )
        burn_24h = burn_24h_result.scalar()
        ncr_burn_last_24h = float(burn_24h) if burn_24h else 0.0
        
        justice_overview = JusticeOverviewMetrics(
            pending_hitl_count=pending_hitl_count,
            appeal_stats=appeal_stats,
            ncr_burn_total=ncr_burn_total,
            ncr_burn_last_24h=ncr_burn_last_24h,
        )
        
        return AuroraStatsResponse(
            total_consent_records=total_consent_records,
            total_privacy_profiles=total_privacy_profiles,
            recall_requests_count=recall_requests_count,
            recall_requests_last_24h=recall_requests_last_24h,
            consent_signatures_last_24h=consent_signatures_last_24h,
            total_violations=total_violations,
            violations_last_24h=violations_last_24h,
            violations_last_7d=violations_last_7d,
            violation_breakdown=violation_breakdown,
            average_cp=average_cp,
            regime_distribution=regime_distribution,
            lockdown_users_count=lockdown_users_count,
            justice_overview=justice_overview,
            generated_at=now,
        )

