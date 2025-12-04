# NovaCore - Testing Guide

## Smoke Test Scripts

### 1. Full Smoke Test (`smoke_test.sh`)

Comprehensive test of all Aurora modules:

```bash
./scripts/smoke_test.sh
```

Tests:
- ✅ Health check
- ✅ Consent session creation
- ✅ Clause acceptance
- ✅ Redline acceptance
- ✅ Consent signing
- ✅ Privacy profile (requires auth)
- ✅ NovaScore (requires auth)
- ✅ Justice violation creation (requires auth)
- ✅ CP state check (requires auth)
- ✅ Recall request (requires auth)
- ✅ Case file (requires auth)

**Note:** Some endpoints require authentication. To test with auth:

```bash
export AUTH_TOKEN="your-jwt-token"
./scripts/smoke_test.sh
```

### 2. Consent Flow Test (`test_consent_flow.sh`)

Quick test of consent signing flow (no auth required):

```bash
./scripts/test_consent_flow.sh
```

This tests:
- Session creation
- Clause acceptance (all 8 clauses)
- Redline acceptance
- Consent signing

## Manual Testing

### 1. Start the API

```bash
uvicorn app.main:app --reload
```

### 2. Health Check

```bash
curl http://localhost:8000/health
```

Expected: `{"status":"ok"}`

### 3. Consent Flow

```bash
# Create session
SESSION_ID=$(curl -s -X POST http://localhost:8000/consent/session \
  -H "Content-Type: application/json" \
  -d '{"user_id":"AUR-TEST-1","client_fingerprint":"dev-01"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['session_id'])")

# Accept clauses
for c in "1.1" "1.2" "2.1" "2.2" "3.1" "3.2" "4.1" "4.2"; do
  curl -X POST http://localhost:8000/consent/clauses \
    -H "Content-Type: application/json" \
    -d "{\"session_id\":\"$SESSION_ID\",\"clause_id\":\"$c\",\"status\":\"ACCEPTED\",\"comprehension_passed\":true}"
done

# Accept redline
curl -X POST http://localhost:8000/consent/redline \
  -H "Content-Type: application/json" \
  -d "{\"session_id\":\"$SESSION_ID\",\"redline_status\":\"ACCEPTED\",\"user_note_hash\":null}"

# Sign
curl -X POST http://localhost:8000/consent/sign \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\":\"$SESSION_ID\",
    \"user_id\":\"AUR-TEST-1\",
    \"contract_version\":\"Aurora-DataEthics-v1.0\",
    \"clauses_accepted\":[\"1.1\",\"1.2\",\"2.1\",\"2.2\",\"3.1\",\"3.2\",\"4.1\",\"4.2\"],
    \"redline_status\":\"ACCEPTED\",
    \"signature_text\":\"Test User\",
    \"client_fingerprint\":\"dev-01\"
  }"
```

### 4. Justice Violation

```bash
curl -X POST http://localhost:8000/justice/violations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "user_id": "AUR-TEST-1",
    "category": "COM",
    "code": "COM_TOXIC",
    "severity": 3,
    "source": "dev-test",
    "context": {"message_id": "123", "reason": "hate_speech"}
  }'
```

### 5. Check CP State

```bash
curl -X GET http://localhost:8000/justice/cp/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 6. NovaScore

```bash
curl -X GET http://localhost:8000/nova-score/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 7. Recall Request

```bash
curl -X POST http://localhost:8000/consent/recall \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "mode": "FULL_EXCLUDE",
    "reason": "Aurora eğitim setinden çıkmak istiyorum."
  }'
```

### 8. Case File (Ombudsman)

```bash
curl -X GET http://localhost:8000/justice/case/AUR-TEST-1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Database Verification

After running tests, verify data in PostgreSQL:

```bash
docker exec -it novacore-postgres psql -U novacore -d novacore

# Check consent records
SELECT * FROM consent_records LIMIT 5;

# Check privacy profiles
SELECT user_id, consent_level, recall_mode FROM user_privacy_profiles;

# Check violations
SELECT user_id, category, code, cp_delta FROM justice_violations;

# Check CP state
SELECT user_id, cp_value, regime FROM justice_cp_state;
```

## Expected Results

### After Consent Signing:
- ✅ `consent_records` table has new record
- ✅ `user_privacy_profiles` table has profile with `consent_level = "FULL"`
- ✅ `data_usage_policy` is populated

### After Violation:
- ✅ `justice_violations` table has new violation
- ✅ `justice_cp_state` has `cp_value > 0`
- ✅ `regime` is calculated based on CP (NORMAL/SOFT_FLAG/PROBATION/RESTRICTED/LOCKDOWN)

### After Recall:
- ✅ `user_privacy_profiles.recall_mode` is set
- ✅ `user_privacy_profiles.recall_requested_at` is set
- ✅ NovaScore `confidence_overall` decreases
- ✅ NovaScore `explanation` mentions recall

## Troubleshooting

### Port Already in Use
If port 8000 is in use:
```bash
# Find process
lsof -i :8000

# Kill process or use different port
uvicorn app.main:app --reload --port 8001
```

### Database Connection Error
```bash
# Check PostgreSQL is running
docker ps | grep novacore-postgres

# Check connection
docker exec novacore-postgres pg_isready -U novacore
```

### Migration Issues
```bash
# Check current migration
alembic current

# Apply migrations
alembic upgrade head

# Check migration history
alembic history
```

