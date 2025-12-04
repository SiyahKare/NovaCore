# Aurora Justice DAO Activation Checklist

## 🎯 Final Activation Steps

Bu checklist tamamlandığında, Aurora Justice Stack **tam DAO-controlled devlet** moduna geçer.

---

## ✅ Checklist

### 1️⃣ Database Migration

```bash
# Activate virtual environment
source .venv/bin/activate

# Generate migration for policy tables
alembic revision --autogenerate -m "Add justice policy params tables"

# Apply migration
alembic upgrade head

# Verify tables exist
psql $DATABASE_URL -c "SELECT * FROM justice_policy_params LIMIT 1;"
psql $DATABASE_URL -c "SELECT * FROM justice_policy_change_log LIMIT 1;"
```

**Expected:** Tables created successfully.

---

### 2️⃣ Initialize Default Policy (v1.0)

```bash
# Seed initial policy
python scripts/init_default_policy.py

# Verify
curl http://localhost:8000/api/v1/justice/policy/current | jq
```

**Expected Response:**
```json
{
  "version": "v1.0",
  "decay_per_day": 1,
  "base_eko": 10,
  "base_com": 15,
  "base_sys": 20,
  "base_trust": 25,
  "threshold_soft_flag": 20,
  "threshold_probation": 40,
  "threshold_restricted": 60,
  "threshold_lockdown": 80,
  "active": true
}
```

---

### 3️⃣ Smart Contract Deployment

**Deploy to target chain:**

1. **AuroraPolicyConfig.sol**
   ```solidity
   // Deploy with Governor address
   constructor(address _governor)
   ```

2. **AuroraConstitution.sol**
   ```solidity
   // Deploy with constitution hash
   constructor(bytes32 _hash)
   ```

3. **Governor Setup**
   - Deploy Governor contract
   - Deploy Timelock (optional)
   - Set Governor as `AuroraPolicyConfig.governor`

**Verify:**
```bash
# Check contract on chain
cast call 0xPolicyConfigAddress "governor()" --rpc-url $RPC_URL
```

---

### 4️⃣ First Sync from DAO

```bash
# Set environment variables
export AURORA_RPC_URL=https://rpc.chain.xyz
export AURORA_POLICY_CONTRACT=0xYourPolicyConfigAddress

# Sync from chain
python scripts/sync_dao_policy.py

# Verify
curl http://localhost:8000/api/v1/justice/policy/current | jq
```

**Expected:** Policy version should show `onchain-<block_number>`.

---

### 5️⃣ Test Enforcement with DAO Policy

**Create test violation:**
```bash
POST /api/v1/justice/violations
{
  "user_id": "test-user",
  "category": "COM",
  "code": "COM_TOXIC",
  "severity": 3
}
```

**Check CP and regime:**
```bash
GET /api/v1/justice/cp/test-user
```

**Verify:**
- CP calculated using DAO-controlled base weights
- Regime calculated using DAO-controlled thresholds
- Decay applied using DAO-controlled decay rate

---

### 6️⃣ Test Simulation Modes

**Mode 1: From Database**
```bash
python scripts/simulate_aurora_policies.py \
  --users 2000 --days 90 --from-db --summary
```

**Mode 2: From On-Chain**
```bash
python scripts/simulate_aurora_policies.py \
  --users 2000 --days 90 --use-dao --summary
```

**Mode 3: Custom Parameters**
```bash
python scripts/simulate_aurora_policies.py \
  --users 2000 --days 90 \
  --decay 2.0 --base-com 18 --summary
```

**Expected:** All three modes work correctly.

---

### 7️⃣ Run Integration Test

```bash
# Full integration test
./scripts/test_dao_integration.sh
```

**Expected:** All tests pass.

---

## 🧬 Aurora's 3-Layer State Architecture

### Layer 1: Chain Law (Mutable Policy)
- **AuroraPolicyConfig.sol** - DAO-controlled parameters
- Can be changed by governance proposals
- Synced to database via `sync_dao_policy.py`

### Layer 2: Constitution (Immutable Law)
- **AuroraConstitution.sol** - Constitution hash
- Cannot be changed, even by DAO
- Protects fundamental rights (data ownership, recall)

### Layer 3: Execution Engine
- **JusticeService** - Calculates CP using DAO policy
- **Enforcement Engine** - Blocks actions based on regime
- **NovaScore** - Integrates CP into reputation score

---

## 🚀 Post-Activation

### Auto-Sync Setup

**Option 1: Cron Job**
```bash
# Add to crontab
*/10 * * * * cd /path/to/novacore && python scripts/sync_dao_policy.py --rpc-url $RPC_URL --contract $CONTRACT
```

**Option 2: Event Listener (Advanced)**
- Watch for `JusticeParamsUpdated` events
- Automatically trigger sync on policy changes

### Monitoring

**Track Policy Changes:**
```sql
SELECT * FROM justice_policy_change_log 
ORDER BY created_at DESC 
LIMIT 10;
```

**Monitor Impact:**
```bash
# Watch stats over time
watch -n 60 'curl -s http://localhost:8000/api/v1/admin/aurora/stats | jq .regime_distribution'
```

---

## ✅ Activation Complete

When all checklist items are complete:

1. ✅ Database has policy tables
2. ✅ Default v1.0 policy seeded
3. ✅ Smart contracts deployed
4. ✅ First sync successful
5. ✅ Enforcement uses DAO policy
6. ✅ All simulation modes work
7. ✅ Integration tests pass

**Aurora Justice Stack is now a fully DAO-controlled digital state!** 🎉

---

## Next Steps

1. **Create First Governance Proposal**
   - Test policy change
   - Include simulation results
   - Vote and execute

2. **Setup Auto-Sync**
   - Cron job or event listener
   - Monitor sync logs

3. **Build Governance UI**
   - Proposal creation interface
   - Voting dashboard
   - Policy history viewer

4. **Constitution IPFS**
   - Upload constitution to IPFS
   - Link hash in AuroraConstitution contract

---

## Troubleshooting

### Policy Not Found
```bash
# Re-initialize default policy
python scripts/init_default_policy.py
```

### Sync Fails
```bash
# Check RPC connection
curl $AURORA_RPC_URL

# Check contract address
cast code $AURORA_POLICY_CONTRACT --rpc-url $RPC_URL
```

### Enforcement Not Working
```bash
# Verify active policy
curl http://localhost:8000/api/v1/justice/policy/current

# Check if policy is being used
# Look for policy version in logs
```

---

**SiyahKare Republic + NovaCore = DAO-controlled, versioned, simulated, enforced digital state.** 🖤

