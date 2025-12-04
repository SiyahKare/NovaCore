# app/core/citizenship.py
"""
Citizenship Level Definitions - Single Source of Truth

DRY: Tüm modüller buradan beslenir.
"""
from enum import Enum
from typing import TypedDict


class CitizenLevel(str, Enum):
    """Vatandaşlık seviyesi - tek kaynak."""
    GHOST = "ghost"           # 0-39: İzleyici, limitli
    RESIDENT = "resident"     # 40-59: Normal citizen
    CORE = "core_citizen"     # 60-79: Premium quest, daha iyi NCR çarpanı
    SOVEREIGN = "sovereign"   # 80-89: DAO görevleri, validator
    PRIME = "prime"           # 90-100: İç çekirdek, governance


class CitizenLevelInfo(TypedDict):
    """Vatandaşlık seviyesi bilgileri."""
    name: str
    description: str
    task_multiplier: float
    withdraw_limit_daily: float
    can_validate: bool
    can_refer: bool


# Single Source of Truth - Tüm modüller buradan beslenir
CITIZEN_LEVEL_INFO: dict[CitizenLevel, CitizenLevelInfo] = {
    CitizenLevel.GHOST: {
        "name": "Ghost",
        "description": "İzleyici, sistemle yüzeysel temas. Görev ve withdraw limitli.",
        "task_multiplier": 0.5,
        "withdraw_limit_daily": 50.0,
        "can_validate": False,
        "can_refer": False,
    },
    CitizenLevel.RESIDENT: {
        "name": "Resident",
        "description": "Normal citizen. Sıradan görev, sınırlı referral.",
        "task_multiplier": 1.0,
        "withdraw_limit_daily": 200.0,
        "can_validate": False,
        "can_refer": True,
    },
    CitizenLevel.CORE: {
        "name": "Core Citizen",
        "description": "Yüksek tavan, premium quest, daha iyi NCR çarpanı.",
        "task_multiplier": 1.2,
        "withdraw_limit_daily": 500.0,
        "can_validate": False,
        "can_refer": True,
    },
    CitizenLevel.SOVEREIGN: {
        "name": "Sovereign",
        "description": "DAO görevleri, validator, yüksek güven limiti.",
        "task_multiplier": 1.4,
        "withdraw_limit_daily": 1000.0,
        "can_validate": True,
        "can_refer": True,
    },
    CitizenLevel.PRIME: {
        "name": "Prime",
        "description": "İç çekirdek. Beta feature'lar, yüksek stake, governance ağırlığı.",
        "task_multiplier": 1.5,
        "withdraw_limit_daily": 2000.0,
        "can_validate": True,
        "can_refer": True,
    },
}


def get_citizen_level_multiplier(level: CitizenLevel | str) -> float:
    """Vatandaşlık seviyesine göre task multiplier."""
    if isinstance(level, str):
        try:
            level = CitizenLevel(level)
        except ValueError:
            return 1.0
    
    return CITIZEN_LEVEL_INFO[level]["task_multiplier"]


def nova_score_to_level(nova_score: float) -> CitizenLevel:
    """NovaScore'dan vatandaşlık seviyesi belirle."""
    if nova_score >= 90:
        return CitizenLevel.PRIME
    if nova_score >= 80:
        return CitizenLevel.SOVEREIGN
    if nova_score >= 60:
        return CitizenLevel.CORE
    if nova_score >= 40:
        return CitizenLevel.RESIDENT
    return CitizenLevel.GHOST

