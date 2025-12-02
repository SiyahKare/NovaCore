# Aurora Enforcement Error Format

## Backend Response

When an action is blocked by Aurora enforcement, the backend returns:

**HTTP Status:** `403 Forbidden`

**Response Body:**
```json
{
  "error": "AURORA_ENFORCEMENT_BLOCKED",
  "message": "Aurora Adalet rejimin: Kilitli (CP: 85). Bu işlemi şu an gerçekleştiremezsin.",
  "regime": "LOCKDOWN",
  "cp_value": 85,
  "action": "WITHDRAW_FUNDS"
}
```

## Frontend Detection

```typescript
interface AuroraEnforcementErrorData {
  error: "AURORA_ENFORCEMENT_BLOCKED";
  message: string;
  regime: "NORMAL" | "SOFT_FLAG" | "PROBATION" | "RESTRICTED" | "LOCKDOWN";
  cp_value: number;
  action?: string;
}

// Check if error is Aurora enforcement
function isAuroraEnforcementError(err: any): boolean {
  return (
    err?.response?.status === 403 &&
    err?.response?.data?.error === "AURORA_ENFORCEMENT_BLOCKED"
  );
}
```

## Usage Example

```typescript
import { useAuroraEnforcementError } from "@/features/justice/AuroraEnforcementError";

function MyComponent() {
  const { error, handleError, clearError } = useAuroraEnforcementError();

  const handleAction = async () => {
    try {
      await api.post("/api/v1/wallet/transfer", data);
    } catch (err) {
      if (handleError(err)) {
        // Aurora enforcement error - modal will show
        return;
      }
      // Handle other errors
      showGenericError(err);
    }
  };

  return (
    <>
      <button onClick={handleAction}>Transfer</button>
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

## Error Message Localization

The `message` field is in Turkish. For internationalization:

```typescript
const regimeMessages: Record<Regime, string> = {
  NORMAL: "Normal",
  SOFT_FLAG: "Soft Warning",
  PROBATION: "Probation",
  RESTRICTED: "Restricted",
  LOCKDOWN: "Lockdown",
};

function getLocalizedMessage(error: AuroraEnforcementErrorData): string {
  return `Your Aurora regime is: ${regimeMessages[error.regime]} (CP: ${error.cp_value}). This action is currently blocked.`;
}
```

