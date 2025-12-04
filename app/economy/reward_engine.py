# app/economy/reward_engine.py
"""
SiyahKare NCR Reward Engine

Madde 3 - NCR Kazanma Mekanizması implementasyonu.

NCR_final = BaseNCR × RewardMultiplier(user)

RewardMultiplier = StreakFactor × SiyahScoreFactor × RiskFactor × NovaFactor
"""
from datetime import datetime
from typing import Optional

from .constitution import (
    ECONOMY_CONSTANTS,
    UserEconomyContext,
    RewardMultiplierResult,
    EconomyMode,
)
from .drm import DynamicRewardManager, MacroContext, compute_final_reward
from ..core.citizenship import get_citizen_level_multiplier


class RewardEngine:
    """
    NCR Ödül Hesaplama Motoru - Madde 3.
    
    Ahlaklı, istikrarlı ve kaliteli vatandaşlar daha fazla kazanır.
    """
    
    def __init__(self, economy_mode: EconomyMode = EconomyMode.NORMAL):
        self.economy_mode = economy_mode
        self.constants = ECONOMY_CONSTANTS
    
    # =========================================================================
    # FACTOR CALCULATIONS
    # =========================================================================
    
    def compute_streak_factor(self, streak_days: int) -> float:
        """
        Streak Factor (1.0 - 1.3)
        
        Her gün için +%1 bonus, maksimum 30 gün.
        """
        capped_days = min(streak_days, self.constants.MAX_STREAK_DAYS)
        factor = 1.0 + (capped_days * self.constants.STREAK_BONUS_PER_DAY)
        return round(factor, 3)
    
    def compute_siyah_factor(self, siyah_score_avg: float) -> float:
        """
        SiyahScore Factor (0.7 - 1.2)
        
        İş kalitesi çarpanı. Düşük kalite → düşük kazanç.
        """
        # Normalize to 0-1
        normalized = max(0.0, min(100.0, siyah_score_avg)) / 100.0
        
        # Scale to 0.7 - 1.2
        factor = self.constants.SIYAH_SCORE_BASE + (normalized * self.constants.SIYAH_SCORE_MAX_BONUS)
        return round(factor, 3)
    
    def compute_risk_factor(self, risk_score: float) -> float:
        """
        Risk Factor (0.0 - 1.0)
        
        Düşük risk = yüksek çarpan.
        Yüksek risk = düşük kazanç.
        """
        # risk_score: 0-10
        # 0 risk → 1.0 factor
        # 10 risk → 0.0 factor
        factor = max(0.0, 1.0 - (risk_score / 10.0))
        return round(factor, 3)
    
    def compute_nova_factor(self, citizen_level: str) -> float:
        """
        Nova Factor (0.5 - 1.5)
        
        Vatandaşlık seviyesine göre çarpan.
        """
        return get_citizen_level_multiplier(citizen_level)
    
    # =========================================================================
    # ECONOMY MODE ADJUSTMENTS
    # =========================================================================
    
    def get_mode_adjustment(self) -> float:
        """
        Ekonomi moduna göre ek çarpan.
        """
        adjustments = {
            EconomyMode.NORMAL: 1.0,
            EconomyMode.GROWTH: 1.2,          # +%20 emission
            EconomyMode.STABILIZATION: 0.8,   # -%20 emission
            EconomyMode.RECOVERY: 0.5,        # -%50 emission
        }
        return adjustments.get(self.economy_mode, 1.0)
    
    # =========================================================================
    # MAIN CALCULATION
    # =========================================================================
    
    def compute_reward_multiplier(self, ctx: UserEconomyContext) -> float:
        """
        RewardMultiplier hesapla.
        
        RewardMultiplier = StreakFactor × SiyahFactor × RiskFactor × NovaFactor × ModeAdjustment
        """
        streak_f = self.compute_streak_factor(ctx.streak_days)
        siyah_f = self.compute_siyah_factor(ctx.siyah_score_avg)
        risk_f = self.compute_risk_factor(ctx.risk_score)
        nova_f = self.compute_nova_factor(ctx.citizen_level)
        mode_adj = self.get_mode_adjustment()
        
        multiplier = streak_f * siyah_f * risk_f * nova_f * mode_adj
        
        # Clamp to bounds
        multiplier = max(
            self.constants.MIN_REWARD_MULTIPLIER,
            min(self.constants.MAX_REWARD_MULTIPLIER, multiplier)
        )
        
        return round(multiplier, 4)
    
    def calculate_reward(
        self,
        ctx: UserEconomyContext,
        base_ncr: float,
        macro_context: Optional[MacroContext] = None,
    ) -> RewardMultiplierResult:
        """
        Final NCR ödülü hesapla.
        
        Args:
            ctx: Kullanıcı ekonomi context'i
            base_ncr: Görevin base NCR değeri
        
        Returns:
            RewardMultiplierResult with breakdown
        """
        # Compute individual factors
        streak_f = self.compute_streak_factor(ctx.streak_days)
        siyah_f = self.compute_siyah_factor(ctx.siyah_score_avg)
        risk_f = self.compute_risk_factor(ctx.risk_score)
        nova_f = self.compute_nova_factor(ctx.citizen_level)
        
        # Compute user multiplier (mikro katman)
        user_multiplier = self.compute_reward_multiplier(ctx)
        
        # Apply macro multiplier if provided (makro katman)
        if macro_context:
            final_ncr, macro_mult = compute_final_reward(
                base_ncr, user_multiplier, macro_context
            )
            multiplier = user_multiplier * macro_mult
        else:
            # Fallback: sadece user multiplier (backward compatibility)
            final_ncr = round(base_ncr * user_multiplier, 2)
            multiplier = user_multiplier
        
        return RewardMultiplierResult(
            user_id=ctx.user_id,
            base_ncr=base_ncr,
            final_ncr=final_ncr,
            multiplier=multiplier,
            streak_factor=streak_f,
            siyah_factor=siyah_f,
            risk_factor=risk_f,
            nova_factor=nova_f,
            streak_days=ctx.streak_days,
            siyah_score_avg=ctx.siyah_score_avg,
            risk_score=ctx.risk_score,
            citizen_level=ctx.citizen_level,
        )
    
    # =========================================================================
    # VALIDATION (Madde 2 - Emek İlkesi)
    # =========================================================================
    
    def validate_reward_eligibility(
        self,
        ctx: UserEconomyContext,
        task_completed: bool,
        quality_score: float,
    ) -> tuple[bool, Optional[str]]:
        """
        Madde 2 - Emek İlkesi: Ödül hak ediliyor mu?
        
        Returns:
            (eligible, reason_if_not)
        """
        # Görev tamamlanmamış
        if not task_completed:
            return False, "Görev tamamlanmadı. Emek yoksa, NCR de yoktur."
        
        # Risk çok yüksek (Madde 6 - Fraud)
        if ctx.risk_score >= 9.0:
            return False, "Risk skoru çok yüksek. Hesap inceleme altında."
        
        # Kalite çok düşük
        if quality_score < 20.0:
            return False, "İş kalitesi minimum standardın altında."
        
        return True, None
    
    # =========================================================================
    # UTILITY
    # =========================================================================
    
    def estimate_daily_earnings(
        self,
        ctx: UserEconomyContext,
        avg_task_count: int = 10,
        avg_task_base_ncr: float = 10.0,
    ) -> float:
        """
        Günlük tahmini kazanç.
        
        Madde 7 - Şeffaflık: Vatandaş ne kazanacağını bilmeli.
        """
        multiplier = self.compute_reward_multiplier(ctx)
        daily_estimate = avg_task_count * avg_task_base_ncr * multiplier
        return round(daily_estimate, 2)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def quick_reward_calc(
    base_ncr: float,
    streak_days: int = 0,
    siyah_score: float = 50.0,
    risk_score: float = 0.0,
    citizen_level: str = "resident",
    economy_mode: EconomyMode = EconomyMode.NORMAL,
) -> float:
    """
    Hızlı ödül hesaplama.
    
    Tam context olmadan basit hesaplama için.
    """
    engine = RewardEngine(economy_mode)
    ctx = UserEconomyContext(
        user_id="temp",
        streak_days=streak_days,
        siyah_score_avg=siyah_score,
        risk_score=risk_score,
        citizen_level=citizen_level,
    )
    result = engine.calculate_reward(ctx, base_ncr)
    return result.final_ncr


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    # Örnek hesaplama
    engine = RewardEngine(EconomyMode.NORMAL)
    
    # İyi vatandaş
    good_citizen = UserEconomyContext(
        user_id="good_user",
        streak_days=15,
        siyah_score_avg=85.0,
        risk_score=0.5,
        citizen_level="core_citizen",
    )
    
    # Riskli vatandaş
    risky_citizen = UserEconomyContext(
        user_id="risky_user",
        streak_days=3,
        siyah_score_avg=45.0,
        risk_score=6.0,
        citizen_level="resident",
    )
    
    base_ncr = 10.0
    
    good_result = engine.calculate_reward(good_citizen, base_ncr)
    risky_result = engine.calculate_reward(risky_citizen, base_ncr)
    
    print(f"İyi Vatandaş: {base_ncr} NCR → {good_result.final_ncr} NCR (x{good_result.multiplier})")
    print(f"  Streak: {good_result.streak_factor}, Siyah: {good_result.siyah_factor}, Risk: {good_result.risk_factor}, Nova: {good_result.nova_factor}")
    
    print(f"\nRiskli Vatandaş: {base_ncr} NCR → {risky_result.final_ncr} NCR (x{risky_result.multiplier})")
    print(f"  Streak: {risky_result.streak_factor}, Siyah: {risky_result.siyah_factor}, Risk: {risky_result.risk_factor}, Nova: {risky_result.nova_factor}")

