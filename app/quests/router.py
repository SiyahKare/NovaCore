"""
Quest Router - FastAPI Endpoints
Telegram bot entegrasyonu için API
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.db import get_session
from app.core.security import get_admin_user
from app.identity.models import User
from app.telegram_gateway.router import get_telegram_account, verify_bridge_token
from app.telegram_gateway.models import TelegramAccount
from .models import UserQuest
from .enums import QuestStatus
from .service import generate_daily_quests_for_user, get_active_quests
from .completion import submit_quest_proof
from .hitl import process_hitl_decision


router = APIRouter(prefix="/api/v1/telegram/quests", tags=["telegram-quests"])

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
    response_model=UserQuest,
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
    
    - AbuseGuard kontrolü
    - HouseEdge reward hesaplama
    - Treasury Cap uygulama
    - NCR + XP dağıtımı
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
        return uq
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


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

