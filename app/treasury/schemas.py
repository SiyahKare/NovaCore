"""
NovaCore Treasury Schemas
API DTO'ları
"""
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.treasury.models import SystemAccountType


class TreasuryFlowOut(BaseModel):
    """Treasury flow output schema."""
    id: str
    ts: datetime
    app: str
    kind: str
    gross_amount: Decimal
    tax_amount: Decimal
    net_to_performer: Decimal
    user_id: Optional[int] = None
    performer_id: Optional[int] = None
    agency_id: Optional[int] = None
    growth_amount: Decimal
    performer_pool_amount: Decimal
    dev_amount: Decimal
    burn_amount: Decimal
    metadata: Dict = Field(default_factory=dict)

    class Config:
        from_attributes = True


class SystemAccountOut(BaseModel):
    """System account output schema."""
    id: str
    account_type: SystemAccountType
    wallet_account_id: Optional[int] = None
    label: str
    description: Optional[str] = None
    agency_id: Optional[int] = None
    balance: Optional[Decimal] = None  # Wallet'dan çekilecek
    metadata: Dict = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TreasurySummary(BaseModel):
    """Treasury summary for AuroraOS dashboard."""
    total_treasury: Decimal
    pools_balance: Dict[str, Decimal]  # POOL_GROWTH, POOL_PERFORMER, POOL_DEV
    last_24h_revenue: Decimal
    last_7d_revenue: Decimal
    total_burned: Decimal
    revenue_by_app: Dict[str, Decimal]  # FLIRTMARKET: X, ONLYVIPS: Y, etc.
    revenue_by_kind: Dict[str, Decimal]  # TIP: X, MESSAGE: Y, etc.


class TreasuryFlowQuery(BaseModel):
    """Treasury flow query parameters."""
    range: str = Field(default="24h", description="24h, 7d, 30d, all")
    app: Optional[str] = None
    kind: Optional[str] = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=50, ge=1, le=100)


class RevenueChartData(BaseModel):
    """Revenue chart data for AuroraOS."""
    labels: List[str]  # Timestamps
    revenue: List[Decimal]
    app_breakdown: Dict[str, List[Decimal]]  # App bazlı breakdown


class RouteRevenueRequest(BaseModel):
    """Route revenue request - events service'den çağrılacak."""
    app: str
    kind: str
    user_id: int
    performer_id: Optional[int] = None
    agency_id: Optional[int] = None
    gross_amount: Decimal
    reference_id: Optional[str] = None
    reference_type: Optional[str] = None
    metadata: Dict = Field(default_factory=dict)

