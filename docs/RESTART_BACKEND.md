# Backend Yeniden Başlatma - CORS Güncellemesi

## ✅ `.env` Dosyası Güncellendi

```bash
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,https://portal.siyahkare.com,https://app.siyahkare.com
```

## 🔄 Backend'i Yeniden Başlat

### Yöntem 1: Manuel Restart (Önerilen)

Backend'i çalıştıran terminal'de:
```bash
# Ctrl+C ile durdur
# Sonra yeniden başlat:
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Yöntem 2: Process Kill + Restart

```bash
# Backend'i durdur
pkill -f "uvicorn.*main:app"

# Yeniden başlat
cd /Users/onur/code/DeltaNova_System/NovaCore
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 🧪 Test

Backend yeniden başladıktan sonra:

```bash
curl -v -X OPTIONS https://api.siyahkare.com/api/v1/identity/telegram/auth \
  -H "Origin: https://portal.siyahkare.com" \
  -H "Access-Control-Request-Method: POST"
```

**Expected:**
```
< access-control-allow-origin: https://portal.siyahkare.com
```

## 📋 Durum

- ✅ `.env` dosyası güncellendi
- ⏳ Backend yeniden başlatılmalı
- ⏳ CORS test edilmeli

