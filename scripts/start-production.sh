#!/bin/bash
# NovaCore Production Başlatma Scripti
# Cloudflare Tunnel ile birlikte backend ve frontend'i başlatır

set -e

echo "🚀 NovaCore Production Başlatılıyor"
echo "===================================="
echo ""

# Renkler
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. Environment kontrolü
echo "📋 Environment kontrol ediliyor..."
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env dosyası bulunamadı. .env.production.example'dan kopyalıyoruz...${NC}"
    if [ -f ".env.production.example" ]; then
        cp .env.production.example .env
        echo -e "${GREEN}✅ .env dosyası oluşturuldu. Lütfen gerekli değerleri doldurun.${NC}"
    else
        echo -e "${RED}❌ .env.production.example bulunamadı!${NC}"
        exit 1
    fi
fi

# 2. Backend kontrolü
echo ""
echo "🔧 Backend kontrol ediliyor..."
if ! command -v uvicorn &> /dev/null; then
    echo -e "${RED}❌ uvicorn bulunamadı. Lütfen Python dependencies'leri yükleyin:${NC}"
    echo "   pip install -e ."
    exit 1
fi

# 3. Frontend kontrolü
echo ""
echo "🎨 Frontend kontrol ediliyor..."
if [ ! -d "apps/citizen-portal" ]; then
    echo -e "${RED}❌ Frontend dizini bulunamadı!${NC}"
    exit 1
fi

if [ ! -f "apps/citizen-portal/.env.local" ]; then
    echo -e "${YELLOW}⚠️  Frontend .env.local bulunamadı. .env.production.example'dan kopyalıyoruz...${NC}"
    if [ -f "apps/citizen-portal/.env.production.example" ]; then
        cp apps/citizen-portal/.env.production.example apps/citizen-portal/.env.local
        echo -e "${GREEN}✅ Frontend .env.local oluşturuldu.${NC}"
    fi
fi

# 4. Cloudflare Tunnel kontrolü
echo ""
echo "🌐 Cloudflare Tunnel kontrol ediliyor..."
if ! command -v cloudflared &> /dev/null; then
    echo -e "${YELLOW}⚠️  cloudflared bulunamadı. Kurulum scriptini çalıştırın:${NC}"
    echo "   ./scripts/setup-cloudflare-tunnel.sh"
    echo ""
    read -p "Devam etmek istiyor musunuz? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 5. Database kontrolü
echo ""
echo "🗄️  Database kontrol ediliyor..."
if ! pg_isready -h localhost -p 5432 &> /dev/null && ! pg_isready -h localhost -p 5433 &> /dev/null; then
    echo -e "${YELLOW}⚠️  PostgreSQL çalışmıyor gibi görünüyor.${NC}"
    echo "   Docker ile başlatmak için: docker-compose up -d postgres"
    echo ""
    read -p "Devam etmek istiyor musunuz? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 6. Servisleri başlat
echo ""
echo "🚀 Servisler başlatılıyor..."
echo ""

# Backend'i arka planda başlat
echo -e "${GREEN}📡 Backend başlatılıyor (port 8000)...${NC}"
uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

# Frontend'i arka planda başlat
echo -e "${GREEN}🎨 Frontend başlatılıyor (port 3000)...${NC}"
cd apps/citizen-portal
npm run dev > ../../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ../..
echo "   Frontend PID: $FRONTEND_PID"

# Cloudflare Tunnel'ı başlat
if command -v cloudflared &> /dev/null; then
    echo -e "${GREEN}🌐 Cloudflare Tunnel başlatılıyor...${NC}"
    # Config file ile başlat (credentials file otomatik kullanılır)
    cloudflared tunnel --config cloudflare-tunnel.yml run novacore-tunnel > tunnel.log 2>&1 &
    TUNNEL_PID=$!
    echo "   Tunnel PID: $TUNNEL_PID"
else
    echo -e "${YELLOW}⚠️  cloudflared bulunamadı, tunnel başlatılmadı.${NC}"
    TUNNEL_PID=""
fi

# 7. Health check
echo ""
echo "⏳ Servislerin hazır olması bekleniyor (10 saniye)..."
sleep 10

echo ""
echo "🏥 Health check yapılıyor..."

# Backend health check
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✅ Backend çalışıyor${NC}"
else
    echo -e "${RED}❌ Backend yanıt vermiyor!${NC}"
fi

# Frontend health check
if curl -s http://localhost:3000 > /dev/null; then
    echo -e "${GREEN}✅ Frontend çalışıyor${NC}"
else
    echo -e "${RED}❌ Frontend yanıt vermiyor!${NC}"
fi

echo ""
echo "===================================="
echo -e "${GREEN}✅ NovaCore Production Hazır!${NC}"
echo ""
echo "🌐 Erişim Adresleri:"
echo "   - Frontend: https://novacore.siyahkare.com"
echo "   - Backend API: https://api.novacore.siyahkare.com"
echo ""
echo "📊 Log Dosyaları:"
echo "   - Backend: backend.log"
echo "   - Frontend: frontend.log"
echo "   - Tunnel: tunnel.log"
echo ""
echo "🛑 Durdurmak için:"
echo "   kill $BACKEND_PID $FRONTEND_PID $TUNNEL_PID"
echo "   veya: pkill -f 'uvicorn|next-server|cloudflared'"
echo ""

# PID'leri dosyaya kaydet
echo "$BACKEND_PID" > .backend.pid
echo "$FRONTEND_PID" > .frontend.pid
[ -n "$TUNNEL_PID" ] && echo "$TUNNEL_PID" > .tunnel.pid

echo "PID'ler kaydedildi: .backend.pid, .frontend.pid, .tunnel.pid"
echo ""

