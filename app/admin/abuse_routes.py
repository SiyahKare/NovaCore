"""
Admin Abuse Routes - Vezir Paneli
AbuseGuard telemetry ve gözetleme endpoint'leri
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, and_, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from pydantic import BaseModel

from app.core.db import get_session
from app.core.security import get_admin_user
from app.identity.models import User
from app.abuse.models import UserRiskProfile, AbuseEvent, AbuseEventType
from app.abuse.repository import AbuseRepository


router = APIRouter(prefix="/api/v1/admin/abuse", tags=["admin", "abuse"])


class RiskScoreDistribution(BaseModel):
    """RiskScore dağılımı."""
    range_0_2: int = 0  # 0-2 (normal)
    range_3_5: int = 0  # 3-5 (low risk)
    range_6_8: int = 0  # 6-8 (medium risk)
    range_9_10: int = 0  # 9-10 (high risk, cooldown)


class EventCounts24h(BaseModel):
    """Son 24 saatteki event sayıları."""
    auto_reject: int = 0
    duplicate_proof: int = 0
    too_fast_completion: int = 0
    low_quality_burst: int = 0
    appeal_rejected: int = 0
    manual_flag: int = 0
    total: int = 0


class AbuseSummaryResponse(BaseModel):
    """Abuse summary response."""
    risk_score_distribution: RiskScoreDistribution
    events_last_24h: EventCounts24h
    total_users_with_risk: int
    users_in_cooldown: int  # RiskScore 9+
    users_requiring_hitl: int  # RiskScore 6+


@router.get(
    "/summary",
    response_model=AbuseSummaryResponse,
    summary="AbuseGuard özet istatistikleri (Vezir Paneli)",
    dependencies=[Depends(get_admin_user)],
)
async def get_abuse_summary(
    session: AsyncSession = Depends(get_session),
):
    """
    AbuseGuard sistem özeti.
    
    Vezir paneli için:
    - RiskScore dağılımı
    - Son 24 saatteki event sayıları
    - Cooldown/HITL durumları
    """
    repo = AbuseRepository(session)
    since_24h = datetime.utcnow() - timedelta(hours=24)
    
    # RiskScore dağılımı
    profiles_result = await session.execute(
        select(UserRiskProfile)
    )
    profiles = profiles_result.scalars().all()
    
    distribution = RiskScoreDistribution()
    users_in_cooldown = 0
    users_requiring_hitl = 0
    
    for profile in profiles:
        score = profile.risk_score
        if score <= 2.0:
            distribution.range_0_2 += 1
        elif score <= 5.0:
            distribution.range_3_5 += 1
        elif score <= 8.0:
            distribution.range_6_8 += 1
            users_requiring_hitl += 1
        else:
            distribution.range_9_10 += 1
            users_in_cooldown += 1
            users_requiring_hitl += 1
    
    # Son 24 saatteki event sayıları
    events_result = await session.execute(
        select(AbuseEvent).where(AbuseEvent.created_at >= since_24h)
    )
    events = events_result.scalars().all()
    
    event_counts = EventCounts24h()
    for event in events:
        if event.event_type == AbuseEventType.AUTO_REJECT:
            event_counts.auto_reject += 1
        elif event.event_type == AbuseEventType.DUPLICATE_PROOF:
            event_counts.duplicate_proof += 1
        elif event.event_type == AbuseEventType.TOO_FAST_COMPLETION:
            event_counts.too_fast_completion += 1
        elif event.event_type == AbuseEventType.LOW_QUALITY_BURST:
            event_counts.low_quality_burst += 1
        elif event.event_type == AbuseEventType.APPEAL_REJECTED:
            event_counts.appeal_rejected += 1
        elif event.event_type == AbuseEventType.MANUAL_FLAG:
            event_counts.manual_flag += 1
        event_counts.total += 1
    
    return AbuseSummaryResponse(
        risk_score_distribution=distribution,
        events_last_24h=event_counts,
        total_users_with_risk=len([p for p in profiles if p.risk_score > 0]),
        users_in_cooldown=users_in_cooldown,
        users_requiring_hitl=users_requiring_hitl,
    )


@router.get(
    "/users/at-risk",
    summary="Yüksek riskli kullanıcılar listesi",
    dependencies=[Depends(get_admin_user)],
)
async def get_at_risk_users(
    min_risk_score: float = 6.0,
    limit: int = 50,
    session: AsyncSession = Depends(get_session),
):
    """
    RiskScore'u belirli threshold'un üstünde olan kullanıcıları listele.
    """
    result = await session.execute(
        select(UserRiskProfile, User)
        .join(User, UserRiskProfile.user_id == User.id)
        .where(UserRiskProfile.risk_score >= min_risk_score)
        .order_by(UserRiskProfile.risk_score.desc())
        .limit(limit)
    )
    rows = result.all()
    
    users = []
    for profile, user in rows:
        users.append({
            "user_id": user.id,
            "username": user.username,
            "display_name": user.display_name,
            "risk_score": profile.risk_score,
            "last_event_at": profile.last_event_at.isoformat() if profile.last_event_at else None,
        })
    
    return {
        "users": users,
        "total": len(users),
        "min_risk_score": min_risk_score,
    }

