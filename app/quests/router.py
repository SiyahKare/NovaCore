"""
Quest Router - FastAPI Endpoints
Telegram bot entegrasyonu için API
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.db import get_session
from app.core.security import get_admin_user, get_current_user
from app.identity.models import User
from app.telegram_gateway.router import get_telegram_account, verify_bridge_token
from app.telegram_gateway.models import TelegramAccount
from .models import UserQuest
from .enums import QuestStatus
from .service import generate_daily_quests_for_user, get_active_quests
from .completion import submit_quest_proof
from .hitl import process_hitl_decision


router = APIRouter(prefix="/api/v1/telegram/quests", tags=["telegram-quests"])

# Web/Citizen Portal router (JWT auth)
web_router = APIRouter(prefix="/api/v1/quests", tags=["quests"])

# Admin/Ombudsman router
admin_router = APIRouter(prefix="/api/v1/admin/quests", tags=["admin-quests"])


class QuestProofPayload(BaseModel):
    """Quest proof submission payload."""
    quest_uuid: str
    proof_type: str  # "text" | "photo" | "link" | "mixed"
    proof_payload_ref: str  # telegram file id / text id / s3 key
    proof_content: Optional[str] = None  # Direct text content (for text proofs)
    source: str = "telegram"  # telegram | web | api | mobile
    message_id: Optional[str] = None  # Telegram message_id / external reference
    ai_score: float | None = None  # Bot tarafında hesapladıysan buradan geç


class QuestSubmitResponse(BaseModel):
    """Quest submission response - Pipeline durumu."""
    status: str  # "pending_review" | "approved" | "rejected" | "under_review"
    quest_uuid: str
    quest_id: int
    reason: Optional[str] = None  # "queued_for_ai_scoring" | "abuse_guard_block" | "approved" | "rejected"
    risk_delta: Optional[float] = None  # AbuseGuard risk değişimi
    ai_score: Optional[float] = None  # AI scoring sonucu (0-100)
    final_reward_ncr: Optional[float] = None  # Final NCR ödülü (approved ise)
    final_reward_xp: Optional[int] = None  # Final XP ödülü (approved ise)
    final_score: Optional[float] = None  # Final quest score
    marketplace_item_id: Optional[int] = None  # Marketplace'e gönderildiyse item ID


class QuestResponse(BaseModel):
    """Quest response."""
    quests: List[UserQuest]
    total_available: int


@router.get(
    "/today",
    response_model=QuestResponse,
    summary="Günlük quest'leri getir",
)
async def list_today_quests(
    telegram_user_id: int,
    session: AsyncSession = Depends(get_session),
    _verified: bool = Depends(verify_bridge_token),
):
    """
    NasipQuest: Kullanıcının bugünkü quest setini döndürür.
    
    Yoksa QuestFactory -> DB üzerinden üretir.
    """
    account = await get_telegram_account(telegram_user_id, session)
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telegram account not found",
        )
    
    # Generate or get existing quests
    quests = await generate_daily_quests_for_user(session, account.user_id)
    
    return QuestResponse(
        quests=quests,
        total_available=len([q for q in quests if q.status == QuestStatus.ASSIGNED]),
    )


@router.post(
    "/submit",
    response_model=QuestSubmitResponse,
    summary="Quest proof gönder",
)
async def submit_quest(
    payload: QuestProofPayload,
    telegram_user_id: int,
    session: AsyncSession = Depends(get_session),
    _verified: bool = Depends(verify_bridge_token),
):
    """
    Quest proof gönder ve ödül al.
    
    Pipeline:
    1. Quest bul ve kontrol et (expired, status)
    2. AbuseGuard pre-check (cooldown, risk)
    3. QuestProof kaydı oluştur
    4. AI Scoring (PRODUCTION/RESEARCH için)
    5. AbuseGuard post-check (flags → events)
    6. RewardEngine v2 ile NCR/XP hesapla
    7. Treasury Cap uygula
    8. Wallet + XP service'e yaz
    9. Marketplace Bridge (AI Score 70+)
    10. Quest finalize (APPROVED / UNDER_REVIEW / REJECTED)
    """
    account = await get_telegram_account(telegram_user_id, session)
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telegram account not found",
        )
    
    try:
        uq = await submit_quest_proof(
            session=session,
            user_id=account.user_id,
            quest_uuid=payload.quest_uuid,
            proof_type=payload.proof_type,
            proof_payload_ref=payload.proof_payload_ref,
            ai_score=payload.ai_score,
            source=payload.source,
            message_id=payload.message_id,
            proof_content=payload.proof_content,
        )
        
        # Marketplace item ID'yi bul (eğer marketplace'e gönderildiyse)
        marketplace_item_id = None
        if uq.status == QuestStatus.APPROVED and uq.final_score and uq.final_score >= 70:
            from app.marketplace.models import MarketplaceItem
            marketplace_stmt = select(MarketplaceItem).where(
                MarketplaceItem.source_quest_id == uq.id
            ).order_by(MarketplaceItem.created_at.desc())
            marketplace_result = await session.execute(marketplace_stmt)
            marketplace_item = marketplace_result.scalar_one_or_none()
            if marketplace_item:
                marketplace_item_id = marketplace_item.id
        
        # Response model'e çevir
        return QuestSubmitResponse(
            status=uq.status.value if hasattr(uq.status, 'value') else str(uq.status),
            quest_uuid=uq.quest_uuid,
            quest_id=uq.id,
            reason=_get_status_reason(uq.status),
            risk_delta=None,  # TODO: AbuseGuard'dan risk_delta çek
            ai_score=uq.final_score,
            final_reward_ncr=uq.final_reward_ncr,
            final_reward_xp=uq.final_reward_xp,
            final_score=uq.final_score,
            marketplace_item_id=marketplace_item_id,
        )
    except ValueError as e:
        error_msg = str(e)
        # AbuseGuard block durumu
        if "cooldown" in error_msg.lower() or "abuse" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=error_msg,
            )
        # Quest expired / not found
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)


def _get_status_reason(status: QuestStatus) -> str:
    """Quest status'a göre reason string'i döndür."""
    status_map = {
        QuestStatus.ASSIGNED: "assigned",
        QuestStatus.SUBMITTED: "queued_for_ai_scoring",
        QuestStatus.APPROVED: "approved",
        QuestStatus.REJECTED: "rejected",
        QuestStatus.UNDER_REVIEW: "under_review",
        QuestStatus.EXPIRED: "expired",
    }
    return status_map.get(status, "unknown")


@router.get(
    "/active",
    response_model=QuestResponse,
    summary="Aktif quest'leri getir",
)
async def get_active_quests_endpoint(
    telegram_user_id: int,
    session: AsyncSession = Depends(get_session),
    _verified: bool = Depends(verify_bridge_token),
):
    """Kullanıcının aktif quest'lerini döndürür."""
    account = await get_telegram_account(telegram_user_id, session)
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telegram account not found",
        )
    
    quests = await get_active_quests(session, account.user_id)
    
    return QuestResponse(
        quests=quests,
        total_available=len([q for q in quests if q.status == QuestStatus.ASSIGNED]),
    )


# ============ Web/Citizen Portal Endpoints ============

class QuestHistoryItem(BaseModel):
    """Quest history item response."""
    id: int
    quest_uuid: str
    quest_type: str
    key: str
    title: str
    description: str
    base_reward_ncr: float
    base_reward_xp: int
    final_reward_ncr: Optional[float]
    final_reward_xp: Optional[int]
    final_score: Optional[float]
    status: str
    assigned_at: datetime
    submitted_at: Optional[datetime]
    resolved_at: Optional[datetime]
    marketplace_item_id: Optional[int] = None


class QuestHistoryResponse(BaseModel):
    """Quest history response."""
    items: List[QuestHistoryItem]
    total: int
    page: int
    per_page: int


@web_router.get(
    "/me/history",
    response_model=QuestHistoryResponse,
    summary="Kendi quest geçmişimi getir",
)
async def get_my_quest_history(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, description="Filter by status: APPROVED, REJECTED, etc."),
):
    """
    Kullanıcının quest geçmişini getirir.
    
    Tamamlanmış quest'leri (APPROVED, REJECTED, UNDER_REVIEW) gösterir.
    """
    from app.marketplace.models import MarketplaceItem
    
    # Base query - tamamlanmış quest'ler
    stmt = select(UserQuest).where(
        UserQuest.user_id == current_user.id
    ).where(
        UserQuest.status.in_([
            QuestStatus.APPROVED,
            QuestStatus.REJECTED,
            QuestStatus.UNDER_REVIEW,
            QuestStatus.EXPIRED,
        ])
    )
    
    # Status filter
    if status_filter:
        try:
            status_enum = QuestStatus[status_filter.upper()]
            stmt = stmt.where(UserQuest.status == status_enum)
        except KeyError:
            pass  # Invalid status, ignore filter
    
    # Count total
    count_stmt = select(UserQuest).where(
        UserQuest.user_id == current_user.id
    ).where(
        UserQuest.status.in_([
            QuestStatus.APPROVED,
            QuestStatus.REJECTED,
            QuestStatus.UNDER_REVIEW,
            QuestStatus.EXPIRED,
        ])
    )
    if status_filter:
        try:
            status_enum = QuestStatus[status_filter.upper()]
            count_stmt = count_stmt.where(UserQuest.status == status_enum)
        except KeyError:
            pass
    
    total_result = await session.execute(count_stmt)
    total = len(total_result.scalars().all())
    
    # Pagination
    offset = (page - 1) * per_page
    stmt = stmt.order_by(UserQuest.resolved_at.desc(), UserQuest.submitted_at.desc()).offset(offset).limit(per_page)
    
    result = await session.execute(stmt)
    quests = result.scalars().all()
    
    # Marketplace item ID'leri bul
    quest_ids = [q.id for q in quests]
    marketplace_items = {}
    if quest_ids:
        marketplace_stmt = select(MarketplaceItem).where(
            MarketplaceItem.source_quest_id.in_(quest_ids)
        )
        marketplace_result = await session.execute(marketplace_stmt)
        for item in marketplace_result.scalars().all():
            if item.source_quest_id:
                marketplace_items[item.source_quest_id] = item.id
    
    # Response'a çevir
    items = []
    for quest in quests:
        items.append(QuestHistoryItem(
            id=quest.id,
            quest_uuid=quest.quest_uuid,
            quest_type=quest.quest_type.value if hasattr(quest.quest_type, 'value') else str(quest.quest_type),
            key=quest.key,
            title=quest.title,
            description=quest.description or "",
            base_reward_ncr=quest.base_reward_ncr,
            base_reward_xp=quest.base_reward_xp,
            final_reward_ncr=quest.final_reward_ncr,
            final_reward_xp=quest.final_reward_xp,
            final_score=quest.final_score,
            status=quest.status.value if hasattr(quest.status, 'value') else str(quest.status),
            assigned_at=quest.assigned_at,
            submitted_at=quest.submitted_at,
            resolved_at=quest.resolved_at,
            marketplace_item_id=marketplace_items.get(quest.id),
        ))
    
    return QuestHistoryResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
    )
