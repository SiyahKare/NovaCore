# NovaCore Frontend

Aurora Justice Stack Frontend - React + TypeScript + Vite

## Quick Start

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build
```

## Development

Frontend runs on `http://localhost:3000` and proxies API requests to `http://localhost:8000`.

## Features

- **Aurora Case View**: Complete case file viewer for Ombudsman
- **Aurora Stats Panel**: Real-time statistics dashboard
- **Regime Badge**: Visual regime indicators
- **Regime Banner**: Contextual regime warnings
- **Enforcement Error Modal**: Aurora-style error handling
- **Send Message Form**: Example FlirtMarket integration

## Project Structure

```
frontend/
├── src/
│   ├── features/
│   │   ├── justice/      # Aurora Justice components
│   │   └── flirtmarket/  # FlirtMarket integration examples
│   ├── App.tsx           # Main app component
│   └── main.tsx          # Entry point
├── package.json
└── vite.config.ts
```

