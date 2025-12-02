# Aurora DAO Governance Flow

## Overview

Aurora Justice Stack policy parameters are controlled by AuroraDAO through on-chain governance. This document describes the complete governance workflow.

## Architecture

```
AuroraDAO → Governor Contract → AuroraPolicyConfig.sol → Sync Script → Database → JusticeService
```

## Governance Workflow

### 1. Policy Analysis Phase

**Current State:**
```bash
# Get current stats
curl http://localhost:8000/api/v1/admin/aurora/stats \
  -H "Authorization: Bearer <admin_token>"

# Get current policy
curl http://localhost:8000/api/v1/justice/policy/current
```

**Simulation:**
```bash
# Simulate with current DAO policy
python scripts/simulate_aurora_policies.py \
  --users 2000 \
  --days 90 \
  --use-dao \
  --summary \
  --output current_policy_sim.json
```

### 2. Proposal Preparation

**Test Proposed Changes:**
```bash
# Simulate with proposed parameters
python scripts/simulate_aurora_policies.py \
  --users 2000 \
  --days 90 \
  --decay 2.0 \
  --base-com 18 \
  --threshold-probation 35 \
  --summary \
  --output proposed_policy_sim.json
```

**Compare Results:**
- Lockdown rate: Current vs Proposed
- Average CP: Current vs Proposed
- Regime distribution: Current vs Proposed

### 3. Documentation

Update `docs/AURORA_POLICY_VERSIONS.md`:

```markdown
## Aurora Justice Policy v1.1 (Proposed)

### Proposed Changes
- Increase decay_per_day: 1 → 2
- Increase base_com: 15 → 18
- Lower probation threshold: 40 → 35

### Simulation Results
- Lockdown rate: 1.9% → 1.2%
- Average CP: 8.7 → 6.2
- NORMAL rate: 71.2% → 75.8%

### Rationale
- Faster user recovery from violations
- Earlier intervention for problematic behavior
- More balanced regime distribution
```

### 4. DAO Proposal

**Proposal Title:**
```
Aurora Justice Policy v1.1 - Increased Decay & Adjusted Thresholds
```

**Proposal Description:**
```markdown
## Summary
This proposal updates Aurora Justice Stack policy parameters to improve user experience and system balance.

## Current Policy (v1.0)
- Decay per day: 1
- Base COM: 15
- Probation threshold: 40

## Proposed Policy (v1.1)
- Decay per day: 2 (+100%)
- Base COM: 18 (+20%)
- Probation threshold: 35 (-12.5%)

## Simulation Results

### Current Policy (2000 users, 90 days)
- Lockdown rate: 1.9%
- Average CP: 8.7
- NORMAL rate: 71.2%

### Proposed Policy (2000 users, 90 days)
- Lockdown rate: 1.2% (-37%)
- Average CP: 6.2 (-29%)
- NORMAL rate: 75.8% (+6.5%)

## Expected Impact
- Faster recovery for users with violations
- Earlier intervention for problematic behavior
- More users in NORMAL regime
- Lower average CP across system

## Simulation Data
- Current: [IPFS link to current_policy_sim.json]
- Proposed: [IPFS link to proposed_policy_sim.json]

## Implementation
If passed, this proposal will:
1. Update `AuroraPolicyConfig` contract parameters
2. Trigger automatic sync to backend database
3. New policy will be active immediately after sync
```

### 5. Voting

DAO members vote on proposal:
- Token-weighted voting
- Quorum requirements
- Voting period (e.g., 7 days)

### 6. Execution

If proposal passes:
1. Governor executes transaction on `AuroraPolicyConfig`
2. Parameters updated on-chain
3. Events emitted

### 7. Sync

**Manual Sync:**
```bash
python scripts/sync_dao_policy.py \
  --rpc-url https://rpc.chain.xyz \
  --contract 0x...
```

**Auto-Sync (Future):**
- Event listener watches for `JusticeParamsUpdated` events
- Automatically triggers sync script
- New policy activated immediately

### 8. Verification

**Check Active Policy:**
```bash
curl http://localhost:8000/api/v1/justice/policy/current
```

**Verify in Database:**
```sql
SELECT * FROM justice_policy_params WHERE active = TRUE;
```

**Monitor Impact:**
```bash
# Watch stats over time
watch -n 60 'curl -s http://localhost:8000/api/v1/admin/aurora/stats | jq'
```

## Constitution Protection

**AuroraConstitution.sol** stores immutable constitution hash:
- Data Ethics & Transparency Contract
- Right to Recall
- Fundamental user rights

**DAO cannot change:**
- Constitution hash (immutable)
- Fundamental rights
- Data ownership principles

**DAO can change:**
- Policy parameters (CP weights, decay, thresholds)
- Enforcement matrix
- Regime definitions

## Best Practices

### 1. Always Simulate Before Proposing

```bash
# Test proposed changes
python scripts/simulate_aurora_policies.py \
  --users 2000 \
  --days 90 \
  --decay 2.0 \
  --summary
```

### 2. Document Changes

Always update `AURORA_POLICY_VERSIONS.md` with:
- Rationale
- Simulation results
- Expected impact
- Real usage observations (after deployment)

### 3. Monitor After Deployment

Track metrics for at least 2 weeks:
- Regime distribution changes
- Average CP trends
- Lockdown rate
- User feedback

### 4. Gradual Changes

Avoid drastic parameter changes:
- Incremental adjustments
- Test in smaller increments
- Monitor impact before next change

## Emergency Procedures

### Rollback Policy

If new policy causes issues:

1. **Immediate**: Create emergency proposal to revert
2. **Fast-track**: Reduce voting period if critical
3. **Sync**: Execute sync immediately after approval

### Manual Override (Emergency Only)

In extreme cases, admin can manually create policy version:

```python
from app.justice.policy_service import PolicyService

# Create emergency policy
await policy_service.create_policy_version(
    version="emergency-rollback-v1.0",
    decay_per_day=1,  # Revert to v1.0
    # ... other v1.0 parameters
    notes="Emergency rollback due to [reason]"
)
```

**Note:** This should only be used in critical situations and must be documented.

## Tools & Scripts

### Policy Management
- `scripts/init_default_policy.py` - Initialize default policy
- `scripts/sync_dao_policy.py` - Sync from on-chain contract
- `scripts/simulate_aurora_policies.py` - Policy simulation

### Monitoring
- `GET /api/v1/justice/policy/current` - Current policy
- `GET /api/v1/admin/aurora/stats` - System statistics

### Documentation
- `docs/AURORA_POLICY_VERSIONS.md` - Policy version history
- `docs/DAO_INTEGRATION.md` - Technical integration guide

## Example: Complete Governance Cycle

```bash
# 1. Analyze current state
curl http://localhost:8000/api/v1/admin/aurora/stats > current_stats.json

# 2. Simulate current policy
python scripts/simulate_aurora_policies.py \
  --use-dao --users 2000 --days 90 --summary > current_sim.txt

# 3. Test proposed changes
python scripts/simulate_aurora_policies.py \
  --decay 2.0 --base-com 18 --users 2000 --days 90 --summary > proposed_sim.txt

# 4. Compare results
diff current_sim.txt proposed_sim.txt

# 5. Create proposal (on DAO platform)
# Include simulation results, stats, rationale

# 6. After voting passes, sync
python scripts/sync_dao_policy.py \
  --rpc-url $AURORA_RPC_URL \
  --contract $AURORA_POLICY_CONTRACT

# 7. Verify
curl http://localhost:8000/api/v1/justice/policy/current | jq

# 8. Monitor
watch -n 300 'curl -s http://localhost:8000/api/v1/admin/aurora/stats | jq .regime_distribution'
```

## Next Steps

1. Deploy `AuroraPolicyConfig` to target chain
2. Setup Governor contract
3. Initialize default policy in database
4. First sync from on-chain contract
5. Setup auto-sync mechanism (event listener)
6. Create first governance proposal

