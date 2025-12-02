"""
FlirtMarket Routes - Example endpoints with Aurora enforcement
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.security import get_current_user
from app.identity.models import User
from app.justice.router import get_justice_service, JusticeService
from app.justice.enforcement import check_action_allowed
from app.justice.policy import Action

router = APIRouter(prefix="/flirtmarket", tags=["flirtmarket"])


# ============ Schemas ============
class SendMessageRequest(BaseModel):
    recipient_id: str
    message: str


class SendMessageResponse(BaseModel):
    message_id: str
    sent_at: str


class StartCallRequest(BaseModel):
    recipient_id: str


class StartCallResponse(BaseModel):
    call_id: str
    started_at: str


class CreateFlirtRequest(BaseModel):
    performer_id: str
    message: str | None = None


class CreateFlirtResponse(BaseModel):
    flirt_id: str
    created_at: str


# ============ Endpoints ============
@router.post(
    "/messages",
    response_model=SendMessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Send message",
    description="Send a message to another user (Aurora enforcement enabled).",
)
async def send_message(
    request: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    justice_service: JusticeService = Depends(get_justice_service),
) -> SendMessageResponse:
    """
    Send a message with Aurora enforcement check.
    
    Blocks if user is in LOCKDOWN or RESTRICTED regime.
    """
    # Aurora Justice Enforcement Check
    cp_state = await justice_service.get_cp(str(current_user.id))
    check_action_allowed(
        cp_state,
        Action.SEND_MESSAGE,
        custom_message=f"Aurora rejimin: {cp_state.regime}. Mesaj gönderemezsin.",
    )
    
    # Normal flow continues...
    # TODO: Implement actual message sending logic
    import uuid
    from datetime import datetime
    
    message_id = str(uuid.uuid4())
    
    return SendMessageResponse(
        message_id=message_id,
        sent_at=datetime.utcnow().isoformat(),
    )


@router.post(
    "/calls/start",
    response_model=StartCallResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start call",
    description="Start a call with another user (Aurora enforcement enabled).",
)
async def start_call(
    request: StartCallRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    justice_service: JusticeService = Depends(get_justice_service),
) -> StartCallResponse:
    """
    Start a call with Aurora enforcement check.
    
    Blocks if user is in LOCKDOWN, RESTRICTED, or PROBATION regime.
    """
    # Aurora Justice Enforcement Check
    cp_state = await justice_service.get_cp(str(current_user.id))
    check_action_allowed(
        cp_state,
        Action.START_CALL,
        custom_message=f"Aurora rejimin: {cp_state.regime}. Call başlatamazsın.",
    )
    
    # Normal flow continues...
    # TODO: Implement actual call starting logic
    import uuid
    from datetime import datetime
    
    call_id = str(uuid.uuid4())
    
    return StartCallResponse(
        call_id=call_id,
        started_at=datetime.utcnow().isoformat(),
    )


@router.post(
    "/flirts",
    response_model=CreateFlirtResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create flirt",
    description="Create a flirt request (Aurora enforcement enabled).",
)
async def create_flirt(
    request: CreateFlirtRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    justice_service: JusticeService = Depends(get_justice_service),
) -> CreateFlirtResponse:
    """
    Create a flirt with Aurora enforcement check.
    
    Blocks if user is in LOCKDOWN regime.
    """
    # Aurora Justice Enforcement Check
    cp_state = await justice_service.get_cp(str(current_user.id))
    check_action_allowed(
        cp_state,
        Action.CREATE_FLIRT,
        custom_message=f"Aurora rejimin: {cp_state.regime}. Flirt oluşturamazsın.",
    )
    
    # Normal flow continues...
    # TODO: Implement actual flirt creation logic
    import uuid
    from datetime import datetime
    
    flirt_id = str(uuid.uuid4())
    
    return CreateFlirtResponse(
        flirt_id=flirt_id,
        created_at=datetime.utcnow().isoformat(),
    )

