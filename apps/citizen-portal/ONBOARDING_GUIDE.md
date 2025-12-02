# Citizen Portal - Landing & Onboarding Guide

## Overview

Citizen Portal now includes:
- **Landing Page** (`/`) - Marketing + manifesto
- **Onboarding Wizard** (`/onboarding`) - 3-step citizen registration
- **Dashboard** (`/dashboard`) - Real API integration

## Landing Page Features

### Hero Section
- Aurora branding
- "Become a Citizen" CTA
- "Open Dashboard" link
- Key features (DAO, Justice, Constitution)

### How It Works
- 3-step explanation
- Consent & Data Sovereignty
- NovaScore & Regime
- DAO-Governed Policy

### CTA Section
- Final call-to-action
- Direct link to onboarding

## Onboarding Wizard

### Step 1: Intro
- Explains Aurora as protocol-state
- Key principles
- "Continue" button

### Step 2: Consent
- Embedded ConsentFlow component
- Multi-step consent agreement
- Must complete before proceeding

### Step 3: NovaScore
- **Real API Integration**
- Fetches NovaScore using `useNovaScore()`
- Fetches CP state using `useJustice()`
- Shows actual data or demo fallback
- "Go to Dashboard" CTA

## API Integration

### Real Data Flow

1. **Onboarding Step 3:**
   ```tsx
   const { score } = useNovaScore()  // Real API call
   const { cpState } = useJustice()  // Real API call
   ```

2. **Dashboard:**
   ```tsx
   const { score, refetch } = useNovaScore()  // With refresh
   const { cpState, refetch } = useJustice()  // With refresh
   ```

### Fallback Behavior

- If API unavailable: Shows demo data with warning
- If API error: Shows error message
- If no data: Shows placeholder

## Testing

### Local Development

```bash
# 1. Start Aurora API
cd ../..
uvicorn app.main:app --reload

# 2. Start Citizen Portal
cd apps/citizen-portal
npm run dev

# 3. Test flow
# - Visit http://localhost:3000
# - Click "Become a Citizen"
# - Complete onboarding
# - Verify dashboard shows real data
```

### Without API

Portal works in demo mode:
- Landing page shows mock data
- Onboarding shows demo NovaScore
- Dashboard shows demo with warning

## Next Steps

- [ ] Auth system integration
- [ ] Real-time updates (WebSocket)
- [ ] Analytics events
- [ ] SEO optimization
- [ ] Share cards (OG images)

