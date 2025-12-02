# app/justice/models.py

from datetime import datetime

from typing import Optional

from sqlmodel import SQLModel, Field, Column, JSON

from sqlalchemy.dialects.postgresql import UUID

import uuid





class ViolationLog(SQLModel, table=True):

    __tablename__ = "justice_violations"



    id: uuid.UUID = Field(

        default_factory=uuid.uuid4,

        sa_column=Column(UUID(as_uuid=True), primary_key=True, index=True),

    )



    user_id: str = Field(index=True)



    category: str = Field(

        index=True

    )  # "EKO" | "COM" | "SYS" | "TRUST"

    code: str = Field(index=True, max_length=64)  # "EKO_NO_SHOW", "COM_TOXIC", vs.

    severity: int = Field(default=1)  # 1–5



    cp_delta: int = Field(

        default=0, description="Bu violation'ın CP'ye katkısı (pozitif)"

    )



    source: Optional[str] = Field(

        default=None,

        description="Olayı raporlayan modül: 'nova-core', 'moderation-bot', vb.",

    )

    context: Optional[dict] = Field(

        default=None,

        sa_column=Column(JSON),

    )



    created_at: datetime = Field(default_factory=datetime.utcnow)





class UserCpState(SQLModel, table=True):

    __tablename__ = "justice_cp_state"



    user_id: str = Field(primary_key=True)

    cp_value: int = Field(default=0, index=True)

    regime: str = Field(default="NORMAL", index=True)  # NORMAL | SOFT_FLAG | PROBATION | RESTRICTED | LOCKDOWN

    last_updated_at: datetime = Field(default_factory=datetime.utcnow)

