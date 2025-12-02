# novacore/app/consent/schemas.py

from datetime import datetime

from typing import List, Optional, Literal, Dict, Any

from pydantic import BaseModel, Field





ClauseId = str  # örn: "1.1", "2.2"





class ConsentSessionCreate(BaseModel):

    user_id: str = Field(..., description="Aurora kullanıcı ID")

    client_fingerprint: Optional[str] = Field(

        None, description="Tarayıcı / cihaz fingerprint"

    )





class ConsentSessionCreated(BaseModel):

    session_id: str

    user_id: str

    created_at: datetime





class ClauseAcceptanceStatus(BaseModel):

    session_id: str

    clause_id: ClauseId

    status: Literal["ACCEPTED", "REJECTED"]

    comprehension_passed: Optional[bool] = Field(

        None, description="Opsiyonel kavrama testi sonucu"

    )

    answered_at: datetime = Field(default_factory=datetime.utcnow)





class RedlineConsentRequest(BaseModel):

    session_id: str

    redline_status: Literal["ACCEPTED", "REJECTED"]

    user_note_hash: Optional[str] = Field(

        None,

        description="Kullanıcının serbest metin açıklamasının hash'i (opsiyonel)",

    )

    answered_at: datetime = Field(default_factory=datetime.utcnow)





class ConsentSignRequest(BaseModel):

    session_id: str

    user_id: str

    contract_version: str = Field(..., example="Aurora-DataEthics-v1.0")

    clauses_accepted: List[ClauseId]

    redline_status: Literal["ACCEPTED", "REJECTED"]

    signature_text: str = Field(..., description="Kullanıcı e-imzası (ad/rumuz)")

    client_fingerprint: Optional[str] = None

    signed_at: datetime = Field(default_factory=datetime.utcnow)





class ConsentRecordResponse(BaseModel):

    record_id: str

    user_id: str

    contract_version: str

    clauses_accepted: List[ClauseId]

    redline_accepted: bool

    signature_text: str

    contract_hash: str

    signed_at: datetime

    created_at: datetime





class DataUsagePolicy(BaseModel):

    allowed: bool

    purposes: List[str] = Field(

        default_factory=list,

        description="['nova_score', 'learning_optimization', 'resource_efficiency']",

    )

    requires_human_ethics_board: bool = False





class PrivacyPolicySnapshot(BaseModel):

    behavioral: DataUsagePolicy

    performance: DataUsagePolicy

    economy: DataUsagePolicy

    redline: DataUsagePolicy





class UserPrivacyProfileResponse(BaseModel):

    user_id: str

    latest_consent_id: Optional[str]

    contract_version: Optional[str]

    policy: Optional[PrivacyPolicySnapshot]

    consent_level: Optional[Literal["FULL", "LIMITED", "MINIMUM"]]

    recall_requested_at: Optional[datetime]

    last_policy_updated_at: Optional[datetime]





class ImmutableLedgerMetadata(BaseModel):

    contract_hash: str

    ledger_slot: Optional[str] = Field(

        None, description="Chain / log id, opsiyonel (ileride)"

    )

    raw_metadata: Dict[str, Any]





class ImmutableLedgerRecord(BaseModel):

    record_id: str

    user_id: str

    contract_version: str

    signed_at: datetime

    created_at: datetime

    immutable: bool = True

    ledger: ImmutableLedgerMetadata





class RecallRequest(BaseModel):

    mode: Literal["ANONYMIZE", "FULL_EXCLUDE"] = Field(

        ..., description="Verinin eğitimden çıkarılma modu"

    )

    reason: Optional[str] = Field(

        None, description="Kullanıcının isteğe bağlı açıklaması"

    )





class RecallStatusResponse(BaseModel):

    user_id: str

    recall_requested_at: Optional[datetime]

    recall_mode: Optional[str] = Field(

        None, description="ANONYMIZE / FULL_EXCLUDE / None"

    )

    recall_completed_at: Optional[datetime] = None

    state: Literal["NONE", "REQUESTED", "IN_PROGRESS", "COMPLETED"]

