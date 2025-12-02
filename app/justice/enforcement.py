# app/justice/enforcement.py

"""
Enforcement helper functions for checking if actions are allowed.

Usage in other modules:

```python
from app.justice.router import get_justice_service
from app.justice.policy import Action, is_action_allowed

@router.post("/messages")
async def send_message(
    body: MessageCreate,
    current_user_id: str = Depends(get_current_user_id),
    justice_service: JusticeService = Depends(get_justice_service),
):
    cp_state = await justice_service.get_cp(current_user_id)
    
    if not is_action_allowed(cp_state.regime, Action.SEND_MESSAGE):
        raise HTTPException(
            status_code=403,
            detail=f"Aurora Adalet rejimin: {cp_state.regime}. Şu an mesaj gönderemezsin.",
        )
    
    # normal flow devam
```
"""

from fastapi import HTTPException, status

from .policy import Action, is_action_allowed, Regime

from .schemas import CpStateResponse


def check_action_allowed(
    cp_state: CpStateResponse,
    action: str,
    custom_message: str | None = None,
) -> None:
    """
    Check if an action is allowed for a user's CP regime.
    
    Raises HTTPException(403) if not allowed.
    
    Args:
        cp_state: User's CP state from JusticeService.get_cp()
        action: Action to check (from Action enum)
        custom_message: Optional custom error message
    """
    if not is_action_allowed(cp_state.regime, action):
        if custom_message:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=custom_message,
            )
        
        regime_names = {
            "NORMAL": "Normal",
            "SOFT_FLAG": "Yumuşak Uyarı",
            "PROBATION": "Gözaltı",
            "RESTRICTED": "Kısıtlı",
            "LOCKDOWN": "Kilitli",
        }
        
        regime_display = regime_names.get(cp_state.regime, cp_state.regime)
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "AURORA_ENFORCEMENT_BLOCKED",
                "message": (
                    f"Aurora Adalet rejimin: {regime_display} (CP: {cp_state.cp_value}). "
                    f"Bu işlemi şu an gerçekleştiremezsin."
                ),
                "regime": cp_state.regime,
                "cp_value": cp_state.cp_value,
                "action": action,
            },
        )

