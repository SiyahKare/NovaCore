# app/justice/nasipcourt_router.py
# NasipCourt DAO v1.0 - API Endpoints

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import List, Optional
from pydantic import BaseModel, Field

from app.core.db import get_session
from app.core.security import get_admin_user
from app.consent.router import get_current_user_id
from app.identity.models import User
from .nasipcourt_models import RiskEvent, JusticeCase, JusticePenalty, JusticeEventType
from .nasipcourt_service import NasipCourtService

router = APIRouter(prefix="/api/v1/justice/nasipcourt", tags=["nasipcourt"])


# --- Request/Response Schemas ---

class RiskEventCreate(BaseModel):
    """RiskEvent oluşturma request."""
    user_id: int
    event_type: JusticeEventType
    score_ai: float = Field(ge=0.0, le=100.0)
    source: str
    meta: Optional[dict] = None


class RiskEventResponse(BaseModel):
    """RiskEvent response."""
    id: int
    event_uuid: str
    user_id: int
    score_ai: float
    score_human: Optional[float]
    event_type: str
    status: str
    timestamp: str
    meta: Optional[dict] = None


class ValidatorVoteRequest(BaseModel):
    """Validator oyu request."""
    vote: str = Field(..., description="APPROVE or REJECT")


class ValidatorVoteResponse(BaseModel):
    """Validator oyu response."""
    consensus_reached: bool
    decision: Optional[str] = None
    approve_count: int
    reject_count: int
    total_votes: int


class CaseResponse(BaseModel):
    """JusticeCase response."""
    id: int
    event_id: int
    validators: List[int]
    validator_votes: dict
    decision: Optional[str]
    consensus_reached: bool
    consensus_at: Optional[str] = None
    created_at: str


# --- Endpoints ---

@router.post(
    "/events",
    response_model=RiskEventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Yeni RiskEvent oluştur",
)
async def create_risk_event(
    body: RiskEventCreate,
    session: AsyncSession = Depends(get_session),
    _admin: User = Depends(get_admin_user),  # Admin/System only
) -> RiskEventResponse:
    """
    Yeni bir RiskEvent oluştur.
    
    - score_ai >= 70: NasipCourt (Case açılır)
    - score_ai >= 40: HITL gerektirir
    - score_ai < 40: Pending
    """
    service = NasipCourtService(session)
    
    event = await service.create_risk_event(
        user_id=body.user_id,
        event_type=body.event_type,
        score_ai=body.score_ai,
        source=body.source,
        meta=body.meta,
    )
    
    return RiskEventResponse(
        id=event.id or 0,
        event_uuid=event.event_uuid,
        user_id=event.user_id,
        score_ai=event.score_ai,
        score_human=event.score_human,
        event_type=event.event_type.value,
        status=event.status,
        timestamp=event.timestamp.isoformat(),
        meta=event.meta,
    )


@router.get(
    "/cases/pending",
    response_model=List[CaseResponse],
    summary="Pending cases (HITL gerektiren)",
)
async def get_pending_cases(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
    _admin: User = Depends(get_admin_user),
) -> List[CaseResponse]:
    """HITL gerektiren pending case'leri getir."""
    stmt = (
        select(JusticeCase)
        .where(JusticeCase.consensus_reached == False)
        .order_by(JusticeCase.created_at.asc())
        .limit(limit)
        .offset(offset)
    )
    
    result = await session.execute(stmt)
    cases = result.scalars().all()
    
    return [
        CaseResponse(
            id=case.id or 0,
            event_id=case.event_id,
            validators=case.validators,
            validator_votes=case.validator_votes,
            decision=case.decision,
            consensus_reached=case.consensus_reached,
            consensus_at=case.consensus_at.isoformat() if case.consensus_at else None,
            created_at=case.created_at.isoformat(),
        )
        for case in cases
    ]


@router.post(
    "/cases/{case_id}/assign-validators",
    response_model=CaseResponse,
    summary="Case'e validator'ları ata",
)
async def assign_validators(
    case_id: int,
    validator_ids: List[int],
    session: AsyncSession = Depends(get_session),
    _admin: User = Depends(get_admin_user),
) -> CaseResponse:
    """Case'e validator'ları ata (max 5)."""
    service = NasipCourtService(session)
    
    case = await service.assign_validators(case_id, validator_ids)
    
    return CaseResponse(
        id=case.id or 0,
        event_id=case.event_id,
        validators=case.validators,
        validator_votes=case.validator_votes,
        decision=case.decision,
        consensus_reached=case.consensus_reached,
        consensus_at=case.consensus_at.isoformat() if case.consensus_at else None,
        created_at=case.created_at.isoformat(),
    )


@router.post(
    "/cases/{case_id}/vote",
    response_model=ValidatorVoteResponse,
    summary="Validator oyu gönder",
)
async def submit_validator_vote(
    case_id: int,
    body: ValidatorVoteRequest,
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
) -> ValidatorVoteResponse:
    """
    Validator oyu gönder.
    
    - %60 çoğunluk sağlanırsa karar verilir
    - Çoğunluğa katılan Validator'a 5 NCR + 10 XP ödül verilir
    """
    service = NasipCourtService(session)
    validator_id = int(current_user_id)
    
    result = await service.submit_validator_vote(
        case_id=case_id,
        validator_id=validator_id,
        vote=body.vote,
    )
    
    return ValidatorVoteResponse(
        consensus_reached=result["consensus_reached"],
        decision=result.get("decision"),
        approve_count=result["approve_count"],
        reject_count=result["reject_count"],
        total_votes=result["total_votes"],
    )


@router.get(
    "/cases/{case_id}",
    response_model=CaseResponse,
    summary="Case detayı",
)
async def get_case(
    case_id: int,
    session: AsyncSession = Depends(get_session),
    _admin: User = Depends(get_admin_user),
) -> CaseResponse:
    """Case detayını getir."""
    stmt = select(JusticeCase).where(JusticeCase.id == case_id)
    result = await session.execute(stmt)
    case = result.scalar_one_or_none()
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found",
        )
    
    return CaseResponse(
        id=case.id or 0,
        event_id=case.event_id,
        validators=case.validators,
        validator_votes=case.validator_votes,
        decision=case.decision,
        consensus_reached=case.consensus_reached,
        consensus_at=case.consensus_at.isoformat() if case.consensus_at else None,
        created_at=case.created_at.isoformat(),
    )


@router.get(
    "/penalties/{user_id}",
    response_model=List[dict],
    summary="Kullanıcının ceza geçmişi",
)
async def get_user_penalties(
    user_id: int,
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
    _admin: User = Depends(get_admin_user),
) -> List[dict]:
    """Kullanıcının ceza geçmişini getir."""
    stmt = (
        select(JusticePenalty)
        .where(JusticePenalty.user_id == user_id)
        .order_by(JusticePenalty.applied_at.desc())
        .limit(limit)
    )
    
    result = await session.execute(stmt)
    penalties = result.scalars().all()
    
    return [
        {
            "id": p.id,
            "penalty_type": p.penalty_type,
            "amount": p.amount,
            "duration_days": p.duration_days,
            "risk_score_delta": p.risk_score_delta,
            "reason": p.reason,
            "applied_at": p.applied_at.isoformat(),
        }
        for p in penalties
    ]

