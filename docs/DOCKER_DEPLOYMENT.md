# Docker ile NovaCore Backend Deployment

EC2 üzerinde sadece backend API'yi Docker ile yayınlama rehberi.

## 🚀 Hızlı Kurulum

### 1. Docker ve Docker Compose Kur

```bash
# Docker kur
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
rm get-docker.sh

# Docker Compose kur
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Yeni grup için logout/login gerekebilir
newgrp docker
```

### 2. Projeyi Klonla

```bash
cd /opt
sudo mkdir -p novacore
sudo chown $USER:$USER novacore
cd novacore
git clone https://github.com/YOUR_USERNAME/NovaCore.git
cd NovaCore
```

### 3. Environment Variables Ayarla

```bash
# .env dosyası oluştur
cp .env.docker.example .env
nano .env

# Şu değerleri değiştir:
# - POSTGRES_PASSWORD: Güçlü bir şifre
# - JWT_SECRET: Güçlü bir secret (openssl rand -hex 32)
# - CORS_ORIGINS: Domain'lerin
```

### 4. Otomatik Deployment

```bash
chmod +x scripts/docker-deploy.sh
./scripts/docker-deploy.sh
```

### 5. Manuel Deployment

```bash
# 1. Build
docker compose -f docker-compose.prod.yml build

# 2. Database'i başlat
docker compose -f docker-compose.prod.yml up -d postgres

# 3. Migration
docker compose -f docker-compose.prod.yml run --rm novacore-api alembic upgrade head

# 4. Tüm servisleri başlat
docker compose -f docker-compose.prod.yml up -d

# 5. Durum kontrolü
docker compose -f docker-compose.prod.yml ps
```

## 📋 Docker Compose Dosyaları

### `docker-compose.prod.yml` (Hot-reload ile)
- Development için uygun
- Kod değişiklikleri otomatik yansır
- Volume mount kullanır

### `docker-compose.prod.no-reload.yml` (Production)
- Production için optimize
- Volume mount yok
- Daha güvenli

## 🔧 Yönetim

### Loglar

```bash
# Tüm loglar
docker compose -f docker-compose.prod.yml logs -f

# Sadece backend
docker compose -f docker-compose.prod.yml logs -f novacore-api

# Sadece database
docker compose -f docker-compose.prod.yml logs -f postgres
```

### Servis Yönetimi

```bash
# Servisleri durdur
docker compose -f docker-compose.prod.yml down

# Servisleri yeniden başlat
docker compose -f docker-compose.prod.yml restart

# Sadece backend'i yeniden başlat
docker compose -f docker-compose.prod.yml restart novacore-api

# Servisleri durdur ve volume'ları sil (DİKKAT!)
docker compose -f docker-compose.prod.yml down -v
```

### Database Yönetimi

```bash
# Database'e bağlan
docker compose -f docker-compose.prod.yml exec postgres psql -U novacore -d novacore

# Backup al
docker compose -f docker-compose.prod.yml exec postgres pg_dump -U novacore novacore > backup_$(date +%Y%m%d).sql

# Backup'tan geri yükle
docker compose -f docker-compose.prod.yml exec -T postgres psql -U novacore -d novacore < backup.sql
```

### Migration

```bash
# Yeni migration çalıştır
docker compose -f docker-compose.prod.yml run --rm novacore-api alembic upgrade head

# Migration geri al
docker compose -f docker-compose.prod.yml run --rm novacore-api alembic downgrade -1
```

## 🔒 Güvenlik

### 1. Port Binding

Docker Compose dosyasında portlar `127.0.0.1:8000:8000` şeklinde bind edilmiş. Bu sayede:
- Sadece localhost'tan erişilebilir
- Cloudflare Tunnel üzerinden güvenli erişim
- Dışarıdan direkt erişim yok

### 2. Environment Variables

`.env` dosyasını asla commit etme! `.gitignore`'da olmalı.

### 3. Database Şifresi

Güçlü bir şifre kullan:
```bash
openssl rand -base64 32
```

## 🌐 Cloudflare Tunnel Entegrasyonu

Backend Docker'da çalışıyorsa, Cloudflare Tunnel'ı host'ta çalıştır:

```bash
# Host'ta Cloudflare Tunnel kur
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb -o /tmp/cloudflared.deb
sudo dpkg -i /tmp/cloudflared.deb

# Tunnel yapılandır
cd /opt/novacore/NovaCore
./scripts/setup-cloudflare-tunnel.sh

# Tunnel'ı başlat (host'ta)
cloudflared tunnel --config cloudflare-tunnel.yml run novacore-tunnel
```

## 📊 Monitoring

### Health Check

```bash
# Backend health
curl http://localhost:8000/health

# Docker container health
docker compose -f docker-compose.prod.yml ps
```

### Resource Usage

```bash
# Container resource kullanımı
docker stats

# Disk kullanımı
docker system df
```

## 🔄 Güncelleme

```bash
# 1. Kodu güncelle
cd /opt/novacore/NovaCore
git pull origin main

# 2. Image'i yeniden build et
docker compose -f docker-compose.prod.yml build --no-cache

# 3. Servisleri yeniden başlat
docker compose -f docker-compose.prod.yml up -d

# 4. Migration varsa çalıştır
docker compose -f docker-compose.prod.yml run --rm novacore-api alembic upgrade head
```

## 🐛 Troubleshooting

### Container Başlamıyor

```bash
# Logları kontrol et
docker compose -f docker-compose.prod.yml logs novacore-api

# Container'a gir
docker compose -f docker-compose.prod.yml exec novacore-api /bin/bash
```

### Database Bağlantı Hatası

```bash
# PostgreSQL logları
docker compose -f docker-compose.prod.yml logs postgres

# Database'e bağlanmayı dene
docker compose -f docker-compose.prod.yml exec postgres psql -U novacore -d novacore
```

### Port Kullanımda

```bash
# Hangi process port'u kullanıyor?
sudo lsof -i :8000
sudo lsof -i :5432

# Docker container'ları kontrol et
docker ps
```

## ✅ Production Checklist

- [ ] `.env` dosyası oluşturuldu ve şifreler değiştirildi
- [ ] Docker ve Docker Compose kuruldu
- [ ] Image build edildi
- [ ] Database migration yapıldı
- [ ] Servisler çalışıyor
- [ ] Health check başarılı
- [ ] Cloudflare Tunnel yapılandırıldı (opsiyonel)
- [ ] Firewall ayarları yapıldı
- [ ] Backup stratejisi belirlendi

