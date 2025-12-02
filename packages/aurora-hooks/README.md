# Aurora Hooks Library

Shared React hooks for Aurora API integration.

## Installation

```bash
cd packages/aurora-hooks
npm install
npm run build
```

## Usage

```tsx
import { useNovaScore, useJustice, usePolicy } from '@aurora/hooks'

function MyComponent() {
  const { score, loading } = useNovaScore()
  const { cpState } = useJustice()
  const { policy } = usePolicy()

  // ...
}
```

## Hooks

- **useNovaScore** - Fetch NovaScore data
- **useJustice** - Fetch CP state and violations
- **useEnforcementError** - Handle enforcement errors
- **useConsentFlow** - Manage consent flow
- **usePolicy** - Fetch current DAO policy
- **useAuroraAPI** - Base API client

## Configuration

Set environment variable:

```bash
VITE_AURORA_API_URL=http://localhost:8000/api/v1
```

