# Aurora Justice Stack v2.0 - Complete Integration Guide

## 🎯 Overview

Aurora Justice Stack v2.0 is a complete governance engine that enforces behavioral rules through CP (Ceza Puanı) and regime-based restrictions.

## Architecture

```
Violation → CP → Regime → Enforcement → NovaScore → Case File
```

### Components

1. **Violation Logging**: Record user violations (EKO, COM, SYS, TRUST)
2. **CP Calculation**: Automatic CP calculation with decay (1 CP/day)
3. **Regime Mapping**: CP → Regime (NORMAL, SOFT_FLAG, PROBATION, RESTRICTED, LOCKDOWN)
4. **Enforcement**: Policy-based action restrictions
5. **NovaScore Integration**: CP affects reputation score
6. **Case File**: Complete user status for operators

## Regime System

| CP Range | Regime | Description |
|----------|--------|-------------|
| 0-19 | NORMAL | Full rights |
| 20-39 | SOFT_FLAG | Warning mode, light restrictions |
| 40-59 | PROBATION | Strict monitoring, some limitations |
| 60-79 | RESTRICTED | Heavy limits, economy/message restrictions |
| 80+ | LOCKDOWN | Account locked, manual review required |

## Enforcement Integration

### Example: Wallet Transfer

```python
from app.justice.router import get_justice_service, JusticeService
from app.justice.enforcement import check_action_allowed
from app.justice.policy import Action

@router.post("/transfer")
async def transfer(
    request: TransferRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    # Aurora Justice Enforcement Check
    justice_service = JusticeService(session)
    cp_state = await justice_service.get_cp(str(current_user.id))
    check_action_allowed(cp_state, Action.WITHDRAW_FUNDS)
    
    # Normal flow continues...
    service = WalletService(session)
    return await service.transfer(current_user.id, request)
```

### Available Actions

- `Action.SEND_MESSAGE` - Send messages
- `Action.START_CALL` - Start calls
- `Action.CREATE_FLIRT` - Create flirts
- `Action.WITHDRAW_FUNDS` - Withdraw funds
- `Action.TOPUP_WALLET` - Top up wallet
- `Action.ACCESS_AURORA` - Access Aurora AI

### Policy Matrix

| Regime | SEND_MESSAGE | START_CALL | CREATE_FLIRT | WITHDRAW | TOPUP | ACCESS_AURORA |
|--------|--------------|------------|--------------|----------|-------|---------------|
| NORMAL | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| SOFT_FLAG | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| PROBATION | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| RESTRICTED | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ |
| LOCKDOWN | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

## API Endpoints

### Justice

- `POST /justice/violations` - Create violation
- `GET /justice/cp/me` - Get my CP state
- `GET /justice/cp/{user_id}` - Get user CP (admin)
- `GET /justice/case/{user_id}` - Get case file (ombudsman)

### Consent

- `POST /consent/session` - Create consent session
- `POST /consent/clauses` - Accept clause
- `POST /consent/redline` - Accept redline
- `POST /consent/sign` - Sign consent
- `GET /consent/profile/me` - Get privacy profile
- `POST /consent/recall` - Request recall
- `GET /consent/recall/status` - Get recall status

### NovaScore

- `GET /nova-score/me` - Get my NovaScore

## Demo Users

Use the seed script to create demo users:

```bash
python scripts/seed_aurora_demo.py
```

This creates:
- **AUR-SIGMA**: Clean citizen (CP 0, FULL consent, high NovaScore)
- **AUR-TROLLER**: Problematic user (violations, PROBATION/RESTRICTED regime)
- **AUR-GHOST**: Privacy-conscious user (recall requested, low confidence NovaScore)

## Testing

### Quick Test

```bash
# Consent flow (no auth required)
./scripts/test_consent_flow.sh

# Full smoke test
./scripts/smoke_test.sh
```

### Manual Testing

1. **Create violation**:
```bash
curl -X POST http://localhost:8000/justice/violations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "user_id": "AUR-TEST-1",
    "category": "COM",
    "code": "COM_TOXIC",
    "severity": 3,
    "source": "dev-test"
  }'
```

2. **Check CP**:
```bash
curl -X GET http://localhost:8000/justice/cp/me \
  -H "Authorization: Bearer TOKEN"
```

3. **Get case file**:
```bash
curl -X GET http://localhost:8000/justice/case/AUR-TEST-1 \
  -H "Authorization: Bearer TOKEN"
```

## Integration Checklist

### Backend

- [x] Violation logging
- [x] CP calculation with decay
- [x] Regime mapping
- [x] Enforcement policy matrix
- [x] NovaScore integration
- [x] Case file endpoint
- [x] Wallet transfer enforcement (example)
- [ ] Message sending enforcement
- [ ] Call starting enforcement
- [ ] Flirt creation enforcement

### Frontend

- [ ] Regime badge component
- [ ] CP indicator
- [ ] Violation history table
- [ ] Case file display
- [ ] Enforcement error messages
- [ ] Ombudsman panel

## Files

- `app/justice/models.py` - ViolationLog, UserCpState models
- `app/justice/schemas.py` - Request/Response schemas
- `app/justice/router.py` - JusticeService and endpoints
- `app/justice/policy.py` - Regime mapping and policy matrix
- `app/justice/enforcement.py` - Enforcement helper functions
- `app/justice/examples.py` - Integration examples
- `scripts/seed_aurora_demo.py` - Demo user seed script
- `docs/OMBUDSMAN_INTEGRATION.md` - Ombudsman integration guide

## Next Steps

1. Add enforcement to critical endpoints (messages, calls, flirts)
2. Build frontend components for regime display
3. Implement role-based access for case file endpoint
4. Add appeal system
5. Create operator console UI

