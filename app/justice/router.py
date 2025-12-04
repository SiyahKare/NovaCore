# app/justice/router.py

from fastapi import APIRouter, Depends, HTTPException, status, Query

from sqlalchemy.ext.asyncio import AsyncSession

from sqlmodel import select

from datetime import datetime
from typing import Optional



from .schemas import (
    ViolationCreate,
    ViolationResponse,
    CpStateResponse,
    CaseFileResponse,
    PolicyParamsResponse,
    AppealCreate,
    AppealResponse,
)

from .models import ViolationLog, UserCpState, TaskAppeal

from .policy import regime_for_cp

from .policy_service import PolicyService

from app.core.db import get_session

from app.consent.router import get_current_user_id, get_consent_service, ConsentService  # Auth helper

# NovaScore import'u lazy olacak (circular import önlemek için)



router = APIRouter(prefix="/api/v1/justice", tags=["justice"])





class JusticeService:

    def __init__(self, session: AsyncSession):

        self.session = session
        self._policy_service = PolicyService(session)
        self._cached_policy = None

    async def _get_policy(self, force_refresh: bool = False):
        """
        Load current Justice policy (DAO parameters) with simple caching.
        """
        if force_refresh or self._cached_policy is None:
            self._cached_policy = await self._policy_service.get_active_policy()
        return self._cached_policy



    async def _get_cp_state(self, user_id: str) -> UserCpState:

        result = await self.session.execute(

            select(UserCpState).where(UserCpState.user_id == user_id)

        )

        obj = result.scalar_one_or_none()

        if obj is None:

            policy = await self._get_policy()

            regime = regime_for_cp(0, policy)

            obj = UserCpState(user_id=user_id, cp_value=0, regime=regime)

            self.session.add(obj)

            await self.session.commit()

            await self.session.refresh(obj)

        return obj



    async def _apply_decay(self, state: UserCpState) -> UserCpState:

        now = datetime.utcnow()

        elapsed_sec = (now - state.last_updated_at).total_seconds()

        if elapsed_sec <= 0:

            return state



        elapsed_days = elapsed_sec / 86400.0
        policy = await self._get_policy()
        decay_amount = int(elapsed_days * policy.decay_per_day)



        if decay_amount <= 0:

            return state



        state.cp_value = max(0, state.cp_value - decay_amount)
        state.last_updated_at = now
        
        # Update regime based on new CP
        state.regime = regime_for_cp(state.cp_value, policy)
        
        self.session.add(state)
        await self.session.commit()
        await self.session.refresh(state)

        return state



    async def _cp_weight_for_violation(self, category: str, severity: int, code: str) -> int:
        """Calculate CP weight for violation using DAO-controlled parameters."""
        policy = await self._get_policy()
        
        # Get base weight from policy
        base_map = {
            "EKO": policy.base_eko,
            "COM": policy.base_com,
            "SYS": policy.base_sys,
            "TRUST": policy.base_trust,
        }
        base = base_map.get(category, policy.base_eko)
        
        # Get severity multiplier from policy
        mul_map = {
            1: policy.severity_multiplier.get("1", 0.5),
            2: policy.severity_multiplier.get("2", 1.0),
            3: policy.severity_multiplier.get("3", 1.5),
            4: policy.severity_multiplier.get("4", 2.0),
            5: policy.severity_multiplier.get("5", 3.0),
        }
        multiplier = mul_map.get(severity, 1.0)
        
        cp = int(base * multiplier)



        # İstersen bazı özel kodları burada override edebilirsin

        if code == "SYS_EXPLOIT":

            cp = max(cp, 60)

        if code == "TRUST_MULTIPLE_ACCOUNTS":

            cp = max(cp, 80)



        return cp



    async def add_violation(self, body: ViolationCreate) -> ViolationResponse:

        state = await self._get_cp_state(body.user_id)

        state = await self._apply_decay(state)

        cp_delta = await self._cp_weight_for_violation(
            category=body.category,
            severity=body.severity,
            code=body.code,
        )



        # log yaz

        v = ViolationLog(

            user_id=body.user_id,

            category=body.category,

            code=body.code,

            severity=body.severity,

            cp_delta=cp_delta,

            source=body.source,

            context=body.context,

        )

        self.session.add(v)



        # cp güncelle
        policy = await self._get_policy()
        old_cp = state.cp_value
        old_regime = state.regime
        state.cp_value = state.cp_value + cp_delta
        state.regime = regime_for_cp(state.cp_value, policy)
        state.last_updated_at = datetime.utcnow()

        self.session.add(state)
        
        # Justice Execution Engine: CP değişikliğini tetikle
        if old_cp != state.cp_value or old_regime != state.regime:
            from .execution_engine import JusticeExecutionEngine
            execution_engine = JusticeExecutionEngine(self.session)
            await execution_engine.on_cp_changed(
                user_id=body.user_id,
                old_cp=old_cp,
                new_cp=state.cp_value,
                old_regime=old_regime,
                new_regime=state.regime,
            )



        await self.session.commit()

        await self.session.refresh(v)

        await self.session.refresh(state)



        return ViolationResponse(

            id=str(v.id),

            user_id=v.user_id,

            category=v.category,  # type: ignore

            code=v.code,

            severity=v.severity,

            cp_delta=v.cp_delta,

            source=v.source,

            created_at=v.created_at,

        )



    async def get_cp(self, user_id: str) -> CpStateResponse:

        state = await self._get_cp_state(user_id)

        state = await self._apply_decay(state)

        # Decay sonrası regime'i de güncelle (policy zaten _apply_decay içinde güncellendi)
        policy = await self._get_policy()
        new_regime = regime_for_cp(state.cp_value, policy)

        if new_regime != state.regime:  # Eğer değiştiyse kaydet

            state.regime = new_regime

            self.session.add(state)

            await self.session.commit()

            await self.session.refresh(state)



        return CpStateResponse(

            user_id=state.user_id,

            cp_value=state.cp_value,

            regime=state.regime,  # type: ignore

            last_updated_at=state.last_updated_at,

        )



    async def list_violations(self, user_id: str, limit: int = 20) -> list[ViolationResponse]:

        """List recent violations for a user."""

        result = await self.session.execute(

            select(ViolationLog)

            .where(ViolationLog.user_id == user_id)

            .order_by(ViolationLog.created_at.desc())

            .limit(limit)

        )

        violations = result.scalars().all()

        return [

            ViolationResponse(

                id=str(v.id),

                user_id=v.user_id,

                category=v.category,  # type: ignore

                code=v.code,

                severity=v.severity,

                cp_delta=v.cp_delta,

                source=v.source,

                created_at=v.created_at,

            )

            for v in violations

        ]





def get_justice_service(
    session: AsyncSession = Depends(get_session),
) -> JusticeService:
    return JusticeService(session)


def get_policy_service(
    session: AsyncSession = Depends(get_session),
) -> PolicyService:
    return PolicyService(session)


@router.get(
    "/policy/current",
    response_model=PolicyParamsResponse,
    summary="Get current active policy parameters",
    description="Returns the currently active DAO-controlled policy parameters.",
)
async def get_current_policy(
    policy_service: PolicyService = Depends(get_policy_service),
) -> PolicyParamsResponse:
    """Get current active policy parameters."""
    policy = await policy_service.get_active_policy()
    return PolicyParamsResponse(
        version=policy.version,
        decay_per_day=policy.decay_per_day,
        base_eko=policy.base_eko,
        base_com=policy.base_com,
        base_sys=policy.base_sys,
        base_trust=policy.base_trust,
        threshold_soft_flag=policy.threshold_soft_flag,
        threshold_probation=policy.threshold_probation,
        threshold_restricted=policy.threshold_restricted,
        threshold_lockdown=policy.threshold_lockdown,
        onchain_address=policy.onchain_address,
        onchain_block=policy.onchain_block,
        synced_at=policy.synced_at,
        notes=policy.notes,
    )





@router.post(

    "/violations",

    response_model=ViolationResponse,

    status_code=status.HTTP_201_CREATED,

    summary="Yeni bir ihlal (violation) kaydı oluştur ve CP güncelle",

)

async def create_violation(

    body: ViolationCreate,

    service: JusticeService = Depends(get_justice_service),

    # istersen burada admin check de koyarsın

    _actor_id: str = Depends(get_current_user_id),

):

    # Şimdilik herkes log yazamaz, ileride role check ekle:

    # if not has_role(_actor_id, "moderator"): raise HTTPException(403,...)

    return await service.add_violation(body)





@router.get(

    "/cp/me",

    response_model=CpStateResponse,

    summary="Giriş yapan kullanıcının CP (Ceza Puanı) durumunu getir",

)

async def get_my_cp(

    service: JusticeService = Depends(get_justice_service),

    current_user_id: str = Depends(get_current_user_id),

):

    return await service.get_cp(current_user_id)





@router.get(

    "/cp/{user_id}",

    response_model=CpStateResponse,

    summary="Belirli kullanıcının CP durumunu getir (admin)",

)

async def get_user_cp_admin(

    user_id: str,

    service: JusticeService = Depends(get_justice_service),

    _actor_id: str = Depends(get_current_user_id),

):

    # TODO: admin yetkisi kontrolü

    return await service.get_cp(user_id)


@router.get(
    "/violations/me",
    response_model=list[ViolationResponse],
    summary="Giriş yapan kullanıcının violation'larını getir",
)
async def get_my_violations(
    service: JusticeService = Depends(get_justice_service),
    current_user_id: str = Depends(get_current_user_id),
    limit: int = Query(20, ge=1, le=100),
):
    """Get current user's violations."""
    return await service.list_violations(current_user_id, limit=limit)





@router.get(

    "/case/{user_id}",

    response_model=CaseFileResponse,

    summary="Bir kullanıcının Aurora durum dosyasını getir (denetçi)",

)

async def get_case_file(

    user_id: str,

    consent_service: ConsentService = Depends(get_consent_service),

    justice_service: JusticeService = Depends(get_justice_service),

    _actor_id: str = Depends(get_current_user_id),

):

    """

    Aurora Case File - Kullanıcının tüm durumunu tek endpoint'te getir.

    Ombudsman / Admin panel için kullanılır.

    TODO: Burada rol kontrolü: sadece 'ombudsman' / 'admin' görsün

    """

    # 1) privacy profile

    try:

        pp = await consent_service.get_privacy_profile(user_id)

    except HTTPException:

        pp = None



    # 2) CP durumu

    cp_state = await justice_service.get_cp(user_id)



    # 3) NovaScore hesapla (lazy import to avoid circular dependency)

    if pp:

        from app.nova_score.router import NovaScoreService

        from app.nova_score.schemas import NovaScoreComponents, ComponentScore

        # Use the same session from justice_service

        nova_score_service = NovaScoreService(justice_service)



        ECO = await nova_score_service.get_economy_features(user_id, pp)

        REL = await nova_score_service.get_reliability_features(user_id, pp)

        SOC = await nova_score_service.get_social_features(user_id, pp)

        IDc = await nova_score_service.get_identity_features(user_id, pp)

        CON = await nova_score_service.get_contribution_features(user_id, pp)



        components = NovaScoreComponents(ECO=ECO, REL=REL, SOC=SOC, ID=IDc, CON=CON)

        cp = cp_state.cp_value

        score, conf_overall, explanation = nova_score_service.combine(components, cp)



        # Recall durumunu kontrol et

        recall_state = "NONE"

        if pp.recall_requested_at:

            recall_state = "REQUESTED"



        if recall_state != "NONE":

            extra_msg = (

                " Verilerini YZ eğitiminden geri çekme talebinde bulunduğun için, "

                "geçmiş verilerin bir kısmı artık kullanılmıyor. NovaScore daha "

                "ihtiyatlı ve kısmi verilere dayanarak hesaplanıyor."

            )

            if explanation:

                explanation = explanation + extra_msg

            else:

                explanation = extra_msg



        nova_score_data = {

            "value": score,

            "components": components,

            "confidence_overall": conf_overall,

            "explanation": explanation,

        }

    else:

        nova_score_data = None



    # 4) son X violation

    violations = await justice_service.list_violations(user_id, limit=20)



    # 5) Build response using proper schema

    from .schemas import CaseFileResponse, NovaScorePayload



    # Convert nova_score_data dict to NovaScorePayload if exists

    nova_score_payload = None

    if nova_score_data:

        # Convert components to dict for response
        components_dict = nova_score_data["components"].model_dump() if hasattr(nova_score_data["components"], "model_dump") else nova_score_data["components"]

        nova_score_payload = NovaScorePayload(

            value=nova_score_data["value"],

            components=components_dict,

            confidence_overall=nova_score_data["confidence_overall"],

            explanation=nova_score_data.get("explanation"),

        )



    # Convert privacy profile to dict for response
    privacy_profile_dict = pp.model_dump() if pp else None

    return CaseFileResponse(

        user_id=user_id,

        privacy_profile=privacy_profile_dict,

        cp_state=cp_state,

        nova_score=nova_score_payload,

        recent_violations=violations,

    )


@router.post(
    "/appeals",
    response_model=AppealResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Task submission için itiraz et",
    description="Reddedilen görev için itiraz et. Appeal fee (5 NCR) ödenir ve görev Ethics Appeal Queue'ya alınır.",
)
async def create_appeal(
    body: AppealCreate,
    current_user_id: str = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_session),
) -> AppealResponse:
    """
    Task submission için itiraz et.
    
    Kullanıcı reddedilen bir görev için itiraz edebilir.
    Appeal fee (5 NCR) ödenir ve görev Ethics Appeal Queue'ya alınır.
    """
    from app.telegram_gateway.task_models import TaskSubmission, SubmissionStatus
    from app.wallet.service import WalletService
    from app.identity.models import User
    
    # Get submission
    submission_query = select(TaskSubmission).where(TaskSubmission.id == body.submission_id)
    submission_result = await session.execute(submission_query)
    submission = submission_result.scalar_one_or_none()
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task submission not found",
        )
    
    # Verify user owns the submission
    user_id_int = int(current_user_id)
    if submission.user_id != user_id_int:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only appeal your own submissions",
        )
    
    # Check if submission is rejected
    if submission.status != SubmissionStatus.REJECTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only appeal rejected submissions",
        )
    
    # Check if appeal already exists
    existing_appeal_query = select(TaskAppeal).where(
        TaskAppeal.submission_id == body.submission_id
    )
    existing_appeal_result = await session.execute(existing_appeal_query)
    existing_appeal = existing_appeal_result.scalar_one_or_none()
    
    if existing_appeal:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Appeal already exists for this submission",
        )
    
    # Charge appeal fee (5 NCR)
    wallet_service = WalletService(session)
    appeal_fee = 5.0
    
    try:
        wallet_tx = await wallet_service.debit(
            user_id=user_id_int,
            amount=appeal_fee,
            source="appeal_fee",
            metadata={"submission_id": body.submission_id},
        )
        appeal_fee_paid = True
    except Exception as e:
        # Insufficient balance or other error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Appeal fee payment failed: {str(e)}",
        )
    
    # Create appeal
    appeal = TaskAppeal(
        submission_id=body.submission_id,
        user_id=current_user_id,
        reason=body.reason,
        status="pending",
        appeal_fee_paid=appeal_fee_paid,
        appeal_fee_tx_id=wallet_tx.id if wallet_tx else None,
    )
    
    session.add(appeal)
    
    # Update submission status to pending (move to Ethics Appeal Queue)
    submission.status = SubmissionStatus.PENDING
    session.add(submission)
    
    await session.commit()
    await session.refresh(appeal)
    
    # Track telemetry event
    from app.telemetry.models import TelemetryEvent
    telemetry_event = TelemetryEvent(
        user_id=user_id_int,
        event="appeal_submitted",
        payload={
            "submission_id": body.submission_id,
            "appeal_id": appeal.id,
        },
        source="nasipquest",
    )
    session.add(telemetry_event)
    await session.commit()
    
    return AppealResponse(
        id=appeal.id or 0,
        submission_id=appeal.submission_id,
        user_id=appeal.user_id,
        reason=appeal.reason,
        status=appeal.status,
        appeal_fee_paid=appeal.appeal_fee_paid,
        created_at=appeal.created_at,
        reviewed_at=appeal.reviewed_at,
        reviewed_by=appeal.reviewed_by,
        review_notes=appeal.review_notes,
    )

