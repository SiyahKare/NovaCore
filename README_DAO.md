# Aurora DAO Integration - Quick Start

## 🎯 Overview

Aurora Justice Stack policy parameters are now **DAO-controlled**. Policy changes go through on-chain governance, ensuring transparency and community control.

## Architecture

```
AuroraDAO → Governor → AuroraPolicyConfig.sol → Sync Script → Database → JusticeService
```

## Quick Setup

### 1. Initialize Default Policy

Before first DAO sync, initialize default policy:

```bash
python scripts/init_default_policy.py
```

This creates the default v1.0 policy in the database.

### 2. Deploy Smart Contracts

Deploy to your target chain:

1. **AuroraPolicyConfig.sol** - Policy parameters contract
2. **AuroraConstitution.sol** - Immutable constitution hash
3. **Governor Contract** - Governance mechanism

See `contracts/` directory for Solidity code.

### 3. First Sync from DAO

After deploying contracts:

```bash
export AURORA_RPC_URL=https://rpc.chain.xyz
export AURORA_POLICY_CONTRACT=0x...

python scripts/sync_dao_policy.py
```

This reads policy from on-chain contract and saves to database.

### 4. Verify

```bash
# Check active policy
curl http://localhost:8000/api/v1/justice/policy/current | jq
```

## Governance Workflow

### 1. Analyze Current State

```bash
# Get stats
curl http://localhost:8000/api/v1/admin/aurora/stats | jq

# Simulate current DAO policy
python scripts/simulate_aurora_policies.py \
  --users 2000 --days 90 --use-dao --summary
```

### 2. Test Proposed Changes

```bash
# Simulate with proposed parameters
python scripts/simulate_aurora_policies.py \
  --users 2000 --days 90 \
  --decay 2.0 --base-com 18 \
  --summary --output proposed_sim.json
```

### 3. Create DAO Proposal

Include in proposal:
- Current stats snapshot
- Simulation results (current vs proposed)
- Expected impact analysis
- IPFS links to simulation JSON

### 4. After Proposal Passes

```bash
# Sync new policy from chain
python scripts/sync_dao_policy.py

# Verify
curl http://localhost:8000/api/v1/justice/policy/current | jq
```

## Simulation Modes

### Mode 1: Use DAO Policy (On-Chain)

```bash
python scripts/simulate_aurora_policies.py \
  --users 2000 --days 90 \
  --use-dao \
  --summary
```

### Mode 2: Use Database Policy

```bash
python scripts/simulate_aurora_policies.py \
  --users 2000 --days 90 \
  --from-db \
  --summary
```

### Mode 3: Custom Parameters

```bash
python scripts/simulate_aurora_policies.py \
  --users 2000 --days 90 \
  --decay 2.0 \
  --base-com 18 \
  --threshold-probation 35 \
  --summary
```

## API Endpoints

### Get Current Policy

```bash
GET /api/v1/justice/policy/current
```

Response:
```json
{
  "version": "onchain-123456",
  "decay_per_day": 1,
  "base_eko": 10,
  "base_com": 15,
  "base_sys": 20,
  "base_trust": 25,
  "threshold_soft_flag": 20,
  "threshold_probation": 40,
  "threshold_restricted": 60,
  "threshold_lockdown": 80,
  "onchain_address": "0x...",
  "onchain_block": 123456,
  "synced_at": "2024-12-01T12:00:00Z"
}
```

## What Can DAO Change?

### ✅ DAO-Controlled
- CP decay rate
- CP base weights (EKO, COM, SYS, TRUST)
- Regime thresholds
- Enforcement matrix
- Severity multipliers

### ❌ DAO Cannot Change
- Constitution (data ethics, recall rights)
- Fundamental user rights
- Data ownership principles

## Files

- `contracts/AuroraPolicyConfig.sol` - Policy parameters contract
- `contracts/AuroraConstitution.sol` - Immutable constitution
- `app/justice/policy_models.py` - Database models
- `app/justice/policy_service.py` - Policy management service
- `scripts/sync_dao_policy.py` - Sync from on-chain
- `scripts/simulate_aurora_policies.py` - Policy simulation
- `scripts/init_default_policy.py` - Initialize default policy
- `docs/DAO_INTEGRATION.md` - Technical guide
- `docs/DAO_GOVERNANCE_FLOW.md` - Governance workflow

## Next Steps

1. Deploy contracts to target chain
2. Setup Governor contract
3. Initialize default policy
4. First sync from DAO
5. Create first governance proposal

Aurora Justice Stack is now **fully DAO-controlled**! 🎉

