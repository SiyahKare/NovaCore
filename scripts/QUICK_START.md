# Aurora State Network - Quick Start Guide

## 🚀 Start the System

### 1. Start PostgreSQL

```bash
docker-compose up -d postgres
```

Wait for PostgreSQL to be ready:
```bash
docker exec novacore-postgres pg_isready -U novacore
```

### 2. Run Migrations

```bash
source .venv/bin/activate
alembic upgrade head
```

### 3. Start the API

```bash
uvicorn app.main:app --reload
```

API will be available at: `http://localhost:8000`

## 🧪 Quick Test

### Test 1: Health Check

```bash
curl http://localhost:8000/health
```

Expected: `{"status":"ok"}`

### Test 2: Consent Flow

```bash
./scripts/test_consent_flow.sh
```

This will:
1. Create a consent session
2. Accept all 8 clauses
3. Accept redline
4. Sign the consent

### Test 3: Full Smoke Test

```bash
./scripts/smoke_test.sh
```

## 📊 Verify in Database

```bash
docker exec -it novacore-postgres psql -U novacore -d novacore

# Check tables
\dt

# Check consent records
SELECT * FROM consent_records LIMIT 5;

# Check privacy profiles
SELECT user_id, consent_level, recall_mode FROM user_privacy_profiles;

# Check CP state
SELECT user_id, cp_value, regime FROM justice_cp_state;
```

## 🔍 API Documentation

Once the API is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🛠️ Troubleshooting

### Port 8000 Already in Use

```bash
# Find what's using it
lsof -i :8000

# Use different port
uvicorn app.main:app --reload --port 8001
```

### PostgreSQL Not Running

```bash
# Check status
docker ps | grep postgres

# Start it
docker-compose up -d postgres

# Check logs
docker logs novacore-postgres
```

### Migration Errors

```bash
# Check current state
alembic current

# See migration history
alembic history

# Rollback if needed
alembic downgrade -1
```

## 📝 Next Steps

1. ✅ System is running
2. ✅ Consent flow works
3. ✅ Test with real auth tokens
4. ✅ Integrate with FlirtMarket/AuroraOS frontend
5. ✅ Add enforcement checks to critical endpoints

