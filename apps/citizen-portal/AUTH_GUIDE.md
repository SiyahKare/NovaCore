# Aurora Auth & Identity Guide

## 🔐 Overview

Aurora Citizen Portal now has full authentication and identity management.

## Backend Endpoints

### `/api/v1/identity/me` (GET)
Get current authenticated citizen's profile.

**Response:**
```json
{
  "id": 1,
  "telegram_id": 123456789,
  "username": "aurora_citizen",
  "display_name": "Aurora Citizen",
  "ton_wallet": null,
  "is_performer": false,
  "is_agency_owner": false,
  "is_admin": false,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### `/api/v1/dev/token` (POST) - Dev Only
Generate a dev token for testing.

**Query Params:**
- `user_id`: User ID or seed identifier (e.g., "AUR-SIGMA")

**Response:**
```json
{
  "token": "eyJ...",
  "user_id": 1,
  "display_name": "AUR-SIGMA"
}
```

## Frontend Components

### `lib/auth.ts`
Token management utilities:
- `getToken()` - Get stored token
- `setToken(token)` - Store token
- `clearToken()` - Remove token
- `isAuthenticated()` - Check if token exists

### `useCurrentCitizen` Hook
Fetch current citizen identity:
```tsx
const { citizen, loading, error, isAuthenticated, refetch } = useCurrentCitizen()
```

### `ProtectedView` Component
Wrap pages that require authentication:
```tsx
<ProtectedView>
  <YourPageContent />
</ProtectedView>
```

### `CitizenSwitcher` Component
Dev-only component for switching between test users:
- AUR-SIGMA (clean citizen)
- AUR-TROLLER (problematic citizen)
- AUR-GHOST (privacy-conscious citizen)

## Protected Pages

These pages now require authentication:
- `/dashboard`
- `/identity`
- `/consent`
- `/justice`
- `/academy`

## Usage Flow

1. **User visits protected page**
   - `ProtectedView` checks authentication
   - If not authenticated → redirect to onboarding

2. **User completes onboarding**
   - Gets JWT token
   - Token stored in localStorage
   - Can access protected pages

3. **Dev Mode Testing**
   - Use `CitizenSwitcher` to switch users
   - Test different CP/Regime scenarios
   - See enforcement in action

## Dev Token Setup

1. **Seed demo users:**
   ```bash
   python scripts/seed_aurora_demo.py
   ```

2. **Start backend (dev mode):**
   ```bash
   uvicorn app.main:app --reload
   ```

3. **Use CitizenSwitcher:**
   - Click on user button
   - Token fetched from `/dev/token`
   - Page reloads with new identity

## Next Steps

- [ ] Real Telegram auth integration
- [ ] Session management
- [ ] Token refresh
- [ ] Remember me option
- [ ] Multi-device support

