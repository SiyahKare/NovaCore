#!/usr/bin/env python3
"""
Aurora Policy Simulation Script
Simulates user behavior and CP/regime evolution over time.

Usage:
    python scripts/simulate_aurora_policies.py --users 1000 --days 90 --decay 1
"""

import argparse
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from collections import defaultdict
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.justice.policy import regime_for_cp


class PolicySimulator:
    """Simulates Aurora Justice Stack policy behavior."""
    
    def __init__(
        self,
        decay_per_day: float = 1.0,
        violation_probability: float = 0.05,
        violation_severity_dist: Dict[int, float] = None,
        # DAO-controlled parameters
        base_eko: int = 10,
        base_com: int = 15,
        base_sys: int = 20,
        base_trust: int = 25,
        threshold_soft_flag: int = 20,
        threshold_probation: int = 40,
        threshold_restricted: int = 60,
        threshold_lockdown: int = 80,
    ):
        self.decay_per_day = decay_per_day
        self.violation_probability = violation_probability
        self.violation_severity_dist = violation_severity_dist or {
            1: 0.3,  # 30% severity 1
            2: 0.3,  # 30% severity 2
            3: 0.2,  # 20% severity 3
            4: 0.15, # 15% severity 4
            5: 0.05, # 5% severity 5
        }
        
        # CP weights by category (DAO-controlled)
        self.cp_base = {
            "EKO": base_eko,
            "COM": base_com,
            "SYS": base_sys,
            "TRUST": base_trust,
        }
        self.severity_multiplier = {
            1: 0.5,
            2: 1.0,
            3: 1.5,
            4: 2.0,
            5: 3.0,
        }
        
        # Regime thresholds (DAO-controlled)
        self.threshold_soft_flag = threshold_soft_flag
        self.threshold_probation = threshold_probation
        self.threshold_restricted = threshold_restricted
        self.threshold_lockdown = threshold_lockdown
    
    def calculate_cp_delta(self, category: str, severity: int, code: str) -> int:
        """Calculate CP delta for a violation."""
        base = self.cp_base.get(category, 10)
        multiplier = self.severity_multiplier.get(severity, 1.0)
        cp = int(base * multiplier)
        
        # Special cases
        if code == "SYS_EXPLOIT":
            cp = max(cp, 60)
        if code == "TRUST_MULTIPLE_ACCOUNTS":
            cp = max(cp, 80)
        
        return cp
    
    def apply_decay(self, cp: float, days: float) -> float:
        """Apply decay to CP over time."""
        decay_amount = days * self.decay_per_day
        return max(0.0, cp - decay_amount)
    
    def _regime_for_cp(self, cp: int) -> str:
        """Calculate regime based on CP using DAO-controlled thresholds."""
        if cp >= self.threshold_lockdown:
            return "LOCKDOWN"
        if cp >= self.threshold_restricted:
            return "RESTRICTED"
        if cp >= self.threshold_probation:
            return "PROBATION"
        if cp >= self.threshold_soft_flag:
            return "SOFT_FLAG"
        return "NORMAL"
    
    def generate_violation(self) -> Tuple[str, int, str]:
        """Generate a random violation."""
        category = random.choice(["EKO", "COM", "SYS", "TRUST"])
        severity = random.choices(
            list(self.violation_severity_dist.keys()),
            weights=list(self.violation_severity_dist.values()),
        )[0]
        
        codes = {
            "EKO": ["EKO_NO_SHOW", "EKO_FRAUD", "EKO_CHARGEBACK"],
            "COM": ["COM_TOXIC", "COM_HARASSMENT", "COM_SPAM"],
            "SYS": ["SYS_EXPLOIT", "SYS_ABUSE", "SYS_BOT"],
            "TRUST": ["TRUST_MULTIPLE_ACCOUNTS", "TRUST_FAKE_ID", "TRUST_SCAM"],
        }
        code = random.choice(codes[category])
        
        return category, severity, code
    
    def simulate_user(
        self,
        user_id: str,
        days: int,
        violation_probability: float = None,
    ) -> Dict:
        """Simulate a single user's journey."""
        if violation_probability is None:
            violation_probability = self.violation_probability
        
        cp = 0.0
        regime_history = []
        violations = []
        current_date = datetime.utcnow() - timedelta(days=days)
        
        for day in range(days):
            # Apply decay
            cp = self.apply_decay(cp, 1.0)
            
            # Check for violation
            if random.random() < violation_probability:
                category, severity, code = self.generate_violation()
                cp_delta = self.calculate_cp_delta(category, severity, code)
                cp += cp_delta
                
                violations.append({
                    "day": day,
                    "category": category,
                    "severity": severity,
                    "code": code,
                    "cp_delta": cp_delta,
                    "cp_after": cp,
                })
            
            # Record regime (using DAO-controlled thresholds)
            regime = self._regime_for_cp(int(cp))
            regime_history.append({
                "day": day,
                "cp": int(cp),
                "regime": regime,
            })
        
        # Final state
        final_regime = self._regime_for_cp(int(cp))
        
        return {
            "user_id": user_id,
            "initial_cp": 0,
            "final_cp": int(cp),
            "final_regime": final_regime,
            "total_violations": len(violations),
            "violations": violations,
            "regime_history": regime_history,
            "days_in_lockdown": sum(1 for r in regime_history if r["regime"] == "LOCKDOWN"),
            "days_in_restricted": sum(1 for r in regime_history if r["regime"] == "RESTRICTED"),
            "days_in_probation": sum(1 for r in regime_history if r["regime"] == "PROBATION"),
        }
    
    def simulate_population(
        self,
        num_users: int,
        days: int,
        violation_probability: float = None,
    ) -> Dict:
        """Simulate a population of users."""
        print(f"Simulating {num_users} users over {days} days...")
        
        users = []
        for i in range(num_users):
            if (i + 1) % 100 == 0:
                print(f"  Progress: {i + 1}/{num_users} users...")
            
            user_data = self.simulate_user(
                f"SIM-{i:04d}",
                days,
                violation_probability,
            )
            users.append(user_data)
        
        # Aggregate statistics
        final_regimes = defaultdict(int)
        final_cp_values = []
        total_violations = 0
        lockdown_users = 0
        restricted_users = 0
        probation_users = 0
        
        for user in users:
            final_regimes[user["final_regime"]] += 1
            final_cp_values.append(user["final_cp"])
            total_violations += user["total_violations"]
            
            if user["final_regime"] == "LOCKDOWN":
                lockdown_users += 1
            elif user["final_regime"] == "RESTRICTED":
                restricted_users += 1
            elif user["final_regime"] == "PROBATION":
                probation_users += 1
        
        avg_cp = sum(final_cp_values) / len(final_cp_values) if final_cp_values else 0
        max_cp = max(final_cp_values) if final_cp_values else 0
        
        return {
            "simulation_params": {
                "num_users": num_users,
                "days": days,
                "decay_per_day": self.decay_per_day,
                "violation_probability": violation_probability or self.violation_probability,
            },
            "summary": {
                "total_users": num_users,
                "average_cp": round(avg_cp, 2),
                "max_cp": max_cp,
                "total_violations": total_violations,
                "average_violations_per_user": round(total_violations / num_users, 2),
                "regime_distribution": dict(final_regimes),
                "lockdown_users": lockdown_users,
                "lockdown_percentage": round(lockdown_users / num_users * 100, 2),
                "restricted_users": restricted_users,
                "restricted_percentage": round(restricted_users / num_users * 100, 2),
                "probation_users": probation_users,
                "probation_percentage": round(probation_users / num_users * 100, 2),
            },
            "users": users[:10],  # Sample of first 10 users
        }


def main():
    parser = argparse.ArgumentParser(
        description="Simulate Aurora Justice Stack policy behavior"
    )
    parser.add_argument(
        "--users",
        type=int,
        default=1000,
        help="Number of users to simulate (default: 1000)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=90,
        help="Number of days to simulate (default: 90)",
    )
    parser.add_argument(
        "--decay",
        type=float,
        default=1.0,
        help="CP decay per day (default: 1.0)",
    )
    parser.add_argument(
        "--base-eko",
        type=int,
        default=10,
        help="Base CP weight for EKO violations (default: 10)",
    )
    parser.add_argument(
        "--base-com",
        type=int,
        default=15,
        help="Base CP weight for COM violations (default: 15)",
    )
    parser.add_argument(
        "--base-sys",
        type=int,
        default=20,
        help="Base CP weight for SYS violations (default: 20)",
    )
    parser.add_argument(
        "--base-trust",
        type=int,
        default=25,
        help="Base CP weight for TRUST violations (default: 25)",
    )
    parser.add_argument(
        "--threshold-soft-flag",
        type=int,
        default=20,
        help="CP threshold for SOFT_FLAG regime (default: 20)",
    )
    parser.add_argument(
        "--threshold-probation",
        type=int,
        default=40,
        help="CP threshold for PROBATION regime (default: 40)",
    )
    parser.add_argument(
        "--threshold-restricted",
        type=int,
        default=60,
        help="CP threshold for RESTRICTED regime (default: 60)",
    )
    parser.add_argument(
        "--threshold-lockdown",
        type=int,
        default=80,
        help="CP threshold for LOCKDOWN regime (default: 80)",
    )
    parser.add_argument(
        "--from-db",
        action="store_true",
        help="Load policy parameters from active database policy instead of CLI args",
    )
    parser.add_argument(
        "--use-dao",
        action="store_true",
        help="Load policy parameters directly from on-chain AuroraPolicyConfig contract",
    )
    parser.add_argument(
        "--rpc-url",
        type=str,
        default=os.getenv("AURORA_RPC_URL"),
        help="RPC URL for blockchain connection (for --use-dao)",
    )
    parser.add_argument(
        "--policy-contract",
        type=str,
        default=os.getenv("AURORA_POLICY_CONTRACT"),
        help="AuroraPolicyConfig contract address (for --use-dao)",
    )
    parser.add_argument(
        "--violation-prob",
        type=float,
        default=0.05,
        help="Daily violation probability per user (default: 0.05 = 5%%)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="aurora_simulation.json",
        help="Output JSON file (default: aurora_simulation.json)",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Only output summary statistics (no user details)",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print detailed summary to console (in addition to JSON)",
    )
    
    args = parser.parse_args()
    
    # Load from on-chain DAO if requested
    if args.use_dao:
        try:
            from web3 import Web3
            
            if not args.rpc_url:
                print("❌ RPC URL required for --use-dao. Use --rpc-url or set AURORA_RPC_URL env var")
                sys.exit(1)
            
            if not args.policy_contract:
                print("❌ Contract address required for --use-dao. Use --policy-contract or set AURORA_POLICY_CONTRACT env var")
                sys.exit(1)
            
            # Load ABI from sync script
            from scripts.sync_dao_policy import AURORA_POLICY_ABI
            
            w3 = Web3(Web3.HTTPProvider(args.rpc_url))
            if not w3.is_connected():
                print(f"❌ Failed to connect to RPC: {args.rpc_url}")
                sys.exit(1)
            
            contract_address = Web3.to_checksum_address(args.policy_contract)
            contract = w3.eth.contract(address=contract_address, abi=AURORA_POLICY_ABI)
            
            print(f"📋 Loading policy from on-chain contract: {contract_address}")
            
            jp = contract.functions.justiceParams().call()
            rt = contract.functions.regimeThresholds().call()
            block_number = w3.eth.block_number
            
            # Handle tuple response
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
            
            print(f"✅ Loaded from chain (block {block_number}):")
            print(f"   Decay: {decay_per_day}, Base weights: EKO={base_eko}, COM={base_com}, SYS={base_sys}, TRUST={base_trust}")
            print(f"   Thresholds: SOFT_FLAG={threshold_soft_flag}, PROBATION={threshold_probation}, "
                  f"RESTRICTED={threshold_restricted}, LOCKDOWN={threshold_lockdown}")
            
            simulator = PolicySimulator(
                decay_per_day=decay_per_day,
                base_eko=base_eko,
                base_com=base_com,
                base_sys=base_sys,
                base_trust=base_trust,
                threshold_soft_flag=threshold_soft_flag,
                threshold_probation=threshold_probation,
                threshold_restricted=threshold_restricted,
                threshold_lockdown=threshold_lockdown,
            )
        except ImportError:
            print("❌ web3 package not installed. Install with: pip install web3")
            sys.exit(1)
        except Exception as e:
            print(f"⚠️  Failed to load from DAO: {e}")
            print("   Falling back to CLI arguments")
            simulator = PolicySimulator(
                decay_per_day=args.decay,
                base_eko=args.base_eko,
                base_com=args.base_com,
                base_sys=args.base_sys,
                base_trust=args.base_trust,
                threshold_soft_flag=args.threshold_soft_flag,
                threshold_probation=args.threshold_probation,
                threshold_restricted=args.threshold_restricted,
                threshold_lockdown=args.threshold_lockdown,
            )
    # Load from database if requested
    elif args.from_db:
        try:
            from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
            from sqlalchemy.orm import sessionmaker
            from app.core.config import settings
            from app.justice.policy_service import PolicyService
            import asyncio
            
            async def load_policy():
                engine = create_async_engine(str(settings.DATABASE_URL))
                async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
                async with async_session() as session:
                    policy_service = PolicyService(session)
                    policy = await policy_service.get_active_policy()
                    return policy
            
            policy = asyncio.run(load_policy())
            print(f"📋 Loaded policy from database: {policy.version}")
            print(f"   Decay: {policy.decay_per_day}, Base weights: EKO={policy.base_eko}, "
                  f"COM={policy.base_com}, SYS={policy.base_sys}, TRUST={policy.base_trust}")
            
            simulator = PolicySimulator(
                decay_per_day=policy.decay_per_day,
                base_eko=policy.base_eko,
                base_com=policy.base_com,
                base_sys=policy.base_sys,
                base_trust=policy.base_trust,
                threshold_soft_flag=policy.threshold_soft_flag,
                threshold_probation=policy.threshold_probation,
                threshold_restricted=policy.threshold_restricted,
                threshold_lockdown=policy.threshold_lockdown,
            )
        except Exception as e:
            print(f"⚠️  Failed to load from DB: {e}")
            print("   Falling back to CLI arguments")
            simulator = PolicySimulator(
                decay_per_day=args.decay,
                base_eko=args.base_eko,
                base_com=args.base_com,
                base_sys=args.base_sys,
                base_trust=args.base_trust,
                threshold_soft_flag=args.threshold_soft_flag,
                threshold_probation=args.threshold_probation,
                threshold_restricted=args.threshold_restricted,
                threshold_lockdown=args.threshold_lockdown,
            )
    else:
        simulator = PolicySimulator(
            decay_per_day=args.decay,
            base_eko=args.base_eko,
            base_com=args.base_com,
            base_sys=args.base_sys,
            base_trust=args.base_trust,
            threshold_soft_flag=args.threshold_soft_flag,
            threshold_probation=args.threshold_probation,
            threshold_restricted=args.threshold_restricted,
            threshold_lockdown=args.threshold_lockdown,
        )
    
    result = simulator.simulate_population(
        num_users=args.users,
        days=args.days,
        violation_probability=args.violation_prob,
    )
    
    if args.summary_only:
        output = {
            "simulation_params": result["simulation_params"],
            "summary": result["summary"],
        }
    else:
        output = result
    
    # Write JSON output
    with open(args.output, "w") as f:
        json.dump(output, f, indent=2, default=str)
    
    # Print summary
    if args.summary or not args.summary_only:
        print_detailed_summary(result, args)
    
    print(f"\n✅ Results saved to: {args.output}")
    if args.summary:
        print("=" * 60)


def print_detailed_summary(result: Dict, args) -> None:
    """Print detailed summary to console."""
    print("\n" + "=" * 60)
    print("AURORA POLICY SIMULATION SUMMARY")
    print("=" * 60)
    
    params = result["simulation_params"]
    summary = result["summary"]
    
    print(f"\nSimulation Parameters:")
    print(f"  Users: {params['num_users']}")
    print(f"  Days: {params['days']}")
    print(f"  Decay per day: {params['decay_per_day']}")
    print(f"  Violation probability: {params['violation_probability'] * 100:.1f}%")
    
    print(f"\nFinal Regime Distribution:")
    regime_order = ["NORMAL", "SOFT_FLAG", "PROBATION", "RESTRICTED", "LOCKDOWN"]
    for regime in regime_order:
        count = summary["regime_distribution"].get(regime, 0)
        percentage = count / params['num_users'] * 100
        bar = "█" * int(percentage / 2)  # Visual bar
        print(f"  {regime:12s}: {count:4d} users ({percentage:5.1f}%) {bar}")
    
    print(f"\nCP Statistics:")
    print(f"  Average CP: {summary['average_cp']:.2f}")
    print(f"  Max CP: {summary['max_cp']}")
    
    # Calculate median CP if we have user data
    if "users" in result and len(result["users"]) > 0:
        cp_values = [u["final_cp"] for u in result["users"]]
        cp_values.sort()
        median_cp = cp_values[len(cp_values) // 2]
        print(f"  Median CP: {median_cp:.1f}")
    
    print(f"\nViolation Statistics:")
    print(f"  Total Violations: {summary['total_violations']}")
    print(f"  Avg Violations/User: {summary['average_violations_per_user']:.2f}")
    
    # Violation category breakdown (if available)
    if "users" in result and len(result["users"]) > 0:
        category_counts = defaultdict(int)
        for user in result["users"]:
            for v in user.get("violations", []):
                category_counts[v["category"]] += 1
        
        total_violations = sum(category_counts.values())
        if total_violations > 0:
            print(f"\n  Top Violation Categories:")
            for category in ["EKO", "COM", "SYS", "TRUST"]:
                count = category_counts.get(category, 0)
                percentage = (count / total_violations) * 100
                print(f"    {category}: {count:4d} ({percentage:5.1f}%)")
    
    print(f"\nCritical Regimes:")
    print(f"  LOCKDOWN:   {summary['lockdown_users']:4d} users ({summary['lockdown_percentage']:5.2f}%)")
    print(f"  RESTRICTED: {summary['restricted_users']:4d} users ({summary['restricted_percentage']:5.2f}%)")
    print(f"  PROBATION:  {summary['probation_users']:4d} users ({summary['probation_percentage']:5.2f}%)")
    
    # Policy assessment
    print(f"\nPolicy Assessment:")
    lockdown_pct = summary['lockdown_percentage']
    if lockdown_pct > 5.0:
        print(f"  ⚠️  WARNING: High LOCKDOWN rate ({lockdown_pct:.1f}%) - Policy may be too strict")
    elif lockdown_pct < 0.5:
        print(f"  ✓  Low LOCKDOWN rate ({lockdown_pct:.1f}%) - Policy appears lenient")
    else:
        print(f"  ✓  LOCKDOWN rate ({lockdown_pct:.1f}%) - Within acceptable range")
    
    normal_pct = (summary["regime_distribution"].get("NORMAL", 0) / params['num_users']) * 100
    if normal_pct > 90:
        print(f"  ⚠️  WARNING: Very high NORMAL rate ({normal_pct:.1f}%) - Policy may be too lenient")
    elif normal_pct < 50:
        print(f"  ⚠️  WARNING: Low NORMAL rate ({normal_pct:.1f}%) - Many users in restricted regimes")
    else:
        print(f"  ✓  NORMAL rate ({normal_pct:.1f}%) - Balanced distribution")
    
    print("=" * 60)


if __name__ == "__main__":
    main()

