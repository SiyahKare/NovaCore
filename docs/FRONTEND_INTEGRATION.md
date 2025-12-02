# Aurora Justice Stack - Frontend Integration Guide

## Overview

This guide covers integrating Aurora Justice Stack into your frontend application, including the case file view and enforcement error handling.

## TypeScript Types

All types are defined in the React components. For standalone use, extract them:

```typescript
// types/aurora.ts
export type Regime = "NORMAL" | "SOFT_FLAG" | "PROBATION" | "RESTRICTED" | "LOCKDOWN";

export interface CpState {
  user_id: string;
  cp_value: number;
  last_updated_at: string;
  regime: Regime;
}

export interface NovaScoreComponent {
  value: number;
  confidence: number;
}

export interface NovaScoreComponents {
  ECO: NovaScoreComponent;
  REL: NovaScoreComponent;
  SOC: NovaScoreComponent;
  ID: NovaScoreComponent;
  CON: NovaScoreComponent;
}

export interface NovaScorePayload {
  value: number;
  components: NovaScoreComponents;
  confidence_overall: number;
  explanation?: string | null;
}

export interface PrivacyProfile {
  user_id: string;
  latest_consent_id?: string | null;
  contract_version?: string | null;
  consent_level?: "FULL" | "LIMITED" | "MINIMUM" | null;
  recall_mode?: "ANONYMIZE" | "FULL_EXCLUDE" | null;
  recall_requested_at?: string | null;
  last_policy_updated_at?: string | null;
}

export interface Violation {
  id: string;
  user_id: string;
  category: "EKO" | "COM" | "SYS" | "TRUST";
  code: string;
  severity: number;
  cp_delta: number;
  source?: string | null;
  created_at: string;
}

export interface CaseFileResponse {
  user_id: string;
  privacy_profile: PrivacyProfile | null;
  cp_state: CpState;
  nova_score: NovaScorePayload | null;
  recent_violations: Violation[];
}

export interface AuroraEnforcementErrorData {
  error: "AURORA_ENFORCEMENT_BLOCKED";
  message: string;
  regime: Regime;
  cp_value: number;
  action?: string;
}
```

## Components

### 1. AuroraCaseView

Complete case file view for Ombudsman/Admin panel.

**Location:** `frontend/src/features/justice/AuroraCaseView.tsx`

**Usage:**

```tsx
import { AuroraCaseView } from "@/features/justice/AuroraCaseView";

<AuroraCaseView 
  userId="AUR-TEST-1" 
  apiBaseUrl="/api/v1"
  token={authToken}
/>
```

**Props:**
- `userId: string` - User ID to fetch case file for
- `apiBaseUrl?: string` - API base URL (default: `/api/v1`)
- `token?: string` - JWT token for authentication

### 2. AuroraEnforcementError

Modal component for displaying enforcement errors (403).

**Location:** `frontend/src/features/justice/AuroraEnforcementError.tsx`

**Usage:**

```tsx
import { 
  AuroraEnforcementError, 
  useAuroraEnforcementError 
} from "@/features/justice/AuroraEnforcementError";

function MyComponent() {
  const { error, handleError, clearError } = useAuroraEnforcementError();

  const handleAction = async () => {
    try {
      await api.post("/some-endpoint", data);
    } catch (err) {
      if (handleError(err)) {
        // Aurora enforcement error handled
        return;
      }
      // Handle other errors
    }
  };

  return (
    <>
      <button onClick={handleAction}>Do Action</button>
      {error && (
        <AuroraEnforcementError
          error={error}
          onDismiss={clearError}
          showAppealLink={true}
        />
      )}
    </>
  );
}
```

### 3. AuroraCasePage

Page component for routing.

**Location:** `frontend/src/features/justice/AuroraCasePage.tsx`

**Usage in router:**

```tsx
import { AuroraCasePage } from "@/features/justice/AuroraCasePage";

<Route path="/admin/aurora/case/:userId" element={<AuroraCasePage />} />
```

## Enforcement Error Handling

### Backend Response Format

When enforcement blocks an action, the backend returns:

```json
{
  "error": "AURORA_ENFORCEMENT_BLOCKED",
  "message": "Aurora Adalet rejimin: Kilitli (CP: 85). Bu işlemi şu an gerçekleştiremezsin.",
  "regime": "LOCKDOWN",
  "cp_value": 85,
  "action": "WITHDRAW_FUNDS"
}
```

### Frontend Integration Pattern

```tsx
import { useAuroraEnforcementError } from "@/features/justice/AuroraEnforcementError";
import axios from "axios";

function TransferButton() {
  const { error, handleError, clearError } = useAuroraEnforcementError();

  const handleTransfer = async () => {
    try {
      await axios.post("/api/v1/wallet/transfer", {
        to_user_id: 123,
        amount: "10.0",
        token: "NCR",
      });
      // Success
    } catch (err) {
      if (handleError(err)) {
        // Aurora enforcement error - modal will show
        return;
      }
      // Other error handling
      console.error("Transfer failed:", err);
    }
  };

  return (
    <>
      <button onClick={handleTransfer}>Transfer</button>
      {error && (
        <AuroraEnforcementError
          error={error}
          onDismiss={clearError}
        />
      )}
    </>
  );
}
```

## Regime Badge Component

Reusable regime badge for user profiles:

```tsx
// RegimeBadge.tsx
import { Regime } from "@/types/aurora";

const regimeLabel: Record<Regime, string> = {
  NORMAL: "Normal",
  SOFT_FLAG: "Yumuşak Uyarı",
  PROBATION: "Gözaltı",
  RESTRICTED: "Kısıtlı",
  LOCKDOWN: "Kilitli",
};

const regimeColorClass: Record<Regime, string> = {
  NORMAL: "bg-emerald-100 text-emerald-800 border-emerald-300",
  SOFT_FLAG: "bg-yellow-100 text-yellow-800 border-yellow-300",
  PROBATION: "bg-orange-100 text-orange-800 border-orange-300",
  RESTRICTED: "bg-red-100 text-red-800 border-red-300",
  LOCKDOWN: "bg-red-900 text-red-100 border-red-700",
};

export const RegimeBadge: React.FC<{ regime: Regime; cp?: number }> = ({
  regime,
  cp,
}) => {
  return (
    <span
      className={`px-2 py-0.5 rounded-full border text-xs font-semibold ${regimeColorClass[regime]}`}
    >
      {regimeLabel[regime]}
      {cp !== undefined && ` (CP: ${cp})`}
    </span>
  );
};
```

## API Integration

### Fetch Case File

```typescript
async function fetchCaseFile(
  userId: string,
  token?: string
): Promise<CaseFileResponse> {
  const res = await fetch(`/api/v1/justice/case/${userId}`, {
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });

  if (!res.ok) {
    throw new Error(`Failed to fetch case file: ${res.status}`);
  }

  return res.json();
}
```

### Handle Enforcement Errors

```typescript
async function handleActionWithEnforcement<T>(
  action: () => Promise<T>
): Promise<T> {
  try {
    return await action();
  } catch (err: any) {
    if (
      err?.response?.status === 403 &&
      err?.response?.data?.error === "AURORA_ENFORCEMENT_BLOCKED"
    ) {
      // Show Aurora enforcement error modal
      throw new AuroraEnforcementError(err.response.data);
    }
    throw err;
  }
}
```

## Styling

Components use Tailwind CSS classes. Ensure your project has Tailwind configured:

```js
// tailwind.config.js
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        slate: {
          // ... slate colors
        },
      },
    },
  },
};
```

## Routing Example

```tsx
// App.tsx or router config
import { AuroraCasePage } from "@/features/justice/AuroraCasePage";

<Routes>
  <Route path="/admin/aurora/case/:userId" element={<AuroraCasePage />} />
</Routes>
```

## Next Steps

1. **Add Regime Badges** to user profiles throughout the app
2. **Integrate enforcement error handling** into critical endpoints
3. **Build appeal system** UI
4. **Add metrics dashboard** for operators

