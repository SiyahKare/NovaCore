#!/bin/bash
# EC2 NovaCore Kurulum Scripti
# Ubuntu 22.04 LTS için optimize edilmiş

set -e

echo "🚀 NovaCore EC2 Kurulumu"
echo "========================"
echo ""

# Renkler
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 1. Sistem güncellemesi
echo -e "${GREEN}📦 Sistem güncelleniyor...${NC}"
sudo apt-get update
sudo apt-get upgrade -y

# 2. Temel paketler
echo -e "${GREEN}📦 Temel paketler kuruluyor...${NC}"
sudo apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    software-properties-common \
    postgresql \
    postgresql-contrib \
    nginx \
    certbot \
    python3-certbot-nginx \
    nodejs \
    npm \
    ufw \
    htop \
    vim

# 3. Python 3.11 kurulumu (Ubuntu 22.04 için)
echo -e "${GREEN}🐍 Python 3.11 kuruluyor...${NC}"
# Ubuntu 22.04'te Python 3.10 varsayılan, 3.11 için deadsnakes PPA ekle
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip

# 4. Node.js LTS kurulumu (npm ile gelen versiyon eski olabilir)
echo -e "${GREEN}📦 Node.js LTS kuruluyor...${NC}"
if ! command -v node &> /dev/null || [ "$(node -v | cut -d'v' -f2 | cut -d'.' -f1)" -lt 20 ]; then
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

# 5. PostgreSQL yapılandırması
echo -e "${GREEN}🗄️  PostgreSQL yapılandırılıyor...${NC}"
sudo systemctl start postgresql
sudo systemctl enable postgresql

# PostgreSQL kullanıcı ve database oluştur
sudo -u postgres psql <<EOF
CREATE USER novacore WITH PASSWORD 'CHANGE_THIS_PASSWORD';
CREATE DATABASE novacore OWNER novacore;
GRANT ALL PRIVILEGES ON DATABASE novacore TO novacore;
\q
EOF

# 6. Python virtual environment
echo -e "${GREEN}🐍 Python virtual environment oluşturuluyor...${NC}"
cd /opt
sudo mkdir -p novacore
sudo chown $USER:$USER novacore
cd novacore

# Python 3.11'i kullan (veya mevcut Python versiyonunu)
PYTHON_CMD=$(which python3.11 || which python3)
$PYTHON_CMD -m venv .venv
source .venv/bin/activate

# 7. Projeyi klonla (GitHub'dan)
echo -e "${GREEN}📥 Proje klonlanıyor...${NC}"
if [ ! -d "NovaCore" ]; then
    git clone https://github.com/YOUR_USERNAME/NovaCore.git
fi
cd NovaCore

# 8. Python dependencies
echo -e "${GREEN}📦 Python dependencies kuruluyor...${NC}"
pip install --upgrade pip
pip install -e .

# 9. Node.js dependencies
echo -e "${GREEN}📦 Node.js dependencies kuruluyor...${NC}"
npm install

# 10. Environment variables
echo -e "${GREEN}⚙️  Environment variables yapılandırılıyor...${NC}"
if [ ! -f .env ]; then
    cat > .env <<EOF
ENV=prod
DATABASE_URL=postgresql+asyncpg://novacore:CHANGE_THIS_PASSWORD@localhost:5432/novacore
DATABASE_URL_SYNC=postgresql://novacore:CHANGE_THIS_PASSWORD@localhost:5432/novacore
JWT_SECRET=$(openssl rand -hex 32)
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=10080
NCR_TREASURY_USER_ID=1
CORS_ORIGINS=https://novacore.siyahkare.com,https://api.novacore.siyahkare.com
LOG_LEVEL=INFO
EOF
    echo -e "${YELLOW}⚠️  .env dosyası oluşturuldu. Lütfen şifreleri değiştirin!${NC}"
fi

# Frontend .env
if [ ! -f apps/citizen-portal/.env.local ]; then
    cat > apps/citizen-portal/.env.local <<EOF
NEXT_PUBLIC_AURORA_API_URL=https://api.novacore.siyahkare.com/api/v1
NEXT_PUBLIC_AURORA_ENV=production
EOF
fi

# 11. Database migration
echo -e "${GREEN}🗄️  Database migration yapılıyor...${NC}"
alembic upgrade head

# 12. Cloudflare Tunnel kurulumu
echo -e "${GREEN}🌐 Cloudflare Tunnel kuruluyor...${NC}"
if ! command -v cloudflared &> /dev/null; then
    curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb -o /tmp/cloudflared.deb
    sudo dpkg -i /tmp/cloudflared.deb
    rm /tmp/cloudflared.deb
fi

# 13. Systemd service'leri oluştur
echo -e "${GREEN}⚙️  Systemd service'leri oluşturuluyor...${NC}"

# Backend service
sudo tee /etc/systemd/system/novacore-backend.service > /dev/null <<EOF
[Unit]
Description=NovaCore Backend API
After=network.target postgresql.service

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/novacore/NovaCore
Environment="PATH=/opt/novacore/.venv/bin"
ExecStart=/opt/novacore/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Frontend service
sudo tee /etc/systemd/system/novacore-frontend.service > /dev/null <<EOF
[Unit]
Description=NovaCore Frontend
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/novacore/NovaCore/apps/citizen-portal
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/npm run start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Cloudflare Tunnel service
sudo tee /etc/systemd/system/novacore-cloudflared.service > /dev/null <<EOF
[Unit]
Description=Cloudflare Tunnel for NovaCore
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/novacore/NovaCore
ExecStart=/usr/local/bin/cloudflared tunnel --config /opt/novacore/NovaCore/cloudflare-tunnel.yml run novacore-tunnel
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 14. Firewall yapılandırması
echo -e "${GREEN}🔥 Firewall yapılandırılıyor...${NC}"
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# 15. Production build
echo -e "${GREEN}🏗️  Production build yapılıyor...${NC}"
cd apps/citizen-portal
npm run build
cd ../..

# 16. Service'leri başlat
echo -e "${GREEN}🚀 Service'ler başlatılıyor...${NC}"
sudo systemctl daemon-reload
sudo systemctl enable novacore-backend
sudo systemctl enable novacore-frontend
sudo systemctl enable novacore-cloudflared

sudo systemctl start novacore-backend
sudo systemctl start novacore-frontend
sudo systemctl start novacore-cloudflared

# 17. Durum kontrolü
echo ""
echo -e "${GREEN}✅ Kurulum tamamlandı!${NC}"
echo ""
echo "📊 Service durumları:"
sudo systemctl status novacore-backend --no-pager -l | head -5
sudo systemctl status novacore-frontend --no-pager -l | head -5
sudo systemctl status novacore-cloudflared --no-pager -l | head -5

echo ""
echo "🌐 Erişim adresleri:"
echo "  - Frontend: https://novacore.siyahkare.com"
echo "  - Backend API: https://api.novacore.siyahkare.com"
echo ""
echo "📝 Sonraki adımlar:"
echo "  1. .env dosyasındaki şifreleri değiştir"
echo "  2. Cloudflare Tunnel'ı yapılandır: ./scripts/setup-cloudflare-tunnel.sh"
echo "  3. Service loglarını kontrol et:"
echo "     sudo journalctl -u novacore-backend -f"
echo "     sudo journalctl -u novacore-frontend -f"
echo "     sudo journalctl -u novacore-cloudflared -f"
echo ""

