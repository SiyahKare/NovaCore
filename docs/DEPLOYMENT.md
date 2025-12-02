# NovaCore Deployment Guide

## 🚀 Cloudflare Tunnel ile Production Deployment

NovaCore'u `novacore.siyahkare.com` altında Cloudflare Tunnel ile yayına alma rehberi.

---

## 📋 Hızlı Başlangıç

### 1. Otomatik Kurulum (Önerilen)

```bash
# Cloudflare Tunnel'ı otomatik kur
./scripts/setup-cloudflare-tunnel.sh
```

Bu script:
- `cloudflared` kurulumunu kontrol eder
- Cloudflare'e otomatik login yapar
- Tunnel'ı otomatik oluşturur
- DNS route'larını otomatik ekler
- Yapılandırma dosyasını oluşturur

**Not:** İlk kez çalıştırıldığında Cloudflare login sayfası açılır, oradan login olman gerekir.

### 2. Environment Variables Ayarla

**Backend `.env`:**
```bash
ENV=prod
CORS_ORIGINS=https://novacore.siyahkare.com,https://api.novacore.siyahkare.com
CLOUDFLARE_TUNNEL_TOKEN=your-token-here
# ... diğer ayarlar
```

**Frontend `apps/citizen-portal/.env.local`:**
```bash
NEXT_PUBLIC_AURORA_API_URL=https://api.novacore.siyahkare.com/api/v1
NEXT_PUBLIC_AURORA_ENV=production
```

### 3. Production Başlatma

```bash
# Production başlatma (tüm servisleri otomatik başlatır)
./scripts/start-production.sh
```

### 4. Manuel Başlatma

```bash
# Terminal 1: Backend
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd apps/citizen-portal
npm run dev

# Terminal 3: Cloudflare Tunnel
cloudflared tunnel run --token $CLOUDFLARE_TUNNEL_TOKEN
```

---

## 🔧 Detaylı Kurulum

Detaylı adımlar için: [CLOUDFLARE_TUNNEL_SETUP.md](./CLOUDFLARE_TUNNEL_SETUP.md)

---

## ✅ Test

- Frontend: https://novacore.siyahkare.com
- Backend API: https://api.novacore.siyahkare.com/health
- Swagger Docs: https://api.novacore.siyahkare.com/docs (dev mode'da)

---

## 🛑 Durdurma

```bash
./scripts/stop-production.sh
```

---

## 📊 Monitoring

- Cloudflare Dashboard → Analytics
- Log dosyaları: `backend.log`, `frontend.log`, `tunnel.log`

