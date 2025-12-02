#!/bin/bash
# NovaCore Full Stack Docker Deployment Script
# Backend + Frontend + Bot + Cloudflare Tunnel

set -e

echo "🐳 NovaCore Full Stack Docker Deployment"
echo "========================================"
echo ""

# Renkler
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 1. Docker kontrolü
echo -e "${GREEN}🐳 Docker kontrol ediliyor...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker bulunamadı. Kurulum yapılıyor...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo -e "${YELLOW}⚠️  Docker kuruldu. Yeni grup ayarları için logout/login gerekebilir.${NC}"
    newgrp docker || true
else
    echo -e "${GREEN}✅ Docker zaten kurulu: $(docker --version)${NC}"
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose bulunamadı. Kurulum yapılıyor...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
else
    echo -e "${GREEN}✅ Docker Compose zaten kurulu${NC}"
fi

echo ""

# 2. .env dosyası kontrolü
echo -e "${GREEN}⚙️  Environment variables kontrol ediliyor...${NC}"
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env dosyası bulunamadı. Oluşturuluyor...${NC}"
    cat > .env <<EOF
# PostgreSQL
POSTGRES_PASSWORD=$(openssl rand -base64 32)

# JWT
JWT_SECRET=$(openssl rand -hex 32)

# CORS
CORS_ORIGINS=https://novacore.siyahkare.com,https://api.novacore.siyahkare.com

# Frontend
NEXT_PUBLIC_AURORA_API_URL=https://api.novacore.siyahkare.com/api/v1
NEXT_PUBLIC_AURORA_ENV=production

# Telegram
TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
TELEGRAM_BRIDGE_TOKEN=$(openssl rand -hex 32)
TELEGRAM_LINK_SECRET=$(openssl rand -hex 32)

# NovaCore URL (bot için)
NOVACORE_URL=http://novacore-api:8000

# Cloudflare Tunnel
CLOUDFLARE_TUNNEL_TOKEN=YOUR_TUNNEL_TOKEN_HERE

# Debug
DEBUG=false
EOF
    echo -e "${YELLOW}⚠️  .env dosyası oluşturuldu. Lütfen şu değerleri doldurun:${NC}"
    echo -e "${YELLOW}   - TELEGRAM_BOT_TOKEN${NC}"
    echo -e "${YELLOW}   - CLOUDFLARE_TUNNEL_TOKEN${NC}"
    echo ""
    read -p "Değerleri doldurdun mu? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}❌ Lütfen .env dosyasını düzenleyin: nano .env${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ .env dosyası mevcut${NC}"
    # Eksik değişkenleri kontrol et
    if ! grep -q "TELEGRAM_BOT_TOKEN" .env || grep -q "YOUR_BOT_TOKEN_HERE" .env; then
        echo -e "${YELLOW}⚠️  TELEGRAM_BOT_TOKEN eksik veya placeholder!${NC}"
    fi
    if ! grep -q "CLOUDFLARE_TUNNEL_TOKEN" .env || grep -q "YOUR_TUNNEL_TOKEN_HERE" .env; then
        echo -e "${YELLOW}⚠️  CLOUDFLARE_TUNNEL_TOKEN eksik veya placeholder!${NC}"
    fi
fi

echo ""

# 3. Cloudflare Tunnel yapılandırması
echo -e "${GREEN}🌐 Cloudflare Tunnel yapılandırması kontrol ediliyor...${NC}"
if [ ! -f cloudflare-tunnel.yml ]; then
    echo -e "${YELLOW}⚠️  cloudflare-tunnel.yml bulunamadı. Oluşturuluyor...${NC}"
    # cloudflare-tunnel.yml zaten var, kontrol et
    if [ -f cloudflare-tunnel.yml ]; then
        echo -e "${GREEN}✅ cloudflare-tunnel.yml mevcut${NC}"
    else
        echo -e "${RED}❌ cloudflare-tunnel.yml dosyası bulunamadı!${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ cloudflare-tunnel.yml mevcut${NC}"
fi

# Cloudflare Tunnel token kontrolü
if [ -z "$CLOUDFLARE_TUNNEL_TOKEN" ] && ! grep -q "CLOUDFLARE_TUNNEL_TOKEN=" .env 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Cloudflare Tunnel token yok. Otomatik kurulum yapılacak...${NC}"
    if [ -f scripts/setup-cloudflare-tunnel.sh ]; then
        chmod +x scripts/setup-cloudflare-tunnel.sh
        ./scripts/setup-cloudflare-tunnel.sh
    else
        echo -e "${YELLOW}⚠️  setup-cloudflare-tunnel.sh bulunamadı. Manuel kurulum gerekebilir.${NC}"
    fi
fi

echo ""

# 4. Next.js standalone output ayarı
echo -e "${GREEN}⚙️  Next.js yapılandırması kontrol ediliyor...${NC}"
if [ -f apps/citizen-portal/next.config.js ]; then
    if ! grep -q "output: 'standalone'" apps/citizen-portal/next.config.js; then
        echo -e "${YELLOW}⚠️  Next.js standalone output ayarı ekleniyor...${NC}"
        # next.config.js'e output: 'standalone' ekle
        # Bu işlem manuel yapılmalı veya sed ile yapılabilir
        echo -e "${YELLOW}⚠️  Lütfen apps/citizen-portal/next.config.js dosyasına 'output: \"standalone\"' ekleyin.${NC}"
    else
        echo -e "${GREEN}✅ Next.js standalone output ayarı mevcut${NC}"
    fi
fi

echo ""

# 5. Docker image build
echo -e "${GREEN}🏗️  Docker image'ler build ediliyor...${NC}"
echo -e "${YELLOW}   Bu işlem birkaç dakika sürebilir...${NC}"
docker compose -f docker-compose.full.yml build --no-cache

echo ""

# 6. Database migration
echo -e "${GREEN}🗄️  Database migration yapılıyor...${NC}"
docker compose -f docker-compose.full.yml up -d postgres

# PostgreSQL'in hazır olmasını bekle
echo "PostgreSQL'in hazır olması bekleniyor..."
for i in {1..30}; do
    if docker compose -f docker-compose.full.yml exec -T postgres pg_isready -U novacore -d novacore > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PostgreSQL hazır${NC}"
        break
    fi
    echo -n "."
    sleep 1
done
echo ""

# Migration çalıştır
echo "Migration çalıştırılıyor..."
docker compose -f docker-compose.full.yml run --rm novacore-api alembic upgrade head

echo ""

# 7. Tüm servisleri başlat
echo -e "${GREEN}🚀 Tüm servisler başlatılıyor...${NC}"
docker compose -f docker-compose.full.yml up -d

echo ""

# 8. Durum kontrolü
echo -e "${GREEN}📊 Servis durumları:${NC}"
sleep 5
docker compose -f docker-compose.full.yml ps

echo ""

# 9. Health check
echo -e "${GREEN}🏥 Health check yapılıyor...${NC}"
sleep 10

# Backend health check
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend API çalışıyor${NC}"
else
    echo -e "${YELLOW}⚠️  Backend API henüz hazır değil (normal, biraz bekleyebilir)${NC}"
fi

# Frontend health check
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend çalışıyor${NC}"
else
    echo -e "${YELLOW}⚠️  Frontend henüz hazır değil (normal, biraz bekleyebilir)${NC}"
fi

echo ""
echo -e "${GREEN}✅ Deployment tamamlandı!${NC}"
echo ""
echo "🌐 Erişim:"
echo "  - Frontend: http://localhost:3000"
echo "  - Backend API: http://localhost:8000"
echo "  - Health Check: http://localhost:8000/health"
echo "  - API Docs: http://localhost:8000/docs"
echo ""
echo "🌍 Cloudflare Tunnel:"
echo "  - Frontend: https://novacore.siyahkare.com"
echo "  - Backend API: https://api.novacore.siyahkare.com"
echo ""
echo "📝 Yönetim komutları:"
echo "  - Logları gör: docker compose -f docker-compose.full.yml logs -f"
echo "  - Sadece backend logları: docker compose -f docker-compose.full.yml logs -f novacore-api"
echo "  - Sadece frontend logları: docker compose -f docker-compose.full.yml logs -f novacore-frontend"
echo "  - Sadece bot logları: docker compose -f docker-compose.full.yml logs -f nasipquest-bot"
echo "  - Servisleri durdur: docker compose -f docker-compose.full.yml down"
echo "  - Servisleri yeniden başlat: docker compose -f docker-compose.full.yml restart"
echo "  - Database backup: docker compose -f docker-compose.full.yml exec postgres pg_dump -U novacore novacore > backup.sql"
echo ""

