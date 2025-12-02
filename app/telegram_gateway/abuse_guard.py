"""
Telegram Gateway - Abuse & Rate Limiting Guards
Spam, abuse ve rate limiting koruması
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.telegram_gateway.task_models import (
    TaskSubmission,
    ReferralReward,
    TaskAssignment,
    Task,
)


class AbuseGuard:
    """Abuse ve rate limiting kontrolü."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def check_task_submission_allowed(
        self,
        user_id: int,
        task_id: str,
        external_id: Optional[str] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Görev submit edilebilir mi kontrol et.
        
        Returns:
            (allowed, reason)
        """
        # 1. Idempotency check (external_id)
        if external_id:
            existing = await self.session.execute(
                select(TaskSubmission).where(
                    TaskSubmission.external_id == external_id
                )
            )
            if existing.scalar_one_or_none():
                return False, "Bu submission zaten işlendi (idempotency)"
        
        # 2. Duplicate check (user_id, task_id)
        existing = await self.session.execute(
            select(TaskSubmission).where(
                and_(
                    TaskSubmission.user_id == user_id,
                    TaskSubmission.task_id == task_id,
                )
            )
        )
        submission = existing.scalar_one_or_none()
        
        if submission:
            # Eğer zaten rewarded ise, tekrar izin verme
            if submission.status == "rewarded":
                return False, "Bu görev zaten tamamlandı ve ödül verildi"
            
            # Eğer pending ise, cooldown kontrolü yap
            if submission.status == "pending":
                # Task'ın cooldown'u var mı kontrol et
                task_result = await self.session.execute(
                    select(Task).where(Task.id == task_id)
                )
                task = task_result.scalar_one_or_none()
                
                if task and task.cooldown_seconds > 0:
                    elapsed = (datetime.utcnow() - submission.submitted_at).total_seconds()
                    if elapsed < task.cooldown_seconds:
                        remaining = int(task.cooldown_seconds - elapsed)
                        return False, f"Cooldown aktif. {remaining} saniye sonra tekrar deneyebilirsin."
        
        # 3. Task max_completions kontrolü
        task_result = await self.session.execute(
            select(Task).where(Task.id == task_id)
        )
        task = task_result.scalar_one_or_none()
        
        if task and task.max_completions_per_user > 0:
            completed_count = await self.session.execute(
                select(func.count(TaskSubmission.id)).where(
                    and_(
                        TaskSubmission.user_id == user_id,
                        TaskSubmission.task_id == task_id,
                        TaskSubmission.status == "rewarded",
                    )
                )
            )
            count = completed_count.scalar_one()
            
            if count >= task.max_completions_per_user:
                return False, f"Bu görev maksimum {task.max_completions_per_user} kez tamamlanabilir"
        
        # 4. Rate limiting: Son 1 saatte kaç submission?
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_count = await self.session.execute(
            select(func.count(TaskSubmission.id)).where(
                and_(
                    TaskSubmission.user_id == user_id,
                    TaskSubmission.submitted_at >= one_hour_ago,
                )
            )
        )
        count = recent_count.scalar_one()
        
        # Max 20 submission per hour
        if count >= 20:
            return False, "Rate limit: Saatte maksimum 20 görev tamamlayabilirsin"
        
        return True, None
    
    async def check_referral_allowed(
        self,
        referrer_user_id: int,
        referred_user_id: int,
    ) -> tuple[bool, Optional[str]]:
        """
        Referral ödülü verilebilir mi kontrol et.
        
        Returns:
            (allowed, reason)
        """
        # 1. Self-referral koruması
        if referrer_user_id == referred_user_id:
            return False, "Kendini refer edemezsin"
        
        # 2. Duplicate check
        existing = await self.session.execute(
            select(ReferralReward).where(
                and_(
                    ReferralReward.referrer_user_id == referrer_user_id,
                    ReferralReward.referred_user_id == referred_user_id,
                )
            )
        )
        if existing.scalar_one_or_none():
            return False, "Bu referral zaten ödüllendirildi"
        
        # 3. Referred user'ın hesap yaşı (spam koruması)
        from app.identity.models import User
        
        referred_user_result = await self.session.execute(
            select(User).where(User.id == referred_user_id)
        )
        referred_user = referred_user_result.scalar_one_or_none()
        
        if referred_user:
            account_age = (datetime.utcnow() - referred_user.created_at).total_seconds()
            # Minimum 1 saat hesap yaşı
            if account_age < 3600:
                return False, "Refer edilen kullanıcının hesabı en az 1 saat olmalı"
        
        return True, None
    
    async def check_task_access(
        self,
        user_id: int,
        task_id: str,
    ) -> tuple[bool, Optional[str]]:
        """
        Kullanıcı bu göreve erişebilir mi?
        
        Returns:
            (allowed, reason)
        """
        # Task var mı ve aktif mi?
        task_result = await self.session.execute(
            select(Task).where(Task.id == task_id)
        )
        task = task_result.scalar_one_or_none()
        
        if not task:
            return False, "Görev bulunamadı"
        
        if task.status != "active":
            return False, f"Görev şu an aktif değil (status: {task.status})"
        
        # Expires check
        if task.expires_at and task.expires_at < datetime.utcnow():
            return False, "Görev süresi dolmuş"
        
        # Assignment check (opsiyonel - eğer assignment gerekiyorsa)
        assignment_result = await self.session.execute(
            select(TaskAssignment).where(
                and_(
                    TaskAssignment.user_id == user_id,
                    TaskAssignment.task_id == task_id,
                    TaskAssignment.is_active == True,
                )
            )
        )
        assignment = assignment_result.scalar_one_or_none()
        
        # Eğer assignment varsa ve expires_at geçmişse
        if assignment and assignment.expires_at and assignment.expires_at < datetime.utcnow():
            return False, "Görev atamanızın süresi dolmuş"
        
        return True, None

