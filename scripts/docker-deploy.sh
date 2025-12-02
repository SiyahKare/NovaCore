#!/bin/bash
# Docker ile NovaCore Backend Deployment Scripti
# EC2 için optimize edilmiş

set -e

echo "🐳 NovaCore Docker Deployment"
echo "============================="
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
    echo -e "${YELLOW}⚠️  .env dosyası bulunamadı. Örnek dosyadan oluşturuluyor...${NC}"
    if [ -f .env.docker.example ]; then
        cp .env.docker.example .env
        echo -e "${YELLOW}⚠️  .env dosyası oluşturuldu. Lütfen şifreleri değiştirin!${NC}"
        echo -e "${YELLOW}   nano .env${NC}"
        read -p "Şifreleri değiştirdin mi? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${RED}❌ Şifreleri değiştirmen gerekiyor!${NC}"
            exit 1
        fi
    else
        echo -e "${RED}❌ .env.docker.example bulunamadı!${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ .env dosyası mevcut${NC}"
fi

echo ""

# 3. Docker image build
echo -e "${GREEN}🏗️  Docker image build ediliyor...${NC}"
docker compose -f docker-compose.prod.yml build --no-cache

echo ""

# 4. Database migration
echo -e "${GREEN}🗄️  Database migration yapılıyor...${NC}"
docker compose -f docker-compose.prod.yml up -d postgres

# PostgreSQL'in hazır olmasını bekle
echo "PostgreSQL'in hazır olması bekleniyor..."
sleep 10

# Migration çalıştır
docker compose -f docker-compose.prod.yml run --rm novacore-api alembic upgrade head

echo ""

# 5. Servisleri başlat
echo -e "${GREEN}🚀 Servisler başlatılıyor...${NC}"
docker compose -f docker-compose.prod.yml up -d

echo ""

# 6. Durum kontrolü
echo -e "${GREEN}📊 Servis durumları:${NC}"
docker compose -f docker-compose.prod.yml ps

echo ""
echo -e "${GREEN}✅ Deployment tamamlandı!${NC}"
echo ""
echo "🌐 Erişim:"
echo "  - Backend API: http://localhost:8000"
echo "  - Health Check: http://localhost:8000/health"
echo "  - API Docs: http://localhost:8000/docs"
echo ""
echo "📝 Yönetim komutları:"
echo "  - Logları gör: docker compose -f docker-compose.prod.yml logs -f"
echo "  - Servisleri durdur: docker compose -f docker-compose.prod.yml down"
echo "  - Servisleri yeniden başlat: docker compose -f docker-compose.prod.yml restart"
echo "  - Database backup: docker compose -f docker-compose.prod.yml exec postgres pg_dump -U novacore novacore > backup.sql"
echo ""

