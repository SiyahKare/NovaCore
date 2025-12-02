"""
Aurora Justice Policy Models - DAO-controlled parameters
"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Column, JSON


class JusticePolicyParams(SQLModel, table=True):
    """
    DAO-controlled policy parameters.
    
    These parameters can be changed by AuroraDAO governance.
    Constitution layer (consent, recall rights) cannot be changed.
    """
    __tablename__ = "justice_policy_params"

    id: Optional[int] = Field(default=None, primary_key=True)
    version: str = Field(index=True, description="Policy version identifier")
    
    # CP Decay
    decay_per_day: int = Field(description="CP decay per day")
    
    # CP Base Weights
    base_eko: int = Field(description="Base CP weight for EKO violations")
    base_com: int = Field(description="Base CP weight for COM violations")
    base_sys: int = Field(description="Base CP weight for SYS violations")
    base_trust: int = Field(description="Base CP weight for TRUST violations")
    
    # Regime Thresholds
    threshold_soft_flag: int = Field(description="CP threshold for SOFT_FLAG regime")
    threshold_probation: int = Field(description="CP threshold for PROBATION regime")
    threshold_restricted: int = Field(description="CP threshold for RESTRICTED regime")
    threshold_lockdown: int = Field(description="CP threshold for LOCKDOWN regime")
    
    # On-chain metadata (if synced from DAO)
    onchain_address: Optional[str] = Field(default=None, description="AuroraPolicyConfig contract address")
    onchain_block: Optional[int] = Field(default=None, description="Block number when synced")
    onchain_tx: Optional[str] = Field(default=None, description="Transaction hash")
    
    # Metadata
    synced_at: datetime = Field(default_factory=datetime.utcnow, description="When this policy was synced")
    active: bool = Field(default=True, index=True, description="Is this policy currently active?")
    notes: Optional[str] = Field(default=None, description="Optional notes about this policy version")
    
    # Severity multipliers (can also be DAO-controlled)
    severity_multiplier: dict = Field(
        default_factory=lambda: {
            "1": 0.5,
            "2": 1.0,
            "3": 1.5,
            "4": 2.0,
            "5": 3.0,
        },
        sa_column=Column(JSON),
        description="Severity multiplier map (1-5)",
    )


class PolicyChangeLog(SQLModel, table=True):
    """
    Log of policy changes for audit trail.
    """
    __tablename__ = "justice_policy_change_log"

    id: Optional[int] = Field(default=None, primary_key=True)
    policy_version: str = Field(index=True)
    changed_by: Optional[str] = Field(default=None, description="DAO address or admin user")
    change_type: str = Field(description="Type of change: 'dao_vote', 'admin_update', 'sync'")
    old_params: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    new_params: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    onchain_tx: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

