# NovaCore Frontend Ecosystem

## 🏗️ Architecture Overview

NovaCore Frontend Ecosystem is built as a **monorepo** with shared libraries and multiple applications:

```
NovaCore/
├── packages/
│   ├── aurora-ui/          # Shared component library
│   └── aurora-hooks/       # Shared React hooks
├── apps/
│   ├── citizen-portal/    # Main citizen frontend (Next.js 14)
│   ├── admin-panel/       # Admin/Ombudsman interface
│   ├── telegram-miniapp/  # Telegram mini app
│   └── aurora-academy/    # Education platform
└── frontend/              # Legacy Vite app (to be migrated)
```

## 📦 Shared Libraries

### `@aurora/ui` - Component Library

**Components:**
- `RegimeBadge` - Visual regime indicator
- `RegimeBanner` - Contextual regime warnings
- `NovaScoreCard` - NovaScore display
- `CPTrendGraph` - CP trend visualization
- `PolicyBreakdown` - Policy parameters
- `DAOChangeLog` - Policy change history
- `EnforcementErrorModal` - Error handling
- `ConsentFlow` - Multi-step consent
- `AppealForm` - Appeal submission
- `RecallRequest` - Data recall

**Design System:**
- Dark cyberpunk theme
- Purple (#8b5cf6), Sky (#0ea5e9), Neon (#00f5ff)
- Semi-transparent cards with blur
- Glow effects for important states

### `@aurora/hooks` - API Hooks

**Hooks:**
- `useNovaScore` - Fetch NovaScore
- `useJustice` - Fetch CP state
- `useEnforcementError` - Handle errors
- `useConsentFlow` - Consent management
- `usePolicy` - DAO policy
- `useAuroraAPI` - Base API client

## 🎯 Applications

### 1. Citizen Portal (Next.js 14)

**Purpose:** Main citizen-facing frontend

**Features:**
- Dashboard
- Profile & NovaScore
- Justice/Regime status
- Appeals & Requests
- Constitution viewer
- DAO Policy Explorer
- NovaCore Academy access

**Tech Stack:**
- Next.js 14 (App Router)
- Server Actions
- shadcn/ui
- Tailwind CSS
- Zustand (state)
- SWR (data fetching)

### 2. Admin/Ombudsman Panel

**Purpose:** Management interface

**Features:**
- Case file viewer
- CP/Regime override
- Stats dashboard
- Violation stream
- Policy proposal drafts
- Enforcement alerts

**Design:**
- Dark control room aesthetic
- Radar/heatmap visualizations
- Real-time monitoring

### 3. Telegram Mini-App

**Purpose:** Lightweight mobile access

**Features:**
- NovaScore widget
- Daily health status
- Regime badge
- Enforcement warnings
- Micro-consent
- DAO feed

### 4. NovaCore Academy

**Purpose:** Education & simulation

**Features:**
- Mini lessons
- Interactive simulation playground
- Badge system
- Policy explorer

## 🚀 Getting Started

### Setup Monorepo

```bash
# Install dependencies
npm install

# Build shared libraries
cd packages/aurora-ui && npm run build
cd packages/aurora-hooks && npm run build

# Start Citizen Portal
cd apps/citizen-portal && npm run dev
```

### Using Shared Libraries

```tsx
// In any app
import { RegimeBadge, NovaScoreCard } from '@aurora/ui'
import { useNovaScore, useJustice } from '@aurora/hooks'
import '@aurora/ui/styles'

function MyComponent() {
  const { score } = useNovaScore()
  const { cpState } = useJustice()

  return (
    <div>
      <RegimeBadge regime={cpState?.regime || 'NORMAL'} />
      {score && <NovaScoreCard novaScore={score} />}
    </div>
  )
}
```

## 📐 Design Principles

1. **Consistency** - Shared components ensure visual consistency
2. **Reusability** - Write once, use everywhere
3. **Type Safety** - Full TypeScript support
4. **Performance** - Optimized builds, tree-shaking
5. **Accessibility** - WCAG compliant components

## 🔄 Migration Path

Current `frontend/` directory will be migrated to:
- Components → `packages/aurora-ui`
- Hooks → `packages/aurora-hooks`
- App → `apps/citizen-portal` (Next.js 14)

## 📚 Documentation

- Component API: `packages/aurora-ui/README.md`
- Hooks API: `packages/aurora-hooks/README.md`
- Integration Guide: `docs/FRONTEND_INTEGRATION.md`

