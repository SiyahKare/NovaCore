"""
Telegram Gateway - Event Service
Event bonus logic ve participation management
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.telegram_gateway.event_models import (
    Event,
    EventTask,
    EventParticipation,
    EventStatus,
)


class EventService:
    """Event işlemleri servisi."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_active_events_for_task(
        self,
        task_id: str,
        user_id: int,
    ) -> list[tuple[Event, EventTask]]:  # type: ignore
        """
        Bir task için aktif event'leri ve event-task bağlantılarını getir.
        
        Sadece kullanıcının katıldığı event'ler döner.
        """
        now = datetime.utcnow()
        
        # Aktif event'leri bul
        events_query = (
            select(Event)
            .where(
                and_(
                    Event.status == EventStatus.ACTIVE,
                    Event.starts_at <= now,
                    Event.ends_at >= now,
                )
            )
        )
        events_result = await self.session.execute(events_query)
        active_events = events_result.scalars().all()
        
        if not active_events:
            return []
        
        # Event ID'leri
        event_ids = [ev.id for ev in active_events]
        
        # Bu task'a bağlı event'leri bul
        event_tasks_query = (
            select(EventTask)
            .where(
                and_(
                    EventTask.task_id == task_id,
                    EventTask.event_id.in_(event_ids),
                )
            )
        )
        event_tasks_result = await self.session.execute(event_tasks_query)
        event_tasks = event_tasks_result.scalars().all()
        
        # Kullanıcının katıldığı event'leri filtrele
        event_task_map = {et.event_id: et for et in event_tasks}
        event_map = {ev.id: ev for ev in active_events}
        
        # Participation kontrolü
        participation_query = (
            select(EventParticipation.event_id)
            .where(
                and_(
                    EventParticipation.user_id == user_id,
                    EventParticipation.event_id.in_(event_ids),
                )
            )
        )
        participation_result = await self.session.execute(participation_query)
        joined_event_ids = set(participation_result.scalars().all())
        
        # Sadece katıldığı event'leri döndür
        result = []
        for event_id, event_task in event_task_map.items():
            if event_id in joined_event_ids:
                event = event_map.get(event_id)
                if event:
                    result.append((event, event_task))
        
        return result
    
    async def apply_event_bonuses(
        self,
        user_id: int,
        task_id: str,
        base_xp: int,
        base_ncr: Decimal,
    ) -> tuple[int, Decimal]:
        """
        Event bonus'larını uygula ve participation'ı güncelle.
        
        Returns:
            (total_xp, total_ncr) - event bonus'ları dahil
        """
        events_with_tasks = await self.get_active_events_for_task(task_id, user_id)
        
        if not events_with_tasks:
            return base_xp, base_ncr
        
        total_xp = base_xp
        total_ncr = base_ncr
        
        for event, event_task in events_with_tasks:
            # Multiplier'ları al (event_task override varsa onu kullan)
            xp_mult = event_task.reward_multiplier_xp or event.reward_multiplier_xp or 1.0
            ncr_mult = event_task.reward_multiplier_ncr or event.reward_multiplier_ncr or 1.0
            
            # Bonus hesapla
            bonus_xp = int(base_xp * (xp_mult - 1.0))
            bonus_ncr = base_ncr * (ncr_mult - 1.0)
            
            total_xp += bonus_xp
            total_ncr += bonus_ncr
            
            # Participation'ı güncelle
            await self.update_event_participation(
                event_id=event.id,
                user_id=user_id,
                xp_earned=base_xp + bonus_xp,
                ncr_earned=base_ncr + bonus_ncr,
            )
        
        return total_xp, total_ncr
    
    async def update_event_participation(
        self,
        event_id: int,
        user_id: int,
        xp_earned: int,
        ncr_earned: Decimal,
    ) -> EventParticipation:
        """
        Event participation'ı güncelle (skor artır).
        """
        participation_query = (
            select(EventParticipation)
            .where(
                and_(
                    EventParticipation.event_id == event_id,
                    EventParticipation.user_id == user_id,
                )
            )
        )
        participation_result = await self.session.execute(participation_query)
        participation = participation_result.scalar_one_or_none()
        
        if not participation:
            # İlk katılım (join olmadan task yapılmış olabilir)
            participation = EventParticipation(
                event_id=event_id,
                user_id=user_id,
                total_xp_earned=xp_earned,
                total_ncr_earned=ncr_earned,
                tasks_completed=1,
            )
            self.session.add(participation)
        else:
            participation.total_xp_earned += xp_earned
            participation.total_ncr_earned += ncr_earned
            participation.tasks_completed += 1
            participation.updated_at = datetime.utcnow()
            self.session.add(participation)
        
        await self.session.commit()
        await self.session.refresh(participation)
        
        return participation
    
    async def get_active_events(
        self,
        user_id: Optional[int] = None,
    ) -> list[Event]:  # type: ignore
        """
        Aktif event'leri getir.
        
        Eğer user_id verilirse, sadece kullanıcının katıldığı event'ler döner.
        """
        now = datetime.utcnow()
        
        query = (
            select(Event)
            .where(
                and_(
                    Event.status == EventStatus.ACTIVE,
                    Event.starts_at <= now,
                    Event.ends_at >= now,
                )
            )
            .order_by(Event.starts_at.desc())
        )
        
        if user_id:
            # Sadece katıldığı event'ler
            participation_query = (
                select(EventParticipation.event_id)
                .where(EventParticipation.user_id == user_id)
            )
            participation_result = await self.session.execute(participation_query)
            joined_event_ids = set(participation_result.scalars().all())
            
            query = query.where(Event.id.in_(joined_event_ids))
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def join_event(
        self,
        event_id: int,
        user_id: int,
    ) -> EventParticipation:
        """
        Kullanıcıyı event'e katıl.
        """
        # Event var mı ve aktif mi?
        event_query = select(Event).where(Event.id == event_id)
        event_result = await self.session.execute(event_query)
        event = event_result.scalar_one_or_none()
        
        if not event:
            raise ValueError("Event not found")
        
        if event.status != EventStatus.ACTIVE:
            raise ValueError(f"Event is not active (status: {event.status})")
        
        now = datetime.utcnow()
        if not (event.starts_at <= now <= event.ends_at):
            raise ValueError("Event is not currently active")
        
        # Zaten katılmış mı?
        participation_query = (
            select(EventParticipation)
            .where(
                and_(
                    EventParticipation.event_id == event_id,
                    EventParticipation.user_id == user_id,
                )
            )
        )
        participation_result = await self.session.execute(participation_query)
        existing = participation_result.scalar_one_or_none()
        
        if existing:
            return existing
        
        # Yeni participation
        participation = EventParticipation(
            event_id=event_id,
            user_id=user_id,
        )
        self.session.add(participation)
        await self.session.commit()
        await self.session.refresh(participation)
        
        return participation
    
    async def get_event_leaderboard(
        self,
        event_id: int,
        limit: int = 20,
    ) -> list[EventParticipation]:
        """
        Event leaderboard'u getir.
        """
        query = (
            select(EventParticipation)
            .where(EventParticipation.event_id == event_id)
            .order_by(
                EventParticipation.total_xp_earned.desc(),
                EventParticipation.tasks_completed.desc(),
            )
            .limit(limit)
        )
        
        result = await self.session.execute(query)
        participations = list(result.scalars().all())
        
        # Rank'leri set et
        for rank, participation in enumerate(participations, 1):
            if participation.rank != rank:
                participation.rank = rank
                self.session.add(participation)
        
        await self.session.commit()
        
        return participations

