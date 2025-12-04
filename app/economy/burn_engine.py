# app/economy/burn_engine.py
"""
SiyahKare NCR Burn Engine

Madde 5 - Enflasyon Kontrolü ve Burn implementasyonu.
Madde 6 - Emek Dışı Kazancın Geçersizliği (Clawback).

NCR_burn = α × Fee_collected
"""
from datetime import datetime
from typing import Optional
import uuid

from .constitution import (
    ECONOMY_CONSTANTS,
    BurnResult,
    ClawbackResult,
    FraudType,
    EconomyMode,
)


class BurnEngine:
    """
    NCR Burn Motoru - Madde 5 & 6.
    
    Fee + Burn mekanizması ile enflasyon kontrolü.
    Clawback ile emek dışı kazancın geçersiz kılınması.
    """
    
    def __init__(self, economy_mode: EconomyMode = EconomyMode.NORMAL):
        self.economy_mode = economy_mode
        self.constants = ECONOMY_CONSTANTS
        
        # Burn oranları moda göre ayarlanır
        self.burn_ratio = self._get_mode_burn_ratio()
    
    def _get_mode_burn_ratio(self) -> float:
        """Ekonomi moduna göre burn oranı."""
        ratios = {
            EconomyMode.NORMAL: self.constants.BURN_RATIO,           # 0.5
            EconomyMode.GROWTH: self.constants.BURN_RATIO * 0.5,     # 0.25 (düşük burn)
            EconomyMode.STABILIZATION: self.constants.BURN_RATIO * 1.5,  # 0.75 (yüksek burn)
            EconomyMode.RECOVERY: self.constants.BURN_RATIO * 2.0,   # 1.0 (maksimum burn)
        }
        return min(1.0, ratios.get(self.economy_mode, self.constants.BURN_RATIO))
    
    # =========================================================================
    # FEE + BURN CALCULATIONS (Madde 5)
    # =========================================================================
    
    def calculate_market_burn(
        self,
        user_id: str,
        gross_amount: float,
    ) -> BurnResult:
        """
        Market işlemi için fee + burn hesapla.
        
        Madde 5.2: Market işlemlerinde fee'nin bir kısmı yakılır.
        """
        fee_rate = self.constants.MARKET_FEE_RATE
        
        fee_amount = gross_amount * fee_rate
        burn_amount = fee_amount * self.burn_ratio
        net_amount = gross_amount - fee_amount
        
        return BurnResult(
            transaction_id=str(uuid.uuid4()),
            user_id=user_id,
            gross_amount=gross_amount,
            fee_amount=round(fee_amount, 4),
            burn_amount=round(burn_amount, 4),
            net_amount=round(net_amount, 4),
            fee_type="market",
            burned_at=datetime.utcnow(),
        )
    
    def calculate_off_ramp_burn(
        self,
        user_id: str,
        gross_amount: float,
    ) -> BurnResult:
        """
        Off-ramp (fiat çıkış) için fee + burn hesapla.
        
        Madde 4.3: Fiat'a çıkış her zaman fee + burn ile çalışır.
        """
        fee_rate = self.constants.OFF_RAMP_FEE_RATE
        
        fee_amount = gross_amount * fee_rate
        burn_amount = fee_amount * self.burn_ratio
        net_amount = gross_amount - fee_amount
        
        return BurnResult(
            transaction_id=str(uuid.uuid4()),
            user_id=user_id,
            gross_amount=gross_amount,
            fee_amount=round(fee_amount, 4),
            burn_amount=round(burn_amount, 4),
            net_amount=round(net_amount, 4),
            fee_type="off_ramp",
            burned_at=datetime.utcnow(),
        )
    
    def calculate_custom_burn(
        self,
        user_id: str,
        gross_amount: float,
        fee_rate: float,
        fee_type: str = "custom",
    ) -> BurnResult:
        """
        Özel fee + burn hesapla.
        
        Stake unlock, transfer, vs. için kullanılabilir.
        """
        fee_amount = gross_amount * fee_rate
        burn_amount = fee_amount * self.burn_ratio
        net_amount = gross_amount - fee_amount
        
        return BurnResult(
            transaction_id=str(uuid.uuid4()),
            user_id=user_id,
            gross_amount=gross_amount,
            fee_amount=round(fee_amount, 4),
            burn_amount=round(burn_amount, 4),
            net_amount=round(net_amount, 4),
            fee_type=fee_type,
            burned_at=datetime.utcnow(),
        )
    
    # =========================================================================
    # CLAWBACK (Madde 6)
    # =========================================================================
    
    def execute_clawback(
        self,
        user_id: str,
        fraud_type: FraudType,
        amount: float,
        reason: Optional[str] = None,
    ) -> ClawbackResult:
        """
        Emek dışı kazancı geri al - Madde 6.
        
        Fraud durumunda:
        1. NCR geri alınır/yakılır
        2. RiskScore yükselir
        3. Cooldown uygulanır
        """
        risk_delta = self.constants.FRAUD_RISK_DELTAS.get(fraud_type.value, 3.0)
        cooldown_hours = self.constants.FRAUD_COOLDOWN_HOURS.get(fraud_type.value, 168)
        
        default_reasons = {
            FraudType.BOT: "Bot/script ile görev spam tespit edildi.",
            FraudType.SYBIL: "Multi-account / Sybil saldırısı tespit edildi.",
            FraudType.EXPLOIT: "Sistem açığı kullanımı (exploit) tespit edildi.",
            FraudType.COPY: "Başka kullanıcının çıktısını kopyalama tespit edildi.",
        }
        
        return ClawbackResult(
            user_id=user_id,
            fraud_type=fraud_type,
            clawed_amount=amount,
            risk_delta=risk_delta,
            cooldown_hours=cooldown_hours,
            reason=reason or default_reasons.get(fraud_type, "Emek dışı kazanç tespit edildi."),
            clawed_at=datetime.utcnow(),
        )
    
    # =========================================================================
    # INACTIVITY FREEZE (Madde 5.4)
    # =========================================================================
    
    def check_inactivity_freeze(
        self,
        user_id: str,
        last_activity_at: Optional[datetime],
        ncr_balance: float,
    ) -> tuple[bool, Optional[str]]:
        """
        Inactivity freeze kontrolü - Madde 5.4.
        
        Uzun süre kullanılamayan bakiyeler Hazinede pasif varlık olarak işaretlenir.
        
        Returns:
            (should_freeze, reason)
        """
        if last_activity_at is None:
            return False, None
        
        days_inactive = (datetime.utcnow() - last_activity_at).days
        
        if days_inactive > self.constants.INACTIVITY_THRESHOLD_DAYS:
            return True, f"{days_inactive} gün inaktif. Bakiye ({ncr_balance} NCR) Hazine'de pasif varlık olarak işaretlendi."
        
        return False, None
    
    # =========================================================================
    # BURN STATISTICS
    # =========================================================================
    
    def estimate_daily_burn(
        self,
        daily_market_volume: float,
        daily_off_ramp_volume: float,
    ) -> dict:
        """
        Günlük tahmini burn miktarı.
        
        Ekonomi yönetimi için metrik.
        """
        market_burn = daily_market_volume * self.constants.MARKET_FEE_RATE * self.burn_ratio
        off_ramp_burn = daily_off_ramp_volume * self.constants.OFF_RAMP_FEE_RATE * self.burn_ratio
        total_burn = market_burn + off_ramp_burn
        
        return {
            "market_burn": round(market_burn, 2),
            "off_ramp_burn": round(off_ramp_burn, 2),
            "total_daily_burn": round(total_burn, 2),
            "burn_ratio": self.burn_ratio,
            "economy_mode": self.economy_mode.value,
        }
    
    def get_burn_summary(
        self,
        total_burned_lifetime: float,
        total_minted_lifetime: float,
    ) -> dict:
        """
        Burn özeti - Madde 5 şeffaflık.
        """
        net_supply_change = total_minted_lifetime - total_burned_lifetime
        burn_rate = total_burned_lifetime / total_minted_lifetime if total_minted_lifetime > 0 else 0.0
        
        return {
            "total_minted": round(total_minted_lifetime, 2),
            "total_burned": round(total_burned_lifetime, 2),
            "net_supply_change": round(net_supply_change, 2),
            "burn_rate_percent": round(burn_rate * 100, 2),
            "deflationary": burn_rate > 0.3,  # %30+ burn = deflationary
        }


# =============================================================================
# TREASURY ENGINE (Madde 5.4)
# =============================================================================

class TreasuryEngine:
    """
    Hazine yönetimi - terk edilmiş bakiyeler ve sistem rezervleri.
    """
    
    def __init__(self):
        self.frozen_balances: dict[str, float] = {}
        self.total_frozen: float = 0.0
    
    def freeze_balance(self, user_id: str, amount: float, reason: str) -> dict:
        """
        Bakiyeyi dondur (inactivity / fraud durumunda).
        """
        self.frozen_balances[user_id] = self.frozen_balances.get(user_id, 0.0) + amount
        self.total_frozen += amount
        
        return {
            "user_id": user_id,
            "frozen_amount": amount,
            "total_frozen_user": self.frozen_balances[user_id],
            "reason": reason,
            "frozen_at": datetime.utcnow().isoformat(),
        }
    
    def unfreeze_balance(
        self,
        user_id: str,
        amount: float,
        reason: str = "User returned",
        apply_burn: bool = False,
        burn_rate: float = 0.1,
    ) -> dict:
        """
        Bakiyeyi çöz (inactivity sonrası geri dönüş).
        
        Args:
            user_id: Kullanıcı ID
            amount: Çözülecek miktar
            reason: Çözme sebebi
            apply_burn: Inactivity cezası olarak burn uygula mı?
            burn_rate: Burn oranı (eğer apply_burn=True ise)
        
        Returns:
            Unfreeze sonucu
        """
        current = self.frozen_balances.get(user_id, 0.0)
        unfreeze_amount = min(amount, current)
        
        # Inactivity cezası: %10 burn (opsiyonel)
        if apply_burn and unfreeze_amount > 0:
            burn_amount = unfreeze_amount * burn_rate
            unfreeze_amount -= burn_amount
            reason += f" (Inactivity penalty: {burn_amount:.2f} NCR burned)"
        
        self.frozen_balances[user_id] = current - unfreeze_amount
        self.total_frozen -= unfreeze_amount
        
        return {
            "user_id": user_id,
            "unfrozen_amount": unfreeze_amount,
            "burned_amount": (current - unfreeze_amount) if apply_burn else 0.0,
            "remaining_frozen": self.frozen_balances[user_id],
            "reason": reason,
            "unfrozen_at": datetime.utcnow().isoformat(),
        }
    
    def get_treasury_stats(self) -> dict:
        """Hazine istatistikleri."""
        return {
            "total_frozen_ncr": self.total_frozen,
            "frozen_accounts": len([u for u, v in self.frozen_balances.items() if v > 0]),
            "largest_frozen": max(self.frozen_balances.values()) if self.frozen_balances else 0.0,
        }


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    engine = BurnEngine(EconomyMode.NORMAL)
    
    # Market işlemi
    market_result = engine.calculate_market_burn("user_123", 100.0)
    print(f"Market İşlemi: 100 NCR")
    print(f"  Fee: {market_result.fee_amount} NCR")
    print(f"  Burn: {market_result.burn_amount} NCR")
    print(f"  Net: {market_result.net_amount} NCR")
    
    # Off-ramp işlemi
    print("\nOff-Ramp İşlemi: 1000 NCR")
    off_ramp_result = engine.calculate_off_ramp_burn("user_123", 1000.0)
    print(f"  Fee: {off_ramp_result.fee_amount} NCR")
    print(f"  Burn: {off_ramp_result.burn_amount} NCR")
    print(f"  Net: {off_ramp_result.net_amount} NCR")
    
    # Clawback
    print("\nFraud Clawback:")
    clawback = engine.execute_clawback("cheater_456", FraudType.BOT, 500.0)
    print(f"  Geri Alınan: {clawback.clawed_amount} NCR")
    print(f"  Risk Delta: +{clawback.risk_delta}")
    print(f"  Cooldown: {clawback.cooldown_hours} saat")
    print(f"  Sebep: {clawback.reason}")
    
    # Günlük burn tahmini
    print("\nGünlük Burn Tahmini:")
    daily = engine.estimate_daily_burn(daily_market_volume=50000, daily_off_ramp_volume=10000)
    print(f"  Market Burn: {daily['market_burn']} NCR")
    print(f"  Off-Ramp Burn: {daily['off_ramp_burn']} NCR")
    print(f"  Toplam: {daily['total_daily_burn']} NCR")

