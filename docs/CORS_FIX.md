# CORS Hatası Çözümü

## 🔍 Sorun

"Failed to fetch" hatası alınıyor. CORS hatası: "Disallowed CORS origin"

## ✅ Çözüm

### 1. `.env` Dosyasını Güncelle

```bash
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,https://portal.siyahkare.com,https://app.siyahkare.com
```

### 2. Backend'i Yeniden Başlat

```bash
# Backend'i durdur
pkill -f "uvicorn.*main:app"

# Backend'i yeniden başlat
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 3. Test

```bash
# CORS test
curl -v -X OPTIONS https://api.siyahkare.com/api/v1/identity/telegram/auth \
  -H "Origin: https://portal.siyahkare.com" \
  -H "Access-Control-Request-Method: POST"

# Expected: access-control-allow-origin: https://portal.siyahkare.com
```

## 📋 Checklist

- [ ] `.env` dosyasında `CORS_ORIGINS` güncellendi
- [ ] Backend yeniden başlatıldı
- [ ] CORS test başarılı
- [ ] Frontend'den istek çalışıyor

## 🐛 Troubleshooting

### CORS Hala Çalışmıyor

1. **Backend çalışıyor mu?**
   ```bash
   curl https://api.siyahkare.com/health
   ```

2. **Environment variable yüklendi mi?**
   ```bash
   # Backend log'larında kontrol et
   # CORS origins: ['https://portal.siyahkare.com', ...]
   ```

3. **Browser console'da CORS hatası var mı?**
   - Network tab'de request'i kontrol et
   - Response headers'da `access-control-allow-origin` var mı?

### Production'da CORS

Production'da `.env` dosyasında mutlaka şunlar olmalı:

```bash
CORS_ORIGINS=https://portal.siyahkare.com,https://app.siyahkare.com,https://www.siyahkare.com
```

