# NovaCore + Aurora Justice - Final Activation Checklist (v1.0)

Bu checklist NovaCore + Aurora Justice'i **tam yetkilendirilmiş**, **DAO-controlled**, **enforced**, **simüle edilebilir**, **vatandaş-kabul edebilir** hale getirir.

## 🚀 Quick Start

**Tek komutla tüm aktivasyon:**

```bash
./scripts/activate_aurora_state.sh
```

## 📋 Manual Checklist

### 1. DB & Migration Setup

#### 1.1 Environment Kontrolü

```bash
cp .env.example .env
# Update .env with your database credentials
```

**Varsayılan port:**
- NovaCore Postgres → **5433** (çakışma çözülmüştü)

#### 1.2 Docker Başlat

```bash
docker-compose up -d postgres
```

#### 1.3 Migration Çalıştır

```bash
source .venv/bin/activate
alembic upgrade head
```

#### Verify

```bash
docker exec -it novacore-postgres psql -U novacore -d novacore -c "\dt"
```

**Görmen gereken kritik tablolar:**
- `consent_sessions`
- `consent_records`
- `user_privacy_profiles`
- `justice_policy_params`
- `justice_policy_change_log`
- `justice_violations`
- `justice_cp_state`

---

### 2. Default Policy Seed (DAO v1.0)

#### 2.1 Varsayılan Policy Yükle

```bash
python scripts/init_default_policy.py
```

Bu:
- v1.0 Aurora Policy'yi DB'ye kaydeder
- PolicyChangeLog'a ilk "genesis" kaydını düşer

#### Verify

```bash
docker exec -it novacore-postgres psql -U novacore -d novacore -c "SELECT * FROM justice_policy_params;"
docker exec -it novacore-postgres psql -U novacore -d novacore -c "SELECT * FROM justice_policy_change_log;"
```

---

### 3. DAO Smart Contract Bağlantısı

#### 3.1 Local / Testnet Deploy

Deploy contracts:
- `contracts/AuroraPolicyConfig.sol`
- `contracts/AuroraConstitution.sol`

Deploy → contract address alınır.

#### 3.2 Sync Script'i Çalıştır (Dry-Run)

```bash
python scripts/sync_dao_policy.py \
  --rpc-url https://rpc.testnet \
  --contract 0x... \
  --dry-run
```

#### Verify

Dry-run'da sadece konsola yazmalı, DB'ye yazmamalı.

#### 3.3 Gerçek Senkron

```bash
python scripts/sync_dao_policy.py \
  --rpc-url https://rpc.testnet \
  --contract 0x...
```

---

### 4. Demo Citizen Seed

#### 4.1 Demo User'ları Yükle

```bash
python scripts/seed_aurora_demo.py
```

Bu oluşturur:
- `AUR-SIGMA` - Clean citizen (CP 0, FULL consent)
- `AUR-TROLLER` - Problematic user (CP ~50, PROBATION regime)
- `AUR-GHOST` - Privacy-conscious (recall requested, low confidence)

#### Verify

```bash
docker exec -it novacore-postgres psql -U novacore -d novacore -c "SELECT user_id, cp_value, regime FROM justice_cp_state WHERE user_id LIKE 'AUR-%';"
```

---

### 5. Core System Testleri

#### 5.1 Consent Flow Test

```bash
./scripts/test_consent_flow.sh
```

**Beklenen:**
- 8 clause accepted
- Redline ok
- Consent record created

#### 5.2 Full Smoke Test

```bash
./scripts/smoke_test.sh
```

**Kapsam:**
- `/health`
- consent → profile → nova-score
- violation → CP değişimi
- recall → confidence drop
- ombudsman → case file

#### 5.3 Enforcement Test (ÇOK KRİTİK)

```bash
./scripts/test_enforcement.sh
```

**Beklenen:**
- CP 80+ → `LOCKDOWN`
- `POST /wallet/transfer` → **403 Aurora Enforcement Error**

#### 5.4 DAO Integration Test

```bash
./scripts/test_dao_integration.sh
```

**Beklenen:**
- On-chain policy → DB'ye doğru şekilde yazılır
- Regime thresholds güncellenir

---

### 6. Frontend Activation (Shared Libraries)

Zaten hazırladık:

#### `packages/aurora-ui`

**Components:**
- RegimeBadge
- RegimeBanner
- NovaScoreCard
- EnforcementErrorModal
- ConsentFlow
- AppealForm
- RecallRequest
- PolicyBreakdown
- DAOChangeLog
- CPTrendGraph

#### `packages/aurora-hooks`

**Hooks:**
- useNovaScore
- useJustice
- usePolicy
- useEnforcementError
- useConsentFlow
- useAuroraAPI

Bu noktada **Citizen Portal** kurulumuna geçilmeye hazır.

---

### 7. CI/CD — Final Activation via GitHub Actions

Aurora'nın gerçek kilit taşı:

#### GitHub Actions Pipeline

**Workflow:** `.github/workflows/aurora-smoke-test.yml`

**Steps:**
1. Postgres service
2. Alembic upgrade
3. API startup
4. Consent flow test
5. Smoke test
6. Enforcement test
7. DAO integration test

**Tümünün yeşil olması Aurora devletinin açılış mührüdür.**

---

### 8. Tek Komutluk Aktivasyon Script

Her şeyi tek komutla yapmak için:

```bash
./scripts/activate_aurora_state.sh
```

**Bu script sırasıyla:**
1. ✅ Migration
2. ✅ Default policy
3. ✅ Demo users
4. ✅ DAO sync (dry-run)
5. ✅ DAO sync (real)
6. ✅ Smoke test
7. ✅ Enforcement test
8. ✅ DAO integration test

**Environment Variables:**

```bash
# Skip tests (if API not running)
export SKIP_TESTS=true

# Skip DAO sync (if contract not deployed)
export SKIP_DAO_SYNC=true

# DAO configuration (if syncing)
export AURORA_RPC_URL=https://rpc.testnet
export AURORA_POLICY_CONTRACT=0x...
```

---

## 🔥 SON ADIM → "Aurora State Opening"

Bunu çalıştırınca devlet resmen **aktif** kabul edilir:

```bash
./scripts/activate_aurora_state.sh
```

**Son satırdaki mesaj:**

```
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║        AURORA STATE IS NOW LIVE                            ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
```

---

## ✅ Verification Checklist

After activation, verify:

- [ ] Database tables created
- [ ] Default policy v1.0 active
- [ ] Demo users seeded
- [ ] API responds to `/health`
- [ ] Consent flow works
- [ ] NovaScore calculation works
- [ ] CP calculation works
- [ ] Enforcement blocks LOCKDOWN users
- [ ] DAO policy sync works (if configured)
- [ ] Frontend libraries ready

---

## 🚨 Troubleshooting

### Migration Fails

```bash
# Check database connection
docker exec -it novacore-postgres psql -U novacore -d novacore -c "SELECT 1;"

# Check Alembic version
alembic current
```

### Policy Not Found

```bash
# Re-initialize
python scripts/init_default_policy.py
```

### API Not Starting

```bash
# Check logs
uvicorn app.main:app --reload --log-level debug

# Check port
lsof -i :8000
```

### Tests Failing

```bash
# Run individual tests
./scripts/test_consent_flow.sh
./scripts/smoke_test.sh
./scripts/test_enforcement.sh
```

---

## 📚 Next Steps

After activation:

1. **Start API:**
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Build Citizen Portal:**
   ```bash
   cd apps/citizen-portal
   npm install
   npm run dev
   ```

3. **Deploy Contracts:**
   - Deploy `AuroraPolicyConfig.sol`
   - Deploy `AuroraConstitution.sol`
   - Sync policy: `python scripts/sync_dao_policy.py`

4. **Setup CI/CD:**
   - Push to GitHub
   - Verify Actions workflow passes

---

**SiyahKare Republic + NovaCore = DAO-controlled, versioned, simulated, enforced digital state.** 🖤

