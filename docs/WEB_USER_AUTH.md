# Web User Authentication (Non-Telegram Users)

## Overview

Aurora Citizen Portal supports both Telegram Mini-App users and regular web users. Since the current system is built around Telegram IDs, web users get synthetic Telegram IDs.

## How It Works

### Web User Creation

When a web user goes through onboarding:

1. **User ID Generation**: A unique identifier is generated: `NEW-CITIZEN-{timestamp}`
2. **Synthetic Telegram ID**: A synthetic `telegram_id` is generated from the user_id hash
   - Range: 900,000,000 - 999,999,999 (900M+ range)
   - This ensures no collision with real Telegram users (Telegram IDs typically start from 1)
3. **User Creation**: User is created with:
   - `telegram_id`: Synthetic ID (900M+ range)
   - `display_name`: The `NEW-CITIZEN-*` identifier
   - `telegram_data`: `{"source": "web", "user_id": "NEW-CITIZEN-..."}`

### Example

```python
# Web user onboarding
user_id = "NEW-CITIZEN-1234567890"
# → Synthetic telegram_id: 900123456 (from hash)
# → User created with display_name: "NEW-CITIZEN-1234567890"
```

## Current Limitations

1. **telegram_id is Required**: The current User model requires `telegram_id` to be non-null
2. **Synthetic IDs**: Web users get synthetic Telegram IDs in the 900M+ range
3. **No Real Telegram Integration**: Web users cannot use Telegram features

## Future Improvements

### Option 1: Make telegram_id Optional (Recommended)

```python
# Future User model
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    telegram_id: int | None = Field(default=None, index=True, unique=True)  # Optional
    email: str | None = Field(default=None, index=True, unique=True)  # For web users
    username: str | None = Field(default=None, index=True)
    display_name: str | None = Field(default=None)
    # ...
```

**Migration Required**: This would require a database migration to make `telegram_id` nullable.

### Option 2: Separate Web User Model

```python
class WebUser(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    display_name: str | None = Field(default=None)
    # ...
```

**Pros**: Clean separation
**Cons**: Requires refactoring all user lookups

## Current Implementation

### Backend: `/api/v1/dev/token`

```python
# Auto-creates web users with synthetic telegram_id
if user_id.startswith("NEW-CITIZEN-"):
    telegram_id = 900000000 + (hash(user_id) % 100000000)
    user = await service.get_or_create_user(
        telegram_id=telegram_id,
        display_name=user_id,
        telegram_data={"source": "web", "user_id": user_id}
    )
```

### Frontend: Onboarding Flow

```typescript
// apps/citizen-portal/app/onboarding/page.tsx
const newUserId = `NEW-CITIZEN-${Date.now()}`
const res = await fetch(`${apiUrl}/dev/token?user_id=${newUserId}`, {
  method: 'POST',
})
// → Backend creates user with synthetic telegram_id
```

## Identifying Web Users

Web users can be identified by:

1. **telegram_id Range**: 900M+ range (900,000,000 - 999,999,999)
2. **telegram_data**: `{"source": "web", "user_id": "NEW-CITIZEN-..."}`
3. **display_name**: Starts with `NEW-CITIZEN-`

## Testing 

```bash
# 1. Start backend
uvicorn app.main:app --reload

# 2. Start frontend
cd apps/citizen-portal
npm run dev

# 3. Visit /onboarding
# → Web user is automatically created with synthetic telegram_id
```

## Notes

- **Telegram Mini-App**: Uses real Telegram IDs (1 - 899,999,999)
- **Web Users**: Use synthetic Telegram IDs (900,000,000+)
- **No Collision**: The 900M+ range ensures no collision with real Telegram users
- **Future-Proof**: When `telegram_id` becomes optional, web users can migrate to email-based auth

