# Citizen Portal Setup Guide

## Quick Start

```bash
cd apps/citizen-portal

# 1. Install dependencies
npm install

# 2. Setup environment
cp .env.local.example .env.local
# Edit .env.local with your API URL

# 3. Build shared libraries first
cd ../../packages/aurora-ui && npm install && npm run build
cd ../aurora-hooks && npm install && npm run build

# 4. Start dev server
cd ../../apps/citizen-portal
npm run dev
```

## Troubleshooting

### Module not found: @aurora/ui

Build the shared libraries first:
```bash
cd ../../packages/aurora-ui && npm run build
cd ../aurora-hooks && npm run build
```

### API connection errors

Ensure Aurora API is running:
```bash
# In NovaCore root
uvicorn app.main:app --reload
```

### TypeScript errors

Run type check:
```bash
npm run type-check
```

## Development

The portal uses:
- Next.js 14 App Router
- Shared components from `@aurora/ui`
- Shared hooks from `@aurora/hooks`
- Tailwind CSS for styling

All pages are client components for now (can be optimized with Server Components later).
