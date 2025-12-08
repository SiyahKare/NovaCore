# 🚀 Hızlı Deployment - Cloudflare Tunnel

## Otomatik Kurulum (Önerilen)

```bash
# 1. Script'i çalıştırılabilir yap
chmod +x scripts/setup_cloudflare_tunnel.sh

# 2. Kurulumu başlat
./scripts/setup_cloudflare_tunnel.sh
```

Script şunları yapar:
- ✅ Cloudflare Tunnel oluşturur
- ✅ DNS route'ları ayarlar (`api.siyahkare.com`, `portal.siyahkare.com`)
- ✅ Systemd service oluşturur
- ✅ Tunnel'ı başlatır

## Gereksinimler

1. **Cloudflare hesabı** (ücretsiz)
2. **Cloudflare API Token** (Account.Cloudflare Tunnel.Edit izni)
3. **cloudflared** kurulu (`brew install cloudflared` veya [kurulum](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/))

## Adımlar

### 1. Cloudflare API Token Oluştur

1. Cloudflare Dashboard → **My Profile** → **API Tokens**
2. **Create Token** → **Custom token**
3. İzinler: **Account** → **Cloudflare Tunnel** → **Edit**
4. Token'ı kopyala

### 2. Otomatik Kurulum

```bash
./scripts/setup_cloudflare_tunnel.sh
```

Script soracak:
- Cloudflare Account ID
- Cloudflare API Token

### 3. Environment Variables

**Backend `.env`:**
```bash
ENV=prod
CORS_ORIGINS=https://portal.siyahkare.com,https://app.siyahkare.com
NOVACORE_URL=https://api.siyahkare.com
FRONTEND_URL=https://portal.siyahkare.com
BACKEND_URL=https://api.siyahkare.com
```

**Frontend `apps/citizen-portal/.env.local`:**
```bash
NEXT_PUBLIC_AURORA_API_URL=https://api.siyahkare.com/api/v1
NEXT_PUBLIC_AURORA_ENV=prod
```

### 4. Servisleri Başlat

```bash
# Backend
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Frontend (başka terminal)
cd apps/citizen-portal
npm run dev
```

### 5. Test

```bash
# Backend
curl https://api.siyahkare.com/health

# Frontend
# Browser: https://portal.siyahkare.com
```

## Manuel Kurulum

Detaylı kurulum için: [docs/CLOUDFLARE_TUNNEL_SETUP.md](./docs/CLOUDFLARE_TUNNEL_SETUP.md)

## Troubleshooting

```bash
# Tunnel durumu
cloudflared tunnel info novacore-siyahkare

# Systemd logları (Linux)
sudo journalctl -u cloudflared-tunnel -f

# Manuel başlatma
./scripts/start_cloudflared_tunnel.sh
```

## 📚 Daha Fazla Bilgi

- [Cloudflare Tunnel Setup](./docs/CLOUDFLARE_TUNNEL_SETUP.md)
- [Cloudflare Setup (Manuel)](./docs/CLOUDFLARE_SETUP.md)
- [Environment Variables](./docs/ENV_CLOUDFLARE.md)

