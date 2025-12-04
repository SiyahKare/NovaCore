# NovaCore Project Structure

## 📁 Directory Tree

```
NovaCore/
├── app/                          # Backend (FastAPI)
│   ├── core/                     # Core utilities
│   │   ├── config.py            # Settings & environment
│   │   ├── db.py                # Database connection
│   │   ├── security.py         # JWT, auth helpers
│   │   └── logging.py          # Structured logging
│   ├── identity/                 # User SSO & Auth
│   │   ├── models.py           # User model
│   │   ├── routes.py           # Auth endpoints
│   │   └── auth_email.py       # Email auth logic
│   ├── wallet/                   # NCR Ledger
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── routes.py
│   │   └── service.py
│   ├── xp_loyalty/               # XP & Level System
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── routes.py
│   │   └── service.py
│   ├── agency/                    # Agency & Performers
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── routes.py
│   ├── events/                    # Event Ingest
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── routes.py
│   ├── admin/                     # Admin Panel Backend
│   │   ├── routes.py
│   │   └── aurora_stats.py
│   ├── consent/                   # Consent & Privacy
│   │   ├── models.py            # ConsentSession, ConsentRecord, UserPrivacyProfile
│   │   ├── schemas.py
│   │   └── router.py           # Consent flow endpoints
│   ├── justice/                   # Justice & CP System
│   │   ├── models.py           # ViolationLog, UserCpState
│   │   ├── schemas.py
│   │   ├── router.py           # Justice endpoints
│   │   ├── policy.py           # Regime calculation
│   │   ├── policy_models.py    # JusticePolicyParams
│   │   └── policy_service.py   # Policy management
│   ├── nova_score/               # NovaScore Calculation
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── router.py
│   ├── telemetry/                 # Growth & Education Tracking
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── router.py
│   ├── flirtmarket/              # FlirtMarket Integration
│   │   └── routes.py
│   └── main.py                   # FastAPI app entry point
│
├── apps/                          # Frontend Applications
│   └── citizen-portal/            # Next.js 14 Citizen Portal
│       ├── app/
│       │   ├── layout.tsx        # Root layout
│       │   ├── page.tsx          # Landing page
│       │   ├── dashboard/        # Dashboard v2
│       │   │   └── page.tsx
│       │   ├── onboarding/       # Multi-step onboarding
│       │   │   └── page.tsx
│       │   ├── academy/          # Educational content
│       │   │   ├── page.tsx
│       │   │   └── start-here/
│       │   ├── consent/         # Consent management
│       │   │   └── page.tsx
│       │   ├── justice/         # Case file viewer
│       │   │   └── page.tsx
│       │   ├── identity/        # Identity page
│       │   │   └── page.tsx
│       │   ├── admin/           # Admin Panel
│       │   │   └── aurora/
│       │   │       ├── layout.tsx
│       │   │       ├── page.tsx        # Overview
│       │   │       ├── stats/
│       │   │       ├── case/
│       │   │       ├── policy/
│       │   │       ├── violations/
│       │   │       ├── users/
│       │   │       └── growth/
│       │   ├── about/           # About page
│       │   ├── demo/            # Demo page
│       │   └── globals.css      # Global styles
│       ├── components/
│       │   ├── ProtectedView.tsx
│       │   └── NovaCoreNav.tsx
│       ├── lib/
│       │   └── auth.ts          # Auth utilities
│       ├── package.json
│       ├── next.config.js
│       └── tailwind.config.ts
│
├── packages/                      # Shared Libraries
│   ├── aurora-ui/                # Shared React Components
│   │   ├── src/
│   │   │   ├── components/
│   │   │   │   ├── RegimeBadge.tsx
│   │   │   │   ├── RegimeBanner.tsx
│   │   │   │   ├── NovaScoreCard.tsx
│   │   │   │   ├── CPTrendGraph.tsx
│   │   │   │   ├── PolicyBreakdown.tsx
│   │   │   │   ├── DAOChangeLog.tsx
│   │   │   │   ├── EnforcementErrorModal.tsx
│   │   │   │   ├── ConsentFlow.tsx
│   │   │   │   ├── AppealForm.tsx
│   │   │   │   ├── RecallRequest.tsx
│   │   │   │   ├── AuroraStatsPanel.tsx
│   │   │   │   ├── AuroraCaseView.tsx
│   │   │   │   ├── AuroraStateHealth.tsx
│   │   │   │   ├── CitizenTimeline.tsx
│   │   │   │   └── TrustFactors.tsx
│   │   │   ├── types/
│   │   │   │   └── index.ts
│   │   │   ├── styles.css
│   │   │   └── index.ts
│   │   └── package.json
│   │
│   └── aurora-hooks/             # Shared React Hooks
│       ├── src/
│       │   ├── useAuroraAPI.ts
│       │   ├── useNovaScore.ts
│       │   ├── useJustice.ts
│       │   ├── usePolicy.ts
│       │   ├── useRegimeTheme.ts
│       │   ├── useCurrentCitizen.ts
│       │   ├── useConsentFlow.ts
│       │   ├── useAuroraEvents.ts
│       │   ├── useGrowthMetrics.ts
│       │   ├── useCitizenState.ts
│       │   └── index.ts
│       └── package.json
│
├── scripts/                       # Utility Scripts
│   ├── activate_aurora_state.sh  # Complete activation
│   ├── activate_aurora_dao.sh    # DAO activation
│   ├── test_consent_flow.sh      # Consent flow test
│   ├── smoke_test.sh             # Full system test
│   ├── test_enforcement.sh       # Enforcement test
│   ├── test_dao_integration.sh   # DAO integration test
│   ├── init_default_policy.py    # Seed default policy
│   ├── sync_dao_policy.py        # Sync from DAO contract
│   ├── seed_aurora_demo.py       # Demo users seed
│   ├── QUICK_START.md
│   └── README_TESTING.md
│
├── docs/                          # Documentation
│   ├── AURORA_STATE_ARCHITECTURE.md
│   ├── AURORA_JUSTICE_V2.md
│   ├── DAO_INTEGRATION.md
│   ├── DAO_GOVERNANCE_FLOW.md
│   ├── FRONTEND_ECOSYSTEM.md
│   ├── FRONTEND_INTEGRATION.md
│   ├── WEB_USER_AUTH.md
│   ├── OMBUDSMAN_INTEGRATION.md
│   ├── RECALL_PROCESS.md
│   ├── DEMO_FLOW.md
│   ├── FINAL_ACTIVATION_CHECKLIST.md
│   ├── DAO_ACTIVATION_CHECKLIST.md
│   └── TESTING_RITUAL.md
│
├── alembic/                       # Database Migrations
│   ├── versions/
│   │   └── *.py                  # Migration files
│   ├── env.py
│   └── alembic.ini
│
├── contracts/                     # Smart Contracts (if exists)
│   ├── AuroraPolicyConfig.sol
│   └── AuroraConstitution.sol
│
├── tests/                         # Test Files
│   └── ...
│
├── .github/
│   └── workflows/
│       └── aurora-smoke-test.yml  # CI/CD
│
├── .env                           # Environment variables
├── .env.example                   # Environment template
├── docker-compose.yml             # PostgreSQL setup
├── requirements.txt              # Python dependencies
├── package.json                  # Monorepo root
├── README.md                     # Main documentation
└── PROJECT_STRUCTURE.md          # This file
```

## 📊 Key Directories

### Backend (`app/`)

| Directory | Purpose |
|-----------|---------|
| `core/` | Config, DB, Security, Logging |
| `identity/` | User SSO, JWT, Email Auth |
| `wallet/` | NCR Ledger operations |
| `xp_loyalty/` | XP & Level system |
| `consent/` | Consent flow, privacy profiles |
| `justice/` | Violation logging, CP, enforcement |
| `nova_score/` | Behavioral reputation score |
| `telemetry/` | Growth & education tracking |
| `admin/` | Admin panel backend |

### Frontend (`apps/`)

| Directory | Purpose |
|-----------|---------|
| `citizen-portal/` | Next.js 14 Citizen Portal |
| `citizen-portal/app/dashboard/` | Dashboard v2 |
| `citizen-portal/app/onboarding/` | Multi-step onboarding |
| `citizen-portal/app/admin/` | Admin Panel |

### Shared Libraries (`packages/`)

| Package | Purpose |
|---------|---------|
| `aurora-ui/` | Shared React components |
| `aurora-hooks/` | Shared data hooks |

## 🔑 Key Files

### Backend Entry Points
- `app/main.py` - FastAPI application
- `alembic/env.py` - Migration environment

### Frontend Entry Points
- `apps/citizen-portal/app/layout.tsx` - Root layout
- `apps/citizen-portal/app/page.tsx` - Landing page

### Configuration
- `.env` - Environment variables
- `docker-compose.yml` - PostgreSQL setup
- `requirements.txt` - Python dependencies
- `package.json` - Monorepo configuration

### Documentation
- `README.md` - Main documentation
- `docs/` - Detailed guides
- `scripts/QUICK_START.md` - Quick start guide

## 📈 File Statistics

```
Backend Python Files:     ~60+
Frontend TypeScript Files: ~120+
Documentation Files:       ~20
Script Files:              ~15
Migration Files:           ~10+
Component Files:           ~20
Hook Files:                ~10
```

## 🔍 Detailed Structure

### Backend Modules (`app/`)

```
app/
├── core/                    # Core utilities (4 files)
│   ├── config.py          # Environment & settings
│   ├── db.py              # Database connection & session
│   ├── security.py        # JWT, auth, get_current_user
│   └── logging.py         # Structured logging
│
├── identity/               # User SSO & Authentication (5 files)
│   ├── models.py          # User model
│   ├── routes.py          # Auth endpoints
│   ├── schemas.py         # Pydantic schemas
│   ├── service.py         # Business logic
│   └── auth_email.py      # Email auth (bcrypt)
│
├── wallet/                 # NCR Ledger (4 files)
│   ├── models.py          # Account, LedgerEntry
│   ├── schemas.py         # BalanceResponse, Transaction
│   ├── routes.py          # Wallet endpoints
│   └── service.py         # Wallet operations
│
├── xp_loyalty/             # XP & Level System (4 files)
│   ├── models.py          # UserLoyalty, XpEvent
│   ├── schemas.py         # LoyaltyProfileResponse
│   ├── routes.py          # Loyalty endpoints
│   └── service.py         # XP calculation
│
├── consent/                # Consent & Privacy (3 files)
│   ├── models.py          # ConsentSession, ConsentRecord, UserPrivacyProfile
│   ├── schemas.py         # Consent schemas
│   └── router.py          # Consent flow endpoints
│
├── justice/                # Justice & CP System (6 files)
│   ├── models.py          # ViolationLog, UserCpState
│   ├── schemas.py         # ViolationResponse, CpStateResponse
│   ├── router.py          # Justice endpoints
│   ├── policy.py          # Regime calculation
│   ├── policy_models.py   # JusticePolicyParams
│   └── policy_service.py  # Policy management
│
├── nova_score/             # NovaScore Calculation (3 files)
│   ├── schemas.py         # NovaScoreResponse
│   └── router.py          # NovaScore endpoints
│
├── telemetry/              # Growth Tracking (3 files)
│   ├── models.py          # TelemetryEvent
│   ├── schemas.py         # Event schemas
│   └── router.py          # Telemetry endpoints
│
├── admin/                  # Admin Panel Backend (2 files)
│   ├── routes.py          # Admin endpoints
│   └── aurora_stats.py    # Stats calculation
│
└── main.py                 # FastAPI app entry point
```

### Frontend Structure (`apps/citizen-portal/`)

```
apps/citizen-portal/
├── app/                    # Next.js App Router
│   ├── layout.tsx         # Root layout with NovaCoreShell
│   ├── page.tsx           # Landing page
│   ├── globals.css        # Global styles (neon, glow effects)
│   │
│   ├── dashboard/         # Dashboard v2
│   │   └── page.tsx       # Main dashboard
│   │
│   ├── onboarding/        # Multi-step onboarding
│   │   └── page.tsx       # Auth → Consent → NovaScore
│   │
│   ├── academy/           # Educational content
│   │   ├── page.tsx       # Academy overview
│   │   ├── start-here/    # "7 Dakikada Aurora" track
│   │   └── modules/       # Module pages
│   │       ├── constitution/
│   │       ├── novascore/
│   │       ├── justice/
│   │       └── dao/
│   │
│   ├── consent/          # Consent management
│   │   └── page.tsx      # Detailed consent view + recall
│   │
│   ├── justice/          # Case file viewer
│   │   └── page.tsx     # User case file
│   │
│   ├── identity/         # Identity page
│   │   └── page.tsx
│   │
│   ├── admin/            # Admin Panel
│   │   └── aurora/
│   │       ├── layout.tsx      # Admin layout
│   │       ├── page.tsx        # Overview
│   │       ├── stats/          # Stats dashboard
│   │       ├── case/           # Case viewer
│   │       ├── policy/         # Policy viewer
│   │       ├── violations/    # Violation stream
│   │       ├── users/         # User management
│   │       └── growth/        # Growth metrics
│   │
│   ├── about/            # About page
│   │   └── page.tsx
│   │
│   └── demo/             # Demo page
│       └── page.tsx
│
├── components/           # App-specific components
│   ├── ProtectedView.tsx # Auth guard
│   └── NovaCoreNav.tsx     # Navigation
│
└── lib/                  # Utilities
    └── auth.ts           # Auth helpers
```

### Shared Libraries (`packages/`)

```
packages/
├── aurora-ui/            # Component Library
│   └── src/
│       ├── components/   # 15+ components
│       ├── types/        # TypeScript types
│       └── styles.css    # Shared styles
│
└── aurora-hooks/        # Data Hooks
    └── src/             # 10+ hooks
```

### Scripts (`scripts/`)

```
scripts/
├── activate_aurora_state.sh    # Complete activation
├── activate_aurora_dao.sh       # DAO activation
├── test_consent_flow.sh        # Consent test
├── smoke_test.sh               # Full system test
├── test_enforcement.sh         # Enforcement test
├── test_dao_integration.sh     # DAO test
├── init_default_policy.py      # Policy seed
├── sync_dao_policy.py          # DAO sync
└── seed_aurora_demo.py         # Demo users
```

### Documentation (`docs/`)

```
docs/
├── AURORA_STATE_ARCHITECTURE.md    # 3-layer architecture
├── AURORA_JUSTICE_V2.md            # Justice stack guide
├── DAO_INTEGRATION.md              # DAO governance
├── FRONTEND_ECOSYSTEM.md           # Frontend architecture
├── FRONTEND_INTEGRATION.md         # Integration guide
├── WEB_USER_AUTH.md                # Web authentication
├── DEMO_FLOW.md                   # Demo script
├── FINAL_ACTIVATION_CHECKLIST.md   # Activation guide
└── ... (20+ docs)
```

## 🎯 Entry Points

### Backend
```bash
uvicorn app.main:app --reload
```

### Frontend
```bash
cd apps/citizen-portal
npm run dev
```

### Database
```bash
alembic upgrade head
```

---

**Last Updated:** Dashboard v2 release

