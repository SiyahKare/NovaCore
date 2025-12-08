# .env Dosyası Cloudflare URL'leri ile Güncellendi

## ✅ Güncellenen Değişkenler

```bash
# Backend API URL (Cloudflare Tunnel)
NOVACORE_URL=https://api.siyahkare.com
BACKEND_URL=https://api.siyahkare.com

# Frontend URL (Cloudflare Tunnel)
FRONTEND_URL=https://portal.siyahkare.com

# CORS Origins (zaten güncellenmişti)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,https://portal.siyahkare.com,https://app.siyahkare.com
```

## 🔄 Etkilenen Servisler

1. **Telegram Bot (`nasipquest_bot`)**: 
   - `NOVACORE_URL` → Backend API çağrıları için
   - `FRONTEND_URL` → `/panel` ve `/web` komutları için

2. **Backend (`app/core/config.py`)**:
   - `BACKEND_URL` → Webhook'lar ve external URL'ler için
   - `FRONTEND_URL` → Deep link'ler için
   - `CORS_ORIGINS` → CORS middleware için

## ⚠️ Önemli Notlar

- **Backend'i yeniden başlat**: `.env` değişikliklerinin yüklenmesi için
- **Telegram Bot'u yeniden başlat**: `NOVACORE_URL` ve `FRONTEND_URL` değişikliklerinin yüklenmesi için
- **Frontend'i kontrol et**: `NEXT_PUBLIC_AURORA_API_URL` environment variable'ı `https://api.siyahkare.com` olmalı

## 🧪 Test

### Backend Test
```bash
curl https://api.siyahkare.com/health
```

### CORS Test
```bash
curl -v -X OPTIONS https://api.siyahkare.com/api/v1/identity/telegram/auth \
  -H "Origin: https://portal.siyahkare.com" \
  -H "Access-Control-Request-Method: POST"
```

**Expected:**
```
< access-control-allow-origin: https://portal.siyahkare.com
```

