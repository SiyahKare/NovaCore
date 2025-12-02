# app/telemetry/router.py
"""
Aurora Telemetry Router - Growth & Education Event Tracking
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func
from datetime import datetime, timedelta
from typing import List

from app.core.db import get_session
from app.core.security import get_current_user, get_admin_user
from app.identity.models import User
from app.telemetry.models import TelemetryEvent
from app.telemetry.schemas import (
    TelemetryEventCreate,
    TelemetryEventResponse,
    GrowthMetricsResponse,
)

router = APIRouter(prefix="/api/v1/telemetry", tags=["telemetry"])


@router.post(
    "/events",
    response_model=TelemetryEventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Track Telemetry Event",
    description="Track a growth or education event (onboarding, academy, justice, etc.).",
)
async def track_event(
    event_data: TelemetryEventCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> TelemetryEventResponse:
    """
    Track a telemetry event.
    
    Event types:
    - onboarding_completed
    - academy_module_viewed
    - academy_module_completed
    - recall_requested
    - appeal_submitted
    - justice_case_viewed (admin)
    """
    # Rate limiting: max 100 events per user per day
    yesterday = datetime.utcnow() - timedelta(days=1)
    count_query = select(func.count()).select_from(
        select(TelemetryEvent.id)
        .where(
            TelemetryEvent.user_id == current_user.id,
            TelemetryEvent.created_at >= yesterday,
        )
        .subquery()
    )
    event_count = (await session.execute(count_query)).scalar_one()
    
    if event_count >= 100:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded: max 100 events per day",
        )

    # Create event
    event = TelemetryEvent(
        user_id=current_user.id,
        event=event_data.event,
        payload=event_data.payload,
        session_id=event_data.session_id,
        source=event_data.source or "citizen-portal",
    )

    session.add(event)
    await session.commit()
    await session.refresh(event)

    return TelemetryEventResponse(
        id=str(event.id),
        user_id=event.user_id,
        event=event.event,
        payload=event.payload,
        created_at=event.created_at,
        session_id=event.session_id,
        source=event.source,
    )


@router.get(
    "/growth",
    response_model=GrowthMetricsResponse,
    summary="Get Growth Metrics",
    description="Get growth and education metrics (admin only).",
)
async def get_growth_metrics(
    _admin: User = Depends(get_admin_user),
    session: AsyncSession = Depends(get_session),
) -> GrowthMetricsResponse:
    """Get growth metrics for admin dashboard."""
    now = datetime.utcnow()
    last_24h = now - timedelta(hours=24)
    last_7d = now - timedelta(days=7)

    # Onboarding metrics
    onboarding_24h_query = select(func.count()).select_from(
        select(TelemetryEvent.id)
        .where(
            TelemetryEvent.event == "onboarding_completed",
            TelemetryEvent.created_at >= last_24h,
        )
        .subquery()
    )
    onboarding_24h = (await session.execute(onboarding_24h_query)).scalar_one()

    onboarding_7d_query = select(func.count()).select_from(
        select(TelemetryEvent.id)
        .where(
            TelemetryEvent.event == "onboarding_completed",
            TelemetryEvent.created_at >= last_7d,
        )
        .subquery()
    )
    onboarding_7d = (await session.execute(onboarding_7d_query)).scalar_one()

    onboarding_total_query = select(func.count()).select_from(
        select(TelemetryEvent.id)
        .where(TelemetryEvent.event == "onboarding_completed")
        .subquery()
    )
    onboarding_total = (await session.execute(onboarding_total_query)).scalar_one()

    # Academy metrics
    academy_views_24h_query = select(func.count()).select_from(
        select(TelemetryEvent.id)
        .where(
            TelemetryEvent.event == "academy_module_viewed",
            TelemetryEvent.created_at >= last_24h,
        )
        .subquery()
    )
    academy_views_24h = (await session.execute(academy_views_24h_query)).scalar_one()

    academy_views_7d_query = select(func.count()).select_from(
        select(TelemetryEvent.id)
        .where(
            TelemetryEvent.event == "academy_module_viewed",
            TelemetryEvent.created_at >= last_7d,
        )
        .subquery()
    )
    academy_views_7d = (await session.execute(academy_views_7d_query)).scalar_one()

    academy_completions_24h_query = select(func.count()).select_from(
        select(TelemetryEvent.id)
        .where(
            TelemetryEvent.event == "academy_module_completed",
            TelemetryEvent.created_at >= last_24h,
        )
        .subquery()
    )
    academy_completions_24h = (await session.execute(academy_completions_24h_query)).scalar_one()

    academy_completions_7d_query = select(func.count()).select_from(
        select(TelemetryEvent.id)
        .where(
            TelemetryEvent.event == "academy_module_completed",
            TelemetryEvent.created_at >= last_7d,
        )
        .subquery()
    )
    academy_completions_7d = (await session.execute(academy_completions_7d_query)).scalar_one()

    # Top modules (last 7 days)
    top_modules_query = (
        select(
            TelemetryEvent.payload["module"].astext.label("module"),
            func.count().label("views"),
        )
        .where(
            TelemetryEvent.event == "academy_module_viewed",
            TelemetryEvent.created_at >= last_7d,
        )
        .group_by(TelemetryEvent.payload["module"].astext)
        .order_by(func.count().desc())
        .limit(10)
    )
    top_modules_result = await session.execute(top_modules_query)
    top_modules = [
        {"module": row.module, "views": row.views}
        for row in top_modules_result.all()
    ]

    # Justice metrics
    recall_24h_query = select(func.count()).select_from(
        select(TelemetryEvent.id)
        .where(
            TelemetryEvent.event == "recall_requested",
            TelemetryEvent.created_at >= last_24h,
        )
        .subquery()
    )
    recall_24h = (await session.execute(recall_24h_query)).scalar_one()

    recall_total_query = select(func.count()).select_from(
        select(TelemetryEvent.id)
        .where(TelemetryEvent.event == "recall_requested")
        .subquery()
    )
    recall_total = (await session.execute(recall_total_query)).scalar_one()

    appeals_24h_query = select(func.count()).select_from(
        select(TelemetryEvent.id)
        .where(
            TelemetryEvent.event == "appeal_submitted",
            TelemetryEvent.created_at >= last_24h,
        )
        .subquery()
    )
    appeals_24h = (await session.execute(appeals_24h_query)).scalar_one()

    appeals_total_query = select(func.count()).select_from(
        select(TelemetryEvent.id)
        .where(TelemetryEvent.event == "appeal_submitted")
        .subquery()
    )
    appeals_total = (await session.execute(appeals_total_query)).scalar_one()

    # Active users (unique users with any event)
    active_24h_query = select(func.count(func.distinct(TelemetryEvent.user_id))).where(
        TelemetryEvent.created_at >= last_24h
    )
    active_24h = (await session.execute(active_24h_query)).scalar_one()

    active_7d_query = select(func.count(func.distinct(TelemetryEvent.user_id))).where(
        TelemetryEvent.created_at >= last_7d
    )
    active_7d = (await session.execute(active_7d_query)).scalar_one()

    return GrowthMetricsResponse(
        onboarding_last_24h=onboarding_24h,
        onboarding_last_7d=onboarding_7d,
        onboarding_total=onboarding_total,
        academy_views_last_24h=academy_views_24h,
        academy_views_last_7d=academy_views_7d,
        academy_module_completions_last_24h=academy_completions_24h,
        academy_module_completions_last_7d=academy_completions_7d,
        top_modules=top_modules,
        recall_requests_last_24h=recall_24h,
        recall_requests_total=recall_total,
        appeals_submitted_last_24h=appeals_24h,
        appeals_submitted_total=appeals_total,
        active_users_last_24h=active_24h,
        active_users_last_7d=active_7d,
        generated_at=now,
    )

