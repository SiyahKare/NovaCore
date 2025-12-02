"""
Aurora Justice Enforcement - Integration Examples

This file shows how to integrate Aurora Justice enforcement checks
into your endpoints.
"""

# ============================================================================
# Example 1: Wallet Transfer with Enforcement
# ============================================================================

"""
from app.justice.router import get_justice_service, JusticeService
from app.justice.enforcement import check_action_allowed
from app.justice.policy import Action

@router.post("/transfer")
async def transfer(
    request: TransferRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    # Check if user can withdraw/transfer funds
    justice_service = JusticeService(session)
    cp_state = await justice_service.get_cp(str(current_user.id))
    check_action_allowed(cp_state, Action.WITHDRAW_FUNDS)
    
    # Normal flow continues...
    service = WalletService(session)
    return await service.transfer(current_user.id, request)
"""

# ============================================================================
# Example 2: FlirtMarket - Create Flirt with Enforcement
# ============================================================================

"""
from app.justice.router import get_justice_service, JusticeService
from app.justice.enforcement import check_action_allowed
from app.justice.policy import Action

@router.post("/flirts")
async def create_flirt(
    body: FlirtCreate,
    current_user_id: str = Depends(get_current_user_id),
    justice_service: JusticeService = Depends(get_justice_service),
):
    # Check if user can create flirts
    cp_state = await justice_service.get_cp(current_user_id)
    check_action_allowed(cp_state, Action.CREATE_FLIRT)
    
    # Normal flow continues...
    ...
"""

# ============================================================================
# Example 3: Message Sending with Enforcement
# ============================================================================

"""
from app.justice.router import get_justice_service, JusticeService
from app.justice.enforcement import check_action_allowed
from app.justice.policy import Action

@router.post("/messages")
async def send_message(
    body: MessageCreate,
    current_user_id: str = Depends(get_current_user_id),
    justice_service: JusticeService = Depends(get_justice_service),
):
    # Check if user can send messages
    cp_state = await justice_service.get_cp(current_user_id)
    check_action_allowed(cp_state, Action.SEND_MESSAGE)
    
    # Normal flow continues...
    ...
"""

# ============================================================================
# Example 4: Call Start with Enforcement
# ============================================================================

"""
from app.justice.router import get_justice_service, JusticeService
from app.justice.enforcement import check_action_allowed
from app.justice.policy import Action

@router.post("/calls/start")
async def start_call(
    body: CallStartRequest,
    current_user_id: str = Depends(get_current_user_id),
    justice_service: JusticeService = Depends(get_justice_service),
):
    # Check if user can start calls
    cp_state = await justice_service.get_cp(current_user_id)
    check_action_allowed(cp_state, Action.START_CALL)
    
    # Normal flow continues...
    ...
"""

# ============================================================================
# Example 5: Custom Error Message
# ============================================================================

"""
from app.justice.enforcement import check_action_allowed
from app.justice.policy import Action
from fastapi import HTTPException

cp_state = await justice_service.get_cp(user_id)

# Custom message
try:
    check_action_allowed(
        cp_state,
        Action.SEND_MESSAGE,
        custom_message=f"Mesaj gönderemezsin. Rejimin: {cp_state.regime}, CP: {cp_state.cp_value}"
    )
except HTTPException as e:
    # Handle the error
    raise e
"""

# ============================================================================
# Example 6: Conditional Enforcement (Soft Check)
# ============================================================================

"""
from app.justice.policy import is_action_allowed, Action

cp_state = await justice_service.get_cp(user_id)

# Soft check - don't raise exception, just return early
if not is_action_allowed(cp_state.regime, Action.SEND_MESSAGE):
    return {
        "allowed": False,
        "reason": f"Rejimin: {cp_state.regime}",
        "cp": cp_state.cp_value
    }

# Normal flow...
"""

