"""
NovaCore Treasury Rules
Vergi oranları, havuz dağılımları ve konfigürasyon
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Tuple


@dataclass
class TreasuryConfig:
    """Treasury konfigürasyonu - vergi oranı ve havuz dağılımı."""
    tax_rate: Decimal
    split: Dict[str, Decimal]


# Default Treasury Konfigürasyonu
TREASURY_CONFIG = {
    "default_tax_rate": Decimal("0.20"),  # %20 platform vergisi
    
    "split": {
        "GROWTH": Decimal("0.40"),        # %40 → Growth Fund
        "PERFORMER_POOL": Decimal("0.30"),  # %30 → Performer Bonus Pool
        "DEV_FUND": Decimal("0.20"),     # %20 → Dev Fund
        "BURN": Decimal("0.10"),         # %10 → Yakılır (supply düşer)
    },
    
    # App / event bazlı override'lar
    "overrides": {
        # Örnek: FlirtMarket tip için farklı oran
        # ("FLIRTMARKET", "TIP"): {
        #     "tax_rate": Decimal("0.25"),
        #     "split": {
        #         "GROWTH": Decimal("0.35"),
        #         "PERFORMER_POOL": Decimal("0.35"),
        #         "DEV_FUND": Decimal("0.20"),
        #         "BURN": Decimal("0.10"),
        #     }
        # },
        
        # Poker rake için farklı oran
        # ("POKER", "RAKE"): {
        #     "tax_rate": Decimal("0.15"),
        #     "split": {
        #         "GROWTH": Decimal("0.50"),
        #         "PERFORMER_POOL": Decimal("0.20"),
        #         "DEV_FUND": Decimal("0.20"),
        #         "BURN": Decimal("0.10"),
        #     }
        # },
    }
}


def resolve_config(app: str, kind: str) -> TreasuryConfig:
    """
    App ve event kind'a göre treasury konfigürasyonunu çöz.
    
    Args:
        app: Uygulama adı (FLIRTMARKET, ONLYVIPS, POKER, etc.)
        kind: Event tipi (TIP, MESSAGE, SUBSCRIPTION, RAKE, etc.)
    
    Returns:
        TreasuryConfig: Vergi oranı ve havuz dağılımı
    """
    # Override kontrolü
    override_key = (app.upper(), kind.upper())
    if override_key in TREASURY_CONFIG["overrides"]:
        override = TREASURY_CONFIG["overrides"][override_key]
        return TreasuryConfig(
            tax_rate=override["tax_rate"],
            split=override["split"]
        )
    
    # Default konfigürasyon
    return TreasuryConfig(
        tax_rate=TREASURY_CONFIG["default_tax_rate"],
        split=TREASURY_CONFIG["split"]
    )


# Pool ID mapping - SystemAccountType ile eşleşme
POOL_ACCOUNT_TYPE_MAP = {
    "GROWTH": "POOL_GROWTH",
    "PERFORMER_POOL": "POOL_PERFORMER",
    "DEV_FUND": "POOL_DEV",
    "BURN": "POOL_BURN",  # Burn için özel hesap yok, direkt yakılır
}

