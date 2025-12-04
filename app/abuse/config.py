"""
AbuseGuard Configuration
RiskScore hesaplama kuralları ve ağırlıklar
"""
from .models import AbuseEventType


# Abuse event ağırlıkları (RiskScore'a eklenen değerler)
ABUSE_EVENT_WEIGHTS = {
    AbuseEventType.LOW_QUALITY_BURST: 1.0,
    AbuseEventType.DUPLICATE_PROOF: 1.0,
    AbuseEventType.TOO_FAST_COMPLETION: 2.0,
    AbuseEventType.AUTO_REJECT: 0.5,
    AbuseEventType.APPEAL_REJECTED: 2.0,
    AbuseEventType.MANUAL_FLAG: 3.0,
    AbuseEventType.TOXIC_CONTENT: 2.0,  # NSFW/toxic içerik → RiskScore +2
}

# RiskScore sınırları
MAX_RISK_SCORE = 10.0
MIN_RISK_SCORE = 0.0

# RiskScore threshold'ları
RISK_THRESHOLD_REWARD_MULTIPLIER_1 = 2.0  # 0-2: 1.0x
RISK_THRESHOLD_REWARD_MULTIPLIER_2 = 5.0  # 3-5: 0.8x
RISK_THRESHOLD_REWARD_MULTIPLIER_3 = 8.0  # 6-8: 0.6x
RISK_THRESHOLD_FORCED_HITL = 6.0          # 6+: HITL zorunlu
RISK_THRESHOLD_COOLDOWN = 9.0              # 9+: Cooldown

# Heuristics thresholds
LOW_QUALITY_BURST_COUNT = 5               # 24 saatte 5+ reject → burst
TOO_FAST_COMPLETION_SECONDS = 10          # < 10 saniye → too fast

