#!/usr/bin/env python3
"""
NovaCore - Demo Seed Script
Creates 3 demo users with different profiles:
- AUR-SIGMA: Clean citizen (CP 0, FULL consent, high NovaScore)
- AUR-TROLLER: Problematic user (violations, PROBATION/RESTRICTED regime)
- AUR-GHOST: Privacy-conscious user (recall requested, low confidence)
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.consent.router import ConsentService
from app.consent.schemas import (
    ConsentSessionCreate,
    ClauseAcceptanceStatus,
    RedlineConsentRequest,
    ConsentSignRequest,
    RecallRequest,
)
from app.justice.router import JusticeService
from app.justice.schemas import ViolationCreate


async def create_consent_for_user(
    service: ConsentService, user_id: str, client_fingerprint: str
) -> str:
    """Create and sign consent for a user."""
    # Create session
    session_resp = await service.create_session(
        ConsentSessionCreate(
            user_id=user_id, client_fingerprint=client_fingerprint
        )
    )
    session_id = session_resp.session_id

    # Accept all clauses
    clauses = ["1.1", "1.2", "2.1", "2.2", "3.1", "3.2", "4.1", "4.2"]
    for clause_id in clauses:
        await service.log_clause_acceptance(
            ClauseAcceptanceStatus(
                session_id=session_id,
                clause_id=clause_id,
                status="ACCEPTED",
                comprehension_passed=True,
                answered_at=datetime.utcnow(),
            )
        )

    # Accept redline
    await service.log_redline_consent(
        RedlineConsentRequest(
            session_id=session_id,
            redline_status="ACCEPTED",
            user_note_hash=None,
            answered_at=datetime.utcnow(),
        )
    )

    # Sign consent
    sign_req = ConsentSignRequest(
        session_id=session_id,
        user_id=user_id,
        contract_version="Aurora-DataEthics-v1.0",
        clauses_accepted=clauses,
        redline_status="ACCEPTED",
        signature_text=f"{user_id} Signature",
        signed_at=datetime.utcnow(),
        client_fingerprint=client_fingerprint,
    )

    # Get legal text and hash
    legal_text = await service.get_legal_text(sign_req.contract_version)
    import json
    import hashlib

    payload_str = json.dumps(sign_req.dict(), sort_keys=True, default=str)
    to_hash = (legal_text + "|" + payload_str).encode("utf-8")
    contract_hash = hashlib.sha256(to_hash).hexdigest()

    ledger_record = await service.write_immutable_record(
        payload=sign_req, contract_hash=contract_hash
    )
    await service.update_privacy_profile_from_consent(ledger_record)

    return ledger_record.record_id


async def seed_demo_users():
    """Seed 3 demo users with different profiles."""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        consent_service = ConsentService(session)
        justice_service = JusticeService(session)

        print("🔷 Seeding Aurora Demo Users...")
        print("")

        # 1. AUR-SIGMA - Clean citizen
        print("1️⃣ Creating AUR-SIGMA (Clean Citizen)...")
        sigma_user = "AUR-SIGMA"
        record_id = await create_consent_for_user(
            consent_service, sigma_user, "demo-seed-01"
        )
        print(f"   ✅ Consent signed: {record_id}")
        print(f"   ✅ CP: 0, Regime: NORMAL")
        print("")

        # 2. AUR-TROLLER - Problematic user
        print("2️⃣ Creating AUR-TROLLER (Problematic User)...")
        troll_user = "AUR-TROLLER"
        record_id = await create_consent_for_user(
            consent_service, troll_user, "demo-seed-02"
        )
        print(f"   ✅ Consent signed: {record_id}")

        # Add violations
        violations = [
            ViolationCreate(
                user_id=troll_user,
                category="COM",
                code="COM_TOXIC",
                severity=3,
                source="demo-seed",
                context={"reason": "Toxic behavior"},
            ),
            ViolationCreate(
                user_id=troll_user,
                category="SYS",
                code="SYS_ABUSE",
                severity=2,
                source="demo-seed",
                context={"reason": "System abuse"},
            ),
            ViolationCreate(
                user_id=troll_user,
                category="COM",
                code="COM_SPAM",
                severity=2,
                source="demo-seed",
                context={"reason": "Spam messages"},
            ),
        ]

        for violation in violations:
            v_resp = await justice_service.add_violation(violation)
            print(f"   ⚠️  Violation added: {v_resp.code} (+{v_resp.cp_delta} CP)")

        cp_state = await justice_service.get_cp(troll_user)
        print(f"   ✅ Final CP: {cp_state.cp_value}, Regime: {cp_state.regime}")
        print("")

        # 3. AUR-GHOST - Privacy-conscious user
        print("3️⃣ Creating AUR-GHOST (Privacy-Conscious User)...")
        ghost_user = "AUR-GHOST"
        record_id = await create_consent_for_user(
            consent_service, ghost_user, "demo-seed-03"
        )
        print(f"   ✅ Consent signed: {record_id}")

        # Request recall
        recall_req = RecallRequest(
            mode="FULL_EXCLUDE",
            reason="Privacy-conscious user, wants full exclusion from AI training",
        )
        await consent_service.request_recall(ghost_user, recall_req)
        print(f"   🔒 Recall requested: FULL_EXCLUDE")
        print(f"   ✅ CP: 0, Regime: NORMAL (but low NovaScore confidence)")
        print("")

        await session.commit()

    print("✅ Demo users seeded successfully!")
    print("")
    print("📋 Test these users:")
    print(f"   GET /justice/case/{sigma_user}  → Clean citizen")
    print(f"   GET /justice/case/{troll_user}  → Problematic user")
    print(f"   GET /justice/case/{ghost_user}  → Privacy-conscious user")
    print("")
    print("📊 Expected profiles:")
    print(f"   {sigma_user}: CP=0, Regime=NORMAL, High NovaScore")
    print(f"   {troll_user}: CP>0, Regime=PROBATION/RESTRICTED, Lower NovaScore")
    print(f"   {ghost_user}: CP=0, Regime=NORMAL, Low confidence NovaScore")


if __name__ == "__main__":
    asyncio.run(seed_demo_users())

