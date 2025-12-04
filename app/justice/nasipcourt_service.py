# app/justice/nasipcourt_service.py
# NasipCourt DAO v1.0 - Justice Execution Engine

from datetime import datetime
from typing import Optional, List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from .nasipcourt_models import RiskEvent, JusticeCase, JusticePenalty, JusticeEventType
from app.abuse.service import AbuseGuard
from app.abuse.models import AbuseEventType
from app.wallet.service import WalletService
from app.core.logging import get_logger

logger = get_logger("nasipcourt")


class NasipCourtService:
    """
    NasipCourt DAO v1.0 - Adalet Algoritması ve Karar Akışı
    
    - AI Scoring: 0-100 skor
    - 70+ → NasipCourt (Case açılır)
    - 40-69 → HITL gerektirir
    - HITL: 5 Validator, %60 çoğunluk
    - Ceza Etkisi: RiskScore +2.0, NASIP burn, Key Lock
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.abuse_guard = AbuseGuard(session)
        self.wallet_service = WalletService(session)
    
    # --- AI Scoring Thresholds ---
    AI_SCORE_NASIPCOURT_THRESHOLD = 70.0  # 70+ → Case açılır
    AI_SCORE_HITL_THRESHOLD = 40.0  # 40-69 → HITL gerektirir
    
    # --- HITL Configuration ---
    HITL_VALIDATOR_COUNT = 5
    HITL_CONSENSUS_THRESHOLD = 0.6  # %60 çoğunluk
    
    # --- Penalty Configuration ---
    REJECT_RISK_SCORE_PENALTY = 2.0  # REJECT olursa RiskScore'a eklenen ceza
    
    async def create_risk_event(
        self,
        user_id: int,
        event_type: JusticeEventType,
        score_ai: float,
        source: str,
        meta: Optional[Dict] = None,
    ) -> RiskEvent:
        """
        Yeni bir RiskEvent oluştur ve duruma göre Case aç.
        
        - score_ai >= 70: NasipCourt (Case açılır)
        - score_ai >= 40: HITL gerektirir
        - score_ai < 40: Pending (manuel inceleme gerekebilir)
        """
        event = RiskEvent(
            user_id=user_id,
            event_type=event_type,
            score_ai=score_ai,
            source=source,
            meta=meta or {},
        )
        
        # Status belirleme
        if score_ai >= self.AI_SCORE_NASIPCOURT_THRESHOLD:
            event.status = "hitl"  # NasipCourt'a gider
        elif score_ai >= self.AI_SCORE_HITL_THRESHOLD:
            event.status = "hitl"  # HITL gerektirir
        else:
            event.status = "pending"  # Manuel inceleme
        
        self.session.add(event)
        await self.session.commit()
        await self.session.refresh(event)
        
        # Case aç (eğer HITL gerekiyorsa)
        if event.status == "hitl":
            await self._open_case(event.id)
        
        logger.info(
            "risk_event_created",
            event_id=event.id,
            user_id=user_id,
            score_ai=score_ai,
            status=event.status,
        )
        
        return event
    
    async def _open_case(self, event_id: int) -> JusticeCase:
        """RiskEvent için JusticeCase aç."""
        case = JusticeCase(
            event_id=event_id,
            validators=[],  # Validator'lar sonra atanacak
            validator_votes={},
        )
        
        self.session.add(case)
        await self.session.commit()
        await self.session.refresh(case)
        
        logger.info("justice_case_opened", case_id=case.id, event_id=event_id)
        
        return case
    
    async def assign_validators(
        self,
        case_id: int,
        validator_ids: List[int],
    ) -> JusticeCase:
        """
        Case'e validator'ları ata (max 5).
        
        Validator seçimi:
        - Level 10+ kullanıcılar
        - Aktif ve güvenilir validator'lar
        - Daha önce bu kullanıcıya karar vermemiş olanlar
        """
        if len(validator_ids) > self.HITL_VALIDATOR_COUNT:
            raise ValueError(f"Maximum {self.HITL_VALIDATOR_COUNT} validators allowed")
        
        stmt = select(JusticeCase).where(JusticeCase.id == case_id)
        result = await self.session.execute(stmt)
        case = result.scalar_one_or_none()
        
        if not case:
            raise ValueError("Case not found")
        
        if case.consensus_reached:
            raise ValueError("Case already has consensus")
        
        case.validators = validator_ids
        case.updated_at = datetime.utcnow()
        
        self.session.add(case)
        await self.session.commit()
        await self.session.refresh(case)
        
        logger.info(
            "validators_assigned",
            case_id=case_id,
            validator_ids=validator_ids,
        )
        
        return case
    
    async def submit_validator_vote(
        self,
        case_id: int,
        validator_id: int,
        vote: str,  # "APPROVE" | "REJECT"
    ) -> Dict:
        """
        Validator oyu gönder ve konsensüs kontrolü yap.
        
        - %60 çoğunluk sağlanırsa karar verilir
        - Çoğunluğa katılan Validator'a 5 NCR + 10 XP ödül verilir
        """
        if vote not in ["APPROVE", "REJECT"]:
            raise ValueError("Vote must be 'APPROVE' or 'REJECT'")
        
        stmt = select(JusticeCase).where(JusticeCase.id == case_id)
        result = await self.session.execute(stmt)
        case = result.scalar_one_or_none()
        
        if not case:
            raise ValueError("Case not found")
        
        if validator_id not in case.validators:
            raise ValueError("Validator not assigned to this case")
        
        if case.consensus_reached:
            raise ValueError("Case already has consensus")
        
        # Oyu kaydet
        case.validator_votes[str(validator_id)] = vote
        case.updated_at = datetime.utcnow()
        
        # Konsensüs kontrolü
        total_votes = len(case.validator_votes)
        approve_count = sum(1 for v in case.validator_votes.values() if v == "APPROVE")
        reject_count = total_votes - approve_count
        
        # %60 çoğunluk kontrolü
        if total_votes >= self.HITL_VALIDATOR_COUNT:
            approve_ratio = approve_count / total_votes
            reject_ratio = reject_count / total_votes
            
            if approve_ratio >= self.HITL_CONSENSUS_THRESHOLD:
                case.decision = "approved"
                case.consensus_reached = True
                case.consensus_at = datetime.utcnow()
                winning_vote = "APPROVE"
            elif reject_ratio >= self.HITL_CONSENSUS_THRESHOLD:
                case.decision = "rejected"
                case.consensus_reached = True
                case.consensus_at = datetime.utcnow()
                winning_vote = "REJECT"
            else:
                # Henüz konsensüs yok
                self.session.add(case)
                await self.session.commit()
                await self.session.refresh(case)
                
                return {
                    "consensus_reached": False,
                    "approve_count": approve_count,
                    "reject_count": reject_count,
                    "total_votes": total_votes,
                }
            
            # Konsensüs sağlandı - Ceza uygula
            await self._execute_decision(case, winning_vote)
            
            # Çoğunluğa katılan Validator'lara ödül ver
            await self._reward_validators(case, winning_vote)
        
        self.session.add(case)
        await self.session.commit()
        await self.session.refresh(case)
        
        return {
            "consensus_reached": case.consensus_reached,
            "decision": case.decision,
            "approve_count": approve_count,
            "reject_count": reject_count,
            "total_votes": total_votes,
        }
    
    async def _execute_decision(
        self,
        case: JusticeCase,
        decision: str,
    ) -> None:
        """
        Karar uygula: Ceza etkilerini tetikle.
        
        - REJECT: RiskScore +2.0, AbuseGuard event log
        - Ağır Suçlar: NASIP burn, Key Lock
        """
        # Get event
        stmt = select(RiskEvent).where(RiskEvent.id == case.event_id)
        result = await self.session.execute(stmt)
        event = result.scalar_one_or_none()
        
        if not event:
            raise ValueError("Event not found")
        
        if decision == "REJECT":
            # RiskScore penalty
            risk_profile = await self.abuse_guard.get_or_create_profile(event.user_id)
            
            # AbuseGuard event log
            await self.abuse_guard.register_event(
                user_id=event.user_id,
                event_type=AbuseEventType.MANUAL_FLAG,
                severity=5.0,
                metadata={
                    "case_id": case.id,
                    "event_id": event.id,
                    "event_type": event.event_type.value,
                    "decision": decision,
                },
            )
            
            # Get updated risk score
            risk_profile = await self.abuse_guard.get_or_create_profile(event.user_id)
            risk_score_delta = self.REJECT_RISK_SCORE_PENALTY
            
            # Penalty kaydı
            penalty = JusticePenalty(
                user_id=event.user_id,
                case_id=case.id,
                event_id=event.id,
                penalty_type="RISK_SCORE_PENALTY",
                risk_score_delta=risk_score_delta,
                reason=f"NasipCourt REJECT decision for {event.event_type.value}",
                applied_by=case.resolved_by,
            )
            
            self.session.add(penalty)
            
            # Ağır suçlar için ek cezalar
            if event.event_type in [JusticeEventType.EXPLOIT, JusticeEventType.FRAUD]:
                # NASIP burn (TODO: Implement NASIP token burn)
                logger.warning(
                    "nasip_burn_required",
                    user_id=event.user_id,
                    case_id=case.id,
                    event_type=event.event_type.value,
                )
            
            if event.event_type == JusticeEventType.COMMUNITY_ATTACK:
                # Key Lock (TODO: Implement NFT metadata update)
                logger.warning(
                    "key_lock_required",
                    user_id=event.user_id,
                    case_id=case.id,
                    event_type=event.event_type.value,
                )
        
        # Update event status
        event.status = "resolved"
        case.resolved_at = datetime.utcnow()
        
        await self.session.commit()
        
        logger.info(
            "decision_executed",
            case_id=case.id,
            decision=decision,
            user_id=event.user_id,
        )
    
    async def _reward_validators(
        self,
        case: JusticeCase,
        winning_vote: str,
    ) -> None:
        """
        Çoğunluğa katılan Validator'lara ödül ver.
        
        - 5 NCR + 10 XP
        """
        from app.xp_loyalty.service import XpLoyaltyService
        xp_service = XpLoyaltyService(self.session)
        
        winning_validators = [
            int(vid) for vid, vote in case.validator_votes.items()
            if vote == winning_vote
        ]
        
        for validator_id in winning_validators:
            # NCR ödülü
            await self.wallet_service.credit(
                user_id=validator_id,
                amount=5.0,
                source="nasipcourt_validator_reward",
                metadata={
                    "case_id": case.id,
                    "winning_vote": winning_vote,
                },
            )
            
            # XP ödülü
            await xp_service.create_xp_event(
                user_id=validator_id,
                amount=10,
                event_type="NASIPCOURT_VALIDATOR_REWARD",
                source_app="aurora",
                metadata={
                    "case_id": case.id,
                    "winning_vote": winning_vote,
                },
            )
        
        logger.info(
            "validators_rewarded",
            case_id=case.id,
            validator_ids=winning_validators,
            reward_ncr=5.0,
            reward_xp=10,
        )

