#!/bin/bash

# Cloudflare Tunnel Bağlantı Script'i
# Mevcut tunnel'ı kullanarak siyahkare.com domain'lerini bağla

set -e

echo "🚀 Cloudflare Tunnel Bağlantısı Başlatılıyor..."

# Renkler
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Tunnel adı
TUNNEL_NAME="novacore-siyahkare"
CONFIG_DIR="$HOME/.cloudflared"
CONFIG_FILE="$CONFIG_DIR/config.yml"

# Tunnel var mı kontrol et
TUNNEL_EXISTS=$(cloudflared tunnel list --output json 2>/dev/null | jq -r ".[] | select(.name==\"$TUNNEL_NAME\") | .id" 2>/dev/null || echo "")

if [ -z "$TUNNEL_EXISTS" ]; then
    echo -e "${YELLOW}🔨 Tunnel bulunamadı, oluşturuluyor: $TUNNEL_NAME${NC}"
    cloudflared tunnel create "$TUNNEL_NAME"
else
    echo -e "${GREEN}✅ Tunnel zaten var: $TUNNEL_NAME${NC}"
fi

# Tunnel ID'yi al
TUNNEL_ID=$(cloudflared tunnel list --output json 2>/dev/null | jq -r ".[] | select(.name==\"$TUNNEL_NAME\") | .id" 2>/dev/null || echo "")

if [ -z "$TUNNEL_ID" ]; then
    echo -e "${RED}❌ Tunnel ID alınamadı!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Tunnel ID: $TUNNEL_ID${NC}"

# Config dizini oluştur
mkdir -p "$CONFIG_DIR"

# Config dosyası oluştur/güncelle
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

# DNS route'ları oluştur
echo -e "${YELLOW}🌐 DNS route'ları oluşturuluyor...${NC}"

# Backend API route
echo -e "${YELLOW}  → api.siyahkare.com${NC}"
cloudflared tunnel route dns "$TUNNEL_NAME" api.siyahkare.com 2>&1 | grep -v "already exists" || {
    echo -e "${YELLOW}    ⚠️  Route zaten var${NC}"
}

# Frontend Portal route
echo -e "${YELLOW}  → portal.siyahkare.com${NC}"
cloudflared tunnel route dns "$TUNNEL_NAME" portal.siyahkare.com 2>&1 | grep -v "already exists" || {
    echo -e "${YELLOW}    ⚠️  Route zaten var${NC}"
}

echo -e "${GREEN}✅ DNS route'ları oluşturuldu${NC}"

# Tunnel'ı başlat
echo -e "${YELLOW}🚀 Tunnel başlatılıyor...${NC}"
echo -e "${YELLOW}💡 Tunnel'ı durdurmak için: Ctrl+C${NC}"
echo ""

# Tunnel'ı başlat (foreground)
cloudflared tunnel --config "$CONFIG_FILE" run "$TUNNEL_NAME"

