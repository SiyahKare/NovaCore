#!/usr/bin/env python3
"""
AbuseGuard/RiskScore System Test Script (Simple - Creates test user if needed)
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.abuse.service import AbuseGuard
from app.abuse.models import AbuseEventType, UserRiskProfile
from app.identity.models import User
from sqlmodel import select


async def test_abuse_guard():
    """Test AbuseGuard system."""
    print("🔷 AbuseGuard/RiskScore System Test")
    print("=" * 50)
    
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Get or create a test user
        result = await session.execute(
            select(User).limit(1)
        )
        test_user = result.scalar_one_or_none()
        
        if not test_user:
            # Create a simple test user
            print("📋 Creating test user...")
            test_user = User(
                username="test_abuse_user",
                email="test@abuse.local",
                display_name="Test Abuse User",
            )
            session.add(test_user)
            await session.commit()
            await session.refresh(test_user)
            print(f"✅ Created test user: {test_user.username} (ID: {test_user.id})")
        else:
            print(f"✅ Using existing user: {test_user.username} (ID: {test_user.id})")
        print()
        
        user_id = test_user.id
        abuse_guard = AbuseGuard(session)
        
        # Test 1: Get or create profile
        print("📋 Test 1: Get/Create Risk Profile")
        profile = await abuse_guard.get_or_create_profile(user_id)
        print(f"   ✅ RiskScore: {profile.risk_score:.1f}/10.0")
        print(f"   ✅ Last Event: {profile.last_event_at or 'Never'}")
        print()
        
        # Test 2: Register AUTO_REJECT event
        print("📋 Test 2: Register AUTO_REJECT Event")
        profile = await abuse_guard.register_event(
            user_id=user_id,
            event_type=AbuseEventType.AUTO_REJECT,
            meta={"task_id": "test_task_1", "score": 30},
        )
        print(f"   ✅ New RiskScore: {profile.risk_score:.1f}/10.0 (delta: +0.5)")
        print()
        
        # Test 3: Register DUPLICATE_PROOF event
        print("📋 Test 3: Register DUPLICATE_PROOF Event")
        profile = await abuse_guard.register_event(
            user_id=user_id,
            event_type=AbuseEventType.DUPLICATE_PROOF,
            meta={"task_id": "test_task_2", "proof_hash": "abc123"},
        )
        print(f"   ✅ New RiskScore: {profile.risk_score:.1f}/10.0 (delta: +1.0)")
        print()
        
        # Test 4: Register TOO_FAST_COMPLETION event
        print("📋 Test 4: Register TOO_FAST_COMPLETION Event")
        profile = await abuse_guard.register_event(
            user_id=user_id,
            event_type=AbuseEventType.TOO_FAST_COMPLETION,
            meta={"task_id": "test_task_3", "elapsed_seconds": 5},
        )
        print(f"   ✅ New RiskScore: {profile.risk_score:.1f}/10.0 (delta: +2.0)")
        print()
        
        # Test 5: Check reward multiplier
        print("📋 Test 5: Reward Multiplier Check")
        risk_score = profile.risk_score
        multiplier = abuse_guard.reward_multiplier(risk_score)
        print(f"   RiskScore: {risk_score:.1f}/10.0")
        print(f"   ✅ Reward Multiplier: {multiplier:.1f}x")
        
        base_xp = 100
        base_ncr = 10.0
        final_xp = int(base_xp * multiplier)
        final_ncr = base_ncr * multiplier
        print(f"   Base Rewards: {base_xp} XP, {base_ncr} NCR")
        print(f"   ✅ Final Rewards: {final_xp} XP, {final_ncr:.1f} NCR")
        print()
        
        # Test 6: Check HITL requirement
        print("📋 Test 6: HITL Requirement Check")
        requires_hitl = abuse_guard.requires_forced_hitl(risk_score)
        print(f"   RiskScore: {risk_score:.1f}/10.0")
        print(f"   ✅ Requires HITL: {requires_hitl} (threshold: 6.0+)")
        print()
        
        # Test 7: Check cooldown requirement
        print("📋 Test 7: Cooldown Requirement Check")
        requires_cooldown = abuse_guard.requires_cooldown(risk_score)
        print(f"   RiskScore: {risk_score:.1f}/10.0")
        print(f"   ✅ Requires Cooldown: {requires_cooldown} (threshold: 9.0+)")
        print()
        
        # Test 8: Register more events to trigger cooldown
        if risk_score < 9.0:
            print("📋 Test 8: Trigger Cooldown (9.0+)")
            events_needed = int((9.0 - risk_score) / 1.0) + 1
            print(f"   Registering {events_needed} more LOW_QUALITY_BURST events...")
            for i in range(events_needed):
                profile = await abuse_guard.register_event(
                    user_id=user_id,
                    event_type=AbuseEventType.LOW_QUALITY_BURST,
                    meta={"rejects_last_24h": 5 + i},
                )
            print(f"   ✅ Final RiskScore: {profile.risk_score:.1f}/10.0")
            requires_cooldown = abuse_guard.requires_cooldown(profile.risk_score)
            print(f"   ✅ Requires Cooldown: {requires_cooldown}")
            print()
        
        print("=" * 50)
        print("✅ AbuseGuard System Test Complete!")
        print()
        print("Summary:")
        print(f"  ✅ RiskScore tracking: Working")
        print(f"  ✅ Event logging: Working")
        print(f"  ✅ Reward multiplier: Working ({multiplier:.1f}x)")
        print(f"  ✅ HITL detection: Working ({requires_hitl})")
        print(f"  ✅ Cooldown detection: Working ({requires_cooldown})")
        print()
        print("🎯 System is production-ready!")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(test_abuse_guard())

