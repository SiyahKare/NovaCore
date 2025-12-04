# NovaCore Citizen Portal

SiyahKare Cumhuriyeti vatandaşlarının kullandığı NovaCore frontend; Aurora Justice Engine bileşenlerini de içerir.

## Tech Stack

- **Next.js 14** (App Router)
- **TypeScript**
- **Tailwind CSS**
- **@aurora/ui** - Shared component library
- **@aurora/hooks** - Shared React hooks

## Getting Started

### Prerequisites

- Node.js 18+
- NovaCore API running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Copy environment file
cp .env.local.example .env.local

# Update .env.local with your API URL
# NEXT_PUBLIC_AURORA_API_URL=http://localhost:8000/api/v1 (legacy env name for NovaCore API)
```

### Development

```bash
# Start dev server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build

```bash
# Build for production
npm run build

# Start production server
npm start
```

## Project Structure

```
apps/citizen-portal/
├── app/              # Next.js App Router pages
│   ├── dashboard/   # Citizen dashboard
│   ├── identity/    # Identity page
│   ├── consent/     # Consent flow
│   └── justice/     # Justice & appeals
├── components/       # Shared components
├── lib/              # Utilities (api, auth, constants)
└── public/           # Static assets
```

## Features

- **Dashboard** - Complete citizen profile overview
- **Identity** - Digital citizenship information
- **Consent** - Privacy and consent management
- **Justice** - CP status, violations, appeals

## Integration

Uses shared libraries:
- `@aurora/ui` - Components (RegimeBadge, NovaScoreCard, etc.)
- `@aurora/hooks` - API hooks (useNovaScore, useJustice, etc.)

## Environment Variables

- `NEXT_PUBLIC_AURORA_API_URL` - Aurora API base URL
- `NEXT_PUBLIC_AURORA_ENV` - Environment (dev/prod)
- `NEXT_PUBLIC_AURORA_CONSTITUTION_HASH` - Constitution hash (optional)

## Next Steps

- [ ] Auth system (OAuth/Identity NFT)
- [ ] Real-time updates (WebSocket)
- [ ] Advanced dashboard features
- [ ] Landing page & onboarding
- [ ] Mobile optimization

