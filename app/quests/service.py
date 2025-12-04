"""
Quest Service - QuestFactory + DB Entegrasyonu
"""
from datetime import datetime, timedelta
from typing import List

from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from .models import UserQuest
from .enums import QuestStatus, QuestType
from .factory import QuestFactory, RuntimeQuest


DEFAULT_EXPIRY_HOURS = 24  # MVP: günlük quest


async def generate_daily_quests_for_user(
    session: AsyncSession,
    user_id: int,
) -> List[UserQuest]:
    """
    Kullanıcı için yeni günlük quest seti üretir:
    
    - QuestFactory'den runtime quest listesi çeker
    - DB'ye UserQuest olarak yazar
    - Zaten bugün oluşturulmuş aktif quest'ler varsa yeniden spam yapmaz (idempotent).
    """
    # Bugün daha önce atanmış quest var mı kontrol et
    today = datetime.utcnow().date()
    today_start = datetime(today.year, today.month, today.day)
    
    stmt = (
        select(UserQuest)
        .where(UserQuest.user_id == user_id)
        .where(UserQuest.assigned_at >= today_start)
        .where(UserQuest.status.in_([QuestStatus.ASSIGNED, QuestStatus.SUBMITTED, QuestStatus.UNDER_REVIEW]))
    )
    result = await session.execute(stmt)
    existing = result.scalars().all()
    
    if existing:
        return existing  # Zaten üretmişiz; aynısını döndür
    
    # QuestFactory: Buradan runtime quest objeleri geliyor
    runtime_quests = QuestFactory.generate_for_user(user_id=user_id)
    
    user_quests: List[UserQuest] = []
    expires_at = datetime.utcnow() + timedelta(hours=DEFAULT_EXPIRY_HOURS)
    
    for rq in runtime_quests:
        uq = UserQuest(
            user_id=user_id,
            quest_uuid=rq.uuid,
            quest_type=rq.type,
            key=rq.key,
            title=rq.title,
            description=rq.description,
            base_reward_ncr=rq.base_ncr,
            base_reward_xp=rq.base_xp,
            expires_at=expires_at,
            status=QuestStatus.ASSIGNED,
        )
        session.add(uq)
        user_quests.append(uq)
    
    await session.commit()
    for uq in user_quests:
        await session.refresh(uq)
    
    return user_quests


async def get_active_quests(
    session: AsyncSession,
    user_id: int,
) -> List[UserQuest]:
    """
    Kullanıcının süresi geçmemiş, kapanmamış quest'lerini döndürür.
    """
    now = datetime.utcnow()
    
    stmt = (
        select(UserQuest)
        .where(UserQuest.user_id == user_id)
        .where(UserQuest.status.in_([QuestStatus.ASSIGNED, QuestStatus.SUBMITTED, QuestStatus.UNDER_REVIEW]))
        .where(UserQuest.expires_at > now)
        .order_by(UserQuest.assigned_at.desc())
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())

