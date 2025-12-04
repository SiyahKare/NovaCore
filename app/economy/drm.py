# app/economy/drm.py
"""
Dynamic Reward Multiplier (DRM)

Makro ekonomi katmanı - Mikro (kullanıcı kalitesi) + Makro (mode & emission) birleşimi.

NCR_final = BaseNCR × UserMultiplier × MacroMultiplier
"""
from dataclasses import dataclass
from typing import Optional

from .constitution import EconomyMode


@dataclass
class MacroContext:
    """
    Makro ekonomi context'i - DRM hesaplama için gerekli metrikler.
    """
    mode: EconomyMode
    
    # Emission metrikleri
    daily_emission_used: float = 0.0
    daily_emission_cap: float = 0.0
    weekly_emission_used: float = 0.0
    weekly_emission_cap: float = 0.0
    
    # Burn metrikleri
    burn_rate_7d: float = 0.0  # 0-1: Son 7 gün yakılan NCR / toplam işlem
    
    # Treasury metrikleri
    treasury_health: float = 0.5  # 0-1: 0 = boş, 1 = hedef doluluk


class DynamicRewardManager:
    """
    Dynamic Reward Multiplier (DRM) - Makro ekonomi katmanı.
    
    Ekonomi şişince ödülü nefes aldırır, durgunlaşınca gaz verir.
    """
    
    MIN_MACRO = 0.5
    MAX_MACRO = 1.5
    
    @classmethod
    def compute_macro_multiplier(cls, ctx: MacroContext) -> float:
        """
        Makro çarpan hesapla.
        
        Args:
            ctx: Makro ekonomi context'i
        
        Returns:
            Macro multiplier (0.5 - 1.5)
        """
        # 1) Emission baskısı
        daily_ratio = (
            ctx.daily_emission_used / ctx.daily_emission_cap
            if ctx.daily_emission_cap > 0 else 0.0
        )
        weekly_ratio = (
            ctx.weekly_emission_used / ctx.weekly_emission_cap
            if ctx.weekly_emission_cap > 0 else 0.0
        )
        
        # 0.0-1.0 arası bir pressure metriği
        pressure = max(daily_ratio, weekly_ratio)
        
        # 2) Mode bazlı base multiplier
        base_by_mode = {
            EconomyMode.NORMAL: 1.0,
            EconomyMode.GROWTH: 1.15,          # +%15 (onboarding/hype dönemi)
            EconomyMode.STABILIZATION: 0.9,    # -%10 (enflasyon kontrolü)
            EconomyMode.RECOVERY: 0.75,        # -%25 (kriz modu)
        }.get(ctx.mode, 1.0)
        
        # 3) Emission pressure'a göre ayar
        if pressure > 1.0:
            # Cap aşılmış → düşür
            pressure_penalty = min(0.5, (pressure - 1.0))  # max -0.5
            macro = base_by_mode * (1.0 - pressure_penalty)
        else:
            # Cap'in altındaysak → biraz bonus
            bonus = (1.0 - pressure) * 0.2  # max +0.2
            macro = base_by_mode * (1.0 + bonus)
        
        # 4) Treasury health ile ince ayar
        if ctx.treasury_health < 0.3:
            # Treasury çok boş → hafif kıs
            macro *= 0.9
        elif ctx.treasury_health > 0.8:
            # Treasury dolu → hafif bonus
            macro *= 1.05
        
        # 5) Burn rate ile denge
        # Yüksek burn = ekonomik sağlık → hafif bonus
        if ctx.burn_rate_7d > 0.3:
            macro *= 1.02
        
        # Clamp
        macro = max(cls.MIN_MACRO, min(cls.MAX_MACRO, macro))
        return round(macro, 3)
    
    @classmethod
    def get_mode_adjustment(cls, mode: EconomyMode) -> float:
        """
        Ekonomi moduna göre base çarpan (hızlı referans için).
        """
        return {
            EconomyMode.NORMAL: 1.0,
            EconomyMode.GROWTH: 1.15,
            EconomyMode.STABILIZATION: 0.9,
            EconomyMode.RECOVERY: 0.75,
        }.get(mode, 1.0)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def compute_final_reward(
    base_ncr: float,
    user_multiplier: float,
    macro_context: MacroContext,
) -> tuple[float, float]:
    """
    Final NCR ödülü hesapla (UserMultiplier × MacroMultiplier).
    
    Args:
        base_ncr: Görevin base NCR değeri
        user_multiplier: Kullanıcı kalitesine göre çarpan (RewardEngine'den)
        macro_context: Makro ekonomi context'i
    
    Returns:
        (final_ncr, macro_multiplier)
    """
    macro_mult = DynamicRewardManager.compute_macro_multiplier(macro_context)
    final_ncr = base_ncr * user_multiplier * macro_mult
    return round(final_ncr, 4), macro_mult


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    # Normal mod - emission cap altında
    normal_ctx = MacroContext(
        mode=EconomyMode.NORMAL,
        daily_emission_used=5000.0,
        daily_emission_cap=10000.0,
        weekly_emission_used=30000.0,
        weekly_emission_cap=70000.0,
        burn_rate_7d=0.25,
        treasury_health=0.6,
    )
    
    # Growth mod - emission cap üstünde
    growth_ctx = MacroContext(
        mode=EconomyMode.GROWTH,
        daily_emission_used=12000.0,  # Cap aşılmış
        daily_emission_cap=10000.0,
        weekly_emission_used=80000.0,
        weekly_emission_cap=70000.0,
        burn_rate_7d=0.15,
        treasury_health=0.4,
    )
    
    base_ncr = 10.0
    user_mult = 1.2  # İyi vatandaş
    
    normal_final, normal_macro = compute_final_reward(base_ncr, user_mult, normal_ctx)
    growth_final, growth_macro = compute_final_reward(base_ncr, user_mult, growth_ctx)
    
    print(f"Normal Mod: {base_ncr} × {user_mult} × {normal_macro} = {normal_final} NCR")
    print(f"Growth Mod (cap aşılmış): {base_ncr} × {user_mult} × {growth_macro} = {growth_final} NCR")
    print(f"\nGrowth mod'da emission cap aşıldığı için macro düştü.")

