"""
Quest Service - QuestFactory Logic
Günlük quest'leri oluşturan ve yöneten servis
"""
from datetime import datetime, timedelta
from typing import Optional
from decimal import Decimal

from sqlalchemy import and_, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.telegram_gateway.task_models import (
    Task,
    TaskAssignment,
    TaskSubmission,
    TaskStatus,
    SubmissionStatus,
)
from app.xp_loyalty.service import XpLoyaltyService


class QuestService:
    """
    Quest generation ve yönetim servisi.
    
    Kullanıcıya günlük quest'leri oluşturur ve atar.
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_user_quests(
        self,
        user_id: int,
        check_onboarding: bool = True,
    ) -> list[Task]:
        """
        Kullanıcı için günlük quest'leri getir.
        
        Args:
            user_id: Kullanıcı ID
            check_onboarding: Onboarding tamamlanmış mı kontrol et
        
        Returns:
            Kullanıcıya atanmış aktif quest'ler
        """
        # TODO: Onboarding check
        # if check_onboarding:
        #     onboarding_complete = await self.check_onboarding_complete(user_id)
        #     if not onboarding_complete:
        #         return []  # Onboarding tamamlanmamışsa quest yok
        
        now = datetime.utcnow()
        
        # Aktif task'ları getir
        active_tasks_query = (
            select(Task)
            .where(
                and_(
                    Task.status == TaskStatus.ACTIVE,
                    or_(
                        Task.expires_at.is_(None),
                        Task.expires_at >= now,
                    ),
                )
            )
        )
        tasks_result = await self.session.execute(active_tasks_query)
        all_tasks = tasks_result.scalars().all()
        
        # Kullanıcıya atanmış quest'leri filtrele
        user_quests = []
        
        for task in all_tasks:
            # Assignment kontrolü
            assignment_result = await self.session.execute(
                select(TaskAssignment).where(
                    and_(
                        TaskAssignment.user_id == user_id,
                        TaskAssignment.task_id == task.id,
                        TaskAssignment.is_active == True,
                        or_(
                            TaskAssignment.expires_at.is_(None),
                            TaskAssignment.expires_at >= now,
                        ),
                    )
                )
            )
            assignment = assignment_result.scalar_one_or_none()
            
            if not assignment:
                # Auto-assign daily tasks
                if task.category == "daily":
                    # Check if user already completed this task today
                    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                    submission_result = await self.session.execute(
                        select(TaskSubmission).where(
                            and_(
                                TaskSubmission.user_id == user_id,
                                TaskSubmission.task_id == task.id,
                                TaskSubmission.submitted_at >= today_start,
                                TaskSubmission.status.in_([
                                    SubmissionStatus.APPROVED,
                                    SubmissionStatus.REWARDED,
                                ]),
                            )
                        )
                    )
                    existing_submission = submission_result.scalar_one_or_none()
                    
                    if not existing_submission:
                        # Create assignment
                        assignment = TaskAssignment(
                            user_id=user_id,
                            task_id=task.id,
                            is_active=True,
                            expires_at=now.replace(hour=23, minute=59, second=59) if task.category == "daily" else None,
                        )
                        self.session.add(assignment)
                        await self.session.commit()
                        await self.session.refresh(assignment)
            
            if assignment:
                # Check completion status
                submission_result = await self.session.execute(
                    select(TaskSubmission).where(
                        and_(
                            TaskSubmission.user_id == user_id,
                            TaskSubmission.task_id == task.id,
                        )
                    ).order_by(TaskSubmission.submitted_at.desc())
                )
                submission = submission_result.scalar_one_or_none()
                
                # Quest status belirle
                if submission and submission.status in [SubmissionStatus.APPROVED, SubmissionStatus.REWARDED]:
                    # Completed
                    continue  # Skip completed quests for now
                else:
                    # Available
                    user_quests.append(task)
        
        return user_quests
    
    async def check_onboarding_complete(self, user_id: int) -> bool:
        """
        Kullanıcının onboarding'i tamamlanmış mı kontrol et.
        
        TODO: Onboarding session kontrolü
        """
        # Placeholder - implement based on onboarding logic
        return True  # For now, assume complete

