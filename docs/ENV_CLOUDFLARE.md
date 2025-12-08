# Environment Variables - Cloudflare Setup

## Backend (.env)

```bash
# Environment
ENV=prod

# Database
DATABASE_URL=postgresql+asyncpg://novacore:password@your-db-host:5432/novacore
DATABASE_URL_SYNC=postgresql://novacore:password@your-db-host:5432/novacore

# JWT
JWT_SECRET=your-production-secret-key-here-change-this
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=10080

# CORS - Cloudflare subdomain'leri
CORS_ORIGINS=https://portal.siyahkare.com,https://app.siyahkare.com,https://www.siyahkare.com

# Backend URL (Cloudflare subdomain)
NOVACORE_URL=https://api.siyahkare.com
BACKEND_URL=https://api.siyahkare.com

# Frontend URL (Cloudflare subdomain)
FRONTEND_URL=https://portal.siyahkare.com

# Telegram Gateway
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_BRIDGE_TOKEN=your-secure-bridge-token-here
TELEGRAM_LINK_SECRET=your-hmac-secret-here

# Telethon (Aurora Contact User Bot - optional)
TELETHON_API_ID=your-telegram-api-id
TELETHON_API_HASH=your-telegram-api-hash

# Redis (optional)
REDIS_URL=redis://your-redis-host:6379/0

# AI Scoring Service
OPENAI_API_KEY=your-openai-api-key

# Logging
LOG_LEVEL=INFO
```

## Frontend (apps/citizen-portal/.env.local)

```bash
# Backend API URL (Cloudflare subdomain)
NEXT_PUBLIC_AURORA_API_URL=https://api.siyahkare.com/api/v1

# Environment
NEXT_PUBLIC_AURORA_ENV=prod

# Telegram Bot ID (opsiyonel)
NEXT_PUBLIC_TELEGRAM_BOT_ID=your-telegram-bot-id

# Constitution Hash (opsiyonel)
NEXT_PUBLIC_AURORA_CONSTITUTION_HASH=
```

## Bot (nasipquest_bot/.env veya NovaCore/.env)

Bot config'i NovaCore root `.env` dosyasından okur:

```bash
# Telegram Bot Token
TELEGRAM_BOT_TOKEN=your-telegram-bot-token

# NovaCore API URL (Cloudflare subdomain)
NOVACORE_URL=https://api.siyahkare.com

# Frontend URL (Cloudflare subdomain)
FRONTEND_URL=https://portal.siyahkare.com

# Bridge Token
TELEGRAM_BRIDGE_TOKEN=your-secure-bridge-token-here

# Bot Debug Mode
BOT_DEBUG=false
```

## Önemli Notlar

1. **CORS Origins**: Backend'de `CORS_ORIGINS` içinde tüm frontend subdomain'leri olmalı
2. **HTTPS**: Cloudflare kullanıyorsanız, tüm URL'ler `https://` ile başlamalı
3. **JWT Secret**: Production'da mutlaka güçlü bir secret kullanın
4. **Database**: VPS üzerindeki database'e erişim için connection string'i güncelleyin
5. **Telegram Webhook**: Bot webhook URL'i Cloudflare subdomain'e ayarlanmalı

## Hızlı Test

```bash
# Backend health check
curl https://api.siyahkare.com/health

# Frontend (browser)
https://portal.siyahkare.com

# Bot webhook test
curl -X POST "https://api.telegram.org/bot<BOT_TOKEN>/getWebhookInfo"
```

