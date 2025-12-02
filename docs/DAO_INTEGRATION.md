# Aurora DAO Integration - Policy Governance

## Overview

Aurora Justice Stack policy parameters are now **DAO-controlled**. This means:
- Policy parameters (CP weights, decay, thresholds) can be changed by AuroraDAO governance
- Constitution layer (consent, recall rights) remains immutable
- All policy changes are tracked and auditable

## Architecture

### On-Chain Layer

**AuroraPolicyConfig.sol** - Smart contract that stores policy parameters:
- `decayPerDay`: CP decay rate
- `baseEko`, `baseCom`, `baseSys`, `baseTrust`: CP base weights
- `regimeThresholds`: SOFT_FLAG, PROBATION, RESTRICTED, LOCKDOWN thresholds
- `enforcement`: Regime x Action matrix

**Governor Contract** - Controls access to `AuroraPolicyConfig`:
- Only governance proposals can change parameters
- Voting mechanism (token-weighted, snapshot, etc.)

### Off-Chain Layer

**Database** - `justice_policy_params` table:
- Stores active policy parameters
- Tracks version history
- Links to on-chain transactions

**Sync Script** - `scripts/sync_dao_policy.py`:
- Reads from on-chain contract
- Writes to database
- Can be triggered manually or automatically

**Backend** - `PolicyService` + `JusticeService`:
- Reads active policy from database
- Uses DAO-controlled parameters for all calculations
- Caches policy for performance

## What Can DAO Change?

### ✅ DAO-Controlled (Policy Layer)

- `DECAY_PER_DAY`: CP decay rate
- CP base weights: `EKO`, `COM`, `SYS`, `TRUST`
- Regime thresholds: `SOFT_FLAG`, `PROBATION`, `RESTRICTED`, `LOCKDOWN`
- Enforcement matrix: Which regime blocks which actions
- Severity multipliers

### ❌ DAO Cannot Change (Constitution Layer)

- Data Ethics & Transparency Contract (Articles 1-4)
- Right to Recall
- Redline principles
- "Aurora citizen owns their data" - fundamental rights

## Usage

### 1. Sync Policy from DAO

```bash
# Manual sync
python scripts/sync_dao_policy.py \
  --rpc-url https://rpc.chain.xyz \
  --contract 0x...

# Or use environment variables
export AURORA_RPC_URL=https://rpc.chain.xyz
export AURORA_POLICY_CONTRACT=0x...
python scripts/sync_dao_policy.py

# Dry run (read but don't save)
python scripts/sync_dao_policy.py --dry-run
```

### 2. Get Current Policy

```bash
# API endpoint
GET /api/v1/justice/policy/current

# Response
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

### 3. Simulate with DAO Policy

```bash
# Use current database policy
python scripts/simulate_aurora_policies.py \
  --users 2000 \
  --days 90 \
  --from-db

# Or specify custom parameters (for testing proposals)
python scripts/simulate_aurora_policies.py \
  --users 2000 \
  --days 90 \
  --decay 2.0 \
  --base-com 18 \
  --threshold-probation 35
```

## Governance Workflow

### 1. Proposal Creation

DAO member creates proposal to change policy:
- Example: "Increase decay_per_day from 1 to 2"
- Includes:
  - Current stats snapshot
  - Simulation results (IPFS JSON link)
  - Expected impact analysis

### 2. Voting

DAO members vote on proposal:
- Token-weighted voting
- Quorum requirements
- Voting period

### 3. Execution

If proposal passes:
- Governor executes transaction on `AuroraPolicyConfig`
- Policy parameters updated on-chain
- Event emitted

### 4. Sync

Sync script reads new parameters:
- Can be triggered automatically (event listener)
- Or manually after proposal execution
- New policy version saved to database
- Old policy deactivated

### 5. Activation

Next request uses new policy:
- `JusticeService` reads active policy from database
- All CP calculations use new parameters
- Regime assignments use new thresholds

## Frontend Integration

### Display Current Policy

```tsx
// Show policy version and source
const policy = await fetch('/api/v1/justice/policy/current');
// Display: "Policy v1.2 – on-chain block #123456 (tx: 0xabc...)"
```

### Show DAO Governance Info

```tsx
// Regime banner with governance note
<RegimeBanner regime={cpState.regime} cp={cpState.cp_value}>
  <div className="text-xs text-slate-500 mt-2">
    Ceza rejimi AuroraDAO tarafından yönetilmektedir. 
    Politika değişiklikleri zincir üzerinde oylanır.
  </div>
</RegimeBanner>
```

## Security Considerations

### Access Control

- Only `Governor` contract can modify `AuroraPolicyConfig`
- No direct admin access to policy parameters
- All changes require governance proposal

### Constitution Protection

- Constitution layer is immutable
- Policy layer cannot override fundamental rights
- Separate contract for constitution hash (optional)

### Audit Trail

- All policy changes logged in `justice_policy_change_log`
- Links to on-chain transactions
- Version history tracked

## Smart Contract (Reference)

See `docs/AURORA_POLICY_CONFIG.sol` for complete contract implementation.

Key functions:
- `setJusticeParams()`: Update CP weights and decay
- `setRegimeThresholds()`: Update regime thresholds
- `setEnforcement()`: Update enforcement matrix
- `isAllowed()`: Check if action allowed for regime

## Next Steps

1. **Deploy Contract**: Deploy `AuroraPolicyConfig` to target chain
2. **Setup Governor**: Configure governance mechanism
3. **Initial Sync**: Run sync script to populate database
4. **Auto-Sync**: Setup event listener or cron job
5. **Frontend**: Add policy display to admin panel
6. **Documentation**: Add governance proposal templates

## Testing

```bash
# Test sync script (dry run)
python scripts/sync_dao_policy.py --dry-run

# Test simulation with DB policy
python scripts/simulate_aurora_policies.py --from-db --users 100 --days 30

# Test API endpoint
curl http://localhost:8000/api/v1/justice/policy/current
```

