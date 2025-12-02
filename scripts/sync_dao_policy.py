#!/usr/bin/env python3
"""
Aurora DAO Policy Sync Script
Syncs policy parameters from on-chain AuroraPolicyConfig contract to database.

Usage:
    python scripts/sync_dao_policy.py --rpc-url https://rpc.chain.xyz --contract 0x...
    
    Or use environment variables:
    AURORA_RPC_URL=https://rpc.chain.xyz
    AURORA_POLICY_CONTRACT=0x...
    python scripts/sync_dao_policy.py
"""
import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.justice.policy_service import PolicyService


# AuroraPolicyConfig ABI (complete)
AURORA_POLICY_ABI = [
    {
        "inputs": [],
        "name": "justiceParams",
        "outputs": [
            {"components": [
                {"internalType": "uint256", "name": "decayPerDay", "type": "uint256"},
                {"internalType": "uint256", "name": "baseEko", "type": "uint256"},
                {"internalType": "uint256", "name": "baseCom", "type": "uint256"},
                {"internalType": "uint256", "name": "baseSys", "type": "uint256"},
                {"internalType": "uint256", "name": "baseTrust", "type": "uint256"}
            ], "internalType": "struct AuroraPolicyConfig.JusticeParams", "name": "", "type": "tuple"}
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "regimeThresholds",
        "outputs": [
            {"components": [
                {"internalType": "uint256", "name": "softFlag", "type": "uint256"},
                {"internalType": "uint256", "name": "probation", "type": "uint256"},
                {"internalType": "uint256", "name": "restricted", "type": "uint256"},
                {"internalType": "uint256", "name": "lockdown", "type": "uint256"}
            ], "internalType": "struct AuroraPolicyConfig.RegimeThresholds", "name": "", "type": "tuple"}
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "governor",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
]


async def sync_from_chain(
    rpc_url: str,
    contract_address: str,
    dry_run: bool = False,
) -> None:
    """
    Sync policy parameters from on-chain contract to database.
    """
    try:
        from web3 import Web3
    except ImportError:
        print("❌ web3 package not installed. Install with: pip install web3")
        sys.exit(1)
    
    print(f"🔗 Connecting to chain: {rpc_url}")
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    
    if not w3.is_connected():
        print(f"❌ Failed to connect to RPC: {rpc_url}")
        sys.exit(1)
    
    print(f"✅ Connected. Chain ID: {w3.eth.chain_id}")
    
    # Get contract
    contract_address = Web3.to_checksum_address(contract_address)
    contract = w3.eth.contract(address=contract_address, abi=AURORA_POLICY_ABI)
    
    print(f"📋 Reading AuroraPolicyConfig at: {contract_address}")
    
    # Read parameters
    try:
        jp = contract.functions.justiceParams().call()
        rt = contract.functions.regimeThresholds().call()
        governor = contract.functions.governor().call()
    except Exception as e:
        print(f"❌ Failed to read contract: {e}")
        sys.exit(1)
    
    # Handle both tuple and list responses
    if isinstance(jp, tuple):
        decay_per_day = jp.decayPerDay
        base_eko = jp.baseEko
        base_com = jp.baseCom
        base_sys = jp.baseSys
        base_trust = jp.baseTrust
    else:
        decay_per_day, base_eko, base_com, base_sys, base_trust = jp
    
    if isinstance(rt, tuple):
        threshold_soft_flag = rt.softFlag
        threshold_probation = rt.probation
        threshold_restricted = rt.restricted
        threshold_lockdown = rt.lockdown
    else:
        threshold_soft_flag, threshold_probation, threshold_restricted, threshold_lockdown = rt
    
    # Get current block
    block_number = w3.eth.block_number
    
    print("\n📊 Policy Parameters from Chain:")
    print(f"  Decay per day: {decay_per_day}")
    print(f"  Base weights: EKO={base_eko}, COM={base_com}, SYS={base_sys}, TRUST={base_trust}")
    print(f"  Thresholds: SOFT_FLAG={threshold_soft_flag}, PROBATION={threshold_probation}, "
          f"RESTRICTED={threshold_restricted}, LOCKDOWN={threshold_lockdown}")
    print(f"  Governor: {governor}")
    print(f"  Block: {block_number}")
    
    if dry_run:
        print("\n🔍 DRY RUN - Not saving to database")
        return
    
    # Save to database
    print("\n💾 Saving to database...")
    
    engine = create_async_engine(str(settings.DATABASE_URL))
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        policy_service = PolicyService(session)
        
        version = f"onchain-{block_number}"
        notes = f"Synced from AuroraPolicyConfig at block {block_number}"
        
        new_policy = await policy_service.create_policy_version(
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
            onchain_address=contract_address,
            onchain_block=block_number,
            onchain_tx=None,  # Could fetch from events if needed
            notes=notes,
        )
        
        print(f"✅ Policy version '{new_policy.version}' saved and activated")
        print(f"   Synced at: {new_policy.synced_at}")
    
    await engine.dispose()


def main():
    parser = argparse.ArgumentParser(
        description="Sync Aurora policy parameters from on-chain contract to database"
    )
    parser.add_argument(
        "--rpc-url",
        type=str,
        default=os.getenv("AURORA_RPC_URL"),
        help="RPC URL for blockchain connection",
    )
    parser.add_argument(
        "--contract",
        type=str,
        default=os.getenv("AURORA_POLICY_CONTRACT"),
        help="AuroraPolicyConfig contract address",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Read from chain but don't save to database",
    )
    
    args = parser.parse_args()
    
    if not args.rpc_url:
        print("❌ RPC URL required. Use --rpc-url or set AURORA_RPC_URL env var")
        sys.exit(1)
    
    if not args.contract:
        print("❌ Contract address required. Use --contract or set AURORA_POLICY_CONTRACT env var")
        sys.exit(1)
    
    import asyncio
    asyncio.run(sync_from_chain(args.rpc_url, args.contract, args.dry_run))


if __name__ == "__main__":
    main()

