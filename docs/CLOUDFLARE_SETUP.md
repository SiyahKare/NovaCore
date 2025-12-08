# Cloudflare Subdomain Setup - siyahkare.com

## 🎯 Amaç

NovaCore sistemini Cloudflare üzerinden `siyahkare.com` altında subdomain'lerle yayınlamak.

## 📋 Önerilen Subdomain Yapısı

### Backend API
- **Subdomain:** `api.siyahkare.com`
- **Açıklama:** NovaCore backend API
- **Port:** 8000 (Cloudflare Tunnel veya VPS üzerinden)

### Frontend (Citizen Portal)
- **Subdomain:** `portal.siyahkare.com`
- **Açıklama:** Vatandaş paneli (Next.js)
- **Port:** 3000 (Cloudflare Tunnel veya VPS üzerinden)

### Alternatif Subdomain'ler
- `novacore.siyahkare.com` → Backend API
- `app.siyahkare.com` → Frontend
- `www.siyahkare.com` → Ana site (opsiyonel)

## 🔧 Cloudflare Konfigürasyonu

### 1. DNS Ayarları

Cloudflare Dashboard → DNS → Records:

```
Type: A (veya CNAME)
Name: api
Content: [VPS IP adresi]
Proxy: ✅ Proxied (Orange Cloud)
TTL: Auto

Type: A (veya CNAME)
Name: portal
Content: [VPS IP adresi]
Proxy: ✅ Proxied (Orange Cloud)
TTL: Auto
```

### 2. SSL/TLS Ayarları

Cloudflare Dashboard → SSL/TLS:

- **Encryption mode:** Full (strict)
- **Always Use HTTPS:** ✅ Enabled
- **Minimum TLS Version:** TLS 1.2

### 3. Cloudflare Tunnel (Önerilen)

Cloudflare Tunnel kullanarak VPS'e bağlantı kurmak:

```bash
# Cloudflare Tunnel kurulumu
cloudflared tunnel create novacore

# Tunnel config dosyası
cat > ~/.cloudflared/config.yml << EOF
tunnel: [TUNNEL_ID]
credentials-file: /home/user/.cloudflared/[TUNNEL_ID].json

ingress:
  - hostname: api.siyahkare.com
    service: http://localhost:8000
  - hostname: portal.siyahkare.com
    service: http://localhost:3000
  - service: http_status:404
EOF

# Tunnel'ı başlat
cloudflared tunnel run novacore
```

### 4. VPS Üzerinden (Alternatif)

Eğer Cloudflare Tunnel kullanmıyorsanız, VPS'te reverse proxy (Nginx) kullanın:

```nginx
# /etc/nginx/sites-available/api.siyahkare.com
server {
    listen 80;
    server_name api.siyahkare.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# /etc/nginx/sites-available/portal.siyahkare.com
server {
    listen 80;
    server_name portal.siyahkare.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🔐 Environment Variables

### Backend (.env)

```bash
# Environment
ENV=prod

# CORS - Cloudflare subdomain'leri
CORS_ORIGINS=https://portal.siyahkare.com,https://app.siyahkare.com,https://www.siyahkare.com

# Backend URL
NOVACORE_URL=https://api.siyahkare.com

# Frontend URL
FRONTEND_URL=https://portal.siyahkare.com

# JWT Secret (production için güçlü bir secret kullanın)
JWT_SECRET=your-production-secret-key-here

# Database (VPS üzerinden)
DATABASE_URL=postgresql+asyncpg://novacore:password@localhost:5432/novacore

# Telegram
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_BRIDGE_TOKEN=your-secure-bridge-token
```

### Frontend (.env.local)

```bash
# Backend API URL
NEXT_PUBLIC_AURORA_API_URL=https://api.siyahkare.com/api/v1

# Environment
NEXT_PUBLIC_AURORA_ENV=prod

# Telegram Bot ID (opsiyonel)
NEXT_PUBLIC_TELEGRAM_BOT_ID=your-bot-id
```

## 🚀 Deployment Adımları

### 1. Backend Deployment

```bash
# VPS'e bağlan
ssh user@your-vps-ip

# Projeyi klonla veya güncelle
cd /opt/novacore
git pull origin main

# Virtual environment'i aktif et
source .venv/bin/activate

# Dependencies'i güncelle
pip install -r requirements.txt

# Environment variables'ı ayarla
cp .env.cloudflare.example .env
nano .env  # Gerekli değerleri doldur

# Database migration
alembic upgrade head

# Backend'i başlat (systemd service veya PM2)
# systemd örneği:
sudo systemctl restart novacore-api

# veya PM2:
pm2 restart novacore-api
```

### 2. Frontend Deployment

```bash
# VPS'e bağlan
ssh user@your-vps-ip

# Projeyi klonla veya güncelle
cd /opt/novacore/apps/citizen-portal
git pull origin main

# Dependencies'i güncelle
npm install

# Environment variables'ı ayarla
cp .env.local.example .env.local
nano .env.local  # Gerekli değerleri doldur

# Build
npm run build

# Production server'ı başlat
npm start

# veya PM2:
pm2 restart citizen-portal
```

### 3. Telegram Bot Webhook

```bash
# Telegram bot webhook'unu Cloudflare subdomain'e ayarla
curl -X POST "https://api.telegram.org/bot<BOT_TOKEN>/setWebhook" \
  -d "url=https://api.siyahkare.com/api/v1/telegram/webhook"
```

## 🔍 Test

### Backend Health Check

```bash
curl https://api.siyahkare.com/health
# Expected: {"status":"ok"}
```

### Frontend

```bash
# Browser'da aç
https://portal.siyahkare.com

# API endpoint test
curl https://api.siyahkare.com/api/v1/identity/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Telegram Bot

```bash
# Bot'ta test
/start
/panel  # Web paneline yönlendirme testi
```

## 📝 Notlar

### CORS
- Backend'de `CORS_ORIGINS` environment variable'ında tüm frontend subdomain'leri olmalı
- Cloudflare proxy kullanıyorsanız, origin header'ları doğru gelir

### SSL
- Cloudflare otomatik SSL sağlar (Full strict mode)
- Backend'de SSL certificate gerekmez (Cloudflare proxy kullanıyorsanız)

### Performance
- Cloudflare CDN cache ayarlarını yapılandırın
- Static assets için Cloudflare cache kullanın
- API responses için cache policy belirleyin

### Security
- Cloudflare WAF (Web Application Firewall) kurallarını ayarlayın
- Rate limiting ekleyin
- DDoS protection aktif

## 🐛 Troubleshooting

### CORS Hatası
- Backend'de `CORS_ORIGINS` doğru mu kontrol et
- Cloudflare proxy aktif mi kontrol et
- Browser console'da CORS hatası var mı kontrol et

### SSL Hatası
- Cloudflare SSL/TLS mode "Full (strict)" olmalı
- Backend'de SSL certificate gerekli (Cloudflare Tunnel kullanmıyorsanız)

### Webhook Hatası
- Telegram webhook URL'i doğru mu kontrol et
- Backend'de webhook endpoint'i çalışıyor mu kontrol et
- Cloudflare firewall kuralları webhook'u engelliyor mu kontrol et

## 📚 Kaynaklar

- [Cloudflare Tunnel Documentation](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [Cloudflare DNS Setup](https://developers.cloudflare.com/dns/)
- [Cloudflare SSL/TLS](https://developers.cloudflare.com/ssl/)

