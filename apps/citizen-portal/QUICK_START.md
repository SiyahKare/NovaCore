# Citizen Portal - Quick Start

## Prerequisites

1. **Aurora API running:**
   ```bash
   # In NovaCore root
   uvicorn app.main:app --reload
   ```

2. **Shared libraries built:**
   ```bash
   # Build UI library
   cd ../../packages/aurora-ui
   npm install
   npm run build

   # Build Hooks library
   cd ../aurora-hooks
   npm install
   npm run build
   ```

## Setup

```bash
cd apps/citizen-portal

# Install dependencies
npm install

# Setup environment
cp .env.local.example .env.local
# Edit .env.local if needed (default: http://localhost:8000/api/v1)

# Start dev server
npm run dev
```

## Access

- **Portal:** http://localhost:3000
- **API:** http://localhost:8000

## Troubleshooting

### Port 3000 already in use

```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Or use different port
PORT=3001 npm run dev
```

### Module not found: @aurora/ui

Build shared libraries first:
```bash
cd ../../packages/aurora-ui && npm run build
cd ../aurora-hooks && npm run build
```

### API connection errors

1. Check API is running:
   ```bash
   curl http://localhost:8000/health
   ```

2. Check API URL in `.env.local`:
   ```
   NEXT_PUBLIC_AURORA_API_URL=http://localhost:8000/api/v1
   ```

### TypeScript errors

```bash
npm run type-check
```

## Development Flow

1. **Start API** (in NovaCore root):
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Start Portal** (in apps/citizen-portal):
   ```bash
   npm run dev
   ```

3. **Test:**
   - Visit http://localhost:3000
   - Click "Become a Citizen"
   - Complete onboarding
   - Check dashboard for real data

## Features

- ✅ Landing page with marketing
- ✅ 3-step onboarding wizard
- ✅ Real API integration
- ✅ Dashboard with live data
- ✅ Error handling & fallbacks

