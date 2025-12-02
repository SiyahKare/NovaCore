# FlirtMarket Message Sending - Complete Example

## Overview

This is a complete end-to-end example of integrating Aurora enforcement into a FlirtMarket message sending feature.

## Backend Endpoint (Example)

```python
# app/flirtmarket/routes.py (example)

from app.justice.router import get_justice_service, JusticeService
from app.justice.enforcement import check_action_allowed
from app.justice.policy import Action

@router.post("/messages")
async def send_message(
    body: MessageCreate,
    current_user_id: str = Depends(get_current_user_id),
    justice_service: JusticeService = Depends(get_justice_service),
):
    # Aurora Justice Enforcement Check
    cp_state = await justice_service.get_cp(current_user_id)
    check_action_allowed(cp_state, Action.SEND_MESSAGE)
    
    # Normal flow continues...
    # ... send message logic ...
    
    return {"message_id": "...", "sent_at": "..."}
```

## Frontend Component

See `frontend/src/features/flirtmarket/SendMessageForm.tsx` for complete implementation.

### Key Features

1. **Enforcement Error Handling**
   - Uses `useAuroraEnforcementError` hook
   - Automatically shows modal on 403
   - Handles other errors separately

2. **User Experience**
   - Loading states
   - Error messages
   - Success callbacks

3. **Integration**
   - Uses FlirtMarketApi client
   - Proper error handling
   - Token management

## Usage

```tsx
import { SendMessageForm } from "@/features/flirtmarket/SendMessageForm";

function MessagePage() {
  const token = useAuthStore((state) => state.token);
  
  return (
    <div>
      <SendMessageForm
        recipientId="performer-123"
        recipientName="Luna"
        token={token}
        onSuccess={() => {
          // Show success toast, navigate, etc.
        }}
      />
    </div>
  );
}
```

## API Client

See `frontend/src/features/flirtmarket/api.ts` for complete API client with enforcement handling.

### Usage

```tsx
import { FlirtMarketApi } from "@/features/flirtmarket/api";
import { useAuroraEnforcementError } from "@/features/justice/AuroraEnforcementError";

function MyComponent() {
  const { handleError, error, clearError } = useAuroraEnforcementError();
  const api = new FlirtMarketApi("/api/v1", token);

  const sendMessage = async () => {
    try {
      await api.sendMessage({
        recipient_id: "123",
        message: "Hello!",
      });
      // Success
    } catch (err) {
      if (handleError(err)) {
        // Aurora enforcement error - modal will show
        return;
      }
      // Other error
      showError(err);
    }
  };

  return (
    <>
      <button onClick={sendMessage}>Send</button>
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

## Regime Badge Integration

Add regime badge to user profiles:

```tsx
import { RegimeBadge } from "@/features/justice/RegimeBadge";

function UserProfile({ user, cpState }) {
  return (
    <div>
      <h2>{user.name}</h2>
      <RegimeBadge
        regime={cpState.regime}
        cp={cpState.cp_value}
        size="md"
        showTooltip
      />
    </div>
  );
}
```

## Regime Banner Integration

Show contextual banners based on regime:

```tsx
import { RegimeBanner } from "@/features/justice/RegimeBanner";

function Dashboard({ cpState }) {
  return (
    <div>
      <RegimeBanner
        regime={cpState.regime}
        cp={cpState.cp_value}
        onDismiss={() => {
          // Store dismissal in localStorage
        }}
      />
      {/* Rest of dashboard */}
    </div>
  );
}
```

## Routing Setup

```tsx
// App.tsx or router config
import { AuroraJusticeRoutes } from "@/features/justice/routes";

<Routes>
  {/* Other routes */}
  <Route path="/admin/aurora/*" element={<AuroraJusticeRoutes />} />
</Routes>
```

## Complete Flow

1. User tries to send message
2. Frontend calls `/api/v1/flirtmarket/messages`
3. Backend checks enforcement:
   - If allowed → message sent
   - If blocked → 403 with structured error
4. Frontend detects 403:
   - Shows `AuroraEnforcementError` modal
   - Displays regime, CP, action blocked
   - Provides appeal link
5. User sees clear explanation and next steps

## Testing

```bash
# 1. Create LOCKDOWN user
POST /justice/violations
{
  "user_id": "test-user",
  "category": "SYS",
  "code": "SYS_EXPLOIT",
  "severity": 5
}

# 2. Try to send message
POST /flirtmarket/messages
{
  "recipient_id": "123",
  "message": "Hello"
}

# Expected: 403 with Aurora enforcement error
```

