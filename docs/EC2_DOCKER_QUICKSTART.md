# EC2 Docker Quick Start

EC2'de sadece backend API'yi Docker ile hızlıca yayınlama.

## 🚀 5 Dakikada Kurulum

### 1. Docker Kur

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker
rm get-docker.sh

# Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
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

### 3. .env Dosyası Oluştur

```bash
cat > .env <<EOF
POSTGRES_PASSWORD=$(openssl rand -base64 32)
JWT_SECRET=$(openssl rand -hex 32)
CORS_ORIGINS=https://novacore.siyahkare.com,https://api.novacore.siyahkare.com
TELEGRAM_BRIDGE_TOKEN=your-bridge-token-here
TELEGRAM_LINK_SECRET=your-hmac-secret-here
EOF
```

### 4. Docker ile Başlat

```bash
# Build ve başlat
docker compose -f docker-compose.prod.yml up -d --build

# Migration çalıştır
docker compose -f docker-compose.prod.yml run --rm novacore-api alembic upgrade head

# Durum kontrolü
docker compose -f docker-compose.prod.yml ps
```

### 5. Test Et

```bash
# Health check
curl http://localhost:8000/health

# API docs
curl http://localhost:8000/docs
```

## 📋 Yönetim

```bash
# Logları gör
docker compose -f docker-compose.prod.yml logs -f novacore-api

# Yeniden başlat
docker compose -f docker-compose.prod.yml restart novacore-api

# Durdur
docker compose -f docker-compose.prod.yml down

# Durdur ve volume'ları sil (DİKKAT!)
docker compose -f docker-compose.prod.yml down -v
```

## 🌐 Cloudflare Tunnel (Opsiyonel)

```bash
# Host'ta Cloudflare Tunnel kur
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb -o /tmp/cloudflared.deb
sudo dpkg -i /tmp/cloudflared.deb

# Tunnel yapılandır
./scripts/setup-cloudflare-tunnel.sh

# Tunnel'ı başlat
cloudflared tunnel --config cloudflare-tunnel.yml run novacore-tunnel
```

## ✅ Hazır!

Backend API artık `http://localhost:8000` adresinde çalışıyor. Cloudflare Tunnel ile `https://api.novacore.siyahkare.com` üzerinden erişilebilir.

