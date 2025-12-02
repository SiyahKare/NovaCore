#!/usr/bin/env python3
"""
Initialize default policy in database.

This script creates the initial v1.0 policy in the database.
Run this before first sync from DAO, or if no policy exists.

Usage:
    python scripts/init_default_policy.py
"""
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import select

from app.core.config import settings
from app.justice.policy_service import PolicyService
from app.justice.policy_models import JusticePolicyParams, PolicyChangeLog


async def main():
    """Initialize default v1.0 policy."""
    print("🔧 Initializing default Aurora Justice Policy v1.0...")
    
    engine = create_async_engine(str(settings.DATABASE_URL))
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        policy_service = PolicyService(session)
        
        # Check if active policy exists
        result = await session.exec(
            select(JusticePolicyParams).where(JusticePolicyParams.active == True)
        )
        existing = result.first()
        
        if existing:
            print(f"⚠️  Active policy already exists: {existing.version}")
            if existing.onchain_block is not None:
                print(f"   This policy is synced from chain (block {existing.onchain_block})")
            response = input("Create new default policy anyway? (y/N): ")
            if response.lower() != 'y':
                print("Cancelled.")
                return
        
        # Create default policy
        default_policy = await policy_service.create_policy_version(
            version="v1.0",
            decay_per_day=1,
            base_eko=10,
            base_com=15,
            base_sys=20,
            base_trust=25,
            threshold_soft_flag=20,
            threshold_probation=40,
            threshold_restricted=60,
            threshold_lockdown=80,
            onchain_address=None,
            onchain_block=None,
            onchain_tx=None,
            notes="Initial Aurora Justice Policy v1.0 - Default values before DAO sync.",
        )
        
        # Create change log entry
        change_log = PolicyChangeLog(
            policy_version=default_policy.version,
            changed_by="SEED_SCRIPT",
            change_type="seed",
            old_params=None,
            new_params={
                "decay_per_day": default_policy.decay_per_day,
                "base_eko": default_policy.base_eko,
                "base_com": default_policy.base_com,
                "base_sys": default_policy.base_sys,
                "base_trust": default_policy.base_trust,
                "threshold_soft_flag": default_policy.threshold_soft_flag,
                "threshold_probation": default_policy.threshold_probation,
                "threshold_restricted": default_policy.threshold_restricted,
                "threshold_lockdown": default_policy.threshold_lockdown,
            },
            onchain_tx=None,
        )
        session.add(change_log)
        await session.commit()
        
        print(f"\n✅ Default policy created: {default_policy.version}")
        print(f"   Decay: {default_policy.decay_per_day}")
        print(f"   Base weights: EKO={default_policy.base_eko}, COM={default_policy.base_com}, "
              f"SYS={default_policy.base_sys}, TRUST={default_policy.base_trust}")
        print(f"   Thresholds: SOFT_FLAG={default_policy.threshold_soft_flag}, "
              f"PROBATION={default_policy.threshold_probation}, "
              f"RESTRICTED={default_policy.threshold_restricted}, "
              f"LOCKDOWN={default_policy.threshold_lockdown}")
        print(f"\n✅ Change log entry created")
    
    await engine.dispose()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

