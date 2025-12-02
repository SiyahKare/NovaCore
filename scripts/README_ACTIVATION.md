# Aurora State Activation Scripts

## Quick Reference

### Complete Activation

```bash
# One command to activate everything
./scripts/activate_aurora_state.sh
```

### Individual Steps

```bash
# 1. Database & Migration
docker-compose up -d postgres
alembic upgrade head

# 2. Default Policy
python scripts/init_default_policy.py

# 3. DAO Sync (after contract deployment)
python scripts/sync_dao_policy.py --rpc-url <RPC> --contract <ADDRESS>

# 4. Demo Users
python scripts/seed_aurora_demo.py

# 5. Tests
./scripts/test_consent_flow.sh
./scripts/smoke_test.sh
./scripts/test_enforcement.sh
./scripts/test_dao_integration.sh
```

## Scripts

### `activate_aurora_state.sh`

**Complete activation script** - Runs all steps automatically.

**Usage:**
```bash
./scripts/activate_aurora_state.sh
```

**Environment Variables:**
- `SKIP_TESTS=true` - Skip test execution
- `SKIP_DAO_SYNC=true` - Skip DAO contract sync
- `AURORA_RPC_URL` - RPC URL for DAO sync
- `AURORA_POLICY_CONTRACT` - Contract address for DAO sync

**What it does:**
1. ✅ Checks prerequisites
2. ✅ Sets up database & migrations
3. ✅ Seeds default policy v1.0
4. ✅ Syncs from DAO contract (if configured)
5. ✅ Seeds demo users
6. ✅ Runs all tests
7. ✅ Verifies frontend libraries
8. ✅ Checks CI/CD setup
9. ✅ Final verification

### `activate_aurora_dao.sh`

**Legacy DAO activation** - Basic DAO setup only.

### `init_default_policy.py`

**Initialize default policy** - Creates v1.0 policy in database.

### `sync_dao_policy.py`

**Sync from DAO** - Fetches policy from on-chain contract.

### `seed_aurora_demo.py`

**Seed demo users** - Creates AUR-SIGMA, AUR-TROLLER, AUR-GHOST.

## Test Scripts

- `test_consent_flow.sh` - Consent flow test
- `smoke_test.sh` - Full system smoke test
- `test_enforcement.sh` - Enforcement mechanism test
- `test_dao_integration.sh` - DAO integration test

## Troubleshooting

### Script Fails

1. Check prerequisites:
   - Python 3 installed
   - Docker installed
   - Virtual environment active

2. Check database:
   ```bash
   docker ps | grep postgres
   docker exec novacore-postgres psql -U novacore -d novacore -c "SELECT 1;"
   ```

3. Check API:
   ```bash
   curl http://localhost:8000/health
   ```

### Skip Steps

```bash
# Skip tests
SKIP_TESTS=true ./scripts/activate_aurora_state.sh

# Skip DAO sync
SKIP_DAO_SYNC=true ./scripts/activate_aurora_state.sh

# Both
SKIP_TESTS=true SKIP_DAO_SYNC=true ./scripts/activate_aurora_state.sh
```

## Verification

After activation, verify:

```bash
# Check policy
curl http://localhost:8000/api/v1/justice/policy/current

# Check demo users
docker exec novacore-postgres psql -U novacore -d novacore -c "SELECT user_id, cp_value, regime FROM justice_cp_state WHERE user_id LIKE 'AUR-%';"

# Check tables
docker exec novacore-postgres psql -U novacore -d novacore -c "\dt"
```

## Next Steps

After successful activation:

1. Start API: `uvicorn app.main:app --reload`
2. Build Citizen Portal: `cd apps/citizen-portal && npm run dev`
3. Deploy contracts: See `contracts/` directory
4. Setup CI/CD: See `.github/workflows/`

