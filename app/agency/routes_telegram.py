"""
Aurora Contact Telegram Dashboard API Routes
Telegram conversation ve lead yönetimi için endpoint'ler
"""
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, Query, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.db import get_session
from app.core.security import get_admin_user
from app.identity.models import User
from app.agency.models import AgencyClient, PipelineStage
from app.agency.services.chat_manager import ChatManager

router = APIRouter(prefix="/api/v1/admin/telegram", tags=["admin-telegram"])


# ============ Response Models ============

class LeadResponse(BaseModel):
    """Lead response model."""
    id: str
    businessName: str
    contactName: Optional[str] = None
    telegramUsername: Optional[str] = None
    phone: Optional[str] = None
    sector: str
    city: Optional[str] = None
    source: str
    score: int  # 0-100
    segment: str  # "hot" | "warm" | "cold" | "spam"
    status: str
    lastMessagePreview: Optional[str] = None
    lastContactAt: Optional[str] = None
    lastContactChannel: Optional[str] = None
    priority: str
    risk: str
    monthlyMsgVolumeEst: Optional[str] = None


class MessageResponse(BaseModel):
    """Message response model."""
    id: str
    from_: str = Field(alias="from")
    text: str
    createdAt: str
    meta: Optional[dict] = None

    class Config:
        populate_by_name = True


class ConversationResponse(BaseModel):
    """Conversation response model."""
    id: str
    leadId: str
    title: str
    channel: str
    unreadCount: int
    lastMessageAt: str
    segment: str
    score: int
    status: str
    messages: List[MessageResponse]


class HandoffEventResponse(BaseModel):
    """Handoff event response model."""
    id: str
    at: str
    from_: str = Field(alias="from")
    to: str
    reason: str
    note: Optional[str] = None

    class Config:
        populate_by_name = True


# ============ Helper Functions ============

def calculate_lead_score(client: AgencyClient) -> int:
    """Lead score hesapla (0-100)."""
    score = 50  # Base score
    
    # Pipeline stage'e göre
    if client.pipeline_stage == PipelineStage.WON:
        score = 100
    elif client.pipeline_stage == PipelineStage.NEGOTIATION:
        score = 85
    elif client.pipeline_stage == PipelineStage.DEMO_DONE:
        score = 75
    elif client.pipeline_stage == PipelineStage.CONTACTED:
        score = 60
    elif client.pipeline_stage == PipelineStage.LEAD:
        score = 40
    
    # MRR'e göre
    if client.monthly_mrr_try > 0:
        score += min(20, int(client.monthly_mrr_try / 100))
    
    return min(100, max(0, score))


def get_lead_segment(score: int) -> str:
    """Score'a göre segment belirle."""
    if score >= 80:
        return "hot"
    elif score >= 60:
        return "warm"
    elif score >= 40:
        return "cold"
    else:
        return "spam"


def agency_client_to_lead(client: AgencyClient) -> LeadResponse:
    """AgencyClient'i LeadResponse'a dönüştür."""
    score = calculate_lead_score(client)
    segment = get_lead_segment(score)
    
    return LeadResponse(
        id=f"lead-{client.id}",
        businessName=client.name,
        contactName=client.contact_person,
        phone=client.contact_phone,
        sector="Unknown",  # TODO: AgencyClient'e sector field'ı ekle
        city=None,  # TODO: AgencyClient'e city field'ı ekle
        source="telegram",
        score=score,
        segment=segment,
        status=client.pipeline_stage.value.lower().replace("_", " "),
        priority="high" if score >= 80 else "medium" if score >= 60 else "low",
        risk="low",  # TODO: Risk hesaplama
        lastContactAt=client.updated_at.isoformat() if client.updated_at else None,
        lastContactChannel="telegram",
    )


# ============ Endpoints ============

@router.get(
    "/conversations",
    response_model=List[ConversationResponse],
    summary="Telegram conversations listesi",
)
async def list_conversations(
    segment: Optional[str] = Query(None, description="Filter by segment: hot, warm, cold, spam"),
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    _admin: User = Depends(get_admin_user),
):
    """
    Telegram conversations listesini getir.
    Şimdilik AgencyClient'lerden oluşturuluyor (ileride Conversation model'e geçilebilir).
    """
    stmt = select(AgencyClient).order_by(AgencyClient.updated_at.desc()).limit(limit)
    
    result = await session.execute(stmt)
    clients = result.scalars().all()
    
    conversations = []
    for client in clients:
        lead = agency_client_to_lead(client)
        
        # Segment filtreleme
        if segment and lead.segment != segment:
            continue
        
        # Mock conversation (ileride gerçek Conversation model'den gelecek)
        conversation = ConversationResponse(
            id=f"conv-{client.id}",
            leadId=lead.id,
            title=f"{client.name} {f'• @{client.contact_person}' if client.contact_person else ''}",
            channel="telegram",
            unreadCount=0,  # TODO: Gerçek unread count
            lastMessageAt=client.updated_at.isoformat() if client.updated_at else datetime.utcnow().isoformat(),
            segment=lead.segment,
            score=lead.score,
            status=lead.status,
            messages=[],  # TODO: Gerçek messages
        )
        conversations.append(conversation)
    
    return conversations


@router.get(
    "/conversations/{conversation_id}",
    response_model=ConversationResponse,
    summary="Conversation detayı",
)
async def get_conversation(
    conversation_id: str,
    session: AsyncSession = Depends(get_session),
    _admin: User = Depends(get_admin_user),
):
    """Conversation detayını getir (messages dahil)."""
    # conversation_id format: "conv-{client_id}"
    client_id = int(conversation_id.replace("conv-", ""))
    
    stmt = select(AgencyClient).where(AgencyClient.id == client_id)
    result = await session.execute(stmt)
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )
    
    lead = agency_client_to_lead(client)
    
    # Mock messages (ileride gerçek Message model'den gelecek)
    messages = [
        MessageResponse(
            id=f"msg-{client.id}-1",
            from_="user",
            text="Merhaba, WhatsApp otomasyonu hakkında bilgi almak istiyorum.",
            createdAt=client.created_at.isoformat() if client.created_at else datetime.utcnow().isoformat(),
        ),
        MessageResponse(
            id=f"msg-{client.id}-2",
            from_="ai",
            text="Merhaba! Aurora Contact'a hoş geldin. WhatsApp otomasyonu hakkında bilgi almak ister misin? 🚀",
            createdAt=datetime.utcnow().isoformat(),
            meta={"action": "reply_only"},
        ),
    ]
    
    conversation = ConversationResponse(
        id=conversation_id,
        leadId=lead.id,
        title=f"{client.name} {f'• @{client.contact_person}' if client.contact_person else ''}",
        channel="telegram",
        unreadCount=0,
        lastMessageAt=client.updated_at.isoformat() if client.updated_at else datetime.utcnow().isoformat(),
        segment=lead.segment,
        score=lead.score,
        status=lead.status,
        messages=messages,
    )
    
    return conversation


@router.get(
    "/leads/{lead_id}",
    response_model=LeadResponse,
    summary="Lead detayı",
)
async def get_lead(
    lead_id: str,
    session: AsyncSession = Depends(get_session),
    _admin: User = Depends(get_admin_user),
):
    """Lead detayını getir."""
    # lead_id format: "lead-{client_id}"
    client_id = int(lead_id.replace("lead-", ""))
    
    stmt = select(AgencyClient).where(AgencyClient.id == client_id)
    result = await session.execute(stmt)
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found",
        )
    
    return agency_client_to_lead(client)


@router.post(
    "/conversations/{conversation_id}/send-message",
    summary="Mesaj gönder",
)
async def send_message(
    conversation_id: str,
    text: str = Query(..., description="Message text"),
    agent_mode: str = Query("hybrid", description="ai-only, hybrid, human-only"),
    session: AsyncSession = Depends(get_session),
    _admin: User = Depends(get_admin_user),
):
    """Conversation'a mesaj gönder (AI veya Manual)."""
    # conversation_id format: "conv-{client_id}"
    client_id = int(conversation_id.replace("conv-", ""))
    
    stmt = select(AgencyClient).where(AgencyClient.id == client_id)
    result = await session.execute(stmt)
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )
    
    chat_manager = ChatManager(session)
    
    # AI mode'da ChatManager'a gönder
    if agent_mode in ["ai-only", "hybrid"]:
        reply, tool_calls = await chat_manager.process_hybrid_chat(
            sender_id=0,  # TODO: Gerçek telegram_user_id
            incoming_text=text,
            pipeline_stage=client.pipeline_stage,
            context={"lead_id": client.id},
        )
        
        # TODO: Telethon client üzerinden mesaj gönder
        # await telethon_client.send_message(client.telegram_user_id, reply)
        
        return {
            "success": True,
            "reply": reply,
            "tool_calls": tool_calls,
        }
    else:
        # Manual mode - direkt gönder
        # TODO: Telethon client üzerinden mesaj gönder
        return {
            "success": True,
            "reply": text,
            "tool_calls": None,
        }


@router.post(
    "/conversations/{conversation_id}/handoff",
    summary="Human handoff tetikle",
)
async def trigger_handoff(
    conversation_id: str,
    reason: str = Query(..., description="Handoff reason"),
    session: AsyncSession = Depends(get_session),
    _admin: User = Depends(get_admin_user),
):
    """Human handoff tetikle."""
    # conversation_id format: "conv-{client_id}"
    client_id = int(conversation_id.replace("conv-", ""))
    
    stmt = select(AgencyClient).where(AgencyClient.id == client_id)
    result = await session.execute(stmt)
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )
    
    chat_manager = ChatManager(session)
    await chat_manager.trigger_human_handoff(
        sender_id=0,  # TODO: Gerçek telegram_user_id
        reason=reason,
    )
    
    return {
        "success": True,
        "message": "Human handoff triggered",
    }


@router.post(
    "/leads/{lead_id}/notes",
    summary="Lead notları kaydet",
)
async def save_lead_notes(
    lead_id: str,
    notes: str = Query(..., description="Notes text"),
    session: AsyncSession = Depends(get_session),
    _admin: User = Depends(get_admin_user),
):
    """Lead notlarını kaydet."""
    # lead_id format: "lead-{client_id}"
    client_id = int(lead_id.replace("lead-", ""))
    
    stmt = select(AgencyClient).where(AgencyClient.id == client_id)
    result = await session.execute(stmt)
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found",
        )
    
    # TODO: Notes model'e kaydet (şimdilik sadece log)
    from app.core.logging import get_logger
    logger = get_logger("telegram_dashboard")
    logger.info(
        "lead_notes_saved",
        lead_id=lead_id,
        client_id=client_id,
        notes_preview=notes[:100],
    )
    
    return {
        "success": True,
        "message": "Notes saved",
    }


@router.get(
    "/stats",
    summary="Dashboard istatistikleri",
)
async def get_dashboard_stats(
    session: AsyncSession = Depends(get_session),
    _admin: User = Depends(get_admin_user),
):
    """Dashboard için istatistikler."""
    stmt = select(AgencyClient)
    result = await session.execute(stmt)
    clients = result.scalars().all()
    
    total = len(clients)
    hot = sum(1 for c in clients if get_lead_segment(calculate_lead_score(c)) == "hot")
    warm = sum(1 for c in clients if get_lead_segment(calculate_lead_score(c)) == "warm")
    cold = sum(1 for c in clients if get_lead_segment(calculate_lead_score(c)) == "cold")
    
    return {
        "totalCallsToday": total,
        "hotCount": hot,
        "warmCount": warm,
        "coldCount": cold,
    }

