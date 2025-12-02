# Aurora Justice Stack - Complete Integration Guide

## 🎯 Overview

This guide covers the complete integration of Aurora Justice Stack into your application, from backend enforcement to frontend UI components.

## 📦 Components

### Backend

1. **Enforcement Check**
   ```python
   from app.justice.enforcement import check_action_allowed
   from app.justice.policy import Action
   
   cp_state = await justice_service.get_cp(user_id)
   check_action_allowed(cp_state, Action.SEND_MESSAGE)
   ```

2. **Error Response Format**
   ```json
   {
     "error": "AURORA_ENFORCEMENT_BLOCKED",
     "message": "Aurora Adalet rejimin: LOCKDOWN (CP: 85)...",
     "regime": "LOCKDOWN",
     "cp_value": 85,
     "action": "SEND_MESSAGE"
   }
   ```

### Frontend

1. **Error Handling Hook**
   ```tsx
   import { useAuroraEnforcementError } from "@/features/justice/AuroraEnforcementError";
   
   const { error, handleError, clearError } = useAuroraEnforcementError();
   ```

2. **Error Modal**
   ```tsx
   import { AuroraEnforcementError } from "@/features/justice/AuroraEnforcementError";
   
   {error && (
     <AuroraEnforcementError
       error={error}
       onDismiss={clearError}
       showAppealLink={true}
     />
   )}
   ```

3. **Regime Badge**
   ```tsx
   import { RegimeBadge } from "@/features/justice/RegimeBadge";
   
   <RegimeBadge regime="PROBATION" cp={45} size="md" showTooltip />
   ```

4. **Regime Banner**
   ```tsx
   import { RegimeBanner } from "@/features/justice/RegimeBanner";
   
   <RegimeBanner regime={cpState.regime} cp={cpState.cp_value} />
   ```

## 🔗 Integration Patterns

### Pattern 1: Direct API Call

```tsx
async function sendMessage() {
  try {
    const response = await fetch("/api/v1/flirtmarket/messages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ recipient_id: "123", message: "Hello" }),
    });

    const data = await response.json();

    if (!response.ok) {
      if (handleError({ response: { status: response.status, data } })) {
        return; // Aurora enforcement error handled
      }
      throw new Error(data.detail);
    }

    // Success
  } catch (err) {
    // Other errors
  }
}
```

### Pattern 2: API Client

```tsx
import { FlirtMarketApi } from "@/features/flirtmarket/api";

const api = new FlirtMarketApi("/api/v1", token);

try {
  await api.sendMessage({ recipient_id: "123", message: "Hello" });
} catch (err) {
  if (handleError(err)) {
    return; // Aurora enforcement error
  }
  // Other errors
}
```

### Pattern 3: React Hook Form

```tsx
import { useForm } from "react-hook-form";
import { useAuroraEnforcementError } from "@/features/justice/AuroraEnforcementError";

function MessageForm() {
  const { handleError, error, clearError } = useAuroraEnforcementError();
  const { handleSubmit, register } = useForm();

  const onSubmit = async (data) => {
    try {
      await api.sendMessage(data);
    } catch (err) {
      if (handleError(err)) return;
      // Other errors
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      {/* Form fields */}
      {error && (
        <AuroraEnforcementError error={error} onDismiss={clearError} />
      )}
    </form>
  );
}
```

## 🎨 UI Integration

### User Profile Card

```tsx
function UserCard({ user, cpState }) {
  return (
    <div className="card">
      <div className="flex items-center justify-between">
        <div>
          <h3>{user.name}</h3>
          <p>{user.bio}</p>
        </div>
        <RegimeBadge
          regime={cpState.regime}
          cp={cpState.cp_value}
          size="sm"
          showTooltip
        />
      </div>
    </div>
  );
}
```

### Dashboard with Banner

```tsx
function Dashboard({ cpState }) {
  const [bannerDismissed, setBannerDismissed] = useState(false);

  return (
    <div>
      {!bannerDismissed && (
        <RegimeBanner
          regime={cpState.regime}
          cp={cpState.cp_value}
          onDismiss={() => setBannerDismissed(true)}
        />
      )}
      {/* Dashboard content */}
    </div>
  );
}
```

### Action Button with Enforcement

```tsx
function ActionButton({ action, onAction }) {
  const { handleError, error, clearError } = useAuroraEnforcementError();

  const handleClick = async () => {
    try {
      await onAction();
    } catch (err) {
      if (handleError(err)) return;
      showError(err);
    }
  };

  return (
    <>
      <button onClick={handleClick}>Do Action</button>
      {error && (
        <AuroraEnforcementError error={error} onDismiss={clearError} />
      )}
    </>
  );
}
```

## 📍 Routing

```tsx
// router.tsx
import { AuroraJusticeRoutes } from "@/features/justice/routes";

<Routes>
  <Route path="/admin/aurora/*" element={<AuroraJusticeRoutes />} />
  {/* Other routes */}
</Routes>
```

## 🧪 Testing

### Test Enforcement Blocking

```typescript
// Test that LOCKDOWN user cannot send messages
it("blocks LOCKDOWN user from sending messages", async () => {
  // Setup: Create LOCKDOWN user
  await createViolations(userId, 5); // CP > 80

  // Attempt to send message
  const response = await api.sendMessage({
    recipient_id: "123",
    message: "Hello",
  });

  // Should be blocked
  expect(response.status).toBe(403);
  expect(response.data.error).toBe("AURORA_ENFORCEMENT_BLOCKED");
  expect(response.data.regime).toBe("LOCKDOWN");
});
```

## 📊 Monitoring

### Track Enforcement Events

```typescript
// Analytics tracking
function trackEnforcementBlock(action: string, regime: Regime, cp: number) {
  analytics.track("aurora_enforcement_blocked", {
    action,
    regime,
    cp_value: cp,
    timestamp: new Date().toISOString(),
  });
}
```

## 🚀 Next Steps

1. **Add Regime Badges** to all user-facing components
2. **Integrate Enforcement** into all critical actions
3. **Add Regime Banners** to dashboard/home screens
4. **Build Appeal System** UI
5. **Add Metrics Dashboard** for operators

## 📚 Files Reference

- `frontend/src/features/justice/AuroraCaseView.tsx` - Case file view
- `frontend/src/features/justice/AuroraEnforcementError.tsx` - Error modal
- `frontend/src/features/justice/RegimeBadge.tsx` - Regime badge component
- `frontend/src/features/justice/RegimeBanner.tsx` - Contextual banner
- `frontend/src/features/flirtmarket/SendMessageForm.tsx` - Complete example
- `frontend/src/features/flirtmarket/api.ts` - API client

