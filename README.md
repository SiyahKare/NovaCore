# SiyahKare Republic · NovaCore Kernel

**DeltaNova Ideology → NovaCore Execution Engine → Aurora Justice Stack**

> SiyahKare Cumhuriyeti, DeltaNova ideolojisini NovaCore çekirdeği üzerinden çalıştırır. NovaCore’un adalet katmanı Aurora Justice Engine’dir.

[![SiyahKare Architecture](https://img.shields.io/badge/SiyahKare-Architecture-black)](./docs/AURORA_STATE_ARCHITECTURE.md)
[![Dashboard v2](https://img.shields.io/badge/Dashboard-v2-blue)](./apps/citizen-portal)
[![DAO Governance](https://img.shields.io/badge/DAO-Governance-green)](./docs/DAO_INTEGRATION.md)

## 🏛️ Devlet Katmanları

1. **SiyahKare Republic (State Layer)** – Vatandaşlık, anayasa, haklar.
2. **DeltaNova Ideology (Philosophy Layer)** – Behavior is Currency, NovaCredit/NovaScore teorisi.
3. **NovaCore Kernel (Execution Layer)** – FastAPI + Next.js runtime, ledger, consent, telemetry, agency.
4. **Aurora Justice Engine (Governance Module)** – CP/Regime, violations, ombudsman, enforcement, DAO policy.

NovaCore + Aurora kombinasyonu şu yetenekleri sağlar:

- **Consent Management**: GDPR-compliant consent flow, immutable ledger
- **Justice System**: CP (Ceza Puanı) calculation, regime-based enforcement
- **NovaScore**: Behavioral reputation score with CP integration
- **Right to Recall**: User data exclusion from AI training
- **Ombudsman**: Complete case file for operator review
- **DAO Governance**: Policy parameters controlled by on-chain governance
- **3-Layer Architecture**: Chain Law (mutable) + Constitution (immutable) + Execution (runtime)
- **Frontend Ecosystem**: Citizen Portal, Admin Panel, Mobile Mini-App
- **Dashboard v2**: Devran-level citizen state console with real-time data

## 📋 Prerequisites

- **Python 3.11+**
- **Node.js 18+** (for frontend)
- **PostgreSQL 14+** (Docker or Homebrew)
- **npm** or **yarn**

### Environment Variables

Create `.env` file in project root:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://novacore:password@localhost:5432/novacore
DATABASE_URL_SYNC=postgresql://novacore:password@localhost:5432/novacore

# JWT
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=10080

# CORS
# Dev: CORS_ORIGINS=http://localhost:3000,http://localhost:5173
# Prod (Cloudflare): CORS_ORIGINS=https://portal.siyahkare.com,https://app.siyahkare.com
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Backend URL (Cloudflare subdomain için)
NOVACORE_URL=http://localhost:8000  # Prod: https://api.siyahkare.com
BACKEND_URL=http://localhost:8000    # Prod: https://api.siyahkare.com

# Frontend URL (Cloudflare subdomain için)
FRONTEND_URL=http://localhost:3000   # Prod: https://portal.siyahkare.com

# Frontend API URL
NEXT_PUBLIC_AURORA_API_URL=http://localhost:8000/api/v1  # Prod: https://api.siyahkare.com/api/v1

# Telegram Gateway (optional)
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_BRIDGE_TOKEN=your-secure-bridge-token-here
TELEGRAM_LINK_SECRET=your-hmac-secret-here  # Optional, uses JWT_SECRET if not set

# Telethon (Aurora Contact User Bot - optional)
TELETHON_API_ID=your-telegram-api-id  # From https://my.telegram.org
TELETHON_API_HASH=your-telegram-api-hash
```

## 🚀 Quick Start

### 1. Backend Setup

```bash
# Clone repository
git clone <repo-url>
cd NovaCore

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database (choose one):
# Option A: Docker
docker-compose up -d postgres

# Option B: Homebrew PostgreSQL
brew services start postgresql@16
createdb novacore
createuser novacore

# Run migrations
alembic upgrade head

# Start API
uvicorn app.main:app --reload
```

**API will be available at:** `http://localhost:8000`  
**API Docs:** `http://localhost:8000/docs`

### 2. Frontend Setup

```bash
# Install dependencies (from project root)
npm install

# Start Citizen Portal
cd apps/citizen-portal
npm install
npm run dev
```

**Citizen Portal:** `http://localhost:3000`  
- **Türkçe:** `http://localhost:3000/tr` (default)
- **English:** `http://localhost:3000/en`
- **Русский:** `http://localhost:3000/ru`
- **Admin Panel:** `http://localhost:3000/tr/admin/aurora`

### 3. Verify Installation

```bash
# Health check
curl http://localhost:8000/health

# Expected: {"status":"ok"}
```

### Quick Test

```bash
# Quick consent flow test
./scripts/test_consent_flow.sh

# Full system smoke test
./scripts/smoke_test.sh

# Enforcement test (LOCKDOWN blocking)
./scripts/test_enforcement.sh
```

**See:** `scripts/QUICK_START.md` for detailed testing guide.

## 📱 Frontend Ecosystem

### NovaCore Citizen Portal

**Next.js 14** tabanlı SiyahKare vatandaş portalı:

- **Dashboard v2**: Devran-level state console (NovaCore telemetry)
  - Real-time citizen state (Identity, Wallet, Loyalty, Privacy, NovaScore, CP, Violations)
  - Aurora Justice Health panel (DAO status, policy version)
  - Citizen Timeline (join, consent, violations, regime changes)
  - Trust Factors (account age, violation frequency, behavior risk)
  - Quick Actions (Recall, Appeal, Consent Review)
- **Onboarding**: Multi-step wizard (Auth, Consent, NovaScore Preview)
- **Academy**: Educational content about DeltaNova & SiyahKare
- **Justice (Aurora)**: Case file viewer
- **Consent**: Detailed consent management with recall
- **Admin Panels**:
  - **Ombudsman Quest Monitor**: Aurora HITL quest review, RiskScore filtering, approve/reject decisions
  - **Telegram Dashboard**: Aurora Contact Business Hunter console (3-column layout)
  - **Economy Dashboard**: NasipQuest economy metrics and charts

**Tech Stack:**
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- shadcn/ui components
- Shared libraries: `@aurora/ui`, `@aurora/hooks`
- **i18n Support**: next-intl (Türkçe, English, Русский)

### NovaCore Admin Console (Aurora Justice Control Room)

**Admin-only** panel for NovaCore yönetimi ve Aurora Justice operasyonu:

- **Overview**: NovaCore stats and case lookup
- **Stats Dashboard**: Full system metrics
- **Case Files**: Ombudsman case viewer
- **Policy Viewer**: Aurora policy and history
- **Violation Stream**: Real-time violation feed
- **User Management**: User list, recall management, admin privileges
- **Growth Metrics**: Telemetry and education tracking
- **Ombudsman Quest Monitor**: Aurora HITL (Human-In-The-Loop) quest review panel
  - RiskScore ≥ 6.0 quest'leri yönetme
  - Onay/Red kararları verme
  - AbuseGuard entegrasyonu
- **Telegram Dashboard**: Aurora Contact Business Hunter console
  - 3-column layout (Queue, Chat, Lead Intelligence)
  - AI/Human hybrid chat
  - Lead scoring ve pipeline takibi
  - Real-time conversation management
- **Economy Dashboard**: NasipQuest economy metrics
  - NCR price tracking
  - Treasury health
  - Daily load statistics
  - RiskScore distribution

**Access:** `/admin/aurora` (requires `is_admin: true`)

### Shared Libraries

**`packages/aurora-ui`**: Shared React components
- RegimeBadge, RegimeBanner
- NovaScoreCard, CPTrendGraph
- PolicyBreakdown, DAOChangeLog
- AuroraStateHealth, CitizenTimeline, TrustFactors
- EnforcementErrorModal, ConsentFlow, AppealForm

**`packages/aurora-hooks`**: Shared data hooks
- `useCitizenState`: Unified citizen state hook (all data in one payload)
- `useNovaScore`, `useJustice`, `usePolicy`
- `useRegimeTheme`: Regime-aware UI theming
- `useCurrentCitizen`, `useConsentFlow`
- `useAuroraEvents`, `useGrowthMetrics`
- `useHitlQuests`: HITL quest monitor hook
- `useTelegramConversations`: Telegram conversation management
- `useTelegramStats`: Dashboard statistics

## 🏗️ Architecture

### SiyahKare Governance Stack

1. **DeltaNova Ideology** (Philosophy) – Behavior is Currency, NovaCredit, manifesto.
2. **Chain Law / DAO Policy** (Mutable) – Aurora policy parameters, validator consensus.
3. **Constitution** (Immutable) – Consent, recall, citizen rights.
4. **NovaCore Execution** (Runtime) – API, ledger, telemetry, Aurora CP/Regime enforcement.

See `docs/AURORA_STATE_ARCHITECTURE.md` for full breakdown.

### Monorepo Structure

```
NovaCore/
  app/                    # Backend (FastAPI)
    core/                 # Config, DB, Security, Logging
    identity/             # User SSO, JWT, Email Auth
    wallet/               # NCR Ledger
    xp_loyalty/           # Level/Tier
    agency/               # NovaAgency, Performers
    events/               # App event ingest
    admin/                # Health, summary, user management
    consent/              # Consent flow, privacy profiles, recall
    justice/              # Violation logging, CP, enforcement (DAO-controlled)
    nova_score/           # Behavioral reputation score
    telemetry/            # Growth & education event tracking
    telegram_gateway/     # Telegram bot bridge, task engine, referral system
    quests/               # Production-ready Quest Engine (UserQuest, QuestFactory, HITL)
    abuse/                # AbuseGuard (RiskScore, abuse detection, reward multipliers)
    wallet/               # NCR Ledger, Treasury Cap, NCR Price Stabilization
    agency/               # Creator → Agency Pipeline, Revenue Share, ChatManager
    voice_engine/         # Telethon client (Aurora Contact User Bot)
    main.py
  apps/                   # Frontend Applications
    citizen-portal/       # Next.js 14 Citizen Portal (i18n: tr/en/ru)
      app/
        [locale]/         # Locale-based routing (tr, en, ru)
          dashboard/      # Dashboard v2
          onboarding/     # Multi-step onboarding
          academy/        # Educational content
          consent/        # Consent management
          justice/        # Case file viewer
          admin/          # Admin Panel
      messages/           # i18n translation files
      middleware.ts       # Locale routing middleware
      navigation.ts       # Locale-aware navigation
  packages/               # Shared Libraries
    aurora-ui/            # Shared React components
    aurora-hooks/         # Shared data hooks
  scripts/               # Utility scripts
  docs/                  # Documentation
  alembic/               # Database migrations
  nasipquest_bot/        # Telegram bot (NasipQuest)
```

## 📡 API Endpoints

> **Full API Documentation:** `http://localhost:8000/docs` (Swagger UI)

### Quick Reference

| Module | Endpoint | Method | Description |
|--------|----------|--------|-------------|
| **Identity** | `/api/v1/identity/me` | GET | Current user profile |
| **Identity** | `/api/v1/identity/register` | POST | Email registration |
| **Identity** | `/api/v1/identity/login` | POST | Email login |
| **Identity** | `/api/v1/dev/token` | GET | Dev mode token |
| **Wallet** | `/api/v1/wallet/me` | GET | NCR balance |
| **Loyalty** | `/api/v1/loyalty/me` | GET | XP, level, tier |
| **Consent** | `/api/v1/consent/profile/me` | GET | Privacy profile |
| **Consent** | `/api/v1/consent/recall` | POST | Request recall |
| **Justice** | `/api/v1/justice/cp/me` | GET | CP state |
| **Justice** | `/api/v1/justice/violations/me` | GET | My violations |
| **NovaScore** | `/api/v1/nova-score/me` | GET | NovaScore |
| **Admin** | `/api/v1/admin/aurora/users` | GET | User list |
| **Admin** | `/api/v1/admin/aurora/users/{id}/admin` | PATCH | Toggle admin |

### Core Modules

**Identity & Auth:**
```
POST /api/v1/identity/telegram/auth  → JWT token (Telegram)
POST /api/v1/identity/register       → Email registration
POST /api/v1/identity/login          → Email login
GET  /api/v1/identity/me           → Current user profile
GET  /api/v1/dev/token             → Dev mode token (testing)
```

**Wallet:**
```
GET  /api/v1/wallet/me             → NCR balance
POST /api/v1/wallet/tx             → Create transaction
POST /api/v1/wallet/transfer       → Transfer (enforcement enabled)
```

**Loyalty:**
```
GET  /api/v1/loyalty/me            → My loyalty profile
POST /api/v1/loyalty/event         → Create XP event
GET  /api/v1/loyalty/profile/{id}  → User loyalty profile
```

### Aurora Justice Engine

**Consent:**
```
POST /api/v1/consent/session              → Create consent session
POST /api/v1/consent/clauses              → Accept clause
POST /api/v1/consent/redline              → Accept redline
POST /api/v1/consent/sign                → Sign consent
GET  /api/v1/consent/profile/me          → Privacy profile
POST /api/v1/consent/recall               → Request recall
GET  /api/v1/consent/recall/status        → Recall status
POST /api/v1/consent/recall/{user_id}/cancel    → Cancel recall (admin)
POST /api/v1/consent/recall/{user_id}/complete  → Complete recall (admin)
```

**Justice:**
```
POST /api/v1/justice/violations          → Create violation
GET  /api/v1/justice/cp/me                → My CP state
GET  /api/v1/justice/cp/{user_id}         → User CP (admin)
GET  /api/v1/justice/violations/me        → My violations
GET  /api/v1/justice/case/{user_id}       → Case file (ombudsman)
GET  /api/v1/justice/policy/current       → Current policy parameters
```

**NovaScore:**
```
GET  /api/v1/nova-score/me                → My NovaScore
```

**Telemetry:**
```
POST /api/v1/telemetry/events             → Track user events
GET  /api/v1/admin/aurora/growth          → Growth metrics (admin)
```

**Admin:**
```
GET  /api/v1/admin/health                 → System health
GET  /api/v1/admin/summary                → System summary
GET  /api/v1/admin/aurora/users            → User list with filters
PATCH /api/v1/admin/aurora/users/{id}/admin → Toggle admin privileges
GET  /api/v1/admin/aurora/violations      → Violation stream
GET  /api/v1/admin/aurora/events          → Event list
GET  /api/v1/admin/aurora/events/{id}     → Event detail
```

**Telegram Gateway (NasipQuest):**
```
POST /api/v1/telegram/link                → Link Telegram account
GET  /api/v1/telegram/me                  → Full profile (wallet, XP, NovaScore, CP)
GET  /api/v1/telegram/tasks               → Available tasks
POST /api/v1/telegram/tasks/{task_id}/submit → Submit task completion
POST /api/v1/telegram/referral/claim      → Claim referral reward
GET  /api/v1/telegram/leaderboard          → Top users leaderboard
GET  /api/v1/telegram/profile-card         → User profile card
GET  /api/v1/telegram/events               → Active events
POST /api/v1/telegram/events/{id}/join     → Join event
GET  /api/v1/telegram/events/{id}/leaderboard → Event leaderboard
POST /api/v1/telegram/streak/checkin      → Streak check-in
GET  /api/v1/telegram/dao/queue            → HITL review queue
```

**Quest Engine (Production-Ready):**
```
GET  /api/v1/telegram/quests/today        → Daily quests
POST /api/v1/telegram/quests/submit        → Submit quest proof
GET  /api/v1/telegram/quests/active        → Active quests
GET  /api/v1/admin/quests/hitl             → HITL queue (admin)
POST /api/v1/admin/quests/{id}/hitl-decision → HITL decision (admin)
```

**Agency & Revenue Share:**
```
GET  /api/v1/agency/assets/viral           → Curated viral assets
POST /api/v1/agency/assets/{id}/record-revenue → Record campaign revenue
PATCH /api/v1/agency/assets/{id}/use       → Mark asset as used
PATCH /api/v1/agency/assets/{id}/approve   → Approve asset
```

**Aurora Contact Telegram Dashboard:**
```
GET  /api/v1/admin/telegram/conversations  → Conversation list
GET  /api/v1/admin/telegram/conversations/{id} → Conversation detail
GET  /api/v1/admin/telegram/leads/{id}     → Lead detail
POST /api/v1/admin/telegram/conversations/{id}/send-message → Send message
POST /api/v1/admin/telegram/conversations/{id}/handoff → Human handoff
POST /api/v1/admin/telegram/leads/{id}/notes → Save lead notes
GET  /api/v1/admin/telegram/stats          → Dashboard statistics
```

**See:** `docs/NASIPQUEST_TASK_ENGINE_V3.md` for complete task engine documentation.

## 🎯 Aurora Justice Activation

Aurora Justice Engine (NovaCore modülü) tamamen **DAO-controlled**. Aktivasyon adımları:

```bash
# Complete activation (all steps)
./scripts/activate_aurora_state.sh

# Or step by step:
alembic upgrade head
python scripts/init_default_policy.py
python scripts/sync_dao_policy.py  # After contract deployment
```

**See:** 
- `docs/FINAL_ACTIVATION_CHECKLIST.md` - Complete activation guide
- `docs/DAO_ACTIVATION_CHECKLIST.md` - DAO-specific guide

## 📊 Dashboard v2 Features

**"Devran Seviyesi"** citizen state console:

### Data Layers (7-Layer Composition)
1. **Identity**: User profile, admin status
2. **Wallet**: NCR balance
3. **Loyalty**: XP, level, tier
4. **Privacy**: Consent status, recall state
5. **NovaScore**: Behavioral reputation
6. **CP State**: Ceza Puanı, regime
7. **Violations**: Recent violation history

### Lighthouse Blocks
- **Aurora Justice Health**: DAO status, policy version, on-chain info
- **Citizen Health**: NovaScore, CP, regime, trend
- **My Actions**: Quick access to Recall, Appeal, Consent Review

### Advanced Features
- **Citizen Timeline**: Event history (join, consent, violations, regime changes)
- **Trust Factors**: Account age, violation frequency, behavior risk, redline compliance
- **Real-time Updates**: Auto-refresh and polling
- **Regime-Aware UI**: Dynamic theming based on user's regime

## 🎨 UI/UX Enhancements

- **Neon Glow Effects**: Cyber-katedral vibe
- **3D Card Depth**: Hover animations
- **Ambient Light**: Pulse effects
- **Gradient Backgrounds**: Regime-aware colors
- **Motion Blur**: Smooth transitions

## 🔐 Authentication

### Web Users (Email-based)
- Email registration and login
- Password hashing with bcrypt
- JWT token generation
- Optional Telegram ID (auto-generated for web users)

### Telegram Users
- Telegram ID verification
- JWT token generation
- Seamless integration with existing system

### Dev Mode
- Quick token generation for testing
- No authentication required

See `docs/WEB_USER_AUTH.md` for details.

## 🧪 Testing

### Demo Users

Seed script creates 3 demo users:
- **AUR-SIGMA**: Clean citizen (CP 0, FULL consent)
- **AUR-TROLLER**: Problematic user (CP ~50, PROBATION regime)
- **AUR-GHOST**: Privacy-conscious (recall requested, low confidence)

Test them:
```bash
GET /api/v1/justice/case/AUR-SIGMA
GET /api/v1/justice/case/AUR-TROLLER
GET /api/v1/justice/case/AUR-GHOST
```

### Smoke Tests

```bash
# Quick consent flow test
./scripts/test_consent_flow.sh

# Full system test
./scripts/smoke_test.sh

# Enforcement test
./scripts/test_enforcement.sh
```

## 🔄 Integration

### Event Integration

FlirtMarket, OnlyVips, PokerVerse, Aurora → NovaCore'a event atar.

**Example: FlirtMarket Integration**

```python
import httpx
from decimal import Decimal

async def report_coin_spent(user_id: int, performer_id: int, amount: Decimal):
    """Report coin spent event to NovaCore."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://novacore/api/v1/events/flirt",
            json={
                "event_type": "COIN_SPENT",
                "user_id": user_id,
                "performer_id": performer_id,
                "amount": str(amount),
                "metadata": {
                    "session_id": "session_123",
                    "timestamp": "2024-01-01T00:00:00Z"
                }
            },
            headers={"Authorization": "Bearer <service_token>"}
        )
        return response.json()
```

### Enforcement Integration

**Check if action is allowed before executing:**

```python
from app.justice.enforcement import check_action_allowed

async def send_message(user_id: str, message: str):
    """Send message with enforcement check."""
    error = await check_action_allowed(
        user_id=user_id,
        action="SEND_MESSAGE",
        session=session
    )
    
    if error:
        # Return 403 with structured error
        raise HTTPException(
            status_code=403,
            detail=error.detail,
            headers={"X-Aurora-Regime": error.regime}
        )
    
    # Proceed with action
    # ...
```

**See:** `docs/FRONTEND_INTEGRATION.md` for complete integration guide.

## 🚀 CI/CD

GitHub Actions automatically runs smoke tests on push/PR:

- PostgreSQL setup
- Migration execution
- API startup
- Full smoke test
- Enforcement test

See `.github/workflows/aurora-smoke-test.yml`

## 📚 Documentation

### Core Architecture
- `docs/AURORA_STATE_ARCHITECTURE.md` - 3-layer architecture
- `docs/AURORA_JUSTICE_V2.md` - Complete Justice Stack guide
- `docs/DAO_INTEGRATION.md` - DAO governance integration
- `docs/DAO_GOVERNANCE_FLOW.md` - Governance flow
- `docs/API_DOCUMENTATION.md` - Complete API reference

### Frontend
- `docs/FRONTEND_ECOSYSTEM.md` - Frontend architecture
- `docs/FRONTEND_INTEGRATION.md` - Integration guide
- `docs/WEB_USER_AUTH.md` - Web authentication
- `docs/I18N_SETUP.md` - Multi-language support (i18n) setup

### Telegram & Task Engine
- `docs/NASIPQUEST_TASK_ENGINE_V3.md` - Complete task engine architecture
- `docs/TELEGRAM_BRIDGE.md` - Telegram bot integration
- `docs/TELEGRAM_TOKENS_EXPLAINED.md` - Token configuration guide
- `docs/BRIDGE_TOKEN_EXPLAINED.md` - Bridge token security
- `docs/LINK_SECRET_EXPLAINED.md` - Start parameter HMAC
- `docs/OMBUDSMAN_INTEGRATION.md` - Ombudsman Paneli ve HITL quest review

### Operations
- `docs/OMBUDSMAN_INTEGRATION.md` - Ombudsman/Operator integration
- `docs/RECALL_PROCESS.md` - Recall process details
- `docs/DEMO_FLOW.md` - Demo flow for pitching
- `docs/FINAL_ACTIVATION_CHECKLIST.md` - Complete activation guide
- `docs/DAO_ACTIVATION_CHECKLIST.md` - DAO-specific guide

### Testing
- `scripts/README_TESTING.md` - Testing guide
- `scripts/QUICK_START.md` - Quick start guide

## 🎯 Sorumluluklar

| Modül | Açıklama |
|-------|----------|
| **Identity/SSO** | Telegram ID ↔ internal `user_id`, JWT üretimi, Email auth (EmailLoginRequest, EmailRegisterRequest) |
| **Wallet/NCR Ledger** | NCR bakiyesi, harcama, kazanma, rake, fee, treasury |
| **XP/Loyalty** | XP events, level, tier (Bronze/Silver/Gold/Diamond) |
| **Agency** | Agency, Performer, operator modelleri, gelir paylaşımı |
| **Events** | FlirtMarket, OnlyVips, PokerVerse, Aurora event ingest |
| **Admin** | Treasury summary, top users, health & stats, user management |
| **Consent** | Consent flow, privacy profiles, immutable ledger, recall |
| **Justice** | Violation logging, CP calculation, regime enforcement (DAO-controlled) |
| **NovaScore** | Behavioral reputation score with CP integration |
| **Telemetry** | Growth & education event tracking |
| **DAO** | Policy governance, on-chain sync, version control |
| **Frontend** | Citizen Portal, Admin Panel, Shared UI/Hooks, i18n (tr/en/ru) |
| **Telegram Gateway** | NasipQuest bot integration, task engine, referral system |
| **Quest Engine** | Production-ready quest system (UserQuest, QuestFactory, HITL) |
| **AbuseGuard** | RiskScore calculation, abuse detection, reward multipliers, cooldown enforcement |
| **Treasury Cap** | Daily NCR limit, damping multipliers, economic sustainability |
| **NCR Price Stabilization** | Dynamic price adjustment based on coverage ratio and flow index |
| **Agency Pipeline** | Creator → Agency conversion, Revenue Share (20/40/40), Content Curator |
| **Aurora Contact** | Telegram User Bot (Telethon), AI/Human hybrid chat, Lead Intelligence |

## 🛠️ Troubleshooting

### Common Issues

#### Backend won't start

```bash
# Check PostgreSQL is running
docker ps | grep postgres
# or
brew services list | grep postgresql

# Check database connection
psql -U novacore -d novacore -c "SELECT 1;"

# Check port 8000
lsof -i :8000
# Kill if needed: kill -9 <PID>
```

#### Migration errors

```bash
# Check current migration state
alembic current

# View migration history
alembic history

# Rollback if needed
alembic downgrade -1

# Re-run migrations
alembic upgrade head
```

#### Frontend build errors

```bash
# Clear node_modules and reinstall
rm -rf node_modules apps/*/node_modules packages/*/node_modules
npm install

# Clear Next.js cache
cd apps/citizen-portal
rm -rf .next
npm run dev
```

#### "Failed to fetch" in Dashboard

1. **Check backend is running:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Check token in localStorage:**
   - Open browser DevTools → Application → Local Storage
   - Verify `aurora_token` exists

3. **Check API URL:**
   - Verify `NEXT_PUBLIC_AURORA_API_URL` in `.env.local`

4. **Check CORS:**
   - Backend should allow `http://localhost:3000`

#### Database connection errors

```bash
# Docker PostgreSQL
docker-compose up -d postgres
docker logs novacore-postgres

# Homebrew PostgreSQL
brew services restart postgresql@16
psql -U novacore -d novacore
```

**See:** `docs/FINAL_ACTIVATION_CHECKLIST.md` for detailed troubleshooting.

## 🔧 Development Workflow

### Backend Development

```bash
# Start with auto-reload
uvicorn app.main:app --reload

# Run specific tests
pytest tests/test_consent.py
pytest tests/test_justice.py

# Create new migration
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### Frontend Development

```bash
# Citizen Portal
cd apps/citizen-portal
npm run dev

# Build shared libraries
cd packages/aurora-ui
npm run build

cd ../aurora-hooks
npm run build
```

### Monorepo Commands

```bash
# Install all dependencies
npm install

# Build all packages
npm run build --workspaces

# Run tests (if configured)
npm test --workspaces
```

## 📊 Common Commands

### Database

```bash
# Connect to database
docker exec -it novacore-postgres psql -U novacore -d novacore

# Check tables
\dt

# View consent records
SELECT * FROM consent_records LIMIT 5;

# View CP state
SELECT user_id, cp_value, regime FROM justice_cp_state;
```

### API Testing

```bash
# Get token (dev mode)
curl -X GET "http://localhost:8000/api/v1/dev/token?user_id=9"

# Test consent flow
curl -X POST http://localhost:8000/api/v1/consent/session \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "9", "client_fingerprint": "test"}'

# Get NovaScore
curl http://localhost:8000/api/v1/nova-score/me \
  -H "Authorization: Bearer <token>"
```

## 🎉 Version History

**v0.5** - Production-Ready Quest Engine & Aurora Contact
- ✅ Production-Ready Quest Engine (UserQuest, QuestFactory, QuestService)
- ✅ AbuseGuard integration (RiskScore, abuse detection, reward multipliers)
- ✅ Treasury Cap system (daily NCR limits, damping multipliers)
- ✅ NCR Price Stabilization Algorithm (coverage ratio, flow index, EMA smoothing)
- ✅ Ombudsman Paneli (HITL Quest Monitor) - RiskScore ≥ 6.0 quest review
- ✅ Creator → Agency Conversion Pipeline (ContentCurator, CreatorAsset)
- ✅ Revenue Share mekanizması (20/40/40 paylaşım: Creator/Treasury/Agency)
- ✅ Aurora Contact Telegram Dashboard (3-column layout, AI/Human hybrid chat)
- ✅ Telethon User Bot integration (Aurora Contact Business Hunter)
- ✅ ChatManager (Grok/GPT hybrid routing, intent classification, tool calling)
- ✅ NasipQuest Economy Dashboard (NCR price, Treasury health, metrics)

**v0.4** - i18n & Task Engine
- ✅ Multi-language support (Türkçe, English, Русский)
- ✅ next-intl integration
- ✅ Locale-aware routing
- ✅ NasipQuest Task Engine v3
- ✅ Task submission & reward system
- ✅ Referral system
- ✅ Event bonus system
- ✅ Leaderboard & profile cards

**v0.3** - Dashboard v2: Devran-level citizen state console
- ✅ Unified `useCitizenState` hook
- ✅ Aurora State Health panel
- ✅ Citizen Timeline
- ✅ Trust Factors
- ✅ Enhanced UI/UX (neon, glow, depth)
- ✅ Real-time data integration

**v0.2** - Aurora Justice Stack v2.0
- ✅ DAO-controlled policy
- ✅ 3-layer architecture
- ✅ Frontend ecosystem
- ✅ Web user authentication
- ✅ Admin panel

**v0.1** - Initial release
- ✅ Core modules
- ✅ Consent & Justice
- ✅ NovaScore

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Before submitting:**
- Run tests: `./scripts/smoke_test.sh`
- Check linting: `npm run lint`
- Update documentation if needed

## 📞 Support

- **Documentation:** See `docs/` directory
- **Issues:** GitHub Issues
- **Quick Start:** `scripts/QUICK_START.md`
- **Activation:** `docs/FINAL_ACTIVATION_CHECKLIST.md`

---

**Aurora = DAO-controlled, constitution-protected, execution-enforced digital state.** 🖤
