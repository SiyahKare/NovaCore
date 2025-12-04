# NovaCore API Documentation

**Version:** 0.4.0  
**Base URL:** `http://localhost:8000` (dev) | `https://api.novacore.siyahkare.com` (prod)  
**API Version:** `/api/v1`

## Table of Contents

1. [Authentication](#authentication)
2. [Identity & Auth](#identity--auth)
3. [Wallet](#wallet)
4. [XP & Loyalty](#xp--loyalty)
5. [NovaCredit](#novacredit)
6. [Agency](#agency)
7. [Events](#events)
8. [Treasury](#treasury)
9. [Consent](#consent)
10. [Justice](#justice)
11. [NovaScore](#novascore)
12. [Telegram Gateway](#telegram-gateway)
13. [Telemetry](#telemetry)
14. [Admin](#admin)
15. [FlirtMarket (Example)](#flirtmarket-example)

---

## Authentication

Most endpoints require JWT authentication via `Authorization: Bearer <token>` header.

### Getting a Token

**Email Registration:**
```bash
POST /api/v1/identity/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "display_name": "John Doe"
}
```

**Email Login:**
```bash
POST /api/v1/identity/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Telegram Auth:**
```bash
POST /api/v1/identity/telegram/auth
Content-Type: application/json

{
  "init_data": "query_id=...&user=..."
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 604800,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "display_name": "John Doe",
    "telegram_id": 123456789,
    "is_admin": false
  }
}
```

---

## Identity & Auth

### Register (Email)

**Endpoint:** `POST /api/v1/identity/register`

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "display_name": "John Doe"  // Optional
}
```

**Response:** `AuthResponse` (see Authentication section)

---

### Login (Email)

**Endpoint:** `POST /api/v1/identity/login`

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:** `AuthResponse`

---

### Telegram Auth

**Endpoint:** `POST /api/v1/identity/telegram/auth`

**Request:**
```json
{
  "init_data": "query_id=...&user=..."
}
```

**Response:** `AuthResponse`

---

### Get Current User

**Endpoint:** `GET /api/v1/identity/me`  
**Auth:** Required

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "display_name": "John Doe",
  "username": "johndoe",
  "telegram_id": 123456789,
  "is_admin": false,
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

### Link Telegram Account

**Endpoint:** `POST /api/v1/identity/telegram/link`  
**Auth:** Required

**Query Parameters:**
- `telegram_user_id` (int, required)
- `telegram_username` (string, optional)
- `telegram_first_name` (string, optional)
- `telegram_last_name` (string, optional)

**Response:** `UserResponse`

---

### Get Telegram Status

**Endpoint:** `GET /api/v1/identity/telegram/status`  
**Auth:** Required

**Response:**
```json
{
  "is_linked": true,
  "telegram_user_id": 123456789,
  "telegram_username": "johndoe",
  "telegram_display_name": "John Doe"
}
```

---

## Wallet

### Get My Balance

**Endpoint:** `GET /api/v1/wallet/me`  
**Auth:** Required

**Query Parameters:**
- `token` (string, default: "NCR")

**Response:**
```json
{
  "user_id": 1,
  "token": "NCR",
  "balance": "1000.00",
  "available": "1000.00",
  "locked": "0.00"
}
```

---

### Get User Balance

**Endpoint:** `GET /api/v1/wallet/balance/{user_id}`

**Query Parameters:**
- `token` (string, default: "NCR")

**Response:** `BalanceResponse`

---

### Create Transaction

**Endpoint:** `POST /api/v1/wallet/tx`

**Request:**
```json
{
  "user_id": 1,
  "token": "NCR",
  "type": "SPEND",
  "amount": "100.00",
  "description": "Purchase",
  "metadata": {}
}
```

**Response:**
```json
{
  "id": 123,
  "user_id": 1,
  "token": "NCR",
  "type": "SPEND",
  "amount": "100.00",
  "balance_after": "900.00",
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

### Get My Transactions

**Endpoint:** `GET /api/v1/wallet/me/transactions`  
**Auth:** Required

**Query Parameters:**
- `page` (int, default: 1)
- `per_page` (int, default: 20, max: 100)
- `token` (string, optional)
- `type` (enum: SPEND, EARN, RAKE, FEE, BURN, optional)

**Response:**
```json
{
  "transactions": [...],
  "total": 50,
  "page": 1,
  "per_page": 20
}
```

---

### Transfer NCR

**Endpoint:** `POST /api/v1/wallet/transfer`  
**Auth:** Required  
**Enforcement:** CP regime check (LOCKDOWN blocks)

**Request:**
```json
{
  "to_user_id": 2,
  "amount": "50.00",
  "token": "NCR",
  "description": "Payment"
}
```

**Response:**
```json
{
  "from_user_id": 1,
  "to_user_id": 2,
  "amount": "50.00",
  "token": "NCR",
  "transaction_id": 123,
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

### Get Treasury Summary

**Endpoint:** `GET /api/v1/wallet/treasury`  
**Auth:** Admin only

**Response:**
```json
{
  "total_treasury": "1000000.00",
  "total_in_circulation": "5000000.00",
  "total_burned": "100000.00"
}
```

---

## XP & Loyalty

### Get My Loyalty Profile

**Endpoint:** `GET /api/v1/loyalty/me`  
**Auth:** Required

**Response:**
```json
{
  "user_id": 1,
  "xp_total": 5000,
  "xp_current_level": 500,
  "level": 5,
  "tier": "SILVER",
  "next_level_xp": 1000,
  "progress_percent": 50.0
}
```

---

### Get User Loyalty Profile

**Endpoint:** `GET /api/v1/loyalty/profile/{user_id}`

**Response:** `LoyaltyProfileResponse`

---

### Get Loyalty Brief

**Endpoint:** `GET /api/v1/loyalty/brief/{user_id}`

**Response:**
```json
{
  "user_id": 1,
  "level": 5,
  "tier": "SILVER"
}
```

---

### Create XP Event

**Endpoint:** `POST /api/v1/loyalty/event`

**Request:**
```json
{
  "user_id": 1,
  "event_type": "quest_complete",
  "xp_amount": 100,
  "metadata": {}
}
```

**Response:**
```json
{
  "id": 123,
  "user_id": 1,
  "event_type": "quest_complete",
  "xp_amount": 100,
  "xp_total_after": 5100,
  "level_after": 5,
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

### Get Leaderboard

**Endpoint:** `GET /api/v1/loyalty/leaderboard`

**Query Parameters:**
- `limit` (int, default: 10, max: 100)
- `offset` (int, default: 0)

**Response:**
```json
{
  "entries": [
    {
      "rank": 1,
      "user_id": 1,
      "xp_total": 10000,
      "level": 10,
      "tier": "GOLD"
    }
  ],
  "total": 100
}
```

---

### Get Stats

**Endpoint:** `GET /api/v1/loyalty/stats`

**Response:**
```json
{
  "total_users": 1000,
  "total_xp": 5000000,
  "average_level": 5.5,
  "tier_distribution": {
    "BRONZE": 500,
    "SILVER": 300,
    "GOLD": 150,
    "DIAMOND": 50
  }
}
```

---

## NovaCredit

### Get My Credit Profile

**Endpoint:** `GET /api/v1/credit/me`  
**Auth:** Required

**Response:**
```json
{
  "user_id": 1,
  "nova_credit": 750,
  "tier": "GOLD",
  "risk_level": "LOW",
  "reputation_score": 85.5,
  "privileges": {
    "can_withdraw": true,
    "can_borrow": true,
    "can_trade": true
  }
}
```

---

### Get Credit Profile

**Endpoint:** `GET /api/v1/credit/profile/{user_id}`

**Response:** `CreditProfile`

---

### Get Credit Brief

**Endpoint:** `GET /api/v1/credit/brief/{user_id}`

**Response:**
```json
{
  "user_id": 1,
  "nova_credit": 750,
  "tier": "GOLD"
}
```

---

### Get My Credit History

**Endpoint:** `GET /api/v1/credit/me/history`  
**Auth:** Required

**Query Parameters:**
- `page` (int, default: 1)
- `per_page` (int, default: 20, max: 100)

**Response:**
```json
{
  "changes": [
    {
      "id": 123,
      "old_score": 700,
      "new_score": 750,
      "delta": 50,
      "reason": "quest_complete",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 50,
  "page": 1,
  "per_page": 20
}
```

---

### Process Behavior Event

**Endpoint:** `POST /api/v1/credit/process`

**Request:**
```json
{
  "user_id": 1,
  "event_type": "PAYMENT_COMPLETED",
  "metadata": {}
}
```

**Response:**
```json
{
  "user_id": 1,
  "old_score": 700,
  "new_score": 750,
  "delta": 50,
  "tier_before": "SILVER",
  "tier_after": "GOLD"
}
```

---

## Agency

### Get My Agency

**Endpoint:** `GET /api/v1/agency/my`  
**Auth:** Required

**Response:**
```json
{
  "id": 1,
  "name": "My Agency",
  "owner_id": 1,
  "total_performers": 10,
  "total_revenue": "100000.00",
  "total_earnings": "80000.00"
}
```

---

### Create Agency

**Endpoint:** `POST /api/v1/agency`  
**Auth:** Required

**Request:**
```json
{
  "name": "My Agency",
  "description": "Agency description"
}
```

**Response:** `AgencyResponse`

---

### Get Agency

**Endpoint:** `GET /api/v1/agency/{agency_id}`

**Response:** `AgencyWithStats`

---

### Update Agency

**Endpoint:** `PATCH /api/v1/agency/{agency_id}`  
**Auth:** Required (Patronice only)

**Request:**
```json
{
  "name": "Updated Name",
  "description": "Updated description"
}
```

**Response:** `AgencyResponse`

---

### List Operators

**Endpoint:** `GET /api/v1/agency/{agency_id}/operators`  
**Auth:** Required

**Response:** `list[OperatorResponse]`

---

### Add Operator

**Endpoint:** `POST /api/v1/agency/{agency_id}/operators`  
**Auth:** Required (Patronice only)

**Request:**
```json
{
  "user_id": 2,
  "role": "MANAGER"
}
```

**Response:** `OperatorResponse`

---

### List Performers

**Endpoint:** `GET /api/v1/agency/{agency_id}/performers`

**Query Parameters:**
- `active_only` (bool, default: true)

**Response:** `list[PerformerResponse]`

---

### Create Performer

**Endpoint:** `POST /api/v1/agency/{agency_id}/performers`  
**Auth:** Required (Patronice/Manager only)

**Request:**
```json
{
  "display_name": "Performer Name",
  "handle": "performer_handle",
  "bio": "Bio text"
}
```

**Response:** `PerformerResponse`

---

### Get Performer

**Endpoint:** `GET /api/v1/performers/{performer_id}`

**Response:** `PerformerResponse`

---

### Calculate Revenue Split

**Endpoint:** `GET /api/v1/performers/{performer_id}/revenue-split`

**Query Parameters:**
- `amount` (decimal, required)

**Response:**
```json
{
  "performer_share": "60.00",
  "agency_share": "30.00",
  "treasury_share": "10.00",
  "total": "100.00"
}
```

---

## Events

### FlirtMarket Event

**Endpoint:** `POST /api/v1/events/flirt`

**Request:**
```json
{
  "event_type": "COIN_SPENT",
  "user_id": 1,
  "performer_id": 1,
  "amount": "100.00",
  "metadata": {}
}
```

**Response:**
```json
{
  "success": true,
  "wallet_tx_id": 123,
  "xp_event_id": 456,
  "revenue_split": {
    "performer": "60.00",
    "agency": "30.00",
    "treasury": "10.00"
  }
}
```

---

### OnlyVips Event

**Endpoint:** `POST /api/v1/events/onlyvips`

**Request:**
```json
{
  "event_type": "PREMIUM_PURCHASED",
  "user_id": 1,
  "performer_id": 1,
  "amount": "50.00",
  "metadata": {}
}
```

**Response:** `EventResult`

---

### PokerVerse Event

**Endpoint:** `POST /api/v1/events/poker`

**Request:**
```json
{
  "event_type": "RAKE",
  "user_id": 1,
  "amount": "10.00",
  "metadata": {}
}
```

**Response:** `EventResult`

---

### Aurora AI Event

**Endpoint:** `POST /api/v1/events/aurora`

**Request:**
```json
{
  "event_type": "TOKEN_BURN",
  "user_id": 1,
  "tokens_burned": 100,
  "metadata": {}
}
```

**Response:** `EventResult`

---

## Treasury

### Get Treasury Summary

**Endpoint:** `GET /api/v1/treasury/summary`

**Response:**
```json
{
  "total_treasury": "1000000.00",
  "pools_balance": {
    "POOL_GROWTH": "500000.00",
    "POOL_PERFORMER": "300000.00",
    "POOL_DEV": "200000.00"
  },
  "last_24h_revenue": "10000.00",
  "last_7d_revenue": "70000.00",
  "total_burned": "100000.00",
  "revenue_by_app": {
    "FlirtMarket": "50000.00",
    "OnlyVips": "30000.00"
  },
  "revenue_by_kind": {
    "COIN_SPENT": "40000.00",
    "RAKE": "20000.00"
  }
}
```

---

### Get Treasury Flows

**Endpoint:** `GET /api/v1/treasury/flows`

**Query Parameters:**
- `range` (string: "24h", "7d", "30d", "all", default: "24h")
- `app` (string, optional)
- `kind` (string, optional)
- `page` (int, default: 1)
- `per_page` (int, default: 50, max: 100)

**Response:** `list[TreasuryFlowOut]`

---

### Get Treasury Pools

**Endpoint:** `GET /api/v1/treasury/pools`

**Response:**
```json
{
  "POOL_GROWTH": {
    "account_type": "POOL_GROWTH",
    "balance": "500000.00"
  },
  "POOL_PERFORMER": {...},
  "POOL_DEV": {...}
}
```

---

### Get Revenue Chart (By App)

**Endpoint:** `GET /api/v1/treasury/charts/revenue-by-app`

**Query Parameters:**
- `range` (string: "7d", "30d", default: "7d")

**Response:**
```json
{
  "labels": ["2024-01-01", "2024-01-02", ...],
  "revenue": ["10000.00", "12000.00", ...],
  "app_breakdown": {
    "FlirtMarket": ["5000.00", "6000.00", ...],
    "OnlyVips": ["3000.00", "4000.00", ...]
  }
}
```

---

### Get Revenue Chart (By Kind)

**Endpoint:** `GET /api/v1/treasury/charts/revenue-by-kind`

**Query Parameters:**
- `range` (string: "7d", "30d", default: "7d")

**Response:** `RevenueChartData`

---

## Consent

### Create Consent Session

**Endpoint:** `POST /api/v1/consent/session`

**Request:**
```json
{
  "user_id": "1",
  "client_fingerprint": "abc123"
}
```

**Response:**
```json
{
  "session_id": "uuid",
  "user_id": "1",
  "status": "PENDING"
}
```

---

### Accept Clause

**Endpoint:** `POST /api/v1/consent/clauses`

**Request:**
```json
{
  "session_id": "uuid",
  "clause_id": "clause_1",
  "accepted": true
}
```

**Response:** `ClauseAcceptanceStatus`

---

### Accept Redline

**Endpoint:** `POST /api/v1/consent/redline`

**Request:**
```json
{
  "session_id": "uuid",
  "redline_id": "redline_1",
  "accepted": true
}
```

**Response:** `RedlineConsentRequest`

---

### Sign Consent

**Endpoint:** `POST /api/v1/consent/sign`

**Request:**
```json
{
  "session_id": "uuid",
  "consent_level": "FULL"
}
```

**Response:** `ConsentRecordResponse`

---

### Get Privacy Profile

**Endpoint:** `GET /api/v1/consent/profile/me`  
**Auth:** Required

**Response:**
```json
{
  "user_id": "1",
  "consent_level": "FULL",
  "policy": {
    "economy": {"allowed": true},
    "behavioral": {"allowed": true},
    "identity": {"allowed": true}
  },
  "recall_requested_at": null,
  "recall_completed_at": null
}
```

---

### Request Recall

**Endpoint:** `POST /api/v1/consent/recall`  
**Auth:** Required

**Request:**
```json
{
  "recall_mode": "FULL"
}
```

**Response:**
```json
{
  "user_id": "1",
  "recall_mode": "FULL",
  "status": "REQUESTED",
  "requested_at": "2024-01-01T00:00:00Z"
}
```

---

### Get Recall Status

**Endpoint:** `GET /api/v1/consent/recall/status`  
**Auth:** Required

**Response:**
```json
{
  "status": "REQUESTED",
  "recall_mode": "FULL",
  "requested_at": "2024-01-01T00:00:00Z",
  "completed_at": null
}
```

---

## Justice

### Create Violation

**Endpoint:** `POST /api/v1/justice/violations`

**Request:**
```json
{
  "user_id": "1",
  "category": "EKO",
  "code": "SPAM_MESSAGE",
  "severity": 2,
  "cp_delta": 5,
  "source": "FlirtMarket",
  "context": {}
}
```

**Response:**
```json
{
  "id": "123",
  "user_id": "1",
  "category": "EKO",
  "code": "SPAM_MESSAGE",
  "severity": 2,
  "cp_delta": 5,
  "cp_after": 5,
  "regime_after": "CLEAN",
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

### Get My CP State

**Endpoint:** `GET /api/v1/justice/cp/me`  
**Auth:** Required

**Response:**
```json
{
  "user_id": "1",
  "cp_value": 0,
  "regime": "CLEAN",
  "last_updated_at": "2024-01-01T00:00:00Z",
  "decay_per_day": 1
}
```

---

### Get User CP State

**Endpoint:** `GET /api/v1/justice/cp/{user_id}`  
**Auth:** Admin only

**Response:** `CpStateResponse`

---

### Get My Violations

**Endpoint:** `GET /api/v1/justice/violations/me`  
**Auth:** Required

**Query Parameters:**
- `limit` (int, default: 20)
- `offset` (int, default: 0)

**Response:**
```json
{
  "violations": [...],
  "total": 10
}
```

---

### Get Case File

**Endpoint:** `GET /api/v1/justice/case/{user_id}`  
**Auth:** Admin only

**Response:**
```json
{
  "user_id": "1",
  "cp_state": {...},
  "violations": [...],
  "consent_profile": {...},
  "nova_score": {...}
}
```

---

### Get Current Policy

**Endpoint:** `GET /api/v1/justice/policy/current`

**Response:**
```json
{
  "version": 1,
  "regime_thresholds": {
    "CLEAN": 0,
    "WARNING": 10,
    "PROBATION": 30,
    "RESTRICTED": 50,
    "LOCKDOWN": 100
  },
  "decay_per_day": 1,
  "onchain_address": "0x..."
}
```

---

### Create Appeal

**Endpoint:** `POST /api/v1/justice/appeals`  
**Auth:** Required

**Request:**
```json
{
  "submission_id": 123,
  "reason": "My submission was incorrectly rejected. I have provided valid proof."
}
```

**Response:**
```json
{
  "id": 1,
  "submission_id": 123,
  "user_id": "1",
  "reason": "My submission was incorrectly rejected...",
  "status": "pending",
  "appeal_fee_paid": true,
  "created_at": "2024-01-01T00:00:00Z",
  "reviewed_at": null,
  "reviewed_by": null,
  "review_notes": null
}
```

**Notes:**
- Appeal fee: 5 NCR (automatically deducted)
- Only rejected submissions can be appealed
- Submission status changes to `pending` (moved to Ethics Appeal Queue)
- One appeal per submission
- Telemetry event `appeal_submitted` is tracked

---

## NovaScore

### Get My NovaScore

**Endpoint:** `GET /api/v1/nova-score/me`  
**Auth:** Required

**Response:**
```json
{
  "user_id": "1",
  "nova_score": 850,
  "components": {
    "ECO": {"value": 80.0, "confidence": 1.0},
    "REL": {"value": 90.0, "confidence": 1.0},
    "SOC": {"value": 85.0, "confidence": 1.0},
    "ID": {"value": 95.0, "confidence": 1.0},
    "CON": {"value": 70.0, "confidence": 0.8}
  },
  "cp": 0,
  "confidence_overall": 0.96,
  "explanation": null
}
```

---

## Telegram Gateway

All Telegram Gateway endpoints require `X-TG-BRIDGE-TOKEN` header.

### Link Telegram User

**Endpoint:** `POST /api/v1/telegram/link`

**Headers:**
- `X-TG-BRIDGE-TOKEN`: Bridge token

**Request:**
```json
{
  "telegram_user_id": 123456789,
  "username": "johndoe",
  "first_name": "John",
  "last_name": "Doe",
  "start_param": "hmac_signature..."  // Optional, for deep linking
}
```

**Response:**
```json
{
  "user_id": 1,
  "telegram_user_id": 123456789,
  "linked": true
}
```

---

### Get Full Profile

**Endpoint:** `GET /api/v1/telegram/me`

**Headers:**
- `X-TG-BRIDGE-TOKEN`: Bridge token

**Query Parameters:**
- `telegram_user_id` (int, required)

**Response:**
```json
{
  "user_id": 1,
  "telegram_user_id": 123456789,
  "username": "johndoe",
  "display_name": "John Doe",
  "wallet": {
    "balance": "1000.00"
  },
  "loyalty": {
    "level": 5,
    "tier": "SILVER",
    "xp_total": 5000
  },
  "nova_score": 850,
  "cp_value": 0,
  "regime": "CLEAN"
}
```

---

### Get Available Tasks

**Endpoint:** `GET /api/v1/telegram/tasks`

**Headers:**
- `X-TG-BRIDGE-TOKEN`: Bridge token

**Query Parameters:**
- `telegram_user_id` (int, required)

**Response:**
```json
{
  "tasks": [
    {
      "id": 1,
      "code": "DAILY_LOGIN",
      "name": "Daily Login",
      "description": "Login every day",
      "difficulty": "EASY",
      "reward_xp": 10,
      "reward_ncr": "5.00",
      "is_completed": false,
      "can_complete": true
    }
  ]
}
```

---

### Submit Task Completion

**Endpoint:** `POST /api/v1/telegram/tasks/{task_id}/submit`

**Headers:**
- `X-TG-BRIDGE-TOKEN`: Bridge token

**Request:**
```json
{
  "telegram_user_id": 123456789,
  "proof_type": "AUTO",
  "proof_data": {},
  "idempotency_key": "unique_key_123"
}
```

**Response:**
```json
{
  "success": true,
  "task_id": 1,
  "reward_xp": 10,
  "reward_ncr": "5.00",
  "xp_total_after": 5010,
  "wallet_balance_after": "1005.00"
}
```

---

### Claim Referral Reward

**Endpoint:** `POST /api/v1/telegram/referral/claim`

**Headers:**
- `X-TG-BRIDGE-TOKEN`: Bridge token

**Request:**
```json
{
  "telegram_user_id": 123456789,
  "referred_telegram_user_id": 987654321,
  "idempotency_key": "unique_key_456"
}
```

**Response:**
```json
{
  "success": true,
  "reward_xp": 50,
  "reward_ncr": "25.00"
}
```

---

### Get Leaderboard

**Endpoint:** `GET /api/v1/telegram/leaderboard`

**Headers:**
- `X-TG-BRIDGE-TOKEN`: Bridge token

**Query Parameters:**
- `limit` (int, default: 10, max: 100)
- `offset` (int, default: 0)

**Response:**
```json
{
  "entries": [
    {
      "rank": 1,
      "user_id": 1,
      "telegram_user_id": 123456789,
      "username": "johndoe",
      "display_name": "John Doe",
      "xp_total": 10000,
      "level": 10
    }
  ],
  "total": 100
}
```

---

### Get Profile Card

**Endpoint:** `GET /api/v1/telegram/profile-card`

**Headers:**
- `X-TG-BRIDGE-TOKEN`: Bridge token

**Query Parameters:**
- `telegram_user_id` (int, required)

**Response:**
```json
{
  "user_id": 1,
  "telegram_user_id": 123456789,
  "username": "johndoe",
  "display_name": "John Doe",
  "level": 5,
  "tier": "SILVER",
  "xp_total": 5000,
  "nova_score": 850,
  "cp_value": 0,
  "regime": "CLEAN"
}
```

---

### Get Active Events

**Endpoint:** `GET /api/v1/telegram/events`

**Headers:**
- `X-TG-BRIDGE-TOKEN`: Bridge token

**Query Parameters:**
- `telegram_user_id` (int, required)

**Response:**
```json
{
  "events": [
    {
      "id": 1,
      "code": "WEEKLY_CHALLENGE",
      "name": "Weekly Challenge",
      "status": "ACTIVE",
      "is_joined": false,
      "starts_at": "2024-01-01T00:00:00Z",
      "ends_at": "2024-01-07T23:59:59Z"
    }
  ]
}
```

---

### Join Event

**Endpoint:** `POST /api/v1/telegram/events/{event_id}/join`

**Headers:**
- `X-TG-BRIDGE-TOKEN`: Bridge token

**Request:**
```json
{
  "telegram_user_id": 123456789
}
```

**Response:**
```json
{
  "success": true,
  "event_id": 1,
  "joined_at": "2024-01-01T00:00:00Z"
}
```

---

### Get Event Leaderboard

**Endpoint:** `GET /api/v1/telegram/events/{event_id}/leaderboard`

**Headers:**
- `X-TG-BRIDGE-TOKEN`: Bridge token

**Query Parameters:**
- `telegram_user_id` (int, required)
- `limit` (int, default: 100, max: 500)

**Response:**
```json
{
  "event_id": 1,
  "event_name": "Weekly Challenge",
  "entries": [
    {
      "rank": 1,
      "user_id": 1,
      "telegram_user_id": 123456789,
      "username": "johndoe",
      "total_xp_earned": 1000,
      "tasks_completed": 10
    }
  ],
  "total_participants": 50
}
```

---

### Streak Check-in

**Endpoint:** `POST /api/v1/telegram/streak/checkin`

**Headers:**
- `X-TG-BRIDGE-TOKEN`: Bridge token

**Request:**
```json
{
  "telegram_user_id": 123456789
}
```

**Response:**
```json
{
  "success": true,
  "current_streak": 5,
  "max_streak": 10,
  "reward_xp": 12,
  "reward_ncr": "1.2",
  "message": "Check-in başarılı! +12 XP, +1.2 NCR (Streak bonus: 5 gün x1.10)",
  "new_balance": "1001.20",
  "new_xp_total": 5012
}
```

**Notes:**
- Streak bonus multipliers:
  - 3+ days: 1.1x
  - 7+ days: 1.25x
  - 14+ days: 1.5x
  - 30+ days: 2.0x
- Can only check in once per day
- Streak resets if missed a day

---

### Get DAO Review Queue

**Endpoint:** `GET /api/v1/telegram/dao/queue`

**Headers:**
- `X-TG-BRIDGE-TOKEN`: Bridge token (Admin only)

**Query Parameters:**
- `limit` (int, default: 50)
- `offset` (int, default: 0)

**Response:**
```json
{
  "submissions": [
    {
      "submission_id": 123,
      "user_id": 1,
      "telegram_user_id": 123456789,
      "username": "johndoe",
      "display_name": "John Doe",
      "task_id": "daily_login",
      "task_title": "Daily Login",
      "proof": "https://example.com/screenshot.jpg",
      "proof_metadata": {
        "image_file_id": "AgACAgIAAxkBAAIBY2...",
        "caption": "Daily login proof"
      },
      "submitted_at": "2024-01-01T00:00:00Z",
      "status": "pending"
    }
  ],
  "total_pending": 10,
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Notes:**
- Returns pending task submissions for manual review
- Requires admin privileges (via bridge token)
- Used by DAO delegates for HITL review

---

## Telemetry

### Track Event

**Endpoint:** `POST /api/v1/telemetry/events`  
**Auth:** Required

**Request:**
```json
{
  "event": "onboarding_completed",
  "payload": {
    "step": "consent"
  },
  "session_id": "session_123",
  "source": "citizen-portal"
}
```

**Response:**
```json
{
  "id": "123",
  "user_id": 1,
  "event": "onboarding_completed",
  "payload": {...},
  "created_at": "2024-01-01T00:00:00Z",
  "session_id": "session_123",
  "source": "citizen-portal"
}
```

---

### Get Growth Metrics

**Endpoint:** `GET /api/v1/telemetry/growth`  
**Auth:** Admin only

**Response:**
```json
{
  "onboarding_last_24h": 10,
  "onboarding_last_7d": 50,
  "onboarding_total": 1000,
  "academy_views_last_24h": 100,
  "academy_views_last_7d": 500,
  "academy_module_completions_last_24h": 20,
  "academy_module_completions_last_7d": 100,
  "top_modules": [
    {"module": "constitution", "views": 200}
  ],
  "recall_requests_last_24h": 2,
  "recall_requests_total": 50,
  "appeals_submitted_last_24h": 1,
  "appeals_submitted_total": 10,
  "active_users_last_24h": 500,
  "active_users_last_7d": 2000,
  "generated_at": "2024-01-01T00:00:00Z"
}
```

---

## Admin

### Health Check

**Endpoint:** `GET /api/v1/admin/health`

**Response:**
```json
{
  "status": "ok",
  "version": "0.1.0",
  "environment": "dev",
  "timestamp": "2024-01-01T00:00:00Z",
  "database": "healthy"
}
```

---

### System Summary

**Endpoint:** `GET /api/v1/admin/summary`  
**Auth:** Admin only

**Response:**
```json
{
  "total_users": 1000,
  "active_users_24h": 500,
  "total_ncr_in_circulation": "5000000.00",
  "treasury_balance": "1000000.00",
  "total_transactions": 10000,
  "total_xp_distributed": 5000000,
  "average_level": 5.5,
  "total_agencies": 10,
  "total_performers": 100,
  "top_users_by_xp": [...],
  "top_users_by_ncr": [...],
  "top_performers": [...]
}
```

---

### Quick Stats

**Endpoint:** `GET /api/v1/admin/stats`

**Response:**
```json
{
  "total_users": 1000,
  "total_ncr": "5000000.00",
  "treasury_ncr": "1000000.00",
  "total_performers": 100
}
```

---

### Aurora Stats

**Endpoint:** `GET /api/v1/admin/aurora/stats`  
**Auth:** Admin only

**Response:**
```json
{
  "total_citizens": 1000,
  "consent_stats": {
    "total_consents": 800,
    "full_consent": 600,
    "partial_consent": 200
  },
  "cp_stats": {
    "average_cp": 5.5,
    "regime_distribution": {
      "CLEAN": 800,
      "WARNING": 100,
      "PROBATION": 50,
      "RESTRICTED": 30,
      "LOCKDOWN": 20
    }
  },
  "nova_score_stats": {
    "average_score": 750,
    "score_distribution": {...}
  }
}
```

---

### List Violations

**Endpoint:** `GET /api/v1/admin/aurora/violations`  
**Auth:** Admin only

**Query Parameters:**
- `limit` (int, default: 50, max: 200)
- `offset` (int, default: 0)
- `category` (string: EKO, COM, SYS, TRUST, optional)
- `severity_min` (int, default: 1, max: 5)
- `severity_max` (int, default: 5, max: 5)
- `since` (datetime, optional)

**Response:**
```json
{
  "items": [
    {
      "id": "123",
      "user_id": "1",
      "category": "EKO",
      "code": "SPAM_MESSAGE",
      "severity": 2,
      "cp_delta": 5,
      "regime_after": "CLEAN",
      "source": "FlirtMarket",
      "message_preview": "Spam message...",
      "meta": {},
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 100,
  "limit": 50,
  "offset": 0
}
```

---

### List Users

**Endpoint:** `GET /api/v1/admin/aurora/users`  
**Auth:** Admin only

**Query Parameters:**
- `page` (int, default: 1)
- `limit` (int, default: 50, max: 200)
- `search` (string, optional)
- `recall_filter` (string: NONE, REQUESTED, COMPLETED, optional)

**Response:**
```json
{
  "users": [
    {
      "user_id": "1",
      "display_name": "John Doe",
      "email": "user@example.com",
      "has_consent": true,
      "consent_level": "FULL",
      "recall_state": "NONE",
      "cp_value": 0,
      "is_admin": false,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1000,
  "page": 1,
  "limit": 50
}
```

---

### Set User Admin Status

**Endpoint:** `PATCH /api/v1/admin/aurora/users/{user_id}/admin`  
**Auth:** Admin only

**Request:**
```json
{
  "is_admin": true
}
```

**Response:**
```json
{
  "user_id": "1",
  "is_admin": true,
  "message": "Admin privileges granted successfully"
}
```

---

### List Events (Admin)

**Endpoint:** `GET /api/v1/admin/events`  
**Auth:** Admin only

**Query Parameters:**
- `status` (string: ACTIVE, ENDED, UPCOMING, optional)
- `event_type` (string: CHALLENGE, TOURNAMENT, optional)
- `limit` (int, default: 50, max: 100)
- `offset` (int, default: 0)

**Response:** `list[EventResponse]`

---

### Get Event Detail (Admin)

**Endpoint:** `GET /api/v1/admin/events/{event_id}`  
**Auth:** Admin only

**Response:** `EventResponse` (with admin stats)

---

### Get Event Participants (Admin)

**Endpoint:** `GET /api/v1/admin/events/{event_id}/participants`  
**Auth:** Admin only

**Query Parameters:**
- `limit` (int, default: 100, max: 500)

**Response:** `EventLeaderboardResponse`

---

### Get Event Stats (Admin)

**Endpoint:** `GET /api/v1/admin/events/{event_id}/stats`  
**Auth:** Admin only

**Response:**
```json
{
  "event_id": 1,
  "event_name": "Weekly Challenge",
  "status": "ACTIVE",
  "stats": {
    "total_participants": 50,
    "total_xp_distributed": 50000,
    "total_ncr_distributed": "25000.00",
    "total_tasks_completed": 500,
    "avg_xp_per_participant": 1000,
    "avg_tasks_per_participant": 10
  },
  "top_3": [...]
}
```

---

## FlirtMarket (Example)

These endpoints demonstrate Aurora Justice enforcement integration.

### Send Message

**Endpoint:** `POST /flirtmarket/messages`  
**Auth:** Required  
**Enforcement:** CP regime check (LOCKDOWN/RESTRICTED blocks)

**Request:**
```json
{
  "recipient_id": "2",
  "message": "Hello!"
}
```

**Response:**
```json
{
  "message_id": "uuid",
  "sent_at": "2024-01-01T00:00:00Z"
}
```

**Error (if blocked):**
```json
{
  "detail": "Aurora rejimin: LOCKDOWN. Mesaj gönderemezsin.",
  "regime": "LOCKDOWN"
}
```

---

### Start Call

**Endpoint:** `POST /flirtmarket/calls/start`  
**Auth:** Required  
**Enforcement:** CP regime check (LOCKDOWN/RESTRICTED/PROBATION blocks)

**Request:**
```json
{
  "recipient_id": "2"
}
```

**Response:**
```json
{
  "call_id": "uuid",
  "started_at": "2024-01-01T00:00:00Z"
}
```

---

### Create Flirt

**Endpoint:** `POST /flirtmarket/flirts`  
**Auth:** Required  
**Enforcement:** CP regime check (LOCKDOWN blocks)

**Request:**
```json
{
  "performer_id": "1",
  "message": "Hello performer!"
}
```

**Response:**
```json
{
  "flirt_id": "uuid",
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

## Error Responses

### Standard Error Format

```json
{
  "detail": "Error message"
}
```

### Common Status Codes

- `200 OK`: Success
- `201 Created`: Resource created
- `400 Bad Request`: Invalid request
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

### Enforcement Error Format

When Aurora Justice blocks an action:

```json
{
  "detail": "Aurora rejimin: LOCKDOWN. Action blocked.",
  "regime": "LOCKDOWN",
  "cp_value": 100,
  "action": "SEND_MESSAGE"
}
```

---

## Rate Limiting

- **Telemetry Events:** 100 events per user per day
- **Task Submissions:** Idempotency-based (duplicate submissions ignored)
- **Referral Claims:** One claim per referred user

---

## Idempotency

Several endpoints support idempotency via `idempotency_key`:

- Task submissions
- Referral claims
- Transaction creation

Duplicate requests with the same `idempotency_key` return the original response without side effects.

---

## Environment Variables

Required environment variables for API operation:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/novacore

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=10080

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Telegram Gateway (optional)
TELEGRAM_BRIDGE_TOKEN=your-bridge-token
TELEGRAM_LINK_SECRET=your-hmac-secret  # Optional, uses JWT_SECRET if not set
```

---

## Swagger UI

Interactive API documentation available at:

- **Development:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

---

## Version History

- **v0.4.0**: i18n support, Telegram Gateway, Task Engine v3
- **v0.3.0**: Dashboard v2, unified citizen state
- **v0.2.0**: Aurora Justice Stack v2.0, DAO governance
- **v0.1.0**: Initial release

---

**Last Updated:** 2024-01-01

