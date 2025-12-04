# app/justice/mod_router.py
# Ombudsman / Validator endpoints for NasipCourt DAO v1.0

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import List, Optional
from datetime import datetime

from app.core.db import get_session
from app.consent.router import get_current_user_id
from app.core.security import get_admin_user
from app.identity.models import User
from .models import TaskAppeal, ViolationLog
from .schemas import AppealResponse
from .nasipcourt_models import RiskEvent, JusticeCase, JusticeEventType
from .nasipcourt_service import NasipCourtService
from app.telegram_gateway.task_models import TaskSubmission, SubmissionStatus
from app.wallet.service import WalletService
from pydantic import BaseModel
from app.quests.models import UserQuest
from app.quests.enums import QuestStatus
from app.abuse.service import AbuseGuard
from app.abuse.models import AbuseEventType

router = APIRouter(prefix="/api/v1/justice/mod", tags=["justice-mod"])


class PendingAppealItem(BaseModel):
    """Pending appeal item for Ombudsman queue."""
    id: int
    submission_id: int
    user_id: str
    reason: str
    status: str
    appeal_fee_paid: bool
    created_at: datetime
    # Additional context
    task_title: Optional[str] = None
    proof_payload_ref: Optional[str] = None
    risk_score: Optional[float] = None


class PendingViolationItem(BaseModel):
    """Pending violation/HITL item for Validator queue (RiskEvent-based)."""
    id: str  # RiskEvent UUID or Quest/Submission ID
    user_id: str
    category: Optional[str] = None  # "COM", "EKO", "SYS", "TRUST" (for RiskEvent)
    code: Optional[str] = None  # "BORDERLINE_TOXIC", etc.
    score_ai: float  # AI Risk Score (0-100)
    source: Optional[str] = None
    status: str  # "pending_hitl", "in_review", etc.
    assigned_validators: List[str] = []  # Validator ID'leri
    created_at: str
    # Legacy fields (for quest/submission compatibility)
    type: Optional[str] = None  # "quest" | "submission" | "risk_event"
    title: Optional[str] = None
    proof_payload_ref: Optional[str] = None
    risk_score: Optional[float] = None  # AbuseGuard RiskScore (0-10)
    quest_uuid: Optional[str] = None
    submission_id: Optional[int] = None


class DecisionRequest(BaseModel):
    """Decision request for Ombudsman/Validator."""
    validator_id: Optional[str] = None  # Auto-filled from current_user_id if not provided
    decision: str  # "APPROVE" | "REJECT"
    note: Optional[str] = None


class DecisionResponse(BaseModel):
    """Decision response for violation/HITL."""
    violation_id: str
    status: str  # "in_review", "resolved"
    consensus_achieved: bool
    current_tally: Optional[dict] = None  # {"APPROVE": 2, "REJECT": 1}
    validator_reward_status: str = "pending"  # "pending", "awarded"
    risk_score_after: Optional[float] = None
    cp_delta: Optional[int] = None


class AppealDecisionRequest(BaseModel):
    """Appeal decision request for Ethics Validator."""
    validator_id: Optional[str] = None  # Auto-filled from current_user_id
    decision: str  # "APPROVED" | "REJECTED"
    review_notes: str


class AppealDecisionResponse(BaseModel):
    """Appeal decision response."""
    appeal_id: int
    status: str  # "approved" | "rejected"
    user_id: str
    fee_action: str  # "REFUNDED" | "FORFEITED"
    penalty_action: Optional[str] = None  # "REVERSED" | "APPLIED"
    reviewed_at: str


@router.get(
    "/appeals/pending",
    response_model=List[PendingAppealItem],
    summary="Pending appeals queue (Ethics Validators - Level 12+)",
)
async def get_pending_appeals(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
    _admin: User = Depends(get_admin_user),  # Admin/Validator only
):
    """
    Get pending appeals for Ethics Validators (Level 12+).
    
    Returns appeals that are pending review and have paid the 5 NCR appeal fee.
    """
    # Get pending appeals
    stmt = (
        select(TaskAppeal, TaskSubmission)
        .join(TaskSubmission, TaskAppeal.submission_id == TaskSubmission.id)
        .where(TaskAppeal.status == "pending")
        .where(TaskAppeal.appeal_fee_paid == True)  # Only paid appeals
        .order_by(TaskAppeal.created_at.asc())
        .limit(limit)
        .offset(offset)
    )
    
    result = await session.execute(stmt)
    rows = result.all()
    
    appeals = []
    for appeal, submission in rows:
        # Get risk score from AbuseGuard
        abuse_guard = AbuseGuard(session)
        risk_profile = await abuse_guard.get_or_create_profile(submission.user_id)
        
        appeals.append(PendingAppealItem(
            id=appeal.id or 0,
            submission_id=appeal.submission_id,
            user_id=appeal.user_id,
            reason=appeal.reason,
            status=appeal.status,
            appeal_fee_paid=appeal.appeal_fee_paid,
            created_at=appeal.created_at,
            proof_payload_ref=submission.proof,
            risk_score=risk_profile.risk_score if risk_profile else None,
        ))
    
    return appeals


@router.post(
    "/appeals/{appeal_id}/decision",
    response_model=AppealDecisionResponse,
    summary="Ethics Validator appeal kararı (Level 12+)",
)
async def submit_appeal_decision(
    appeal_id: int,
    body: AppealDecisionRequest,
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
    _admin: User = Depends(get_admin_user),  # Ethics Validator/Admin only
):
    """
    Ethics Validator tarafından itiraz sürecini sonlandırır.
    
    Logic:
    - APPROVED: 5 NCR iade edilir ve kullanıcının RiskScore'u -2.0 temizlenir.
    - REJECTED: 5 NCR ücreti Treasury'ye akar ve kullanıcı RiskScore +2.0 cezası alır.
    """
    validator_id = int(current_user_id)
    
    # Get appeal
    appeal_stmt = select(TaskAppeal).where(TaskAppeal.id == appeal_id)
    appeal_result = await session.execute(appeal_stmt)
    appeal = appeal_result.scalar_one_or_none()
    
    if not appeal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appeal not found",
        )
    
    if appeal.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Appeal already {appeal.status}",
        )
    
    user_id_int = int(appeal.user_id)
    wallet_service = WalletService(session)
    abuse_guard = AbuseGuard(session)
    
    now = datetime.utcnow()
    
    if body.decision == "APPROVED":
        # APPROVED: Refund fee and reverse penalty
        # 1. Refund 5 NCR
        if appeal.appeal_fee_paid and appeal.appeal_fee_tx_id:
            await wallet_service.credit(
                user_id=user_id_int,
                amount=5.0,
                source="appeal_fee_refund",
                metadata={
                    "appeal_id": appeal_id,
                    "original_tx_id": appeal.appeal_fee_tx_id,
                },
            )
        
        # 2. Reverse RiskScore penalty (-2.0)
        # Note: AbuseGuard doesn't have direct reversal, but we can log a positive event
        # For now, we'll just update the appeal status
        # TODO: Implement RiskScore reversal mechanism
        
        appeal.status = "approved"
        appeal.reviewed_at = now
        appeal.reviewed_by = validator_id
        appeal.review_notes = body.review_notes
        
        # Update submission status
        submission_stmt = select(TaskSubmission).where(TaskSubmission.id == appeal.submission_id)
        submission_result = await session.execute(submission_stmt)
        submission = submission_result.scalar_one_or_none()
        
        if submission:
            submission.status = SubmissionStatus.APPROVED
            session.add(submission)
        
        fee_action = "REFUNDED"
        penalty_action = "REVERSED"
        
    else:  # REJECTED
        # REJECTED: Forfeit fee to Treasury and apply penalty
        # 1. Fee already paid, goes to Treasury (no action needed, already debited)
        # 2. Apply RiskScore +2.0 penalty
        await abuse_guard.register_event(
            user_id=user_id_int,
            event_type=AbuseEventType.APPEAL_REJECTED,
            severity=5.0,
            metadata={
                "appeal_id": appeal_id,
                "validator_id": validator_id,
                "review_notes": body.review_notes,
            },
        )
        
        appeal.status = "rejected"
        appeal.reviewed_at = now
        appeal.reviewed_by = validator_id
        appeal.review_notes = body.review_notes
        
        fee_action = "FORFEITED"
        penalty_action = "APPLIED"
    
    session.add(appeal)
    await session.commit()
    await session.refresh(appeal)
    
    return AppealDecisionResponse(
        appeal_id=appeal_id,
        status=appeal.status,
        user_id=appeal.user_id,
        fee_action=fee_action,
        penalty_action=penalty_action,
        reviewed_at=appeal.reviewed_at.isoformat() if appeal.reviewed_at else now.isoformat(),
    )


@router.get(
    "/violations/pending",
    response_model=List[PendingViolationItem],
    summary="Pending violations/HITL queue (DAO Validators - Level 10+)",
)
async def get_pending_violations(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
    _admin: User = Depends(get_admin_user),  # Admin/Validator only
):
    """
    Get pending violations/HITL items for DAO Validators (Level 10+).
    
    Returns:
    - RiskEvent'ler (status=hitl, score_ai 40-69 Gri Alan)
    - HITL-routed quests (status=UNDER_REVIEW, risk_score >= 6.0)
    - Pending task submissions (status=PENDING, high risk)
    """
    items = []
    
    # 1. Get RiskEvent'ler (NasipCourt DAO v1.0 - Gri Alan)
    risk_event_stmt = (
        select(RiskEvent, JusticeCase)
        .outerjoin(JusticeCase, RiskEvent.id == JusticeCase.event_id)
        .where(RiskEvent.status == "hitl")
        .where(RiskEvent.score_ai >= 40.0)
        .where(RiskEvent.score_ai < 70.0)  # Gri Alan
        .order_by(RiskEvent.timestamp.asc())
        .limit(limit)
        .offset(offset)
    )
    
    risk_event_result = await session.execute(risk_event_stmt)
    risk_event_rows = risk_event_result.all()
    
    for event, case in risk_event_rows:
        assigned_validators = []
        if case:
            assigned_validators = [str(vid) for vid in case.validators]
        
        # Get AbuseGuard RiskScore
        abuse_guard = AbuseGuard(session)
        risk_profile = await abuse_guard.get_or_create_profile(event.user_id)
        risk_score = risk_profile.risk_score if risk_profile else 0.0
        
        items.append(PendingViolationItem(
            id=event.event_uuid,
            user_id=str(event.user_id),
            category=None,  # RiskEvent doesn't have category, use event_type
            code=event.event_type.value,
            score_ai=event.score_ai,
            source=event.source,
            status="pending_hitl" if not case or not case.consensus_reached else "in_review",
            assigned_validators=assigned_validators,
            created_at=event.timestamp.isoformat(),
            type="risk_event",
            risk_score=risk_score,
        ))
    
    # 2. Get HITL-routed quests (legacy support)
    quest_stmt = (
        select(UserQuest)
        .where(UserQuest.status == QuestStatus.UNDER_REVIEW)
        .where(UserQuest.abuse_risk_snapshot >= 6.0)
        .order_by(UserQuest.submitted_at.asc())
        .limit(limit)
        .offset(offset)
    )
    
    quest_result = await session.execute(quest_stmt)
    quests = quest_result.scalars().all()
    
    for quest in quests:
        items.append(PendingViolationItem(
            id=str(quest.id or 0),
            user_id=str(quest.user_id),
            score_ai=quest.final_score or 0.0,
            status="pending_hitl",
            assigned_validators=[],
            created_at=(quest.submitted_at or quest.assigned_at).isoformat(),
            type="quest",
            title=quest.title,
            proof_payload_ref=quest.proof_payload_ref,
            risk_score=quest.abuse_risk_snapshot or 0.0,
            quest_uuid=quest.quest_uuid,
        ))
    
    # 3. Get pending task submissions (high risk) - legacy support
    submission_stmt = (
        select(TaskSubmission)
        .where(TaskSubmission.status == SubmissionStatus.PENDING)
        .order_by(TaskSubmission.submitted_at.asc())
        .limit(limit)
        .offset(offset)
    )
    
    submission_result = await session.execute(submission_stmt)
    submissions = submission_result.scalars().all()
    
    for submission in submissions:
        abuse_guard = AbuseGuard(session)
        risk_profile = await abuse_guard.get_or_create_profile(submission.user_id)
        risk_score = risk_profile.risk_score if risk_profile else 0.0
        
        if risk_score >= 6.0:
            items.append(PendingViolationItem(
                id=str(submission.id),
                user_id=str(submission.user_id),
                score_ai=0.0,  # No AI score for legacy submissions
                status="pending_hitl",
                assigned_validators=[],
                created_at=(submission.submitted_at or datetime.utcnow()).isoformat(),
                type="submission",
                title=f"Task {submission.task_id}",
                proof_payload_ref=submission.proof,
                risk_score=risk_score,
                submission_id=submission.id,
            ))
    
    # Sort by created_at
    items.sort(key=lambda x: x.created_at)
    
    return items[:limit]


@router.post(
    "/violations/{violation_id}/decision",
    response_model=DecisionResponse,
    summary="Submit decision for violation/HITL case (RiskEvent-based)",
)
async def submit_violation_decision(
    violation_id: str,  # RiskEvent UUID or legacy ID
    body: DecisionRequest,
    session: AsyncSession = Depends(get_session),
    current_user_id: str = Depends(get_current_user_id),
    _admin: User = Depends(get_admin_user),  # Admin/Validator only
):
    """
    Submit decision for a violation/HITL case.
    
    - APPROVE: Reward user, reduce risk score
    - REJECT: Apply penalty, increase risk score, log MANUAL_FLAG
    
    Logic: %60 çoğunluk sağlandığında, çoğunluğa katılan Validator'a 5 NCR + 10 XP ödül verilir.
    REJECT kararı, kullanıcının RiskScore'una +2.0 ceza katsayısı ekler.
    """
    validator_id = int(current_user_id)
    validator_id_str = str(validator_id)
    
    # Try RiskEvent first (NasipCourt DAO v1.0)
    risk_event_stmt = select(RiskEvent).where(RiskEvent.event_uuid == violation_id)
    risk_event_result = await session.execute(risk_event_stmt)
    risk_event = risk_event_result.scalar_one_or_none()
    
    if risk_event:
        # Get or create JusticeCase
        case_stmt = select(JusticeCase).where(JusticeCase.event_id == risk_event.id)
        case_result = await session.execute(case_stmt)
        case = case_result.scalar_one_or_none()
        
        if not case:
            # Create case if doesn't exist
            nasipcourt_service = NasipCourtService(session)
            case = await nasipcourt_service._open_case(risk_event.id)
        
        # Submit validator vote
        vote = "APPROVE" if body.decision == "APPROVE" else "REJECT"
        consensus_result = await nasipcourt_service.submit_validator_vote(
            case_id=case.id or 0,
            validator_id=validator_id,
            vote=vote,
        )
        
        # Get updated risk score
        abuse_guard = AbuseGuard(session)
        risk_profile = await abuse_guard.get_or_create_profile(risk_event.user_id)
        risk_score_after = risk_profile.risk_score if risk_profile else None
        
        return DecisionResponse(
            violation_id=violation_id,
            status="in_review" if not consensus_result["consensus_reached"] else "resolved",
            consensus_achieved=consensus_result["consensus_reached"],
            current_tally={
                "APPROVE": consensus_result["approve_count"],
                "REJECT": consensus_result["reject_count"],
            },
            validator_reward_status="awarded" if consensus_result["consensus_reached"] else "pending",
            risk_score_after=risk_score_after,
        )
    
    # Legacy: Try quest (by ID)
    try:
        case_id_int = int(violation_id)
        quest_stmt = select(UserQuest).where(UserQuest.id == case_id_int)
        quest_result = await session.execute(quest_stmt)
        quest = quest_result.scalar_one_or_none()
        
        if quest:
            from app.quests.hitl import process_hitl_decision
            
            hitl_decision = "APPROVED" if body.decision == "APPROVE" else "REJECTED"
            
            decision_result = await process_hitl_decision(
                session=session,
                quest_id=case_id_int,
                admin_user_id=validator_id,
                decision=hitl_decision,
                reason=body.note,
            )
            
            return DecisionResponse(
                violation_id=violation_id,
                status="resolved",
                consensus_achieved=True,
                current_tally={"APPROVE": 1 if body.decision == "APPROVE" else 0, "REJECT": 1 if body.decision == "REJECT" else 0},
                validator_reward_status="pending",  # Legacy quests don't have consensus
                risk_score_after=decision_result.get("new_risk_score"),
            )
        
        # Legacy: Try submission
        submission_stmt = select(TaskSubmission).where(TaskSubmission.id == case_id_int)
        submission_result = await session.execute(submission_stmt)
        submission = submission_result.scalar_one_or_none()
        
        if submission:
            abuse_guard = AbuseGuard(session)
            
            if body.decision == "APPROVE":
                submission.status = SubmissionStatus.APPROVED
            elif body.decision == "REJECT":
                submission.status = SubmissionStatus.REJECTED
                
                await abuse_guard.register_event(
                    user_id=submission.user_id,
                    event_type=AbuseEventType.MANUAL_FLAG,
                    severity=5.0,
                    metadata={
                        "submission_id": case_id_int,
                        "validator_id": validator_id,
                        "note": body.note,
                    },
                )
            
            session.add(submission)
            await session.commit()
            
            risk_profile = await abuse_guard.get_or_create_profile(submission.user_id)
            
            return DecisionResponse(
                violation_id=violation_id,
                status="resolved",
                consensus_achieved=True,
                current_tally={"APPROVE": 1 if body.decision == "APPROVE" else 0, "REJECT": 1 if body.decision == "REJECT" else 0},
                validator_reward_status="pending",
                risk_score_after=risk_profile.risk_score if risk_profile else None,
            )
    except ValueError:
        pass  # Not an integer ID
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Violation not found (neither RiskEvent, quest, nor submission)",
    )

