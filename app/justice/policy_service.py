"""
Aurora Justice Policy Service - DAO-controlled parameter management
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.justice.policy_models import JusticePolicyParams


class PolicyService:
    """Service for managing DAO-controlled policy parameters."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_active_policy(self) -> JusticePolicyParams:
        """
        Get the currently active policy parameters.
        
        Falls back to default values if no active policy exists.
        """
        result = await self.session.exec(
            select(JusticePolicyParams).where(
                JusticePolicyParams.active == True
            ).order_by(JusticePolicyParams.synced_at.desc())
        )
        policy = result.first()
        
        if policy is None:
            # Fallback to default policy (v1.0)
            return JusticePolicyParams(
                version="default-v1.0",
                decay_per_day=1,
                base_eko=10,
                base_com=15,
                base_sys=20,
                base_trust=25,
                threshold_soft_flag=20,
                threshold_probation=40,
                threshold_restricted=60,
                threshold_lockdown=80,
                active=True,
            )
        
        return policy
    
    async def create_policy_version(
        self,
        version: str,
        decay_per_day: int,
        base_eko: int,
        base_com: int,
        base_sys: int,
        base_trust: int,
        threshold_soft_flag: int,
        threshold_probation: int,
        threshold_restricted: int,
        threshold_lockdown: int,
        onchain_address: Optional[str] = None,
        onchain_block: Optional[int] = None,
        onchain_tx: Optional[str] = None,
        notes: Optional[str] = None,
        severity_multiplier: Optional[dict] = None,
    ) -> JusticePolicyParams:
        """
        Create a new policy version and deactivate old ones.
        """
        # Deactivate all existing policies
        await self.session.exec(
            select(JusticePolicyParams).where(
                JusticePolicyParams.active == True
            )
        )
        existing = await self.session.exec(
            select(JusticePolicyParams).where(
                JusticePolicyParams.active == True
            )
        )
        for old_policy in existing.all():
            old_policy.active = False
            self.session.add(old_policy)
        
        # Create new policy
        new_policy = JusticePolicyParams(
            version=version,
            decay_per_day=decay_per_day,
            base_eko=base_eko,
            base_com=base_com,
            base_sys=base_sys,
            base_trust=base_trust,
            threshold_soft_flag=threshold_soft_flag,
            threshold_probation=threshold_probation,
            threshold_restricted=threshold_restricted,
            threshold_lockdown=threshold_lockdown,
            onchain_address=onchain_address,
            onchain_block=onchain_block,
            onchain_tx=onchain_tx,
            notes=notes,
            severity_multiplier=severity_multiplier or {
                "1": 0.5,
                "2": 1.0,
                "3": 1.5,
                "4": 2.0,
                "5": 3.0,
            },
            active=True,
        )
        
        self.session.add(new_policy)
        await self.session.commit()
        await self.session.refresh(new_policy)
        
        return new_policy

