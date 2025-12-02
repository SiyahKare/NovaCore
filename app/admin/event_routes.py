"""
Admin Event Management Routes
Event'leri yönetmek için admin endpoint'leri
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.db import get_session
from app.core.security import get_current_user
from app.identity.models import User
from app.telegram_gateway.event_models import (
    Event,
    EventTask,
    EventParticipation,
    EventReward,
    EventStatus,
    EventType,
)
from app.telegram_gateway.event_schemas import (
    EventResponse,
    EventLeaderboardResponse,
    EventLeaderboardEntry,
)

router = APIRouter(prefix="/api/v1/admin/events", tags=["admin-events"])


def get_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Admin kullanıcı kontrolü."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


@router.get(
    "",
    response_model=list[EventResponse],
    summary="Tüm event'leri listele (admin)",
)
async def list_events(
    status_filter: Optional[str] = Query(None, alias="status", description="Event status filter"),
    event_type: Optional[str] = Query(None, description="Event type filter"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
    _admin: User = Depends(get_admin_user),
):
    """
    Tüm event'leri listele (admin).
    
    Filter: status, event_type
    """
    query = select(Event)
    
    if status_filter:
        try:
            status_enum = EventStatus(status_filter.upper())
            query = query.where(Event.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_filter}",
            )
    
    if event_type:
        try:
            type_enum = EventType(event_type.upper())
            query = query.where(Event.event_type == type_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid event_type: {event_type}",
            )
    
    query = query.order_by(Event.starts_at.desc()).limit(limit).offset(offset)
    
    result = await session.execute(query)
    events = result.scalars().all()
    
    events_response = []
    for event in events:
        # Participation count
        participation_count_result = await session.execute(
            select(func.count(EventParticipation.id)).where(
                EventParticipation.event_id == event.id
            )
        )
        participation_count = participation_count_result.scalar_one() or 0
        
        events_response.append(
            EventResponse(
                id=event.id,
                code=event.code,
                name=event.name,
                description=event.description,
                event_type=event.event_type.value,
                status=event.status.value,
                starts_at=event.starts_at,
                ends_at=event.ends_at,
                reward_multiplier_xp=event.reward_multiplier_xp,
                reward_multiplier_ncr=event.reward_multiplier_ncr,
                max_participants=event.max_participants,
                min_level_required=event.min_level_required,
                is_joined=False,  # Admin için
                user_rank=None,
                user_score={"participation_count": participation_count},  # Metadata olarak
            )
        )
    
    return events_response


@router.get(
    "/{event_id}",
    response_model=EventResponse,
    summary="Event detayı (admin)",
)
async def get_event_detail_admin(
    event_id: int,
    session: AsyncSession = Depends(get_session),
    _admin: User = Depends(get_admin_user),
):
    """
    Event detayını getir (admin).
    """
    event_query = select(Event).where(Event.id == event_id)
    event_result = await session.execute(event_query)
    event = event_result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )
    
    # Get event tasks
    tasks_query = select(EventTask).where(EventTask.event_id == event_id)
    tasks_result = await session.execute(tasks_query)
    tasks = tasks_result.scalars().all()
    
    # Participation count
    participation_count_result = await session.execute(
        select(func.count(EventParticipation.id)).where(
            EventParticipation.event_id == event_id
        )
    )
    participation_count = participation_count_result.scalar_one() or 0
    
    # Total XP/NCR distributed
    total_xp_result = await session.execute(
        select(func.sum(EventParticipation.total_xp_earned)).where(
            EventParticipation.event_id == event_id
        )
    )
    total_xp = total_xp_result.scalar_one() or 0
    
    total_ncr_result = await session.execute(
        select(func.sum(EventParticipation.total_ncr_earned)).where(
            EventParticipation.event_id == event_id
        )
    )
    total_ncr = total_ncr_result.scalar_one() or 0
    
    total_tasks_result = await session.execute(
        select(func.sum(EventParticipation.tasks_completed)).where(
            EventParticipation.event_id == event_id
        )
    )
    total_tasks = total_tasks_result.scalar_one() or 0
    
    return EventResponse(
        id=event.id,
        code=event.code,
        name=event.name,
        description=event.description,
        event_type=event.event_type.value,
        status=event.status.value,
        starts_at=event.starts_at,
        ends_at=event.ends_at,
        reward_multiplier_xp=event.reward_multiplier_xp,
        reward_multiplier_ncr=event.reward_multiplier_ncr,
        max_participants=event.max_participants,
        min_level_required=event.min_level_required,
        is_joined=False,
        user_rank=None,
        user_score={
            "xp": total_xp,
            "tasks_completed": total_tasks,
            "participation_count": participation_count,
        },
    )


@router.get(
    "/{event_id}/participants",
    response_model=EventLeaderboardResponse,
    summary="Event katılımcıları (admin)",
)
async def get_event_participants_admin(
    event_id: int,
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    _admin: User = Depends(get_admin_user),
):
    """
    Event katılımcılarını getir (admin).
    """
    # Get event
    event_query = select(Event).where(Event.id == event_id)
    event_result = await session.execute(event_query)
    event = event_result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )
    
    # Get participations
    participation_query = (
        select(EventParticipation)
        .where(EventParticipation.event_id == event_id)
        .order_by(
            EventParticipation.total_xp_earned.desc(),
            EventParticipation.tasks_completed.desc(),
        )
        .limit(limit)
    )
    
    participation_result = await session.execute(participation_query)
    participations = participation_result.scalars().all()
    
    # Update ranks
    for rank, participation in enumerate(participations, 1):
        if participation.rank != rank:
            participation.rank = rank
            session.add(participation)
    
    await session.commit()
    
    # Get user info
    from app.telegram_gateway.models import TelegramAccount
    
    entries = []
    for participation in participations:
        # Get telegram account
        account_query = (
            select(TelegramAccount)
            .where(TelegramAccount.user_id == participation.user_id)
        )
        account_result = await session.execute(account_query)
        account = account_result.scalar_one_or_none()
        
        if not account:
            # Fallback to user
            user_query = select(User).where(User.id == participation.user_id)
            user_result = await session.execute(user_query)
            user = user_result.scalar_one_or_none()
            
            if not user:
                continue
            
            entries.append(
                EventLeaderboardEntry(
                    rank=participation.rank or 0,
                    user_id=participation.user_id,
                    telegram_user_id=0,
                    username=user.username,
                    display_name=user.display_name,
                    total_xp_earned=participation.total_xp_earned,
                    total_ncr_earned=str(participation.total_ncr_earned),
                    tasks_completed=participation.tasks_completed,
                )
            )
            continue
        
        # Get user
        user_query = select(User).where(User.id == participation.user_id)
        user_result = await session.execute(user_query)
        user = user_result.scalar_one()
        
        entries.append(
            EventLeaderboardEntry(
                rank=participation.rank or 0,
                user_id=participation.user_id,
                telegram_user_id=account.telegram_user_id,
                username=account.username or user.username,
                display_name=user.display_name or account.first_name,
                total_xp_earned=participation.total_xp_earned,
                total_ncr_earned=str(participation.total_ncr_earned),
                tasks_completed=participation.tasks_completed,
            )
        )
    
    # Total participants count
    count_query = (
        select(func.count(EventParticipation.id))
        .where(EventParticipation.event_id == event_id)
    )
    count_result = await session.execute(count_query)
    total_participants = count_result.scalar_one() or 0
    
    return EventLeaderboardResponse(
        event_id=event_id,
        event_name=event.name,
        entries=entries,
        total_participants=total_participants,
        updated_at=datetime.utcnow(),
    )


@router.get(
    "/{event_id}/stats",
    summary="Event istatistikleri (admin)",
)
async def get_event_stats_admin(
    event_id: int,
    session: AsyncSession = Depends(get_session),
    _admin: User = Depends(get_admin_user),
):
    """
    Event istatistiklerini getir (admin).
    """
    # Get event
    event_query = select(Event).where(Event.id == event_id)
    event_result = await session.execute(event_query)
    event = event_result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )
    
    # Stats
    participation_count_result = await session.execute(
        select(func.count(EventParticipation.id)).where(
            EventParticipation.event_id == event_id
        )
    )
    participation_count = participation_count_result.scalar_one() or 0
    
    total_xp_result = await session.execute(
        select(func.sum(EventParticipation.total_xp_earned)).where(
            EventParticipation.event_id == event_id
        )
    )
    total_xp = total_xp_result.scalar_one() or 0
    
    total_ncr_result = await session.execute(
        select(func.sum(EventParticipation.total_ncr_earned)).where(
            EventParticipation.event_id == event_id
        )
    )
    total_ncr = total_ncr_result.scalar_one() or 0
    
    total_tasks_result = await session.execute(
        select(func.sum(EventParticipation.tasks_completed)).where(
            EventParticipation.event_id == event_id
        )
    )
    total_tasks = total_tasks_result.scalar_one() or 0
    
    # Event tasks count
    tasks_count_result = await session.execute(
        select(func.count(EventTask.id)).where(EventTask.event_id == event_id)
    )
    tasks_count = tasks_count_result.scalar_one() or 0
    
    # Top 3 participants
    top_participants_query = (
        select(EventParticipation)
        .where(EventParticipation.event_id == event_id)
        .order_by(EventParticipation.total_xp_earned.desc())
        .limit(3)
    )
    top_participants_result = await session.execute(top_participants_query)
    top_participants = top_participants_result.scalars().all()
    
    return {
        "event_id": event_id,
        "event_name": event.name,
        "event_code": event.code,
        "status": event.status.value,
        "event_type": event.event_type.value,
        "starts_at": event.starts_at,
        "ends_at": event.ends_at,
        "stats": {
            "total_participants": participation_count,
            "total_xp_distributed": total_xp,
            "total_ncr_distributed": str(total_ncr),
            "total_tasks_completed": total_tasks,
            "event_tasks_count": tasks_count,
            "avg_xp_per_participant": total_xp / participation_count if participation_count > 0 else 0,
            "avg_tasks_per_participant": total_tasks / participation_count if participation_count > 0 else 0,
        },
        "top_3": [
            {
                "user_id": p.user_id,
                "xp": p.total_xp_earned,
                "tasks": p.tasks_completed,
                "rank": idx + 1,
            }
            for idx, p in enumerate(top_participants)
        ],
    }

