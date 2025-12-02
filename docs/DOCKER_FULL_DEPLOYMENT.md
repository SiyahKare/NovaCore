# NovaCore Full Stack Docker Deployment

Backend + Frontend + Bot + Cloudflare Tunnel için tam Docker deployment rehberi.

## 🚀 Hızlı Kurulum

### 1. EC2'ye Bağlan

```bash
ssh -i DeltaNova.pem ubuntu@13.60.8.219
```

### 2. Projeyi Klonla (Eğer Yapılmadıysa)

```bash
cd /opt
sudo mkdir -p novacore
sudo chown $USER:$USER novacore
cd novacore
git clone https://github.com/YOUR_USERNAME/NovaCore.git
cd NovaCore
```

### 3. Otomatik Deployment

```bash
chmod +x scripts/docker-full-deploy.sh
./scripts/docker-full-deploy.sh
```

Bu script:
- Docker ve Docker Compose kurulumunu kontrol eder
- `.env` dosyası oluşturur (gerekirse)
- Cloudflare Tunnel yapılandırmasını kontrol eder
- Tüm Docker image'lerini build eder
- Database migration yapar
- Tüm servisleri başlatır

### 4. Manuel Deployment

```bash
# 1. .env dosyası oluştur
cat > .env <<EOF
POSTGRES_PASSWORD=$(openssl rand -base64 32)
JWT_SECRET=$(openssl rand -hex 32)
CORS_ORIGINS=https://novacore.siyahkare.com,https://api.novacore.siyahkare.com
NEXT_PUBLIC_AURORA_API_URL=https://api.novacore.siyahkare.com/api/v1
NEXT_PUBLIC_AURORA_ENV=production
TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
TELEGRAM_BRIDGE_TOKEN=$(openssl rand -hex 32)
TELEGRAM_LINK_SECRET=$(openssl rand -hex 32)
NOVACORE_URL=http://novacore-api:8000
CLOUDFLARE_TUNNEL_TOKEN=YOUR_TUNNEL_TOKEN_HERE
DEBUG=false
EOF

# 2. Build ve başlat
docker compose -f docker-compose.full.yml up -d --build

# 3. Migration
docker compose -f docker-compose.full.yml run --rm novacore-api alembic upgrade head

# 4. Durum kontrolü
docker compose -f docker-compose.full.yml ps
```

## 📋 Servisler

### Backend API (FastAPI)
- **Container:** `novacore-api`
- **Port:** `8000` (localhost only)
- **Health:** `http://localhost:8000/health`
- **Docs:** `http://localhost:8000/docs`

### Frontend (Next.js)
- **Container:** `novacore-frontend`
- **Port:** `3000` (localhost only)
- **Health:** `http://localhost:3000`

### NasipQuest Bot
- **Container:** `nasipquest-bot`
- **Logs:** `docker compose -f docker-compose.full.yml logs -f nasipquest-bot`

### Cloudflare Tunnel
- **Container:** `novacore-cloudflared`
- **Frontend:** `https://novacore.siyahkare.com`
- **Backend:** `https://api.novacore.siyahkare.com`

## 🔧 Yönetim

### Loglar

```bash
# Tüm loglar
docker compose -f docker-compose.full.yml logs -f

# Sadece backend
docker compose -f docker-compose.full.yml logs -f novacore-api

# Sadece frontend
docker compose -f docker-compose.full.yml logs -f novacore-frontend

# Sadece bot
docker compose -f docker-compose.full.yml logs -f nasipquest-bot

# Sadece tunnel
docker compose -f docker-compose.full.yml logs -f cloudflared
```

### Servis Yönetimi

```bash
# Servisleri durdur
docker compose -f docker-compose.full.yml down

# Servisleri yeniden başlat
docker compose -f docker-compose.full.yml restart

# Sadece bir servisi yeniden başlat
docker compose -f docker-compose.full.yml restart novacore-api

# Servisleri durdur ve volume'ları sil (DİKKAT!)
docker compose -f docker-compose.full.yml down -v
```

### Database Yönetimi

```bash
# Database'e bağlan
docker compose -f docker-compose.full.yml exec postgres psql -U novacore -d novacore

# Backup al
docker compose -f docker-compose.full.yml exec postgres pg_dump -U novacore novacore > backup_$(date +%Y%m%d).sql

# Backup'tan geri yükle
docker compose -f docker-compose.full.yml exec -T postgres psql -U novacore -d novacore < backup.sql
```

### Migration

```bash
# Yeni migration çalıştır
docker compose -f docker-compose.full.yml run --rm novacore-api alembic upgrade head

# Migration geri al
docker compose -f docker-compose.full.yml run --rm novacore-api alembic downgrade -1
```

## 🔒 Güvenlik

### 1. Port Binding

Tüm servisler sadece `127.0.0.1` üzerinden erişilebilir:
- Backend: `127.0.0.1:8000`
- Frontend: `127.0.0.1:3000`
- Database: `127.0.0.1:5432`

Dışarıdan erişim sadece Cloudflare Tunnel üzerinden.

### 2. Environment Variables

`.env` dosyasını asla commit etme! `.gitignore`'da olmalı.

### 3. Şifreler

Güçlü şifreler kullan:
```bash
openssl rand -base64 32  # PostgreSQL
openssl rand -hex 32     # JWT
```

## 🌐 Cloudflare Tunnel

### Token Alma

1. Cloudflare Dashboard → Zero Trust → Tunnels
2. "Create a tunnel" → "Cloudflared"
3. Token'ı kopyala ve `.env` dosyasına ekle

### Yapılandırma

`cloudflare-tunnel.yml` dosyası otomatik olarak:
- `api.novacore.siyahkare.com` → Backend API
- `novacore.siyahkare.com` → Frontend

### DNS Ayarları

Tunnel oluşturulduğunda DNS kayıtları otomatik eklenir. Manuel kontrol için:
```bash
# Tunnel listesi
cloudflared tunnel list

# DNS route'ları
cloudflared tunnel route dns list novacore-tunnel
```

## 🔄 Güncelleme

```bash
# 1. Kodu güncelle
cd /opt/novacore/NovaCore
git pull origin main

# 2. Image'leri yeniden build et
docker compose -f docker-compose.full.yml build --no-cache

# 3. Servisleri yeniden başlat
docker compose -f docker-compose.full.yml up -d

# 4. Migration varsa çalıştır
docker compose -f docker-compose.full.yml run --rm novacore-api alembic upgrade head
```

## 🐛 Troubleshooting

### Container Başlamıyor

```bash
# Logları kontrol et
docker compose -f docker-compose.full.yml logs <container-name>

# Container'a gir
docker compose -f docker-compose.full.yml exec <container-name> /bin/sh
```

### Frontend Build Hatası

```bash
# Next.js standalone output kontrolü
grep "output:" apps/citizen-portal/next.config.js

# Manuel build
cd apps/citizen-portal
npm run build
```

### Bot Çalışmıyor

```bash
# Bot logları
docker compose -f docker-compose.full.yml logs nasipquest-bot

# Bot token kontrolü
docker compose -f docker-compose.full.yml exec nasipquest-bot env | grep TELEGRAM_BOT_TOKEN
```

### Cloudflare Tunnel Bağlanmıyor

```bash
# Tunnel logları
docker compose -f docker-compose.full.yml logs cloudflared

# Token kontrolü
echo $CLOUDFLARE_TUNNEL_TOKEN

# Manuel test
cloudflared tunnel run --token $CLOUDFLARE_TUNNEL_TOKEN
```

## ✅ Production Checklist

- [ ] `.env` dosyası oluşturuldu ve tüm değerler dolduruldu
- [ ] Docker ve Docker Compose kuruldu
- [ ] Tüm image'ler build edildi
- [ ] Database migration yapıldı
- [ ] Tüm servisler çalışıyor
- [ ] Health check'ler başarılı
- [ ] Cloudflare Tunnel yapılandırıldı ve çalışıyor
- [ ] DNS kayıtları doğru
- [ ] Firewall ayarları yapıldı
- [ ] Backup stratejisi belirlendi

