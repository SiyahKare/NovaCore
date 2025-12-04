"""
AbuseGuard Repository
Database I/O operations for RiskScore system
"""
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from .models import UserRiskProfile, AbuseEvent, AbuseEventType
from app.telegram_gateway.task_models import TaskSubmission, SubmissionStatus


class AbuseRepository:
    """AbuseGuard için repository katmanı."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_profile(self, user_id: int) -> Optional[UserRiskProfile]:
        """Kullanıcı risk profilini getir."""
        result = await self.session.execute(
            select(UserRiskProfile).where(UserRiskProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def save_profile(self, profile: UserRiskProfile) -> UserRiskProfile:
        """Risk profilini kaydet/güncelle."""
        profile.updated_at = datetime.utcnow()
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        return profile
    
    async def log_event(self, event: AbuseEvent) -> AbuseEvent:
        """Abuse event'ini logla."""
        self.session.add(event)
        await self.session.commit()
        await self.session.refresh(event)
        return event
    
    async def count_rejected_tasks(
        self,
        user_id: int,
        since: datetime,
    ) -> int:
        """Belirli bir zamandan sonraki reject sayısını say."""
        result = await self.session.execute(
            select(func.count(TaskSubmission.id)).where(
                and_(
                    TaskSubmission.user_id == user_id,
                    TaskSubmission.status == SubmissionStatus.REJECTED,
                    TaskSubmission.submitted_at >= since,
                )
            )
        )
        return result.scalar_one() or 0
    
    async def get_recent_events(
        self,
        user_id: int,
        event_type: Optional[AbuseEventType] = None,
        since: Optional[datetime] = None,
    ) -> list[AbuseEvent]:
        """Kullanıcının son abuse event'lerini getir."""
        query = select(AbuseEvent).where(AbuseEvent.user_id == user_id)
        
        if event_type:
            query = query.where(AbuseEvent.event_type == event_type)
        
        if since:
            query = query.where(AbuseEvent.created_at >= since)
        
        query = query.order_by(AbuseEvent.created_at.desc())
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

