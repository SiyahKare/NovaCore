"""
Telegram Gateway Router
Telegram bot ↔ NovaCore bridge endpoints
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, and_

from app.core.config import settings
from app.core.db import get_session
from app.identity.models import User
from app.identity.service import IdentityService
from app.wallet.service import WalletService
from app.xp_loyalty.service import XpLoyaltyService

from .models import TelegramAccount
from .schemas import (
    TelegramLinkRequest,
    TelegramLinkResponse,
    TelegramMeResponse,
    TelegramTasksResponse,
    TelegramTask,
    TelegramTaskSubmitRequest,
    TelegramTaskSubmitResponse,
    TelegramReferralClaimRequest,
    TelegramReferralClaimResponse,
    TelegramStreakCheckinRequest,
    TelegramStreakCheckinResponse,
    PendingTaskSubmission,
    DAOQueueResponse,
    QuestResponse,
)
from .leaderboard_schemas import (
    LeaderboardResponse,
    LeaderboardEntry,
    ProfileCardResponse,
)
from .event_service import EventService
from .quest_service import QuestService
from .event_schemas import (
    ActiveEventsResponse,
    EventResponse,
    EventJoinResponse,
    EventLeaderboardResponse,
    EventLeaderboardEntry,
)
from app.abuse.service import AbuseGuard
from app.abuse.models import AbuseEventType

router = APIRouter(prefix="/api/v1/telegram", tags=["telegram"])


# --- Security ---

async def verify_bridge_token(
    x_tg_bridge_token: str | None = Header(None, alias="X-TG-BRIDGE-TOKEN"),
) -> bool:
    """
    Telegram bridge token doğrulama.
    
    Bot → NovaCore arası servis token.
    .env'de TELEGRAM_BRIDGE_TOKEN olarak tanımlı.
    
    Prod'da token zorunlu (hard fail).
    """
    expected_token = getattr(settings, "TELEGRAM_BRIDGE_TOKEN", None)
    
    # Prod'da token zorunlu
    if settings.is_prod:
        if not expected_token:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="TELEGRAM_BRIDGE_TOKEN not configured in production",
            )
        
        if not x_tg_bridge_token or x_tg_bridge_token != expected_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing Telegram bridge token",
            )
    else:
        # Dev mode: token yoksa uyar ama geç
        if expected_token and (not x_tg_bridge_token or x_tg_bridge_token != expected_token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing Telegram bridge token",
            )
    
    return True


async def get_telegram_account(
    telegram_user_id: int,
    session: AsyncSession = Depends(get_session),
) -> TelegramAccount | None:
    """Telegram account'u telegram_user_id ile bul."""
    result = await session.execute(
        select(TelegramAccount).where(
            TelegramAccount.telegram_user_id == telegram_user_id
        )
    )
    return result.scalar_one_or_none()


async def get_or_create_telegram_account(
    telegram_user_id: int,
    username: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
) -> tuple[TelegramAccount, User]:
    """
    Telegram account'u bul veya oluştur.
    
    Eğer yoksa:
    1. User'ı telegram_id ile bul veya oluştur
    2. TelegramAccount oluştur
    """
    # Önce TelegramAccount var mı bak
    account = await get_telegram_account(telegram_user_id, session)
    
    if account:
        # User'ı çek
        result = await session.execute(
            select(User).where(User.id == account.user_id)
        )
        user = result.scalar_one()
        
        # last_seen_at güncelle
        account.last_seen_at = datetime.utcnow()
        session.add(account)
        await session.commit()
        await session.refresh(account)
        
        return account, user
    
    # Yeni account oluştur
    identity_service = IdentityService(session)
    
    # User'ı telegram_id ile bul veya oluştur
    user = await identity_service.get_user_by_telegram_id(telegram_user_id)
    
    if not user:
        # Yeni user oluştur
        display_name = f"{first_name or ''} {last_name or ''}".strip() or username or f"User {telegram_user_id}"
        
        user = await identity_service.create_user(
            telegram_id=telegram_user_id,
            username=username,
            display_name=display_name,
        )
    
    # TelegramAccount oluştur
    account = TelegramAccount(
        user_id=user.id,
        telegram_user_id=telegram_user_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        first_seen_at=datetime.utcnow(),
        last_seen_at=datetime.utcnow(),
    )
    
    session.add(account)
    await session.commit()
    await session.refresh(account)
    
    return account, user


# --- Endpoints ---

@router.post(
    "/link",
    response_model=TelegramLinkResponse,
    summary="Telegram kullanıcısını NovaCore User ile eşle",
)
async def link_telegram_user(
    payload: TelegramLinkRequest,
    session: AsyncSession = Depends(get_session),
    _verified: bool = Depends(verify_bridge_token),
):
    """
    Telegram kullanıcısını NovaCore User ile eşle.
    
    Bot'tan `/start` komutu geldiğinde çağrılır.
    start_param varsa HMAC doğrulanır, yoksa telegram_user_id ile user bulunur/oluşturulur.
    """
    # Start param verification (if provided)
    verified_user_id = None
    if payload.start_param:
        is_valid, param_payload = verify_start_param(payload.start_param)
        if is_valid and param_payload:
            verified_user_id = param_payload.get("telegram_user_id")
            # Verify telegram_user_id matches
            if verified_user_id != payload.telegram_user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Start param telegram_user_id mismatch",
                )
        else:
            # Invalid signature - still allow but log warning
            # In production, you might want to reject this
            pass
    
    account, user = await get_or_create_telegram_account(
        telegram_user_id=payload.telegram_user_id,
        username=payload.username,
        first_name=payload.first_name,
        last_name=payload.last_name,
        session=session,
    )
    
    return TelegramLinkResponse(
        success=True,
        user_id=user.id,
        telegram_account_id=account.id,
        message="Telegram account linked successfully",
    )


@router.get(
    "/me",
    response_model=TelegramMeResponse,
    summary="Telegram kullanıcısının tam profil bilgisi",
)
async def get_telegram_me(
    telegram_user_id: int,
    session: AsyncSession = Depends(get_session),
    _verified: bool = Depends(verify_bridge_token),
):
    """
    Telegram kullanıcısının tam profil bilgisi.
    
    Wallet, XP, NovaScore, CP bilgilerini içerir.
    """
    account = await get_telegram_account(telegram_user_id, session)
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telegram account not found. Call /link first.",
        )
    
    # User'ı çek
    result = await session.execute(
        select(User).where(User.id == account.user_id)
    )
    user = result.scalar_one()
    
    # Wallet balance
    wallet_service = WalletService(session)
    wallet = await wallet_service.get_account(user.id)
    balance = str(wallet.balance) if wallet else "0"
    
    # XP/Loyalty
    loyalty_service = XpLoyaltyService(session)
    loyalty = await loyalty_service.get_loyalty_profile(user.id)
    
    # NovaScore & CP (optional, may fail if consent not signed)
    nova_score = None
    cp_value = 0
    regime = "NORMAL"
    
    try:
        # Get CP
        from app.justice.router import JusticeService
        
        justice_service = JusticeService(session)
        cp_state = await justice_service.get_cp(str(user.id))
        if cp_state:
            cp_value = cp_state.cp_value
            regime = cp_state.regime
        
        # Get NovaScore (requires consent)
        from app.consent.router import ConsentService
        from app.nova_score.router import NovaScoreService
        
        consent_service = ConsentService(session)
        try:
            pp = await consent_service.get_privacy_profile(str(user.id))
            nova_score_service = NovaScoreService(justice_service)
            
            ECO = await nova_score_service.get_economy_features(str(user.id), pp)
            REL = await nova_score_service.get_reliability_features(str(user.id), pp)
            SOC = await nova_score_service.get_social_features(str(user.id), pp)
            IDc = await nova_score_service.get_identity_features(str(user.id), pp)
            CON = await nova_score_service.get_contribution_features(str(user.id), pp)
            
            from app.nova_score.schemas import NovaScoreComponents
            components = NovaScoreComponents(ECO=ECO, REL=REL, SOC=SOC, ID=IDc, CON=CON)
            
            score, _, _ = nova_score_service.combine(components, cp_value)
            nova_score = score
        except HTTPException:
            # Privacy profile not found - consent not signed
            pass
    except Exception:
        # NovaScore/CP may not be available
        pass
    
    return TelegramMeResponse(
        user_id=user.id,
        telegram_user_id=account.telegram_user_id,
        username=account.username or user.username,
        display_name=user.display_name or account.first_name,
        wallet_balance=balance,
        xp_total=loyalty.xp_total if loyalty else 0,
        level=loyalty.level if loyalty else 1,
        tier=loyalty.tier if loyalty else "Bronze",
        xp_to_next_level=loyalty.xp_to_next_level if loyalty else 0,
        nova_score=nova_score,
        cp_value=cp_value,
        regime=regime,
        first_seen_at=account.first_seen_at,
        last_seen_at=account.last_seen_at,
    )


@router.get(
    "/tasks",
    response_model=TelegramTasksResponse,
    summary="Kullanıcıya özel görev listesi",
)
async def get_telegram_tasks(
    telegram_user_id: int,
    session: AsyncSession = Depends(get_session),
    _verified: bool = Depends(verify_bridge_token),
):
    """
    Kullanıcıya özel görev listesi.
    
    Şu an mock data döner. İleride task service'ten çekilecek.
    """
    account = await get_telegram_account(telegram_user_id, session)
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telegram account not found",
        )
    
    # Mock tasks (ileride task service'ten çekilecek)
    tasks = [
        TelegramTask(
            id="daily_login",
            title="Günlük Giriş",
            description="Her gün bot'a giriş yap",
            category="daily",
            reward_xp=10,
            reward_ncr="1.0",
            status="available",
        ),
        TelegramTask(
            id="refer_friend",
            title="Arkadaş Davet Et",
            description="Bir arkadaşını davet et",
            category="special",
            reward_xp=50,
            reward_ncr="5.0",
            status="available",
        ),
    ]
    
    return TelegramTasksResponse(
        tasks=tasks,
        total_available=len([t for t in tasks if t.status == "available"]),
        total_completed=0,
    )


@router.post(
    "/tasks/{task_id}/submit",
    response_model=TelegramTaskSubmitResponse,
    summary="Görev tamamlama",
)
async def submit_telegram_task(
    task_id: str,
    payload: TelegramTaskSubmitRequest,
    telegram_user_id: int,
    session: AsyncSession = Depends(get_session),
    _verified: bool = Depends(verify_bridge_token),
):
    """
    Görev tamamlama.
    
    Bot'tan görev tamamlandığında çağrılır.
    XP ve NCR ödülü verilir.
    """
    account = await get_telegram_account(telegram_user_id, session)
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telegram account not found",
        )
    
    # Abuse guards (old + new)
    from .abuse_guard import AbuseGuard as OldAbuseGuard
    old_abuse_guard = OldAbuseGuard(session)
    risk_abuse_guard = AbuseGuard(session)
    
    # Check cooldown (RiskScore 9+)
    risk_profile = await risk_abuse_guard.get_or_create_profile(account.user_id)
    if risk_abuse_guard.requires_cooldown(risk_profile.risk_score):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Hesabınız cooldown'da (RiskScore: {risk_profile.risk_score:.1f}/10). Lütfen daha sonra tekrar deneyin.",
        )
    
    # Check task access (old guard)
    access_allowed, access_reason = await old_abuse_guard.check_task_access(
        user_id=account.user_id,
        task_id=task_id,
    )
    if not access_allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=access_reason or "Göreve erişim reddedildi",
        )
    
    # Check submission allowed (idempotency + rate limit - old guard)
    submission_allowed, submission_reason = await old_abuse_guard.check_task_submission_allowed(
        user_id=account.user_id,
        task_id=task_id,
        external_id=payload.metadata.get("external_id") if payload.metadata else None,
    )
    if not submission_allowed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=submission_reason or "Görev submit edilemez",
        )
    
    # Get task details
    from app.telegram_gateway.task_models import Task, TaskSubmission, SubmissionStatus, TaskAssignment
    import hashlib
    
    task_result = await session.execute(
        select(Task).where(Task.id == task_id)
    )
    task = task_result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Görev bulunamadı",
        )
    
    # Get assignment time for too-fast detection
    assignment_result = await session.execute(
        select(TaskAssignment).where(
            and_(
                TaskAssignment.user_id == account.user_id,
                TaskAssignment.task_id == task_id,
            )
        ).order_by(TaskAssignment.assigned_at.desc())
    )
    assignment = assignment_result.scalar_one_or_none()
    assigned_at = assignment.assigned_at if assignment else None
    
    # Check duplicate proof (if proof provided)
    proof_hash = None
    if payload.proof:
        proof_hash = hashlib.sha256(payload.proof.encode()).hexdigest()
        await risk_abuse_guard.check_duplicate_proof(
            user_id=account.user_id,
            task_id=task_id,
            proof_hash=proof_hash,
        )
    
    # Check too fast completion
    if assigned_at:
        await risk_abuse_guard.check_too_fast_completion(
            user_id=account.user_id,
            task_id=task_id,
            assigned_at=assigned_at,
        )
    
    # Create submission (idempotent)
    submission_metadata = payload.metadata or {}
    if proof_hash:
        submission_metadata["proof_hash"] = proof_hash
    
    submission = TaskSubmission(
        user_id=account.user_id,
        task_id=task_id,
        proof=payload.proof,
        proof_metadata=submission_metadata,
        status=SubmissionStatus.PENDING,
        external_id=payload.metadata.get("external_id") if payload.metadata else None,
    )
    session.add(submission)
    await session.commit()
    await session.refresh(submission)
    
    # Auto-approve logic with RiskScore check
    auto_approve = False
    if task.proof_type == "none":
        # Simple tasks: auto-approve if RiskScore < 6 (no forced HITL)
        if not risk_abuse_guard.requires_forced_hitl(risk_profile.risk_score):
            auto_approve = True
    
    # TODO: AI Scoring integration here
    # For now, we'll use simple auto-approve/reject logic
    # In production, you'd call: score_result = await score_task(task, payload)
    # total_score = score_result.total_score
    # if total_score < 50: → REJECTED + AUTO_REJECT event
    # elif 50 <= total_score < 70: → PENDING (HITL)
    # else: → APPROVED
    
    if auto_approve:
        submission.status = SubmissionStatus.APPROVED
        session.add(submission)
        await session.commit()
    else:
        # For now, keep as PENDING (will be reviewed manually or by AI)
        # If we had AI scoring, we'd set status based on score here
        pass
    
    # Check for auto-reject (if status is REJECTED, register event)
    if submission.status == SubmissionStatus.REJECTED:
        # Register AUTO_REJECT event
        await risk_abuse_guard.register_event(
            user_id=account.user_id,
            event_type=AbuseEventType.AUTO_REJECT,
            meta={
                "task_id": task_id,
                "submission_id": submission.id,
            },
        )
        # Check for low quality burst
        await risk_abuse_guard.check_low_quality_burst(account.user_id)
    
    # Reward (if approved)
    if submission.status == SubmissionStatus.APPROVED:
        from app.telegram_gateway.task_models import TaskReward
        from decimal import Decimal
        
        # Refresh risk profile (may have changed from events)
        risk_profile = await risk_abuse_guard.get_or_create_profile(account.user_id)
        
        # Base rewards
        base_xp = task.reward_xp
        base_ncr = Decimal(str(task.reward_ncr))
        
        # Compute final rewards (Event bonuses + RiskScore multiplier)
        # Single source of truth: EventService.compute_final_rewards
        event_service = EventService(session)
        total_xp, pre_treasury_ncr, risk_multiplier = await event_service.compute_final_rewards(
            user_id=account.user_id,
            task_id=task_id,
            base_xp=base_xp,
            base_ncr=base_ncr,
            risk_score=risk_profile.risk_score,
        )
        
        # Apply Treasury Cap (günlük limit kontrolü)
        from app.wallet.treasury_cap import apply_treasury_cap
        from decimal import Decimal
        
        treasury_adjusted_ncr, treasury_meta = await apply_treasury_cap(
            session=session,
            pre_treasury_ncr=float(pre_treasury_ncr),
        )
        total_ncr = Decimal(str(treasury_adjusted_ncr))
        
        # XP event (total XP with bonuses)
        from app.xp_loyalty.schemas import XpEventCreate
        
        loyalty_service = XpLoyaltyService(session)
        xp_event = await loyalty_service.create_xp_event(
            XpEventCreate(
                user_id=account.user_id,
                amount=total_xp,
                event_type="TASK_COMPLETED",
                source_app="aurora",
                metadata={"task_id": task_id, "proof": payload.proof, "base_xp": base_xp, "bonus_xp": total_xp - base_xp},
            )
        )
        
        # NCR reward (Treasury-adjusted NCR)
        wallet_service = WalletService(session)
        wallet_metadata = {
            "task_id": task_id,
            "submission_id": submission.id,
            "base_ncr": str(base_ncr),
            "bonus_ncr": str(pre_treasury_ncr - base_ncr),
            "treasury": treasury_meta,  # Treasury cap metadata
        }
        wallet_tx = await wallet_service.credit(
            user_id=account.user_id,
            amount=float(total_ncr),
            source="telegram_task",
            metadata=wallet_metadata,
        )
        
        # Create reward record
        reward = TaskReward(
            submission_id=submission.id,
            user_id=account.user_id,
            task_id=task_id,
            xp_amount=total_xp,
            ncr_amount=str(total_ncr),
            xp_event_id=xp_event.id if xp_event else None,
            wallet_tx_id=wallet_tx.id if wallet_tx else None,
        )
        session.add(reward)
        
        submission.status = SubmissionStatus.REWARDED
        session.add(submission)
        await session.commit()

        # Content Curator Hook: Eğer submission yüksek kaliteli ise CreatorAsset'e dönüştür
        try:
            from app.agency.services.content_curator import curate_from_submission
            asset = await curate_from_submission(session, submission.id)
            if asset:
                # Log success (optional)
                pass
        except Exception as e:
            # Curator hatası reward'ı etkilemesin
            import logging
            logging.getLogger("content_curator").error(f"Failed to curate submission {submission.id}: {e}")

        # Get updated balance
        wallet = await wallet_service.get_account(account.user_id)
        loyalty = await loyalty_service.get_loyalty_profile(account.user_id)
        
        # Bonus mesajı
        bonus_msg = ""
        if total_xp > base_xp:
            bonus_msg = f" (Event bonus: +{total_xp - base_xp} XP)"
        if total_ncr > base_ncr:
            bonus_msg += f" (+{total_ncr - base_ncr} NCR)"
        
        # RiskScore mesajı (eğer multiplier < 1.0 ise)
        risk_msg = ""
        if risk_multiplier < 1.0:
            risk_msg = f" (RiskScore: {risk_profile.risk_score:.1f}/10, çarpan: {risk_multiplier:.1f}x)"
        
        # Treasury mesajı (eğer damping uygulandıysa)
        treasury_msg = ""
        if treasury_meta.get("treasury_applied") and treasury_meta.get("multiplier", 1.0) < 1.0:
            load_pct = treasury_meta.get("load_ratio", 0.0) * 100
            treasury_msg = f" (Treasury yük: %{load_pct:.1f}, ödeme: {treasury_meta.get('multiplier', 1.0):.1f}x)"
        
        return TelegramTaskSubmitResponse(
            success=True,
            task_id=task_id,
            reward_xp=total_xp,
            reward_ncr=str(total_ncr),
            message=f"Görev tamamlandı! +{total_xp} XP, +{total_ncr} NCR{bonus_msg}{risk_msg}{treasury_msg}",
            new_balance=str(wallet.balance) if wallet else "0",
            new_xp_total=loyalty.xp_total if loyalty else 0,
            risk_score=risk_profile.risk_score,
            hitl_required=risk_abuse_guard.requires_forced_hitl(risk_profile.risk_score),
            reward_multiplier=risk_multiplier,
        )
    else:
        # Pending review - refresh risk profile for response
        risk_profile = await risk_abuse_guard.get_or_create_profile(account.user_id)
        return TelegramTaskSubmitResponse(
            success=True,
            task_id=task_id,
            reward_xp=0,
            reward_ncr="0",
            message="Görev submit edildi, onay bekleniyor.",
            new_balance="0",
            new_xp_total=0,
            risk_score=risk_profile.risk_score,
            hitl_required=risk_abuse_guard.requires_forced_hitl(risk_profile.risk_score),
            reward_multiplier=1.0,
        )


@router.get(
    "/quests",
    response_model=QuestResponse,
    summary="Günlük quest'leri getir",
)
async def get_user_quests(
    telegram_user_id: int,
    session: AsyncSession = Depends(get_session),
    _verified: bool = Depends(verify_bridge_token),
):
    """
    Kullanıcı için günlük quest'leri getir.
    
    - Onboarding tamamlanmamışsa boş liste döner
    - Günlük quest'ler otomatik atanır
    - Tamamlanmış quest'ler filtrelenir
    """
    account = await get_telegram_account(telegram_user_id, session)
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telegram account not found",
        )
    
    quest_service = QuestService(session)
    quests = await quest_service.get_user_quests(
        user_id=account.user_id,
        check_onboarding=True,
    )
    
    # Convert to TelegramTask format
    quest_tasks = []
    for task in quests:
        quest_tasks.append(
            TelegramTask(
                id=task.id,
                title=task.title,
                description=task.description,
                category=task.category,
                difficulty=task.difficulty.value,
                task_type=task.task_type.value,
                proof_type=task.proof_type.value,
                reward_xp=task.reward_xp,
                reward_ncr=task.reward_ncr,
                status="available",
                cooldown_seconds=task.cooldown_seconds,
                expires_at=task.expires_at,
                streak_required=task.streak_required,
                max_completions_per_user=task.max_completions_per_user,
            )
        )
    
    return QuestResponse(
        quests=quest_tasks,
        total_available=len(quest_tasks),
        onboarding_required=False,  # TODO: Check onboarding status
    )


@router.post(
    "/referral/claim",
    response_model=TelegramReferralClaimResponse,
    summary="Referral ödülü talep et (idempotent)",
)
async def claim_referral(
    payload: TelegramReferralClaimRequest,
    telegram_user_id: int,
    session: AsyncSession = Depends(get_session),
    _verified: bool = Depends(verify_bridge_token),
):
    """
    Referral ödülü talep et (idempotent).
    
    Kullanıcı bir referral code ile kayıt olduğunda çağrılır.
    Self-referral koruması var.
    """
    account = await get_telegram_account(telegram_user_id, session)
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telegram account not found",
        )
    
    # Find referrer by code (mock - ileride referral service'ten çekilecek)
    from app.identity.models import User
    
    # Mock: referral_code formatı "REF-{user_id}" olabilir
    referrer_user_id = None
    if payload.referral_code.startswith("REF-"):
        try:
            referrer_user_id = int(payload.referral_code.split("-")[1])
        except ValueError:
            pass
    
    if not referrer_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Geçersiz referral code",
        )
    
    # Abuse guard
    abuse_guard = AbuseGuard(session)
    
    referral_allowed, referral_reason = await abuse_guard.check_referral_allowed(
        referrer_user_id=referrer_user_id,
        referred_user_id=account.user_id,
    )
    if not referral_allowed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=referral_reason or "Referral ödülü verilemez",
        )
    
    # Default rewards
    reward_xp = 100
    reward_ncr = "10.0"
    
    # Create referral reward record
    from app.telegram_gateway.task_models import ReferralReward
    
    reward = ReferralReward(
        referrer_user_id=referrer_user_id,
        referred_user_id=account.user_id,
        referral_code=payload.referral_code,
        xp_amount=reward_xp,
        ncr_amount=reward_ncr,
    )
    session.add(reward)
    await session.commit()
    await session.refresh(reward)
    
    # XP event (for referrer)
    from app.xp_loyalty.schemas import XpEventCreate
    
    loyalty_service = XpLoyaltyService(session)
    xp_event = await loyalty_service.create_xp_event(
        XpEventCreate(
            user_id=referrer_user_id,
            amount=reward_xp,
            event_type="REFERRAL_REWARD",
            source_app="aurora",
            metadata={"referral_code": payload.referral_code, "referred_user_id": account.user_id},
        )
    )
    
    # NCR reward (for referrer)
    wallet_service = WalletService(session)
    wallet_tx = await wallet_service.credit(
        user_id=referrer_user_id,
        amount=float(reward_ncr),
        source="referral",
        metadata={"referral_code": payload.referral_code, "referred_user_id": account.user_id},
    )
    
    # Update reward record
    reward.xp_event_id = xp_event.id if xp_event else None
    reward.wallet_tx_id = wallet_tx.id if wallet_tx else None
    session.add(reward)
    await session.commit()
    
    return TelegramReferralClaimResponse(
        success=True,
        reward_xp=reward_xp,
        reward_ncr=reward_ncr,
        message=f"Referral ödülü alındı! +{reward_xp} XP, +{reward_ncr} NCR",
    )


@router.get(
    "/leaderboard",
    response_model=LeaderboardResponse,
    summary="Leaderboard (top users)",
)
async def get_telegram_leaderboard(
    period: str = "all_time",  # "daily", "weekly", "all_time"
    limit: int = 10,
    session: AsyncSession = Depends(get_session),
    _verified: bool = Depends(verify_bridge_token),
):
    """
    Leaderboard - En yüksek XP'li kullanıcılar.
    """
    from app.telegram_gateway.task_models import TaskSubmission, SubmissionStatus, ReferralReward
    from app.xp_loyalty.models import UserLoyalty
    from sqlalchemy import func, case
    
    # Time filter
    if period == "daily":
        since = datetime.utcnow() - timedelta(days=1)
    elif period == "weekly":
        since = datetime.utcnow() - timedelta(days=7)
    else:
        since = None
    
    # Get top users by XP
    query = (
        select(
            UserLoyalty.user_id,
            UserLoyalty.xp_total,
            UserLoyalty.level,
            UserLoyalty.tier,
        )
        .order_by(UserLoyalty.xp_total.desc())
        .limit(limit)
    )
    
    if since:
        # Filter by recent activity (simplified - check last submission)
        pass  # TODO: Add time-based filtering
    
    result = await session.execute(query)
    top_users = result.all()
    
    # Build entries with additional stats
    entries = []
    for rank, (user_id, xp_total, level, tier) in enumerate(top_users, 1):
        # Get telegram account
        account_result = await session.execute(
            select(TelegramAccount).where(TelegramAccount.user_id == user_id)
        )
        account = account_result.scalar_one_or_none()
        
        if not account:
            continue
        
        # Get user
        user_result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one()
        
        # Count tasks completed
        tasks_count_result = await session.execute(
            select(func.count(TaskSubmission.id)).where(
                and_(
                    TaskSubmission.user_id == user_id,
                    TaskSubmission.status == SubmissionStatus.REWARDED,
                )
            )
        )
        tasks_completed = tasks_count_result.scalar_one() or 0
        
        # Count referrals
        referrals_count_result = await session.execute(
            select(func.count(ReferralReward.id)).where(
                ReferralReward.referrer_user_id == user_id
            )
        )
        referrals_count = referrals_count_result.scalar_one() or 0
        
        entries.append(
            LeaderboardEntry(
                rank=rank,
                user_id=user_id,
                telegram_user_id=account.telegram_user_id,
                username=account.username or user.username,
                display_name=user.display_name or account.first_name,
                xp_total=xp_total,
                level=level,
                tier=tier,
                tasks_completed=tasks_completed,
                referrals_count=referrals_count,
            )
        )
    
    return LeaderboardResponse(
        entries=entries,
        total_users=len(entries),
        period=period,
        updated_at=datetime.utcnow(),
    )


@router.get(
    "/profile-card",
    response_model=ProfileCardResponse,
    summary="Profil kartı",
)
async def get_telegram_profile_card(
    telegram_user_id: int,
    session: AsyncSession = Depends(get_session),
    _verified: bool = Depends(verify_bridge_token),
):
    """
    Kullanıcının profil kartı (stats + achievements).
    """
    account = await get_telegram_account(telegram_user_id, session)
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telegram account not found",
        )
    
    # Get user
    user_result = await session.execute(
        select(User).where(User.id == account.user_id)
    )
    user = user_result.scalar_one()
    
    # Get loyalty
    loyalty_service = XpLoyaltyService(session)
    loyalty = await loyalty_service.get_loyalty_profile(account.user_id)
    
    # Count stats
    from app.telegram_gateway.task_models import TaskSubmission, SubmissionStatus, ReferralReward
    from sqlalchemy import func
    
    tasks_count_result = await session.execute(
        select(func.count(TaskSubmission.id)).where(
            and_(
                TaskSubmission.user_id == account.user_id,
                TaskSubmission.status == SubmissionStatus.REWARDED,
            )
        )
    )
    tasks_completed = tasks_count_result.scalar_one() or 0
    
    referrals_count_result = await session.execute(
        select(func.count(ReferralReward.id)).where(
            ReferralReward.referrer_user_id == account.user_id
        )
    )
    referrals_count = referrals_count_result.scalar_one() or 0
    
    # Calculate rank (simplified)
    from app.xp_loyalty.models import UserLoyalty
    
    rank_query = (
        select(func.count(UserLoyalty.user_id))
        .where(UserLoyalty.xp_total > loyalty.xp_total)
    )
    rank_result = await session.execute(rank_query)
    rank_all_time = (rank_result.scalar_one() or 0) + 1
    
    # Achievements (mock)
    achievements = []
    if loyalty.level >= 10:
        achievements.append("Level 10")
    if tasks_completed >= 50:
        achievements.append("50 Görev")
    if referrals_count >= 10:
        achievements.append("10 Referral")
    
    return ProfileCardResponse(
        user_id=user.id,
        telegram_user_id=account.telegram_user_id,
        username=account.username or user.username,
        display_name=user.display_name or account.first_name,
        xp_total=loyalty.xp_total,
        level=loyalty.level,
        tier=loyalty.tier,
        tasks_completed=tasks_completed,
        referrals_count=referrals_count,
        rank_all_time=rank_all_time,
        rank_weekly=None,  # TODO: Calculate weekly rank
        achievements=achievements,
        first_seen_at=account.first_seen_at,
        last_seen_at=account.last_seen_at,
    )


# --- Event Endpoints ---

@router.get(
    "/events/active",
    response_model=ActiveEventsResponse,
    summary="Aktif event'leri listele",
)
async def get_active_events(
    telegram_user_id: int,
    session: AsyncSession = Depends(get_session),
    _verified: bool = Depends(verify_bridge_token),
):
    """
    Kullanıcının katıldığı aktif event'leri listele.
    """
    account = await get_telegram_account(telegram_user_id, session)
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telegram account not found",
        )
    
    event_service = EventService(session)
    active_events = await event_service.get_active_events(user_id=account.user_id)
    
    # Get user's participation data
    from app.telegram_gateway.event_models import EventParticipation
    
    events_response = []
    for event in active_events:
        # Participation bilgisi
        participation_query = (
            select(EventParticipation)
            .where(
                and_(
                    EventParticipation.event_id == event.id,
                    EventParticipation.user_id == account.user_id,
                )
            )
        )
        participation_result = await session.execute(participation_query)
        participation = participation_result.scalar_one_or_none()
        
        events_response.append(
            EventResponse(
                id=event.id,
                code=event.code,
                name=event.name,
                description=event.description,
                event_type=event.event_type.value,
                status=event.status.value,
                starts_at=event.starts_at,
                ends_at=event.ends_at,
                reward_multiplier_xp=event.reward_multiplier_xp,
                reward_multiplier_ncr=event.reward_multiplier_ncr,
                max_participants=event.max_participants,
                min_level_required=event.min_level_required,
                is_joined=participation is not None,
                user_rank=participation.rank if participation else None,
                user_score={
                    "xp": participation.total_xp_earned if participation else 0,
                    "tasks_completed": participation.tasks_completed if participation else 0,
                } if participation else None,
            )
        )
    
    return ActiveEventsResponse(
        events=events_response,
        total_active=len(events_response),
    )


@router.get(
    "/events/{event_id}",
    response_model=EventResponse,
    summary="Event detayı",
)
async def get_event_detail(
    event_id: int,
    telegram_user_id: int,
    session: AsyncSession = Depends(get_session),
    _verified: bool = Depends(verify_bridge_token),
):
    """
    Event detayını getir.
    """
    account = await get_telegram_account(telegram_user_id, session)
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telegram account not found",
        )
    
    # Get event
    from app.telegram_gateway.event_models import Event, EventParticipation
    
    event_query = select(Event).where(Event.id == event_id)
    event_result = await session.execute(event_query)
    event = event_result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )
    
    # Participation bilgisi
    participation_query = (
        select(EventParticipation)
        .where(
            and_(
                EventParticipation.event_id == event.id,
                EventParticipation.user_id == account.user_id,
            )
        )
    )
    participation_result = await session.execute(participation_query)
    participation = participation_result.scalar_one_or_none()
    
    return EventResponse(
        id=event.id,
        code=event.code,
        name=event.name,
        description=event.description,
        event_type=event.event_type.value,
        status=event.status.value,
        starts_at=event.starts_at,
        ends_at=event.ends_at,
        reward_multiplier_xp=event.reward_multiplier_xp,
        reward_multiplier_ncr=event.reward_multiplier_ncr,
        max_participants=event.max_participants,
        min_level_required=event.min_level_required,
        is_joined=participation is not None,
        user_rank=participation.rank if participation else None,
        user_score={
            "xp": participation.total_xp_earned if participation else 0,
            "tasks_completed": participation.tasks_completed if participation else 0,
        } if participation else None,
    )


@router.post(
    "/events/{event_id}/join",
    response_model=EventJoinResponse,
    summary="Event'e katıl",
)
async def join_event(
    event_id: int,
    telegram_user_id: int,
    session: AsyncSession = Depends(get_session),
    _verified: bool = Depends(verify_bridge_token),
):
    """
    Kullanıcıyı event'e katıl.
    """
    account = await get_telegram_account(telegram_user_id, session)
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telegram account not found",
        )
    
    event_service = EventService(session)
    
    try:
        participation = await event_service.join_event(
            event_id=event_id,
            user_id=account.user_id,
        )
        
        # Get event name
        from app.telegram_gateway.event_models import Event
        
        event_query = select(Event).where(Event.id == event_id)
        event_result = await session.execute(event_query)
        event = event_result.scalar_one()
        
        return EventJoinResponse(
            success=True,
            message=f"{event.name} event'ine katıldın!",
            event_id=event_id,
            event_name=event.name,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/events/{event_id}/leaderboard",
    response_model=EventLeaderboardResponse,
    summary="Event leaderboard",
)
async def get_event_leaderboard(
    event_id: int,
    limit: int = 20,
    session: AsyncSession = Depends(get_session),
    _verified: bool = Depends(verify_bridge_token),
):
    """
    Event leaderboard'unu getir.
    """
    # Get event
    from app.telegram_gateway.event_models import Event, EventParticipation
    from sqlalchemy import func
    
    event_query = select(Event).where(Event.id == event_id)
    event_result = await session.execute(event_query)
    event = event_result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )
    
    event_service = EventService(session)
    participations = await event_service.get_event_leaderboard(
        event_id=event_id,
        limit=limit,
    )
    
    # Get user info for each participation
    from app.telegram_gateway.models import TelegramAccount
    
    entries = []
    for participation in participations:
        # Get telegram account
        account_query = (
            select(TelegramAccount)
            .where(TelegramAccount.user_id == participation.user_id)
        )
        account_result = await session.execute(account_query)
        account = account_result.scalar_one_or_none()
        
        if not account:
            continue
        
        # Get user
        user_query = select(User).where(User.id == participation.user_id)
        user_result = await session.execute(user_query)
        user = user_result.scalar_one()
        
        entries.append(
            EventLeaderboardEntry(
                rank=participation.rank or 0,
                user_id=participation.user_id,
                telegram_user_id=account.telegram_user_id,
                username=account.username or user.username,
                display_name=user.display_name or account.first_name,
                total_xp_earned=participation.total_xp_earned,
                total_ncr_earned=str(participation.total_ncr_earned),
                tasks_completed=participation.tasks_completed,
            )
        )
    
    # Total participants count
    count_query = (
        select(func.count(EventParticipation.id))
        .where(EventParticipation.event_id == event_id)
    )
    count_result = await session.execute(count_query)
    total_participants = count_result.scalar_one() or 0
    
    return EventLeaderboardResponse(
        event_id=event_id,
        event_name=event.name,
        entries=entries,
        total_participants=total_participants,
        updated_at=datetime.utcnow(),
    )


@router.post(
    "/streak/checkin",
    response_model=TelegramStreakCheckinResponse,
    summary="Günlük streak check-in",
)
async def streak_checkin(
    payload: TelegramStreakCheckinRequest,
    session: AsyncSession = Depends(get_session),
    _verified: bool = Depends(verify_bridge_token),
):
    """
    Günlük streak check-in.
    
    Kullanıcı her gün bot'a giriş yaptığında çağrılır.
    Streak sayacı artar ve XP/NCR ödülü verilir.
    """
    account = await get_telegram_account(payload.telegram_user_id, session)
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Telegram account not found",
        )
    
    # Get loyalty profile
    loyalty_service = XpLoyaltyService(session)
    loyalty = await loyalty_service.get_loyalty_profile(account.user_id)
    
    # Check if already checked in today
    from app.xp_loyalty.models import XpEvent
    from sqlalchemy import func, cast, Date
    
    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())
    
    checkin_query = (
        select(func.count(XpEvent.id))
        .where(
            and_(
                XpEvent.user_id == account.user_id,
                XpEvent.event_type == "STREAK_CHECKIN",
                cast(XpEvent.created_at, Date) == today,
            )
        )
    )
    checkin_result = await session.execute(checkin_query)
    already_checked_in = (checkin_result.scalar_one() or 0) > 0
    
    if already_checked_in:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Zaten bugün check-in yaptın!",
        )
    
    # Calculate streak
    # Get last check-in date
    last_checkin_query = (
        select(XpEvent.created_at)
        .where(
            and_(
                XpEvent.user_id == account.user_id,
                XpEvent.event_type == "STREAK_CHECKIN",
            )
        )
        .order_by(XpEvent.created_at.desc())
        .limit(1)
    )
    last_checkin_result = await session.execute(last_checkin_query)
    last_checkin = last_checkin_result.scalar_one_or_none()
    
    current_streak = loyalty.current_streak if loyalty else 0
    max_streak = loyalty.max_streak if loyalty else 0
    
    if last_checkin:
        last_date = last_checkin.date()
        yesterday = (datetime.utcnow() - timedelta(days=1)).date()
        
        if last_date == yesterday:
            # Streak continues
            current_streak += 1
        elif last_date == today:
            # Already checked in today (shouldn't happen, but double-check)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Zaten bugün check-in yaptın!",
            )
        else:
            # Streak broken, reset to 1
            current_streak = 1
    else:
        # First check-in
        current_streak = 1
    
    # Update max streak
    if current_streak > max_streak:
        max_streak = current_streak
    
    # Calculate rewards (base + streak bonus)
    base_xp = 10
    base_ncr = "1.0"
    
    # Streak bonus multipliers
    streak_multiplier = 1.0
    if current_streak >= 30:
        streak_multiplier = 2.0
    elif current_streak >= 14:
        streak_multiplier = 1.5
    elif current_streak >= 7:
        streak_multiplier = 1.25
    elif current_streak >= 3:
        streak_multiplier = 1.1
    
    reward_xp = int(base_xp * streak_multiplier)
    reward_ncr = str(float(base_ncr) * streak_multiplier)
    
    # Create XP event
    from app.xp_loyalty.schemas import XpEventCreate
    
    xp_event = await loyalty_service.create_xp_event(
        XpEventCreate(
            user_id=account.user_id,
            amount=reward_xp,
            event_type="STREAK_CHECKIN",
            source_app="nasipquest",
            metadata={
                "streak_days": current_streak,
                "streak_multiplier": streak_multiplier,
            },
        )
    )
    
    # Update loyalty streak
    if loyalty:
        loyalty.current_streak = current_streak
        loyalty.max_streak = max_streak
        session.add(loyalty)
    
    # NCR reward
    wallet_service = WalletService(session)
    wallet_tx = await wallet_service.credit(
        user_id=account.user_id,
        amount=float(reward_ncr),
        source="streak_checkin",
        metadata={"streak_days": current_streak},
    )
    
    await session.commit()
    
    # Get updated balance
    wallet = await wallet_service.get_account(account.user_id)
    updated_loyalty = await loyalty_service.get_loyalty_profile(account.user_id)
    
    bonus_msg = ""
    if streak_multiplier > 1.0:
        bonus_msg = f" (Streak bonus: {current_streak} gün x{streak_multiplier:.2f})"
    
    return TelegramStreakCheckinResponse(
        success=True,
        current_streak=current_streak,
        max_streak=max_streak,
        reward_xp=reward_xp,
        reward_ncr=reward_ncr,
        message=f"Check-in başarılı! +{reward_xp} XP, +{reward_ncr} NCR{bonus_msg}",
        new_balance=str(wallet.balance) if wallet else "0",
        new_xp_total=updated_loyalty.xp_total if updated_loyalty else 0,
    )


@router.get(
    "/dao/queue",
    response_model=DAOQueueResponse,
    summary="DAO inceleme kuyruğu (pending submissions)",
)
async def get_dao_queue(
    limit: int = 50,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
    _verified: bool = Depends(verify_bridge_token),
):
    """
    DAO Vekilleri için manuel inceleme kuyruğu.
    
    Pending durumundaki task submission'ları listeler.
    Bridge token + Admin yetki kontrolü gereklidir.
    """
    # Admin check (via bridge token - in production, verify admin status)
    # For now, bridge token is sufficient (admin-only endpoint)
    
    from app.telegram_gateway.task_models import TaskSubmission, Task, SubmissionStatus
    from sqlalchemy import func
    
    # Get pending submissions
    query = (
        select(TaskSubmission, Task, TelegramAccount, User)
        .join(Task, TaskSubmission.task_id == Task.id)
        .join(TelegramAccount, TaskSubmission.user_id == TelegramAccount.user_id)
        .join(User, TaskSubmission.user_id == User.id)
        .where(TaskSubmission.status == SubmissionStatus.PENDING)
        .order_by(TaskSubmission.submitted_at.asc())
        .limit(limit)
        .offset(offset)
    )
    
    result = await session.execute(query)
    rows = result.all()
    
    submissions = []
    for submission, task, account, user in rows:
        submissions.append(
            PendingTaskSubmission(
                submission_id=submission.id,
                user_id=submission.user_id,
                telegram_user_id=account.telegram_user_id,
                username=account.username or user.username,
                display_name=user.display_name or account.first_name,
                task_id=task.id,
                task_title=task.title,
                proof=submission.proof,
                proof_metadata=submission.proof_metadata or {},
                submitted_at=submission.submitted_at,
                status=submission.status.value,
            )
        )
    
    # Count total pending
    count_query = (
        select(func.count(TaskSubmission.id))
        .where(TaskSubmission.status == SubmissionStatus.PENDING)
    )
    count_result = await session.execute(count_query)
    total_pending = count_result.scalar_one() or 0
    
    return DAOQueueResponse(
        submissions=submissions,
        total_pending=total_pending,
        updated_at=datetime.utcnow(),
    )

