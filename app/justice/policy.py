# app/justice/policy.py

from typing import Literal



Regime = Literal["NORMAL", "SOFT_FLAG", "PROBATION", "RESTRICTED", "LOCKDOWN"]



class Action(str):

    """Action types that can be restricted by regime."""

    SEND_MESSAGE = "SEND_MESSAGE"

    START_CALL = "START_CALL"

    CREATE_FLIRT = "CREATE_FLIRT"

    WITHDRAW_FUNDS = "WITHDRAW_FUNDS"

    TOPUP_WALLET = "TOPUP_WALLET"

    ACCESS_AURORA = "ACCESS_AURORA"



# Policy matrix: regime -> action -> allowed (bool)

POLICY_MATRIX = {

    "NORMAL": {

        Action.SEND_MESSAGE: True,

        Action.START_CALL: True,

        Action.CREATE_FLIRT: True,

        Action.WITHDRAW_FUNDS: True,

        Action.TOPUP_WALLET: True,

        Action.ACCESS_AURORA: True,

    },

    "SOFT_FLAG": {

        Action.SEND_MESSAGE: True,

        Action.START_CALL: True,

        Action.CREATE_FLIRT: True,

        Action.WITHDRAW_FUNDS: True,

        Action.TOPUP_WALLET: True,

        Action.ACCESS_AURORA: True,

    },

    "PROBATION": {

        Action.SEND_MESSAGE: True,

        Action.START_CALL: True,

        Action.CREATE_FLIRT: True,

        Action.WITHDRAW_FUNDS: True,

        Action.TOPUP_WALLET: True,

        Action.ACCESS_AURORA: True,

    },

    "RESTRICTED": {

        Action.SEND_MESSAGE: True,

        Action.START_CALL: False,  # örnek: call yok

        Action.CREATE_FLIRT: True,

        Action.WITHDRAW_FUNDS: True,

        Action.TOPUP_WALLET: True,

        Action.ACCESS_AURORA: True,

    },

    "LOCKDOWN": {

        Action.SEND_MESSAGE: False,

        Action.START_CALL: False,

        Action.CREATE_FLIRT: False,

        Action.WITHDRAW_FUNDS: False,

        Action.TOPUP_WALLET: False,

        Action.ACCESS_AURORA: False,

    },

}



def regime_for_cp(
    cp: int,
    policy: "JusticePolicyParams | None" = None,
) -> str:
    """
    Calculate regime based on CP value.
    
    Uses policy thresholds if provided, otherwise defaults to v1.0 thresholds.
    """
    if policy:
        if cp >= policy.threshold_lockdown:
            return "LOCKDOWN"
        if cp >= policy.threshold_restricted:
            return "RESTRICTED"
        if cp >= policy.threshold_probation:
            return "PROBATION"
        if cp >= policy.threshold_soft_flag:
            return "SOFT_FLAG"
        return "NORMAL"
    
    # Fallback to default thresholds (v1.0)
    if cp >= 80:
        return "LOCKDOWN"
    if cp >= 60:
        return "RESTRICTED"
    if cp >= 40:
        return "PROBATION"
    if cp >= 20:
        return "SOFT_FLAG"
    return "NORMAL"



def is_action_allowed(regime: Regime, action: str) -> bool:

    """Check if an action is allowed for a given regime."""

    return POLICY_MATRIX.get(regime, {}).get(action, False)

