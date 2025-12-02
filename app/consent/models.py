# app/consent/models.py

from datetime import datetime

from typing import Optional, List

from sqlmodel import SQLModel, Field, Column, JSON

from sqlalchemy.dialects.postgresql import UUID

import uuid





class ConsentSession(SQLModel, table=True):

    __tablename__ = "consent_sessions"



    id: uuid.UUID = Field(

        default_factory=uuid.uuid4,

        sa_column=Column(UUID(as_uuid=True), primary_key=True, index=True),

    )

    user_id: str = Field(index=True)

    client_fingerprint: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)

    is_active: bool = Field(default=True)





class ConsentClauseLog(SQLModel, table=True):

    __tablename__ = "consent_clause_logs"



    id: uuid.UUID = Field(

        default_factory=uuid.uuid4,

        sa_column=Column(UUID(as_uuid=True), primary_key=True, index=True),

    )

    session_id: uuid.UUID = Field(index=True)

    user_id: str = Field(index=True)

    clause_id: str = Field(index=True)  # "1.1", "2.2" vs

    status: str = Field(index=True)     # "ACCEPTED" | "REJECTED"

    comprehension_passed: Optional[bool] = None

    answered_at: datetime = Field(default_factory=datetime.utcnow)





class RedlineConsent(SQLModel, table=True):

    __tablename__ = "consent_redline"



    id: uuid.UUID = Field(

        default_factory=uuid.uuid4,

        sa_column=Column(UUID(as_uuid=True), primary_key=True, index=True),

    )

    session_id: uuid.UUID = Field(index=True)

    user_id: str = Field(index=True)

    redline_status: str = Field(index=True)  # "ACCEPTED" | "REJECTED"

    user_note_hash: Optional[str] = None

    answered_at: datetime = Field(default_factory=datetime.utcnow)





class ConsentRecord(SQLModel, table=True):

    __tablename__ = "consent_records"



    id: uuid.UUID = Field(

        default_factory=uuid.uuid4,

        sa_column=Column(UUID(as_uuid=True), primary_key=True, index=True),

    )

    user_id: str = Field(index=True)

    contract_version: str = Field(index=True)

    clauses_accepted: List[str] = Field(

        sa_column=Column(JSON), default_factory=list

    )

    redline_accepted: bool = Field(default=True)

    signature_text: str

    contract_hash: str = Field(index=True)

    signed_at: datetime = Field(default_factory=datetime.utcnow)

    created_at: datetime = Field(default_factory=datetime.utcnow)

    client_fingerprint: Optional[str] = None





class UserPrivacyProfile(SQLModel, table=True):

    __tablename__ = "user_privacy_profiles"



    user_id: str = Field(primary_key=True)

    latest_consent_id: Optional[uuid.UUID] = Field(

        default=None, foreign_key="consent_records.id"

    )

    contract_version: Optional[str] = Field(default=None)

    data_usage_policy: dict = Field(

        sa_column=Column(JSON), default_factory=dict

    )

    consent_level: Optional[str] = Field(default=None)  # FULL / LIMITED / MINIMUM

    # Recall (Geri Çekme) alanları
    recall_mode: Optional[str] = Field(
        default=None
    )  # "ANONYMIZE" / "FULL_EXCLUDE"
    recall_requested_at: Optional[datetime] = None
    recall_completed_at: Optional[datetime] = None

    last_policy_updated_at: datetime = Field(default_factory=datetime.utcnow)

