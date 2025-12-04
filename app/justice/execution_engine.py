# app/justice/execution_engine.py
# Justice Execution Engine - CP Regime Enforcement

"""
Justice Execution Engine: CP Regime → Yaptırım

Bu motor, CP Regime'in (CLEAN → LOCKDOWN) sisteme fiziksel olarak bağlandığı
arka plan motorudur. Her CP değişikliğinde tetiklenir ve Enforcement Matrix'e
göre kullanıcı haklarını kısıtlar.

Enforcement Matrix:
- RESTRICTED: Wallet Transfer kısıtlanır
- LOCKDOWN: DM block, airdrop/claim hakları dondurulur
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from .models import UserCpState
from .policy import Action, is_action_allowed, Regime
from .schemas import CpStateResponse
from app.core.logging import get_logger

logger = get_logger("justice_execution")


class JusticeExecutionEngine:
    """
    Justice Execution Engine - CP Regime Enforcement
    
    CP değişikliklerini izler ve Enforcement Matrix'e göre yaptırım uygular.
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def check_action_allowed(
        self,
        user_id: str,
        action: Action,
        cp_state: Optional[CpStateResponse] = None,
    ) -> bool:
        """
        Kullanıcının bir aksiyonu gerçekleştirip gerçekleştiremeyeceğini kontrol et.
        
        Args:
            user_id: User ID
            action: Action to check (from Action enum)
            cp_state: Optional CP state (if not provided, fetched from DB)
        
        Returns:
            True if action is allowed, False otherwise
        """
        if cp_state is None:
            # Fetch CP state
            stmt = select(UserCpState).where(UserCpState.user_id == user_id)
            result = await self.session.execute(stmt)
            cp_state_obj = result.scalar_one_or_none()
            
            if not cp_state_obj:
                # No CP state = CLEAN regime
                regime = "NORMAL"
            else:
                regime = cp_state_obj.regime
        else:
            regime = cp_state.regime
        
        allowed = is_action_allowed(regime, action.value)
        
        if not allowed:
            logger.info(
                "action_blocked",
                user_id=user_id,
                action=action.value,
                regime=regime,
            )
        
        return allowed
    
    async def enforce_regime_restrictions(
        self,
        user_id: str,
        cp_state: CpStateResponse,
    ) -> dict:
        """
        Kullanıcının mevcut regime'ine göre kısıtlamaları uygula.
        
        Returns:
            Dict with blocked actions and restrictions
        """
        restrictions = {
            "regime": cp_state.regime,
            "cp_value": cp_state.cp_value,
            "blocked_actions": [],
            "restrictions": {},
        }
        
        # Check each action
        for action in Action:
            allowed = await self.check_action_allowed(user_id, action, cp_state)
            if not allowed:
                restrictions["blocked_actions"].append(action.value)
        
        # Regime-specific restrictions
        if cp_state.regime == "RESTRICTED":
            restrictions["restrictions"]["wallet_transfer"] = True
            restrictions["restrictions"]["withdraw_funds"] = True
        
        if cp_state.regime == "LOCKDOWN":
            restrictions["restrictions"]["wallet_transfer"] = True
            restrictions["restrictions"]["withdraw_funds"] = True
            restrictions["restrictions"]["send_message"] = True
            restrictions["restrictions"]["dm_access"] = True
            restrictions["restrictions"]["airdrop_claim"] = True
        
        return restrictions
    
    async def on_cp_changed(
        self,
        user_id: str,
        old_cp: int,
        new_cp: int,
        old_regime: str,
        new_regime: str,
    ) -> None:
        """
        CP değişikliğinde tetiklenir ve yaptırımları uygular.
        
        Bu fonksiyon, JusticeService.add_violation veya CP güncellemelerinde
        otomatik olarak çağrılmalıdır.
        """
        if old_regime != new_regime:
            logger.info(
                "regime_changed",
                user_id=user_id,
                old_regime=old_regime,
                new_regime=new_regime,
                old_cp=old_cp,
                new_cp=new_cp,
            )
            
            # Regime değişikliğinde özel işlemler
            if new_regime == "LOCKDOWN":
                # LOCKDOWN: Account locked, manual review required
                logger.warning(
                    "user_lockdown",
                    user_id=user_id,
                    cp_value=new_cp,
                )
                # TODO: Trigger manual review notification
                # TODO: Block all actions
                
            elif new_regime == "RESTRICTED":
                # RESTRICTED: Heavy limits
                logger.info(
                    "user_restricted",
                    user_id=user_id,
                    cp_value=new_cp,
                )
                # TODO: Apply wallet transfer restrictions
                # TODO: Notify user about restrictions


# Helper function for easy import
async def check_action_allowed_for_user(
    session: AsyncSession,
    user_id: str,
    action: Action,
) -> bool:
    """
    Helper function to check if user can perform an action.
    
    Usage:
    ```python
    from app.justice.execution_engine import check_action_allowed_for_user
    from app.justice.policy import Action
    
    if not await check_action_allowed_for_user(session, user_id, Action.WITHDRAW_FUNDS):
        raise HTTPException(403, "Action not allowed")
    ```
    """
    engine = JusticeExecutionEngine(session)
    return await engine.check_action_allowed(user_id, action)

