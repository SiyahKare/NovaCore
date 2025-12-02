# Aurora Test Ritüeli

**Tek komutla dövülebilen devlet**: `./scripts/smoke_test.sh`

## 🎯 Test Ritüeli (State Machine)

### 1. Ortam Hazırlığı

```bash
# PostgreSQL başlat
docker-compose up -d postgres

# Virtual environment aktif et
source .venv/bin/activate

# Migration'ları uygula
alembic upgrade head
```

**Beklenen:** Migration'lar başarıyla uygulanır, tablolar oluşur.

### 2. API Başlat

```bash
uvicorn app.main:app --reload
```

**Beklenen:** API `http://localhost:8000` adresinde çalışır, `/health` endpoint'i `{"status":"ok"}` döner.

### 3. Hızlı Test (Consent Flow)

```bash
./scripts/test_consent_flow.sh
```

**Test eder:**
- ✅ Session creation
- ✅ Clause acceptance (8 clause)
- ✅ Redline acceptance
- ✅ Consent signing

**Beklenen:** Exit code 0, consent record oluşur.

### 4. Tam Test (Full Smoke Test)

```bash
./scripts/smoke_test.sh
```

**Test eder:**
- ✅ Health check
- ✅ Consent flow
- ✅ Privacy profile
- ✅ NovaScore
- ✅ Justice violations
- ✅ CP state
- ✅ Recall request
- ✅ Case file

**Beklenen:** Exit code 0, tüm endpoint'ler çalışır.

### 5. Enforcement Test (Kritik)

```bash
./scripts/test_enforcement.sh
```

**Test eder:**
- ✅ User'ı LOCKDOWN rejimine çıkarır
- ✅ Wallet transfer endpoint'ini çağırır
- ✅ HTTP 403 bekler (enforcement çalışıyor mu?)

**Beklenen:** Exit code 0, LOCKDOWN user transfer yapamaz.

### 6. Demo Users Seed

```bash
python scripts/seed_aurora_demo.py
```

**Oluşturur:**
- **AUR-SIGMA**: Clean citizen
- **AUR-TROLLER**: Problematic user
- **AUR-GHOST**: Privacy-conscious user

**Test:**
```bash
curl http://localhost:8000/justice/case/AUR-SIGMA
curl http://localhost:8000/justice/case/AUR-TROLLER
curl http://localhost:8000/justice/case/AUR-GHOST
```

## 🚨 CI/CD Integration

GitHub Actions otomatik olarak çalıştırır:

1. PostgreSQL service başlatır
2. Migration'ları uygular
3. API'yi başlatır
4. Smoke test çalıştırır
5. Enforcement test çalıştırır

**CI yeşil** → Aurora Devlet Motoru ayakta  
**CI kırmızı** → Migration, API veya protokol kırık

## 📊 Test Coverage

### Backend Tests

- [x] Consent flow (session → clauses → redline → sign)
- [x] Privacy profile creation
- [x] NovaScore calculation
- [x] Violation logging
- [x] CP calculation with decay
- [x] Regime mapping
- [x] Enforcement blocking
- [x] Recall request
- [x] Case file generation

### Integration Tests

- [x] Consent → Privacy Profile
- [x] Violation → CP → Regime
- [x] CP → NovaScore impact
- [x] Regime → Enforcement
- [x] Recall → NovaScore confidence

## 🔍 Debugging

### Test Fails?

1. **Check PostgreSQL:**
   ```bash
   docker ps | grep postgres
   docker exec novacore-postgres pg_isready -U novacore
   ```

2. **Check API:**
   ```bash
   curl http://localhost:8000/health
   ```

3. **Check Migrations:**
   ```bash
   alembic current
   alembic history
   ```

4. **Check Logs:**
   ```bash
   # API logs
   tail -f logs/novacore.log
   
   # PostgreSQL logs
   docker logs novacore-postgres
   ```

### Common Issues

**Port 8000 in use:**
```bash
lsof -i :8000
# Kill process or use different port
uvicorn app.main:app --reload --port 8001
```

**Migration errors:**
```bash
alembic downgrade -1  # Rollback
alembic upgrade head  # Retry
```

**Database connection:**
```bash
# Check DATABASE_URL in .env
# Check PostgreSQL is running
docker-compose ps postgres
```

## 📝 Adding New Tests

### New Endpoint Test

Add to `smoke_test.sh`:

```bash
echo -e "${YELLOW}📋 Test N: New Endpoint${NC}"
RESPONSE=$(api_call "GET" "/new-endpoint" "" "")
if echo "$RESPONSE" | grep -q "expected_field"; then
    print_test "New endpoint works" "PASS"
else
    print_test "New endpoint failed" "FAIL"
fi
```

### New Enforcement Test

Add to `test_enforcement.sh`:

```bash
echo -e "${YELLOW}📋 Step N: Test new action${NC}"
RESPONSE=$(api_call "POST" "/new-action" "{}" "-H \"Authorization: Bearer test-token\"")
HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
if [ "$HTTP_CODE" = "403" ]; then
    print_test "New action blocked for LOCKDOWN" "PASS"
else
    print_test "Enforcement failed" "FAIL"
fi
```

## ✅ Success Criteria

**Aurora Devlet Motoru ayakta** if:

- ✅ All smoke tests pass (exit code 0)
- ✅ Enforcement test blocks LOCKDOWN users
- ✅ CI pipeline green
- ✅ Demo users seed successfully
- ✅ Case file endpoint returns complete data

**Exit code = truth, not feelings.**

