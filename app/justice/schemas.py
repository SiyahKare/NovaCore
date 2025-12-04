# app/justice/schemas.py

from datetime import datetime

from typing import Optional, Literal

from pydantic import BaseModel, Field


class PolicyParamsResponse(BaseModel):
    """Current active policy parameters."""
    version: str
    decay_per_day: int
    base_eko: int
    base_com: int
    base_sys: int
    base_trust: int
    threshold_soft_flag: int
    threshold_probation: int
    threshold_restricted: int
    threshold_lockdown: int
    onchain_address: Optional[str] = None
    onchain_block: Optional[int] = None
    synced_at: datetime
    notes: Optional[str] = None





ViolationCategory = Literal["EKO", "COM", "SYS", "TRUST"]





class ViolationCreate(BaseModel):

    user_id: str = Field(..., description="Ceza yazılacak user id")

    category: ViolationCategory

    code: str = Field(..., description="İç kod: EKO_NO_SHOW, COM_TOXIC, vs.")

    severity: int = Field(..., ge=1, le=5)

    source: Optional[str] = Field(

        None, description="Olay kaynağı (örn: 'flirtmarket', 'moderation-bot')"

    )

    context: Optional[dict] = Field(

        None, description="Serbest context metadata (optional)"

    )





class ViolationResponse(BaseModel):

    id: str

    user_id: str

    category: ViolationCategory

    code: str

    severity: int

    cp_delta: int

    source: Optional[str]

    created_at: datetime





class CpStateResponse(BaseModel):

    user_id: str

    cp_value: int = Field(..., ge=0)

    regime: Literal["NORMAL", "SOFT_FLAG", "PROBATION", "RESTRICTED", "LOCKDOWN"]

    last_updated_at: datetime





class NovaScorePayload(BaseModel):
    """NovaScore payload for case file."""
    value: int
    components: dict  # Will be NovaScoreComponents, but using dict to avoid circular import
    confidence_overall: float
    explanation: Optional[str] = None


class CaseFileResponse(BaseModel):
    """Aurora Case File - Complete user status for Ombudsman/Admin."""
    user_id: str
    privacy_profile: Optional[dict] = None  # UserPrivacyProfileResponse, but dict to avoid circular import
    cp_state: CpStateResponse
    nova_score: Optional[NovaScorePayload] = None
    recent_violations: list[ViolationResponse]


# ============ Admin Violation Stream ============
from typing import Any, Dict, List


class AdminViolationItem(BaseModel):
    """Admin view of a violation for the violation stream."""
    id: str
    user_id: str
    category: str  # "EKO" | "COM" | "SYS" | "TRUST"
    code: str  # "COM_TOXIC", "SYS_EXPLOIT", ...
    severity: int  # 1-5
    cp_delta: float
    regime_after: Optional[str] = None
    source: Optional[str] = None
    message_preview: Optional[str] = None
    meta: Dict[str, Any] = {}
    created_at: datetime


class AdminViolationListResponse(BaseModel):
    """Paginated response for admin violation stream."""
    items: List[AdminViolationItem]
    total: int
    limit: int
    offset: int


# ============ Appeal System ============
class AppealCreate(BaseModel):
    """Appeal request for rejected task submission."""
    submission_id: int = Field(..., description="Task submission ID to appeal")
    reason: str = Field(..., min_length=10, max_length=500, description="Appeal reason (min 10 chars)")


class AppealResponse(BaseModel):
    """Appeal response."""
    id: int
    submission_id: int
    user_id: str
    reason: str
    status: str = "pending"  # "pending", "approved", "rejected"
    appeal_fee_paid: bool = False
    created_at: datetime
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[int] = None
    review_notes: Optional[str] = None
