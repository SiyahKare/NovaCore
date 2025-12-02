# NovaCore - NovaCredit Module
# Davranış Skoru & Vatandaşlık Ekonomisi

"""
NovaCredit = Devletin Kalbi

wallet   → saf para (NCR, ledger, bakiyeler)
nova_credit → davranış kredisi (0-1000, risk, reputation)
xp_loyalty  → gamified XP, streak, badge (Battle pass gibi)

XP = oyunlaştırma
NovaCredit = devlet skoru
"""

from app.nova_credit.models import CitizenScore, ScoreChange, CreditTier
from app.nova_credit.rules import EventCategory, CATEGORY_WEIGHTS
from app.nova_credit.routes import router

__all__ = [
    "CitizenScore",
    "ScoreChange",
    "CreditTier",
    "EventCategory",
    "CATEGORY_WEIGHTS",
    "router",
]

