# Cloudflare Quick Start - siyahkare.com

## 🚀 Hızlı Kurulum

### 1. Cloudflare DNS Ayarları

Cloudflare Dashboard → DNS → Records:

```
Type: A
Name: api
Content: [VPS IP]
Proxy: ✅ Proxied
TTL: Auto

Type: A
Name: portal
Content: [VPS IP]
Proxy: ✅ Proxied
TTL: Auto
```

### 2. Backend Environment Variables

`.env` dosyasına ekle:

```bash
ENV=prod
CORS_ORIGINS=https://portal.siyahkare.com,https://app.siyahkare.com
NOVACORE_URL=https://api.siyahkare.com
FRONTEND_URL=https://portal.siyahkare.com
BACKEND_URL=https://api.siyahkare.com
```

### 3. Frontend Environment Variables

`apps/citizen-portal/.env.local` dosyasına ekle:

```bash
NEXT_PUBLIC_AURORA_API_URL=https://api.siyahkare.com/api/v1
NEXT_PUBLIC_AURORA_ENV=prod
```

### 4. Bot Environment Variables

Bot config'i NovaCore root `.env` dosyasından okur:

```bash
NOVACORE_URL=https://api.siyahkare.com
FRONTEND_URL=https://portal.siyahkare.com
```

### 5. Telegram Webhook

```bash
curl -X POST "https://api.telegram.org/bot<BOT_TOKEN>/setWebhook" \
  -d "url=https://api.siyahkare.com/api/v1/telegram/webhook"
```

## ✅ Test

```bash
# Backend
curl https://api.siyahkare.com/health

# Frontend
# Browser: https://portal.siyahkare.com

# Bot
/start
/panel
```

## 📚 Detaylı Dokümantasyon

- [Cloudflare Setup Guide](./CLOUDFLARE_SETUP.md)
- [Environment Variables](./ENV_CLOUDFLARE.md)

