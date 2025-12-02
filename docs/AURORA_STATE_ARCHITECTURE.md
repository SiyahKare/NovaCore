# Aurora State Network - 3-Layer Architecture

## Overview

Aurora State Network implements a **3-layer state architecture** that separates mutable policy from immutable constitution, ensuring both flexibility and protection of fundamental rights.

---

## 🧬 Layer Architecture

### **Layer 1: Chain Law (Mutable Policy)**

**Purpose:** DAO-controlled policy parameters that can evolve based on governance.

**Components:**
- `AuroraPolicyConfig.sol` - Smart contract storing policy parameters
- `Governor Contract` - Controls access to policy changes
- `justice_policy_params` table - Database cache of on-chain policy

**What Can Change:**
- CP decay rate (`decayPerDay`)
- CP base weights (`baseEko`, `baseCom`, `baseSys`, `baseTrust`)
- Regime thresholds (`softFlag`, `probation`, `restricted`, `lockdown`)
- Enforcement matrix (regime × action permissions)
- Severity multipliers

**Change Process:**
1. DAO member creates proposal
2. Community votes
3. Governor executes transaction
4. Policy updated on-chain
5. Sync script updates database
6. JusticeService uses new policy immediately

**Files:**
- `contracts/AuroraPolicyConfig.sol`
- `app/justice/policy_models.py`
- `scripts/sync_dao_policy.py`

---

### **Layer 2: Constitution (Immutable Law)**

**Purpose:** Protect fundamental rights that cannot be changed, even by DAO.

**Components:**
- `AuroraConstitution.sol` - Stores constitution hash immutably
- Constitution document (IPFS or canonical text)
- SHA256 hash verification

**What Cannot Change:**
- Data Ethics & Transparency Contract (Articles 1-4)
- Right to Recall
- Redline principles
- "Aurora citizen owns their data" - fundamental principle
- User consent requirements

**Protection:**
- Constitution hash stored in immutable contract
- Cannot be modified, even by DAO
- New constitution requires new contract deployment (v2.0)

**Files:**
- `contracts/AuroraConstitution.sol`
- `app/consent/models.py` (consent records)
- `app/consent/router.py` (recall endpoints)

---

### **Layer 3: Execution Engine (Runtime)**

**Purpose:** Execute policy and constitution in real-time.

**Components:**
- `JusticeService` - Calculates CP using DAO policy
- `Enforcement Engine` - Blocks actions based on regime
- `NovaScore` - Integrates CP into reputation
- `ConsentService` - Manages user consent and recall

**How It Works:**
1. **Policy Application:**
   - `JusticeService._get_policy()` → Reads active policy from DB
   - `_cp_weight_for_violation()` → Uses DAO-controlled base weights
   - `_apply_decay()` → Uses DAO-controlled decay rate
   - `regime_for_cp()` → Uses DAO-controlled thresholds

2. **Enforcement:**
   - `check_action_allowed()` → Checks regime × action matrix
   - Blocks actions for restricted regimes
   - Returns structured 403 errors

3. **Constitution Protection:**
   - Consent flow cannot be bypassed
   - Recall rights always available
   - Data ownership principles enforced

**Files:**
- `app/justice/router.py` (JusticeService)
- `app/justice/enforcement.py`
- `app/justice/policy.py`
- `app/nova_score/router.py`

---

## 🔄 Data Flow

### Policy Change Flow

```
DAO Proposal → Vote → Governor Execute
    ↓
AuroraPolicyConfig.sol (on-chain)
    ↓
sync_dao_policy.py (sync script)
    ↓
justice_policy_params (database)
    ↓
JusticeService._get_policy() (runtime)
    ↓
CP Calculation / Regime Assignment
    ↓
Enforcement Check
```

### Constitution Verification Flow

```
Constitution Document
    ↓
SHA256 Hash
    ↓
AuroraConstitution.sol (immutable)
    ↓
UI Display: "Constitution v1.0, hash: 0x..."
    ↓
User can verify: verifyConstitution(document)
```

---

## 🛡️ Security Model

### Policy Layer Security

- **Access Control:** Only Governor can modify `AuroraPolicyConfig`
- **Governance:** All changes require proposal + vote
- **Audit Trail:** `PolicyChangeLog` tracks all changes
- **Versioning:** Policy versions tracked in database

### Constitution Layer Security

- **Immutability:** Hash stored in immutable contract
- **Verification:** `verifyConstitution()` allows document verification
- **Separation:** Constitution changes require new contract deployment

### Execution Layer Security

- **Policy Cache:** Cached for performance, refreshed on sync
- **Fallback:** Default policy if no active policy exists
- **Validation:** All policy parameters validated before use

---

## 📊 State Transitions

### Policy Version Transition

```
v1.0 (default) → v1.1 (DAO proposal) → v1.2 (DAO proposal) → ...
```

Each transition:
1. DAO proposal created
2. Community votes
3. On-chain update
4. Database sync
5. Runtime activation

### User State Transition

```
User Action → Violation → CP Increase → Regime Change → Enforcement
```

All using DAO-controlled parameters.

---

## 🎯 Design Principles

### 1. Separation of Concerns

- **Policy (Mutable):** DAO controls
- **Constitution (Immutable):** Protected
- **Execution (Runtime):** Applies both

### 2. Transparency

- All policy changes on-chain
- All changes logged
- All changes verifiable

### 3. Flexibility

- Policy can evolve
- Parameters tunable
- Simulation before deployment

### 4. Protection

- Constitution cannot be changed
- Fundamental rights protected
- User data ownership guaranteed

---

## 🔍 Verification

### Verify Policy Source

```bash
# Check active policy
curl http://localhost:8000/api/v1/justice/policy/current

# Verify on-chain
cast call $POLICY_CONTRACT "justiceParams()" --rpc-url $RPC_URL
```

### Verify Constitution

```bash
# Check constitution hash
cast call $CONSTITUTION_CONTRACT "constitutionHash()" --rpc-url $RPC_URL

# Verify document
cast call $CONSTITUTION_CONTRACT "verifyConstitution(string)" --rpc-url $RPC_URL
```

---

## 📈 Evolution Path

### Current State (v1.0)

- Default policy parameters
- Basic enforcement
- Constitution v1.0

### Future Enhancements

1. **Policy Automation:**
   - Event listener for auto-sync
   - Chainlink Automation integration

2. **Constitution v2.0:**
   - New contract deployment
   - Migration path for users
   - Backward compatibility

3. **Advanced Governance:**
   - Multi-sig support
   - Timelock for critical changes
   - Emergency pause mechanism

---

## 🎉 Conclusion

Aurora State Network's 3-layer architecture provides:

- **Flexibility:** Policy can evolve through DAO
- **Protection:** Constitution protects fundamental rights
- **Transparency:** All changes on-chain and verifiable
- **Accountability:** Full audit trail of policy changes

**Aurora = DAO-controlled, constitution-protected, execution-enforced digital state.** 🖤

