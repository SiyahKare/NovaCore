# Aurora UI Component Library

Shared component library for all Aurora frontend applications.

## Installation

```bash
cd packages/aurora-ui
npm install
npm run build
```

## Usage

```tsx
import { RegimeBadge, NovaScoreCard, EnforcementErrorModal } from '@aurora/ui'
import '@aurora/ui/styles'

function MyComponent() {
  return (
    <div>
      <RegimeBadge regime="LOCKDOWN" />
      <NovaScoreCard novaScore={scoreData} />
    </div>
  )
}
```

## Components

- **RegimeBadge** - Visual regime indicator
- **RegimeBanner** - Contextual regime warnings
- **NovaScoreCard** - NovaScore display with components
- **CPTrendGraph** - CP trend visualization
- **PolicyBreakdown** - Policy parameters display
- **DAOChangeLog** - Policy change history
- **EnforcementErrorModal** - Aurora enforcement error handling
- **ConsentFlow** - Multi-step consent flow
- **AppealForm** - Appeal submission form
- **RecallRequest** - Data recall request form

## Design System

Aurora UI uses a dark, cyberpunk-inspired design system:

- **Colors**: Purple (#8b5cf6), Sky (#0ea5e9), Neon (#00f5ff)
- **Background**: Dark slate (#0a0a0f)
- **Cards**: Semi-transparent with blur effects
- **Animations**: Subtle glow effects for important states

## Development

```bash
# Build
npm run build

# Type check
npm run type-check

# Watch mode
npm run dev
```

