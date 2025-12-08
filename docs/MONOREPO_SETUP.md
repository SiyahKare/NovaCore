# Aurora Monorepo Setup

## Structure

```
NovaCore/
├── package.json          # Root workspace config
├── packages/
│   ├── aurora-ui/        # Component library
│   └── aurora-hooks/     # Hooks library
└── apps/
    └── citizen-portal/   # Next.js app
```

## Setup

### Option 1: Root Install (Recommended)

```bash
# From root directory
npm install

# This installs all packages and apps
```

### Option 2: Individual Setup

```bash
# 1. Build shared libraries
cd packages/aurora-ui
npm install
npm run build

cd ../aurora-hooks
npm install
npm run build

# 2. Install portal
cd ../../apps/citizen-portal
npm install
```

## Development

### Start API
```bash
# From root
uvicorn app.main:app --reload
```

### Start Portal
```bash
# From root
cd apps/citizen-portal
npm run dev

# Or from root (if using npm workspaces)
npm run dev --workspace=apps/citizen-portal
```

## Troubleshooting

### workspace:* not supported

If npm doesn't support `workspace:*`, use `file:` protocol:
```json
{
  "dependencies": {
    "@aurora/ui": "file:../../packages/aurora-ui",
    "@aurora/hooks": "file:../../packages/aurora-hooks"
  }
}
```

### Module not found

1. Build shared libraries first
2. Ensure `dist/` folders exist
3. Restart dev server

### Port conflicts

```bash
# Kill port 3000
lsof -ti:3000 | xargs kill -9

# Or use different port
PORT=3001 npm run dev
```

