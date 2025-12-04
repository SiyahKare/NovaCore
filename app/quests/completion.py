"""
Quest Completion - AbuseGuard + HouseEdge Entegrasyonu
"""
from datetime import datetime
from typing import Optional
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from .models import UserQuest
from .proof_models import QuestProof
from .enums import QuestStatus
from app.abuse.service import AbuseGuard
from app.abuse.models import AbuseEventType
from app.core.logging import get_logger

logger = get_logger("quest_completion")
from app.wallet.service import WalletService
from app.wallet.schemas import TransactionCreate
from app.wallet.models import LedgerEntryType
from app.xp_loyalty.service import XpLoyaltyService
from app.xp_loyalty.schemas import XpEventCreate
from app.telegram_gateway.event_service import EventService
from app.wallet.treasury_cap import apply_treasury_cap
from app.economy.reward_engine import RewardEngine, UserEconomyContext
from app.economy.drm import MacroContext, DynamicRewardManager, EconomyMode
from app.core.citizenship import nova_score_to_level
from .marketplace_bridge import check_and_send_to_marketplace, _infer_category_from_quest
from app.scoring.service import score_quest
from app.scoring.models import QuestScoringInput


async def get_user_state(
    session: AsyncSession,
    user_id: int,
) -> dict:
    """
    Kullanıcının state'ini topla (level, streak, siyah_score, risk_score).
    
    Returns:
        {
            "level": int,
            "streak": int,
            "siyah_score": float,  # Placeholder - NovaScore'dan gelecek
            "risk_score": float,
        }
    """
    # Level & Streak
    loyalty_service = XpLoyaltyService(session)
    loyalty = await loyalty_service.get_loyalty_profile(user_id)
    
    # RiskScore
    abuse_guard = AbuseGuard(session)
    risk_profile = await abuse_guard.get_or_create_profile(user_id)
    
    # SiyahScore (Placeholder - NovaScore'dan gelecek)
    # Şimdilik basit bir hesaplama
    siyah_score = 75.0  # Default
    if loyalty:
        # Level ve streak'e göre basit bir siyah_score tahmini
        siyah_score = min(100.0, 60.0 + (loyalty.level * 5) + (loyalty.current_streak * 0.5))
    
    return {
        "level": loyalty.level if loyalty else 1,
        "streak": loyalty.current_streak if loyalty else 0,
        "siyah_score": siyah_score,
        "risk_score": risk_profile.risk_score,
    }


async def calculate_ncr_reward_v2(
    session: AsyncSession,
    base_ncr: float,
    base_xp: int,
    user_id: int,
    level: int,
    streak: int,
    siyah_score: float,
    risk_score: float,
    ai_score: float,
    nova_score: Optional[float] = None,
    citizen_level: Optional[str] = None,
) -> tuple[float, int, float]:
    """
    RewardEngine + DRM ile final reward hesaplama (v2).
    
    NCR_final = BaseNCR × UserMultiplier × MacroMultiplier
    
    Returns:
        (final_ncr, final_xp, total_multiplier)
    """
    # NovaScore'dan citizen level çıkar (eğer yoksa)
    if not citizen_level:
        if nova_score is not None:
            from app.core.citizenship import nova_score_to_level
            citizen_level = nova_score_to_level(nova_score).value
        else:
            citizen_level = "resident"  # Default
    
    # UserEconomyContext oluştur
    user_ctx = UserEconomyContext(
        user_id=str(user_id),
        streak_days=streak,
        siyah_score_avg=siyah_score,
        risk_score=risk_score,
        citizen_level=citizen_level,
    )
    
    # RewardEngine ile user multiplier hesapla
    reward_engine = RewardEngine(EconomyMode.NORMAL)  # TODO: Gerçek mode'u al
    user_multiplier = reward_engine.compute_reward_multiplier(user_ctx)
    
    # Macro multiplier (şimdilik 1.0 - DRM metrics hazır olunca güncellenecek)
    macro_ctx = MacroContext(
        mode=EconomyMode.NORMAL,
        daily_emission_used=0.0,  # TODO: Gerçek metrikleri al
        daily_emission_cap=10000.0,
        weekly_emission_used=0.0,
        weekly_emission_cap=70000.0,
        burn_rate_7d=0.25,
        treasury_health=0.6,
    )
    macro_multiplier = DynamicRewardManager.compute_macro_multiplier(macro_ctx)
    
    # Final NCR
    final_ncr = base_ncr * user_multiplier * macro_multiplier
    final_ncr = max(0.0, round(final_ncr, 2))
    
    # XP (user multiplier ile)
    final_xp = int(base_xp * user_multiplier)
    final_xp = max(0, final_xp)
    
    # Total multiplier (for logging)
    total_multiplier = user_multiplier * macro_multiplier
    
    return final_ncr, final_xp, total_multiplier


async def submit_quest_proof(
    session: AsyncSession,
    user_id: int,
    quest_uuid: str,
    proof_type: str,
    proof_payload_ref: str,
    ai_score: Optional[float] = None,
    source: str = "telegram",
    message_id: Optional[str] = None,
    proof_content: Optional[str] = None,
) -> UserQuest:
    """
    Kullanıcı proof gönderir:
    
    - AbuseGuard event log
    - AI scoring (varsa)
    - HouseEdge ile final NCR hesaplama
    - Treasury Cap uygulama
    - NCR + XP cüzdana basma
    """
    # Get quest
    stmt = select(UserQuest).where(
        UserQuest.user_id == user_id,
        UserQuest.quest_uuid == quest_uuid,
    )
    result = await session.execute(stmt)
    uq = result.scalar_one_or_none()
    
    if not uq:
        raise ValueError("Quest not found or not assigned to user.")
    
    # Süre ve durum kontrol
    now = datetime.utcnow()
    if uq.expires_at < now:
        uq.status = QuestStatus.EXPIRED
        await session.commit()
        raise ValueError("Quest has expired.")
    
    if uq.status not in [QuestStatus.ASSIGNED, QuestStatus.SUBMITTED]:
        raise ValueError(f"Quest not in completable state: {uq.status}")
    
    # Get user state
    user_state = await get_user_state(session, user_id)
    
    # AbuseGuard: risk snapshot
    abuse_guard = AbuseGuard(session)
    risk_profile = await abuse_guard.get_or_create_profile(user_id)
    risk_snapshot = risk_profile.risk_score
    
    # Cooldown kontrolü
    if abuse_guard.requires_cooldown(risk_snapshot):
        raise ValueError("Account on cooldown due to abuse risk")
    
    # QuestProof kaydı oluştur
    proof_content_str = proof_content or proof_payload_ref
    
    quest_proof = QuestProof(
        user_id=user_id,
        user_quest_id=uq.id,
        source=source,
        message_id=message_id,
        proof_type=proof_type,
        content=proof_content_str,
        metadata=None,  # TODO: File URL, dimensions vs. ekle
    )
    session.add(quest_proof)
    
    # Proof meta kaydet (backward compatibility)
    uq.proof_type = proof_type
    uq.proof_payload_ref = proof_payload_ref
    uq.submitted_at = now
    uq.status = QuestStatus.SUBMITTED
    
    # AI Scoring Service - Quest'i puanla
    # Eğer manuel ai_score verilmişse onu kullan, yoksa AI scoring yap
    scoring_flags: list[str] = []
    suggested_tags: list[str] = []
    
    if ai_score is not None:
        final_ai_score = ai_score
    else:
        # Quest kategorisini çıkar
        quest_category = _infer_category_from_quest(uq)
        
        # Proof payload'ı çöz
        # Önce proof_content'i kullan, yoksa proof_payload_ref'den al
        proof_payload = proof_content if proof_content else proof_payload_ref
        
        # AI Scoring
        scoring_input = QuestScoringInput(
            user_id=user_id,
            quest_key=uq.key,
            category=quest_category.value,
            proof_type=proof_type,
            proof_payload=proof_payload,
            lang="tr",
        )
        
        scoring_result = await score_quest(scoring_input)
        final_ai_score = scoring_result.score
        scoring_flags = scoring_result.flags
        suggested_tags = scoring_result.suggested_tags
        
        # QuestProof'a AI scoring sonuçlarını kaydet
        quest_proof.ai_score = final_ai_score
        quest_proof.ai_flags = ",".join(scoring_flags) if scoring_flags else None
        quest_proof.ai_tags = ",".join(suggested_tags) if suggested_tags else None
    
    uq.final_score = final_ai_score
    
    # Scoring flags ve tags'i metadata'ya ekle (TODO: UserQuest modeline field ekle)
    # Şimdilik logging ile kaydediyoruz
    logger.info(
        "quest_scored",
        quest_uuid=quest_uuid,
        user_id=user_id,
        ai_score=final_ai_score,
        flags=scoring_flags,
        tags=suggested_tags,
    )
    
    # AbuseGuard: risk snapshot
    uq.abuse_risk_snapshot = risk_snapshot
    
    # RewardEngine v2 ile reward hesabı
    # TODO: NovaScore'u gerçekten çek (şimdilik None)
    reward_ncr, reward_xp, edge_multiplier = await calculate_ncr_reward_v2(
        session=session,
        base_ncr=uq.base_reward_ncr,
        base_xp=uq.base_reward_xp,
        user_id=user_id,
        level=user_state["level"],
        streak=user_state["streak"],
        siyah_score=user_state["siyah_score"],
        risk_score=user_state["risk_score"],
        ai_score=final_ai_score,
        nova_score=None,  # TODO: NovaScore service'den çek
        citizen_level=None,  # TODO: NovaScore'dan çıkar
    )
    
    # Treasury Cap uygula
    treasury_adjusted_ncr, treasury_meta = await apply_treasury_cap(
        session=session,
        pre_treasury_ncr=reward_ncr,
    )
    
    uq.final_reward_ncr = treasury_adjusted_ncr
    uq.final_reward_xp = reward_xp
    uq.house_edge_snapshot = edge_multiplier
    
    # AbuseGuard: high-risk ise HITL queue'ya at
    hitl_required = abuse_guard.requires_forced_hitl(risk_snapshot)
    
    if hitl_required or final_ai_score < 50:
        # HITL required
        uq.status = QuestStatus.UNDER_REVIEW
        
        # Auto-reject event (if AI score too low)
        if final_ai_score < 50:
            await abuse_guard.register_event(
                user_id=user_id,
                event_type=AbuseEventType.AUTO_REJECT,
                meta={"quest_uuid": quest_uuid, "ai_score": final_ai_score},
            )
        
        # AbuseGuard: Scoring flags kontrolü
        if scoring_flags:
            # NSFW/Toxic flag → RiskScore +2, CP +10
            if "nsfw_or_toxic" in scoring_flags:
                await abuse_guard.register_event(
                    user_id=user_id,
                    event_type=AbuseEventType.TOXIC_CONTENT,
                    meta={"quest_uuid": quest_uuid, "flags": scoring_flags},
                )
            
            # Low quality → RiskScore +1
            if "low_quality" in scoring_flags and final_ai_score < 40:
                await abuse_guard.register_event(
                    user_id=user_id,
                    event_type=AbuseEventType.LOW_QUALITY_BURST,
                    meta={"quest_uuid": quest_uuid, "ai_score": final_ai_score},
                )
    else:
        # Direkt onay: NCR + XP cüzdana bas
        uq.status = QuestStatus.APPROVED
        uq.resolved_at = datetime.utcnow()
        
        # NCR reward
        wallet_service = WalletService(session)
        wallet_tx = await wallet_service.create_transaction(
            TransactionCreate(
                user_id=user_id,
                amount=Decimal(str(treasury_adjusted_ncr)),
                token="NCR",
                type=LedgerEntryType.EARN,
                source_app="nasipquest",
                reference_id=uq.quest_uuid,
                reference_type="quest_completion",
                metadata={
                    "quest_key": uq.key,
                    "base_ncr": uq.base_reward_ncr,
                    "final_ncr": treasury_adjusted_ncr,
                    "treasury": treasury_meta,
                    "edge_multiplier": edge_multiplier,
                },
            )
        )
        
        # XP reward
        loyalty_service = XpLoyaltyService(session)
        xp_event = await loyalty_service.create_xp_event(
            XpEventCreate(
                user_id=user_id,
                amount=reward_xp,
                event_type="QUEST_COMPLETED",
                source_app="nasipquest",
                metadata={
                    "quest_uuid": uq.quest_uuid,
                    "quest_key": uq.key,
                    "base_xp": uq.base_reward_xp,
                    "final_xp": reward_xp,
                },
            )
        )
        
        # AbuseGuard: quest approved event
        # (Positive event - risk score düşürebilir)
        
        # High quality quest → CreatorAsset candidate
        if final_ai_score >= 85 and not scoring_flags:
            # TODO: CreatorAsset candidate etiketi ekle
            # Bu ileride "featured" slotlar için kullanılacak
            pass
        
        # Marketplace Bridge: AI Score 70+ ise marketplace'e gönder
        marketplace_item_id = await check_and_send_to_marketplace(
            session=session,
            user_quest=uq,
            ai_score=final_ai_score,
        )
        
        if marketplace_item_id:
            # Marketplace'e gönderildi - metadata'ya ekle
            if uq.proof_payload_ref:
                # proof_payload_ref metadata olarak saklanıyor, marketplace_item_id ekle
                pass  # TODO: Metadata'ya ekle
    
    await session.commit()
    await session.refresh(uq)
    
    return uq

