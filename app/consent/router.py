# novacore/app/consent/router.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from app.core.security import get_admin_user

from typing import List

from datetime import datetime

import hashlib

import json

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from sqlmodel import select

from app.core.db import get_session



from .schemas import (

    ConsentSessionCreate,

    ConsentSessionCreated,

    ClauseAcceptanceStatus,

    RedlineConsentRequest,

    ConsentSignRequest,

    ConsentRecordResponse,

    UserPrivacyProfileResponse,

    ImmutableLedgerRecord,

    ImmutableLedgerMetadata,

    DataUsagePolicy,

    PrivacyPolicySnapshot,

    RecallRequest,

    RecallStatusResponse,

)

from .models import (

    ConsentSession as ConsentSessionModel,

    ConsentClauseLog,

    RedlineConsent,

    ConsentRecord as ConsentRecordModel,

    UserPrivacyProfile as UserPrivacyProfileModel,

)

from app.core.db import get_session

from app.core.security import get_current_user

from app.identity.models import User



# --- Helper Functions ---



async def get_current_user_id(current_user: User = Depends(get_current_user)) -> str:

    """Get current user ID as string from authenticated user."""

    return str(current_user.id)





# --- Service Implementation ---



class ConsentService:

    """

    NovaCore consent motoru için service katmanı.

    Burada DB, immutable ledger ve privacy profile yönetimini soyutluyoruz.

    """



    def __init__(self, session: AsyncSession):

        self.session = session



    # --- SESSION ---



    async def create_session(

        self, payload: ConsentSessionCreate

    ) -> ConsentSessionCreated:

        obj = ConsentSessionModel(

            user_id=payload.user_id,

            client_fingerprint=payload.client_fingerprint,

        )

        self.session.add(obj)

        await self.session.commit()

        await self.session.refresh(obj)



        return ConsentSessionCreated(

            session_id=str(obj.id),

            user_id=obj.user_id,

            created_at=obj.created_at,

        )



    async def validate_session(self, session_id: str) -> bool:

        try:

            session_uuid = uuid.UUID(session_id)

        except ValueError:

            return False



        result = await self.session.execute(

            select(ConsentSessionModel).where(

                ConsentSessionModel.id == session_uuid,

                ConsentSessionModel.is_active == True,

            )

        )

        obj = result.scalar_one_or_none()

        return obj is not None



    # --- CLAUSES ---



    async def log_clause_acceptance(self, status: ClauseAcceptanceStatus) -> None:

        # Session'dan user_id çek

        try:

            session_uuid = uuid.UUID(status.session_id)

        except ValueError:

            raise HTTPException(

                status_code=status.HTTP_400_BAD_REQUEST,

                detail="Invalid session ID format",

            )



        session_result = await self.session.execute(

            select(ConsentSessionModel).where(ConsentSessionModel.id == session_uuid)

        )

        session_obj = session_result.scalar_one_or_none()

        if not session_obj:

            raise HTTPException(

                status_code=status.HTTP_404_NOT_FOUND,

                detail="Session not found",

            )



        obj = ConsentClauseLog(

            session_id=session_uuid,

            user_id=session_obj.user_id,

            clause_id=status.clause_id,

            status=status.status,

            comprehension_passed=status.comprehension_passed,

            answered_at=status.answered_at,

        )

        self.session.add(obj)

        await self.session.commit()



    async def all_clauses_accepted(self, session_id: str) -> bool:

        # kritik maddeler listesi config'ten de gelebilir

        REQUIRED = {"1.1", "1.2", "2.1", "2.2", "3.1", "3.2", "4.1", "4.2"}



        try:

            session_uuid = uuid.UUID(session_id)

        except ValueError:

            return False



        result = await self.session.execute(

            select(ConsentClauseLog).where(

                ConsentClauseLog.session_id == session_uuid,

                ConsentClauseLog.status == "ACCEPTED",

            )

        )

        accepted_ids = {row.clause_id for row in result.scalars().all()}

        return REQUIRED.issubset(accepted_ids)



    # --- REDLINE ---



    async def log_redline_consent(self, req: RedlineConsentRequest) -> None:

        try:

            session_uuid = uuid.UUID(req.session_id)

        except ValueError:

            raise HTTPException(

                status_code=status.HTTP_400_BAD_REQUEST,

                detail="Invalid session ID format",

            )



        session_result = await self.session.execute(

            select(ConsentSessionModel).where(ConsentSessionModel.id == session_uuid)

        )

        session_obj = session_result.scalar_one_or_none()

        if not session_obj:

            raise HTTPException(

                status_code=status.HTTP_404_NOT_FOUND,

                detail="Session not found",

            )



        obj = RedlineConsent(

            session_id=session_uuid,

            user_id=session_obj.user_id,

            redline_status=req.redline_status,

            user_note_hash=req.user_note_hash,

            answered_at=req.answered_at,

        )

        self.session.add(obj)

        await self.session.commit()



    async def redline_accepted(self, session_id: str) -> bool:

        try:

            session_uuid = uuid.UUID(session_id)

        except ValueError:

            return False



        result = await self.session.execute(

            select(RedlineConsent).where(

                RedlineConsent.session_id == session_uuid,

                RedlineConsent.redline_status == "ACCEPTED",

            )

        )

        return result.scalar_one_or_none() is not None



    # --- SIGN / LEDGER ---



    async def get_legal_text(self, contract_version: str) -> str:

        # Şimdilik hardcoded; ileride config'ten çekersin

        return f"SiyahKare Veri Etiği ve Şeffaflık Sözleşmesi ({contract_version})"



    async def write_immutable_record(

        self, *, payload: ConsentSignRequest, contract_hash: str

    ) -> ImmutableLedgerRecord:

        record = ConsentRecordModel(

            user_id=payload.user_id,

            contract_version=payload.contract_version,

            clauses_accepted=payload.clauses_accepted,

            redline_accepted=(payload.redline_status == "ACCEPTED"),

            signature_text=payload.signature_text,

            contract_hash=contract_hash,

            signed_at=payload.signed_at,

            client_fingerprint=payload.client_fingerprint,

        )

        self.session.add(record)

        await self.session.commit()

        await self.session.refresh(record)



        now = record.created_at



        return ImmutableLedgerRecord(

            record_id=str(record.id),

            user_id=record.user_id,

            contract_version=record.contract_version,

            signed_at=record.signed_at,

            created_at=now,

            immutable=True,

            ledger=ImmutableLedgerMetadata(

                contract_hash=contract_hash,

                ledger_slot=None,

                raw_metadata=payload.dict(),

            ),

        )



    async def update_privacy_profile_from_consent(

        self, record: ImmutableLedgerRecord

    ) -> UserPrivacyProfileResponse:

        # Sözleşmeye göre default FULL policy snapshot

        policy = PrivacyPolicySnapshot(

            behavioral=DataUsagePolicy(

                allowed=True,

                purposes=[

                    "nova_score",

                    "learning_optimization",

                    "resource_efficiency",

                ],

            ),

            performance=DataUsagePolicy(

                allowed=True,

                purposes=["nova_score", "learning_optimization"],

            ),

            economy=DataUsagePolicy(

                allowed=True,

                purposes=["nova_score", "resource_efficiency"],

            ),

            redline=DataUsagePolicy(

                allowed=True,

                purposes=[],

                requires_human_ethics_board=True,

            ),

        )



        # DB'de UserPrivacyProfile upsert et

        result = await self.session.execute(

            select(UserPrivacyProfileModel).where(

                UserPrivacyProfileModel.user_id == record.user_id

            )

        )

        obj = result.scalar_one_or_none()

        if obj is None:

            obj = UserPrivacyProfileModel(

                user_id=record.user_id,

                latest_consent_id=uuid.UUID(record.record_id),

                contract_version=record.contract_version,

                data_usage_policy=policy.dict(),

                consent_level="FULL",

                recall_requested_at=None,

            )

            self.session.add(obj)

        else:

            obj.latest_consent_id = uuid.UUID(record.record_id)

            obj.contract_version = record.contract_version

            obj.data_usage_policy = policy.dict()

            obj.consent_level = "FULL"

            obj.last_policy_updated_at = datetime.utcnow()



        await self.session.commit()



        return UserPrivacyProfileResponse(

            user_id=obj.user_id,

            latest_consent_id=str(obj.latest_consent_id)

            if obj.latest_consent_id

            else None,

            contract_version=obj.contract_version,

            policy=policy,

            consent_level=obj.consent_level,

            recall_requested_at=obj.recall_requested_at,

            last_policy_updated_at=obj.last_policy_updated_at,

        )



    async def get_record(self, record_id: str) -> ImmutableLedgerRecord:

        try:

            record_uuid = uuid.UUID(record_id)

        except ValueError:

            raise HTTPException(

                status_code=status.HTTP_400_BAD_REQUEST,

                detail="Invalid record ID format",

            )



        result = await self.session.execute(

            select(ConsentRecordModel).where(ConsentRecordModel.id == record_uuid)

        )

        record = result.scalar_one_or_none()

        if not record:

            raise HTTPException(

                status_code=status.HTTP_404_NOT_FOUND,

                detail="Consent record not found",

            )



        return ImmutableLedgerRecord(

            record_id=str(record.id),

            user_id=record.user_id,

            contract_version=record.contract_version,

            signed_at=record.signed_at,

            created_at=record.created_at,

            immutable=True,

            ledger=ImmutableLedgerMetadata(

                contract_hash=record.contract_hash,

                ledger_slot=None,

                raw_metadata={

                    "clauses_accepted": record.clauses_accepted,

                    "redline_accepted": record.redline_accepted,

                    "signature_text": record.signature_text,

                    "contract_version": record.contract_version,

                    "signed_at": record.signed_at.isoformat(),

                },

            ),

        )



    async def get_record_full(self, record_id: str) -> tuple[ImmutableLedgerRecord, ConsentRecordModel]:
        """Get both ImmutableLedgerRecord and ConsentRecordModel."""
        ledger_record = await self.get_record(record_id)
        
        try:
            record_uuid = uuid.UUID(record_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid record ID format",
            )

        result = await self.session.execute(
            select(ConsentRecordModel).where(ConsentRecordModel.id == record_uuid)
        )
        record = result.scalar_one_or_none()
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consent record not found",
            )
        
        return ledger_record, record

    async def get_privacy_profile(

        self, user_id: str

    ) -> UserPrivacyProfileResponse:

        result = await self.session.execute(

            select(UserPrivacyProfileModel).where(

                UserPrivacyProfileModel.user_id == user_id

            )

        )

        obj = result.scalar_one_or_none()

        if obj is None:

            raise HTTPException(

                status_code=status.HTTP_404_NOT_FOUND,

                detail="Privacy profile not found",

            )



        policy = PrivacyPolicySnapshot(**obj.data_usage_policy)



        return UserPrivacyProfileResponse(

            user_id=obj.user_id,

            latest_consent_id=str(obj.latest_consent_id)

            if obj.latest_consent_id

            else None,

            contract_version=obj.contract_version,

            policy=policy,

            consent_level=obj.consent_level,

            recall_requested_at=obj.recall_requested_at,

            last_policy_updated_at=obj.last_policy_updated_at,

        )



    async def request_recall(

        self, user_id: str, body: RecallRequest

    ) -> RecallStatusResponse:

        result = await self.session.execute(

            select(UserPrivacyProfileModel).where(

                UserPrivacyProfileModel.user_id == user_id

            )

        )

        obj = result.scalar_one_or_none()

        if obj is None:

            # Kullanıcının daha önce consent'i yoksa, profil yarat

            obj = UserPrivacyProfileModel(

                user_id=user_id,

                data_usage_policy={},

                consent_level=None,

            )

            self.session.add(obj)



        now = datetime.utcnow()

        obj.recall_mode = body.mode

        obj.recall_requested_at = now

        obj.recall_completed_at = None

        obj.last_policy_updated_at = now



        await self.session.commit()

        await self.session.refresh(obj)
        
        # Background işlem başlatılacak (async olarak çağrılacak)
        # Burada gerçek pipeline hook'ları devreye girecek



        return RecallStatusResponse(

            user_id=obj.user_id,

            recall_requested_at=obj.recall_requested_at,

            recall_mode=obj.recall_mode,

            recall_completed_at=obj.recall_completed_at,

            state="REQUESTED",

        )



    async def get_recall_status(self, user_id: str) -> RecallStatusResponse:

        result = await self.session.execute(

            select(UserPrivacyProfileModel).where(

                UserPrivacyProfileModel.user_id == user_id

            )

        )

        obj = result.scalar_one_or_none()

        if obj is None or obj.recall_mode is None:

            return RecallStatusResponse(

                user_id=user_id,

                recall_requested_at=None,

                recall_mode=None,

                recall_completed_at=None,

                state="NONE",

            )



        if obj.recall_completed_at is not None:

            state = "COMPLETED"

        elif obj.recall_requested_at is not None:

            # Eğer recall_requested_at var ama completed_at yoksa, işlem devam ediyor demektir
            # Background job çalışıyor olabilir
            # İstersen background job state'ine bakıp IN_PROGRESS yapabilirsin
            # Şimdilik REQUESTED olarak bırakıyoruz (işlem başladı ama henüz tamamlanmadı)
            state = "REQUESTED"

        else:

            state = "NONE"



        return RecallStatusResponse(

            user_id=obj.user_id,

            recall_requested_at=obj.recall_requested_at,

            recall_mode=obj.recall_mode,

            recall_completed_at=obj.recall_completed_at,

            state=state,

        )





def get_consent_service(

    session: AsyncSession = Depends(get_session),

) -> ConsentService:

    return ConsentService(session)


# --- Background Processing ---

async def process_recall_request(
    user_id: str,
    recall_mode: str,
):
    """
    Recall talebini arka planda işle.
    
    Bu fonksiyon:
    1. Feature store'dan kullanıcı verilerini siler/anonimleştirir
    2. Training log'larını işaretler (exclusion)
    3. İşlem tamamlandığında recall_completed_at set eder
    """
    from app.consent.models import UserPrivacyProfile as UserPrivacyProfileModel
    from sqlmodel import select
    from app.core.db import get_session
    import structlog
    import asyncio
    
    logger = structlog.get_logger()
    
    try:
        # Yeni bir session oluştur (background task için)
        async for session in get_session():
            try:
                # 1. Feature Store temizleme
                # TODO: Gerçek feature store entegrasyonu
                # if recall_mode == "FULL_EXCLUDE":
                #     await feature_store.delete_user_features(user_id)
                # elif recall_mode == "ANONYMIZE":
                #     await feature_store.anonymize_user_features(user_id)
                
                logger.info(
                    "recall_processing_started",
                    user_id=user_id,
                    recall_mode=recall_mode,
                )
                
                # 2. Training log exclusion
                # TODO: Gerçek training pipeline entegrasyonu
                # await training_log.mark_user_events_for_exclusion(user_id)
                
                logger.info(
                    "recall_processing_feature_store",
                    user_id=user_id,
                    recall_mode=recall_mode,
                )
                
                # Simüle edilmiş işlem süresi (gerçekte feature store işlemi zaman alabilir)
                await asyncio.sleep(2)  # Simüle edilmiş işlem
                
                # 3. Privacy profile'ı güncelle - recall_completed_at set et
                result = await session.execute(
                    select(UserPrivacyProfileModel).where(
                        UserPrivacyProfileModel.user_id == user_id
                    )
                )
                obj = result.scalar_one_or_none()
                
                if obj:
                    obj.recall_completed_at = datetime.utcnow()
                    obj.last_policy_updated_at = datetime.utcnow()
                    session.add(obj)
                    await session.commit()
                    await session.refresh(obj)
                    
                    logger.info(
                        "recall_processing_completed",
                        user_id=user_id,
                        recall_mode=recall_mode,
                        completed_at=obj.recall_completed_at.isoformat(),
                    )
                else:
                    logger.warning(
                        "recall_processing_user_not_found",
                        user_id=user_id,
                    )
                    
            except Exception as e:
                logger.error(
                    "recall_processing_failed",
                    user_id=user_id,
                    recall_mode=recall_mode,
                    error=str(e),
                )
            finally:
                break  # Session context manager'dan çık
                
    except Exception as e:
        logger.error(
            "recall_processing_session_error",
            user_id=user_id,
            recall_mode=recall_mode,
            error=str(e),
        )


router = APIRouter(prefix="/api/v1/consent", tags=["consent"])





# --- ENDPOINTS ---





@router.post(

    "/session",

    response_model=ConsentSessionCreated,

    summary="Yeni bir onay oturumu başlat",

)

async def create_consent_session(

    body: ConsentSessionCreate,

    service: ConsentService = Depends(get_consent_service),

):

    # opsiyonel: body.user_id'i auth'tan override et

    return await service.create_session(body)





@router.post(

    "/clauses",

    status_code=status.HTTP_204_NO_CONTENT,

    summary="Madde madde onay durumunu logla",

)

async def accept_clause(

    body: ClauseAcceptanceStatus,

    service: ConsentService = Depends(get_consent_service),

):

    if not await service.validate_session(body.session_id):

        raise HTTPException(

            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid session"

        )



    if body.status not in ("ACCEPTED", "REJECTED"):

        raise HTTPException(

            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid clause status"

        )



    await service.log_clause_acceptance(body)

    return





@router.post(

    "/redline",

    status_code=status.HTTP_204_NO_CONTENT,

    summary="Kırmızı Hat (Madde 2.2) onayını kaydet",

)

async def accept_redline(

    body: RedlineConsentRequest,

    service: ConsentService = Depends(get_consent_service),

):

    if not await service.validate_session(body.session_id):

        raise HTTPException(

            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid session"

        )



    await service.log_redline_consent(body)

    return





@router.post(

    "/sign",

    response_model=ConsentRecordResponse,

    summary="Sözleşmeyi imzala ve immutable kayıt yarat",

)

async def sign_consent(

    body: ConsentSignRequest,

    service: ConsentService = Depends(get_consent_service),

):

    # 1) session valid mi?

    if not await service.validate_session(body.session_id):

        raise HTTPException(

            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid session"

        )



    # 2) tüm maddeler onaylanmış mı?

    if not await service.all_clauses_accepted(body.session_id):

        raise HTTPException(

            status_code=status.HTTP_403_FORBIDDEN,

            detail="Incomplete acceptance flow",

        )



    # 3) kırmızı hat kabul edilmiş mi?

    if body.redline_status != "ACCEPTED" or not await service.redline_accepted(

        body.session_id

    ):

        raise HTTPException(

            status_code=status.HTTP_403_FORBIDDEN,

            detail="Redline clause not accepted",

        )



    # 4) legal metni çek + hash hesapla

    legal_text = await service.get_legal_text(body.contract_version)



    # Hash: legal_text + sorted payload JSON + timestamp

    payload_for_hash = body.dict()

    payload_for_hash_str = json.dumps(payload_for_hash, sort_keys=True, default=str)

    to_hash = (legal_text + "|" + payload_for_hash_str).encode("utf-8")

    contract_hash = hashlib.sha256(to_hash).hexdigest()



    # 5) immutable ledger'e yaz

    ledger_record = await service.write_immutable_record(

        payload=body, contract_hash=contract_hash

    )



    # 6) privacy profile güncelle

    await service.update_privacy_profile_from_consent(ledger_record)



    return ConsentRecordResponse(

        record_id=ledger_record.record_id,

        user_id=ledger_record.user_id,

        contract_version=ledger_record.contract_version,

        clauses_accepted=body.clauses_accepted,

        redline_accepted=True,

        signature_text=body.signature_text,

        contract_hash=contract_hash,

        signed_at=ledger_record.signed_at,

        created_at=ledger_record.created_at,

    )





@router.get(

    "/records/{record_id}",

    response_model=ConsentRecordResponse,

    summary="İmzalanmış sözleşme kaydını getir",

)

async def get_consent_record(

    record_id: str, service: ConsentService = Depends(get_consent_service)

):

    ledger_record, record = await service.get_record_full(record_id)

    return ConsentRecordResponse(

        record_id=ledger_record.record_id,

        user_id=ledger_record.user_id,

        contract_version=ledger_record.contract_version,

        clauses_accepted=record.clauses_accepted,

        redline_accepted=record.redline_accepted,

        signature_text=record.signature_text,

        contract_hash=ledger_record.ledger.contract_hash,

        signed_at=ledger_record.signed_at,

        created_at=ledger_record.created_at,

    )





@router.get(

    "/profile/me",

    response_model=UserPrivacyProfileResponse,

    summary="Giriş yapan kullanıcının privacy profilini getir",

)

async def get_my_privacy_profile(

    service: ConsentService = Depends(get_consent_service),

    current_user_id: str = Depends(get_current_user_id),

):

    return await service.get_privacy_profile(current_user_id)





@router.post(

    "/recall",

    response_model=RecallStatusResponse,

    summary="Veri geri çekme (recall) isteği oluştur",

)

async def request_recall(

    body: RecallRequest,

    background_tasks: BackgroundTasks,

    service: ConsentService = Depends(get_consent_service),

    current_user_id: str = Depends(get_current_user_id),

):

    """

    Kullanıcı verilerinin YZ eğitiminden anonimleştirilerek /

    tamamen çıkarılması için istek oluşturur.

    Aurora, bu isteği 48 saat içinde işlemekle yükümlüdür.

    """

    result = await service.request_recall(current_user_id, body)
    
    # Background task başlat - recall işlemini arka planda tamamla
    background_tasks.add_task(
        process_recall_request,
        user_id=current_user_id,
        recall_mode=body.mode,
    )
    
    return result





@router.get(

    "/recall/status",

    response_model=RecallStatusResponse,

    summary="Kullanıcının geri çekme isteğinin durumunu getir",

)

async def get_recall_status(

    service: ConsentService = Depends(get_consent_service),

    current_user_id: str = Depends(get_current_user_id),

):

    return await service.get_recall_status(current_user_id)


# ============ Admin Recall Management ============
@router.post(
    "/recall/{user_id}/cancel",
    response_model=RecallStatusResponse,
    summary="Recall talebini iptal et (admin only)",
)
async def cancel_recall(
    user_id: str,
    service: ConsentService = Depends(get_consent_service),
    _admin = Depends(get_admin_user),
):
    """Admin: Recall talebini iptal et (kullanıcı vazgeçti veya hata var)."""
    from app.consent.models import UserPrivacyProfile as UserPrivacyProfileModel
    from sqlmodel import select
    from datetime import datetime
    
    result = await service.session.execute(
        select(UserPrivacyProfileModel).where(
            UserPrivacyProfileModel.user_id == user_id
        )
    )
    obj = result.scalar_one_or_none()
    
    if not obj or not obj.recall_requested_at:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recall request not found for this user",
        )
    
    if obj.recall_completed_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel completed recall request",
        )
    
    # İptal et: recall alanlarını temizle
    obj.recall_mode = None
    obj.recall_requested_at = None
    obj.recall_completed_at = None
    obj.last_policy_updated_at = datetime.utcnow()
    
    await service.session.commit()
    await service.session.refresh(obj)
    
    return RecallStatusResponse(
        user_id=obj.user_id,
        recall_requested_at=None,
        recall_mode=None,
        recall_completed_at=None,
        state="NONE",
    )


@router.post(
    "/recall/{user_id}/complete",
    response_model=RecallStatusResponse,
    summary="Recall talebini manuel olarak tamamla (admin only)",
)
async def complete_recall_manual(
    user_id: str,
    service: ConsentService = Depends(get_consent_service),
    _admin = Depends(get_admin_user),
):
    """
    Admin: Recall talebini manuel olarak tamamla.
    
    Bu endpoint çağrıldığında:
    1. Feature store'dan veriler silinmiş/anonimleştirilmiş olmalı (manuel işlem)
    2. Training log'ları işaretlenmiş olmalı (manuel işlem)
    3. recall_completed_at set edilir
    """
    from app.consent.models import UserPrivacyProfile as UserPrivacyProfileModel
    from sqlmodel import select
    from datetime import datetime
    import structlog
    
    logger = structlog.get_logger()
    
    result = await service.session.execute(
        select(UserPrivacyProfileModel).where(
            UserPrivacyProfileModel.user_id == user_id
        )
    )
    obj = result.scalar_one_or_none()
    
    if not obj or not obj.recall_requested_at:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recall request not found for this user",
        )
    
    if obj.recall_completed_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recall request already completed",
        )
    
    # Manuel tamamlama: recall_completed_at set et
    obj.recall_completed_at = datetime.utcnow()
    obj.last_policy_updated_at = datetime.utcnow()
    
    await service.session.commit()
    await service.session.refresh(obj)
    
    logger.info(
        "recall_manually_completed",
        user_id=user_id,
        recall_mode=obj.recall_mode,
        completed_at=obj.recall_completed_at.isoformat(),
        admin_id=str(_admin.id),
    )
    
    return RecallStatusResponse(
        user_id=obj.user_id,
        recall_requested_at=obj.recall_requested_at,
        recall_mode=obj.recall_mode,
        recall_completed_at=obj.recall_completed_at,
        state="COMPLETED",
    )
