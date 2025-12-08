#!/bin/bash

# Cloudflare Tunnel Setup Script
# siyahkare.com için otomatik Cloudflare Tunnel kurulumu

set -e

echo "🚀 Cloudflare Tunnel Kurulumu Başlatılıyor..."

# Renkler
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Kontroller
if ! command -v cloudflared &> /dev/null; then
    echo -e "${RED}❌ cloudflared bulunamadı!${NC}"
    echo "Kurulum için: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/"
    exit 1
fi

# Cloudflare hesap bilgileri
# Environment variable'lardan oku veya interaktif sor
if [ -z "$CF_ACCOUNT_ID" ]; then
    echo -e "${YELLOW}📋 Cloudflare Account ID gerekli:${NC}"
    read -p "Cloudflare Account ID: " CF_ACCOUNT_ID
fi

if [ -z "$CF_API_TOKEN" ]; then
    echo -e "${YELLOW}📋 Cloudflare API Token gerekli (gerekli izinler: Account.Cloudflare Tunnel.Edit):${NC}"
    read -p "Cloudflare API Token: " CF_API_TOKEN
fi

if [ -z "$CF_ACCOUNT_ID" ] || [ -z "$CF_API_TOKEN" ]; then
    echo -e "${RED}❌ Account ID ve API Token gerekli!${NC}"
    echo -e "${YELLOW}💡 İpucu: Environment variable olarak ayarlayabilirsiniz:${NC}"
    echo "   export CF_ACCOUNT_ID='your-account-id'"
    echo "   export CF_API_TOKEN='your-api-token'"
    exit 1
fi

# Tunnel adı
TUNNEL_NAME="novacore-siyahkare"
CONFIG_DIR="$HOME/.cloudflared"
CONFIG_FILE="$CONFIG_DIR/config.yml"

echo -e "${GREEN}✅ cloudflared bulundu${NC}"

# Tunnel oluştur
echo -e "${YELLOW}🔨 Tunnel oluşturuluyor: $TUNNEL_NAME${NC}"
cloudflared tunnel create "$TUNNEL_NAME" || {
    echo -e "${YELLOW}⚠️  Tunnel zaten var, devam ediliyor...${NC}"
}

# Tunnel ID'yi al
TUNNEL_ID=$(cloudflared tunnel list --output json | jq -r ".[] | select(.name==\"$TUNNEL_NAME\") | .id")

if [ -z "$TUNNEL_ID" ]; then
    echo -e "${RED}❌ Tunnel ID alınamadı!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Tunnel ID: $TUNNEL_ID${NC}"

# Config dizini oluştur
mkdir -p "$CONFIG_DIR"

# Config dosyası oluştur
echo -e "${YELLOW}📝 Config dosyası oluşturuluyor...${NC}"
cat > "$CONFIG_FILE" << EOF
tunnel: $TUNNEL_ID
credentials-file: $CONFIG_DIR/$TUNNEL_ID.json

ingress:
  # Backend API
  - hostname: api.siyahkare.com
    service: http://localhost:8000
  
  # Frontend Portal
  - hostname: portal.siyahkare.com
    service: http://localhost:3000
  
  # Catch-all (404)
  - service: http_status:404
EOF

echo -e "${GREEN}✅ Config dosyası oluşturuldu: $CONFIG_FILE${NC}"

# DNS route oluştur
echo -e "${YELLOW}🌐 DNS route'ları oluşturuluyor...${NC}"

# Backend API route
cloudflared tunnel route dns "$TUNNEL_NAME" api.siyahkare.com || {
    echo -e "${YELLOW}⚠️  Backend route zaten var${NC}"
}

# Frontend Portal route
cloudflared tunnel route dns "$TUNNEL_NAME" portal.siyahkare.com || {
    echo -e "${YELLOW}⚠️  Frontend route zaten var${NC}"
}

echo -e "${GREEN}✅ DNS route'ları oluşturuldu${NC}"

# Systemd service oluştur (Linux için)
if command -v systemctl &> /dev/null; then
    echo -e "${YELLOW}⚙️  Systemd service oluşturuluyor...${NC}"
    
    SERVICE_FILE="/etc/systemd/system/cloudflared-tunnel.service"
    
    sudo tee "$SERVICE_FILE" > /dev/null << EOF
[Unit]
Description=Cloudflare Tunnel for NovaCore
After=network.target

[Service]
Type=simple
User=$USER
ExecStart=/usr/local/bin/cloudflared tunnel --config $CONFIG_FILE run $TUNNEL_NAME
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable cloudflared-tunnel
    sudo systemctl start cloudflared-tunnel
    
    echo -e "${GREEN}✅ Systemd service oluşturuldu ve başlatıldı${NC}"
    echo -e "${YELLOW}📋 Service durumu: sudo systemctl status cloudflared-tunnel${NC}"
else
    echo -e "${YELLOW}⚠️  Systemd bulunamadı, manuel başlatma gerekli${NC}"
    echo -e "${YELLOW}📋 Manuel başlatma: cloudflared tunnel --config $CONFIG_FILE run $TUNNEL_NAME${NC}"
fi

# Test
echo -e "${YELLOW}🧪 Tunnel test ediliyor...${NC}"
sleep 2

if cloudflared tunnel info "$TUNNEL_NAME" &> /dev/null; then
    echo -e "${GREEN}✅ Tunnel başarıyla çalışıyor!${NC}"
else
    echo -e "${RED}❌ Tunnel test başarısız!${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 Cloudflare Tunnel kurulumu tamamlandı!${NC}"
echo ""
echo -e "${YELLOW}📋 Sonraki adımlar:${NC}"
echo "1. Backend'i başlat: uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo "2. Frontend'i başlat: cd apps/citizen-portal && npm run dev"
echo "3. Test et:"
echo "   - Backend: https://api.siyahkare.com/health"
echo "   - Frontend: https://portal.siyahkare.com"
echo ""
echo -e "${YELLOW}📚 Dokümantasyon: docs/CLOUDFLARE_SETUP.md${NC}"

