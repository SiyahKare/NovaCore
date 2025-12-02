# EC2 Docker Deployment - Hızlı Başlangıç

EC2'de tüm sistemi (Backend + Frontend + Bot + Cloudflare Tunnel) Docker ile yayınlama.

## 🚀 Adım Adım Kurulum

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

### 3. Deployment Scriptini Çalıştır

```bash
chmod +x scripts/ec2-docker-deploy.sh
./scripts/ec2-docker-deploy.sh
```

Script otomatik olarak:
- ✅ Docker ve Docker Compose kurulumunu kontrol eder
- ✅ `.env` dosyası oluşturur (gerekirse)
- ✅ Cloudflare Tunnel yapılandırmasını kontrol eder
- ✅ Tüm Docker image'lerini build eder
- ✅ Database migration yapar
- ✅ Tüm servisleri başlatır

### 4. .env Dosyasını Düzenle

Script `.env` dosyasını oluşturur, ancak şu değerleri manuel doldurman gerekir:

```bash
nano .env
```

**Doldurulması Gerekenler:**
- `TELEGRAM_BOT_TOKEN`: BotFather'dan aldığın bot token
- `CLOUDFLARE_TUNNEL_TOKEN`: Cloudflare Dashboard'dan aldığın tunnel token

**Cloudflare Tunnel Token Alma:**
1. Cloudflare Dashboard → Zero Trust → Tunnels
2. "Create a tunnel" → "Cloudflared"
3. Token'ı kopyala ve `.env` dosyasına ekle

### 5. Servisleri Başlat

`.env` dosyasını düzenledikten sonra:

```bash
docker compose -f docker-compose.full.yml up -d
```

## 📋 Servis Durumları

```bash
# Tüm servislerin durumunu gör
docker compose -f docker-compose.full.yml ps

# Logları gör
docker compose -f docker-compose.full.yml logs -f

# Sadece backend logları
docker compose -f docker-compose.full.yml logs -f novacore-api

# Sadece frontend logları
docker compose -f docker-compose.full.yml logs -f novacore-frontend

# Sadece bot logları
docker compose -f docker-compose.full.yml logs -f nasipquest-bot
```

## 🌐 Erişim

### Localhost (EC2 içinden)
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- Health Check: `http://localhost:8000/health`
- API Docs: `http://localhost:8000/docs`

### Cloudflare Tunnel (Dışarıdan)
- Frontend: `https://novacore.siyahkare.com`
- Backend API: `https://api.novacore.siyahkare.com`

## 🔧 Yönetim

### Servisleri Yeniden Başlat

```bash
# Tüm servisler
docker compose -f docker-compose.full.yml restart

# Sadece bir servis
docker compose -f docker-compose.full.yml restart novacore-api
```

### Servisleri Durdur

```bash
# Servisleri durdur (volume'lar korunur)
docker compose -f docker-compose.full.yml down

# Servisleri durdur ve volume'ları sil (DİKKAT!)
docker compose -f docker-compose.full.yml down -v
```

### Database Backup

```bash
# Backup al
docker compose -f docker-compose.full.yml exec postgres pg_dump -U novacore novacore > backup_$(date +%Y%m%d).sql

# Backup'tan geri yükle
docker compose -f docker-compose.full.yml exec -T postgres psql -U novacore -d novacore < backup.sql
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
grep CLOUDFLARE_TUNNEL_TOKEN .env
```

## ✅ Checklist

- [ ] EC2'ye bağlandım
- [ ] Projeyi klonladım
- [ ] Deployment scriptini çalıştırdım
- [ ] `.env` dosyasını düzenledim
- [ ] `TELEGRAM_BOT_TOKEN` ekledim
- [ ] `CLOUDFLARE_TUNNEL_TOKEN` ekledim
- [ ] Tüm servisler çalışıyor
- [ ] Health check'ler başarılı
- [ ] Cloudflare Tunnel çalışıyor
- [ ] Frontend erişilebilir
- [ ] Backend API erişilebilir

