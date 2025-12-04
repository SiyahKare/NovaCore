"""
Content Curator Service
Task → CreatorAsset dönüşümü ve ajans havuzuna aktarım
"""
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.agency.models import CreatorAsset, CreatorAssetStatus, AssetMediaType
from app.telegram_gateway.task_models import TaskSubmission
from app.identity.models import User
from app.abuse.service import AbuseGuard
from app.xp_loyalty.service import XpLoyaltyService
from app.core.logging import get_logger

logger = get_logger("content_curator")


class ContentCuratorConfig:
    """
    Ajansa düşecek içerikler için threshold ayarları.
    """
    MIN_AI_SCORE = 90.0  # AI total score eşiği
    MAX_RISK_SCORE = 3.0  # RiskScore bu seviyenin altında olmalı
    MIN_SIYAH_SCORE = 75.0  # vibe kalitesi
    ALLOWED_MEDIA_TYPES = {"IMAGE", "VIDEO"}  # text-only içeriği şimdilik almıyoruz


async def should_curate(
    session: AsyncSession,
    submission: TaskSubmission,
    user: User,
) -> bool:
    """
    Bu submission, ajans havuzuna girmeyi hak ediyor mu?
    """
    # AI score kontrolü (proof_metadata içinde olabilir)
    ai_total_score = submission.proof_metadata.get("ai_total_score") if submission.proof_metadata else None
    
    if ai_total_score is None:
        return False
    
    if ai_total_score < ContentCuratorConfig.MIN_AI_SCORE:
        return False
    
    # RiskScore kontrolü
    abuse_guard = AbuseGuard(session)
    risk_profile = await abuse_guard.get_or_create_profile(user.id)
    
    if risk_profile.risk_score > ContentCuratorConfig.MAX_RISK_SCORE:
        return False
    
    # SiyahScore kontrolü (Loyalty'den level/streak'e göre tahmin)
    loyalty_service = XpLoyaltyService(session)
    loyalty = await loyalty_service.get_loyalty_profile(user.id)
    
    # Basit SiyahScore tahmini (level + streak'e göre)
    siyah_score = 60.0
    if loyalty:
        siyah_score = min(100.0, 60.0 + (loyalty.level * 5) + (loyalty.current_streak * 0.5))
    
    if siyah_score < ContentCuratorConfig.MIN_SIYAH_SCORE:
        return False
    
    # Proof type kontrolü (Task'tan alınır)
    # TaskSubmission'da task_id var, Task'ı çekip proof_type kontrol edelim
    from app.telegram_gateway.task_models import Task
    task_result = await session.execute(
        select(Task).where(Task.id == submission.task_id)
    )
    task = task_result.scalar_one_or_none()
    
    if not task:
        return False
    
    proof_type = task.proof_type.value if task.proof_type else ""
    if proof_type.upper() not in ContentCuratorConfig.ALLOWED_MEDIA_TYPES:
        return False
    
    return True


def infer_media_type(submission: TaskSubmission, task_proof_type: str) -> AssetMediaType:
    """Media tipini çıkar."""
    proof_type = (task_proof_type or "").upper()
    if proof_type == "VIDEO":
        return AssetMediaType.VIDEO
    if proof_type == "TEXT":
        return AssetMediaType.TEXT
    return AssetMediaType.IMAGE


def build_tags(submission: TaskSubmission, task_title: str) -> Optional[str]:
    """Tag'leri oluştur."""
    tags = []
    
    # Task key'den (varsa)
    if submission.proof_metadata and submission.proof_metadata.get("task_key"):
        tags.append(submission.proof_metadata.get("task_key"))
    
    # Basit keyword heuristics
    title = (task_title or "").lower()
    if "whatsapp" in title:
        tags.append("boss_whatsapp")
    if "manifest" in title:
        tags.append("manifest")
    if "fork" in title:
        tags.append("timeline_fork")
    if "meme" in title:
        tags.append("meme")
    if "hook" in title:
        tags.append("hook")
    
    return ",".join(sorted(set(tags))) if tags else None


async def curate_from_submission(
    session: AsyncSession,
    submission_id: int,
) -> Optional[CreatorAsset]:
    """
    TaskSubmission → CreatorAsset dönüşümü.
    
    Görev pipeline'ı, başarılı submission sonrası burayı çağırır.
    """
    # Get submission
    submission_result = await session.execute(
        select(TaskSubmission).where(TaskSubmission.id == submission_id)
    )
    submission = submission_result.scalar_one_or_none()
    
    if not submission:
        return None
    
    # Get user
    user_result = await session.execute(
        select(User).where(User.id == submission.user_id)
    )
    user = user_result.scalar_one_or_none()
    
    if not user:
        return None
    
    # Check if should curate
    if not await should_curate(session, submission, user):
        return None
    
    # Get task for proof_type and title
    from app.telegram_gateway.task_models import Task
    task_result = await session.execute(
        select(Task).where(Task.id == submission.task_id)
    )
    task = task_result.scalar_one_or_none()
    
    if not task:
        return None
    
    # Get AI scores from metadata
    metadata = submission.proof_metadata or {}
    ai_total_score = metadata.get("ai_total_score", 0.0)
    ai_creativity_score = metadata.get("ai_creativity_score", 0.0)
    ai_aesthetic_score = metadata.get("ai_aesthetic_score", 0.0)
    ai_algo_fit_score = metadata.get("ai_algo_fit_score", 0.0)
    
    # Get RiskScore snapshot
    abuse_guard = AbuseGuard(session)
    risk_profile = await abuse_guard.get_or_create_profile(user.id)
    
    # Get SiyahScore snapshot
    loyalty_service = XpLoyaltyService(session)
    loyalty = await loyalty_service.get_loyalty_profile(user.id)
    siyah_score = 60.0
    if loyalty:
        siyah_score = min(100.0, 60.0 + (loyalty.level * 5) + (loyalty.current_streak * 0.5))
    
    # Infer media type
    media_type = infer_media_type(submission, task.proof_type.value if task.proof_type else "")
    
    # Build asset
    asset = CreatorAsset(
        user_id=submission.user_id,
        task_id=submission.task_id,
        submission_id=submission.id,
        media_type=media_type,
        media_url=submission.proof or "",  # S3 / CDN URL
        caption=metadata.get("ai_generated_caption") or metadata.get("user_caption"),
        hook_script=metadata.get("ai_generated_hook"),
        platform_hint=metadata.get("platform_hint"),
        ai_total_score=ai_total_score,
        ai_creativity_score=ai_creativity_score,
        ai_aesthetic_score=ai_aesthetic_score,
        ai_algo_fit_score=ai_algo_fit_score,
        siyah_score_snapshot=siyah_score,
        risk_score_snapshot=risk_profile.risk_score,
        tags=build_tags(submission, task.title),
        status=CreatorAssetStatus.CURATED,
    )
    
    session.add(asset)
    await session.commit()
    await session.refresh(asset)
    
    logger.info(
        "creator_asset_curated",
        asset_id=asset.id,
        user_id=asset.user_id,
        submission_id=submission_id,
        ai_score=ai_total_score,
    )
    
    return asset

