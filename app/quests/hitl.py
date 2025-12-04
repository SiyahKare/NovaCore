"""
HITL (Human-In-The-Loop) Decision Processing
Ombudsman karar verme mekanizması
"""
from typing import Optional
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.quests.models import UserQuest
from app.quests.enums import QuestStatus
from app.abuse.service import AbuseGuard
from app.wallet.service import WalletService
from app.xp_loyalty.service import XpLoyaltyService
from app.core.logging import get_logger

logger = get_logger("hitl")


async def process_hitl_decision(
    session: AsyncSession,
    quest_id: int,
    admin_user_id: int,
    decision: str,  # "APPROVED" or "REJECTED"
    reason: Optional[str] = None,
) -> dict:
    """
    Ombudsman'ın manuel inceleme kuyruğundaki (HITL) bir görev hakkında karar vermesi.
    
    Args:
        session: Database session
        quest_id: UserQuest ID
        admin_user_id: Admin/Ombudsman user ID
        decision: "APPROVED" or "REJECTED"
        reason: Optional reason for the decision
    
    Returns:
        Decision result with reward info and risk status
    """
    # Get quest
    stmt = select(UserQuest).where(UserQuest.id == quest_id)
    result = await session.execute(stmt)
    uq = result.scalar_one_or_none()
    
    if not uq:
        raise ValueError("Quest not found")
    
    if uq.status != QuestStatus.UNDER_REVIEW:
        raise ValueError(f"Quest not in HITL review state. Current status: {uq.status}")
    
    if decision not in ["APPROVED", "REJECTED"]:
        raise ValueError("Decision must be 'APPROVED' or 'REJECTED'")
    
    now = datetime.utcnow()
    
    if decision == "APPROVED":
        # Approve: Give rewards
        if not uq.final_reward_ncr or not uq.final_reward_xp:
            raise ValueError("Quest rewards not calculated. Cannot approve.")
        
        wallet_service = WalletService(session)
        xp_service = XpLoyaltyService(session)
        
        # Credit NCR
        await wallet_service.credit(
            user_id=uq.user_id,
            amount=float(uq.final_reward_ncr),
            source="quest_hitl_approved",
            metadata={
                "quest_id": quest_id,
                "quest_uuid": uq.quest_uuid,
                "admin_user_id": admin_user_id,
                "reason": reason,
            },
        )
        
        # Credit XP
        await xp_service.create_xp_event(
            user_id=uq.user_id,
            amount=uq.final_reward_xp,
            event_type="QUEST_APPROVED_HITL",
            source_app="aurora",
            metadata={
                "quest_id": quest_id,
                "quest_uuid": uq.quest_uuid,
                "admin_user_id": admin_user_id,
            },
        )
        
        uq.status = QuestStatus.APPROVED
        uq.resolved_at = now
        
        # AbuseGuard: Positive outcome (risk reduction)
        abuse_guard = AbuseGuard(session)
        # Note: AbuseGuard doesn't have a direct "on_quest_approved" method,
        # but we can log a positive event if needed
        
        logger.info(
            "hitl_quest_approved",
            quest_id=quest_id,
            user_id=uq.user_id,
            admin_user_id=admin_user_id,
            reward_ncr=uq.final_reward_ncr,
            reward_xp=uq.final_reward_xp,
        )
        
    else:  # REJECTED
        # Reject: No rewards, log abuse event
        uq.status = QuestStatus.REJECTED
        uq.resolved_at = now
        
        # AbuseGuard: Log rejection event
        abuse_guard = AbuseGuard(session)
        await abuse_guard.register_event(
            user_id=uq.user_id,
            event_type="MANUAL_FLAG",  # From AbuseEventType
            severity=5.0,  # Moderate severity for manual rejection
            metadata={
                "quest_id": quest_id,
                "quest_uuid": uq.quest_uuid,
                "admin_user_id": admin_user_id,
                "reason": reason,
                "rejection_source": "hitl_ombudsman",
            },
        )
        
        logger.info(
            "hitl_quest_rejected",
            quest_id=quest_id,
            user_id=uq.user_id,
            admin_user_id=admin_user_id,
            reason=reason,
        )
    
    session.add(uq)
    await session.commit()
    await session.refresh(uq)
    
    # Get updated risk profile
    abuse_guard = AbuseGuard(session)
    risk_profile = await abuse_guard.get_or_create_profile(uq.user_id)
    
    return {
        "quest_id": quest_id,
        "status": uq.status.value,
        "reward_ncr": uq.final_reward_ncr if decision == "APPROVED" else 0.0,
        "reward_xp": uq.final_reward_xp if decision == "APPROVED" else 0,
        "new_risk_score": risk_profile.risk_score,
    }

