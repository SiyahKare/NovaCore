"""
AbuseGuard Service
NasipQuest ekonomisini koruyan risk motoru
"""
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from .models import UserRiskProfile, AbuseEvent, AbuseEventType
from .config import (
    ABUSE_EVENT_WEIGHTS,
    MAX_RISK_SCORE,
    MIN_RISK_SCORE,
    RISK_THRESHOLD_REWARD_MULTIPLIER_1,
    RISK_THRESHOLD_REWARD_MULTIPLIER_2,
    RISK_THRESHOLD_REWARD_MULTIPLIER_3,
    RISK_THRESHOLD_FORCED_HITL,
    RISK_THRESHOLD_COOLDOWN,
    LOW_QUALITY_BURST_COUNT,
    TOO_FAST_COMPLETION_SECONDS,
)
from .repository import AbuseRepository
from app.telegram_gateway.task_models import TaskSubmission, SubmissionStatus


class AbuseGuard:
    """
    NasipQuest ekonomisini koruyan risk motoru.
    
    RiskScore hesaplar, ödül çarpanlarını uygular, HITL zorunluluğunu belirler.
    """
    
    def __init__(self, session: AsyncSession):
        self.repo = AbuseRepository(session)
        self.session = session
    
    async def get_or_create_profile(self, user_id: int) -> UserRiskProfile:
        """Kullanıcı risk profilini getir veya oluştur."""
        profile = await self.repo.get_profile(user_id)
        if profile is None:
            profile = UserRiskProfile(
                user_id=user_id,
                risk_score=0.0,
            )
            profile = await self.repo.save_profile(profile)
        return profile
    
    async def register_event(
        self,
        user_id: int,
        event_type: AbuseEventType,
        override_delta: Optional[float] = None,
        meta: Optional[dict] = None,
    ) -> UserRiskProfile:
        """
        Abuse event'ini kaydet ve RiskScore'u güncelle.
        
        Args:
            user_id: Kullanıcı ID
            event_type: Event tipi
            override_delta: Delta değerini override et (opsiyonel)
            meta: Event metadata
        
        Returns:
            Güncellenmiş risk profili
        """
        profile = await self.get_or_create_profile(user_id)
        
        # Delta hesapla
        base_delta = ABUSE_EVENT_WEIGHTS.get(event_type, 0.0)
        delta = override_delta if override_delta is not None else base_delta
        
        # RiskScore'u güncelle
        new_score = profile.risk_score + delta
        new_score = max(MIN_RISK_SCORE, min(MAX_RISK_SCORE, new_score))
        
        profile.risk_score = new_score
        profile.last_event_at = datetime.utcnow()
        
        # Event logla
        event = AbuseEvent(
            user_id=user_id,
            event_type=event_type,
            delta=delta,
            meta=meta or {},
        )
        
        await self.repo.save_profile(profile)
        await self.repo.log_event(event)
        
        return profile
    
    # ------ DECISION LOGIC ------
    
    @staticmethod
    def reward_multiplier(risk_score: float) -> float:
        """
        RiskScore'a göre ödül çarpanı.
        
        0-2: 1.0x (normal)
        3-5: 0.8x (düşük risk)
        6-8: 0.6x (orta risk)
        9-10: 0.0x (yüksek risk, ödül yok)
        """
        if risk_score <= RISK_THRESHOLD_REWARD_MULTIPLIER_1:
            return 1.0
        if risk_score <= RISK_THRESHOLD_REWARD_MULTIPLIER_2:
            return 0.8
        if risk_score <= RISK_THRESHOLD_REWARD_MULTIPLIER_3:
            return 0.6
        return 0.0
    
    @staticmethod
    def requires_forced_hitl(risk_score: float) -> bool:
        """
        6+ risk → AI auto-approve yok, her şey insan gözünden geçer.
        """
        return risk_score >= RISK_THRESHOLD_FORCED_HITL
    
    @staticmethod
    def requires_cooldown(risk_score: float) -> bool:
        """
        9+ risk → hesabı soğut.
        """
        return risk_score >= RISK_THRESHOLD_COOLDOWN
    
    # ------ HEURISTICS ------
    
    async def check_low_quality_burst(self, user_id: int) -> bool:
        """
        Son 24 saatte 5+ auto-reject varsa → LOW_QUALITY_BURST event.
        
        Returns:
            True if burst detected
        """
        since = datetime.utcnow() - timedelta(hours=24)
        rejects = await self.repo.count_rejected_tasks(user_id=user_id, since=since)
        
        if rejects >= LOW_QUALITY_BURST_COUNT:
            await self.register_event(
                user_id=user_id,
                event_type=AbuseEventType.LOW_QUALITY_BURST,
                meta={"rejects_last_24h": rejects},
            )
            return True
        return False
    
    async def check_too_fast_completion(
        self,
        user_id: int,
        task_id: str,
        assigned_at: Optional[datetime],
    ) -> bool:
        """
        Görev çok hızlı tamamlandı mı kontrol et.
        
        Args:
            user_id: Kullanıcı ID
            task_id: Görev ID
            assigned_at: Görev atanma zamanı
        
        Returns:
            True if too fast
        """
        if not assigned_at:
            return False
        
        elapsed = (datetime.utcnow() - assigned_at).total_seconds()
        
        if elapsed < TOO_FAST_COMPLETION_SECONDS:
            await self.register_event(
                user_id=user_id,
                event_type=AbuseEventType.TOO_FAST_COMPLETION,
                meta={
                    "task_id": task_id,
                    "elapsed_seconds": elapsed,
                },
            )
            return True
        return False
    
    async def check_duplicate_proof(
        self,
        user_id: int,
        task_id: str,
        proof_hash: Optional[str],
    ) -> bool:
        """
        Aynı proof daha önce kullanıldı mı kontrol et.
        
        Args:
            user_id: Kullanıcı ID
            task_id: Görev ID
            proof_hash: Proof'un hash'i (md5/sha256)
        
        Returns:
            True if duplicate
        """
        if not proof_hash:
            return False
        
        # Son 30 günde aynı hash ile submission var mı?
        since = datetime.utcnow() - timedelta(days=30)
        
        from sqlalchemy import func
        
        # JSONB field'ı kontrol et
        result = await self.session.execute(
            select(TaskSubmission).where(
                and_(
                    TaskSubmission.user_id == user_id,
                    TaskSubmission.submitted_at >= since,
                )
            )
        )
        submissions = result.scalars().all()
        
        # Check if any submission has the same proof_hash in metadata
        for sub in submissions:
            if sub.proof_metadata and sub.proof_metadata.get("proof_hash") == proof_hash:
                await self.register_event(
                    user_id=user_id,
                    event_type=AbuseEventType.DUPLICATE_PROOF,
                    meta={
                        "task_id": task_id,
                        "previous_submission_id": sub.id,
                        "proof_hash": proof_hash,
                    },
                )
                return True
        return False

