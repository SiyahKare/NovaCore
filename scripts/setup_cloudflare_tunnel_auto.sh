#!/bin/bash

# Cloudflare Tunnel Setup Script (Non-Interactive)
# Environment variable'lardan Cloudflare bilgilerini okur

set -e

echo "🚀 Cloudflare Tunnel Kurulumu Başlatılıyor (Non-Interactive)..."

# Renkler
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Kontroller
if ! command -v cloudflared &> /dev/null; then
    echo -e "${RED}❌ cloudflared bulunamadı!${NC}"
    echo "Kurulum için: brew install cloudflared"
    exit 1
fi

if ! command -v jq &> /dev/null; then
    echo -e "${RED}❌ jq bulunamadı!${NC}"
    echo "Kurulum için: brew install jq"
    exit 1
fi

# Cloudflare hesap bilgileri (environment variable'lardan)
if [ -z "$CF_ACCOUNT_ID" ] || [ -z "$CF_API_TOKEN" ]; then
    echo -e "${RED}❌ CF_ACCOUNT_ID ve CF_API_TOKEN environment variable'ları gerekli!${NC}"
    echo ""
    echo -e "${YELLOW}Kullanım:${NC}"
    echo "  export CF_ACCOUNT_ID='your-account-id'"
    echo "  export CF_API_TOKEN='your-api-token'"
    echo "  ./scripts/setup_cloudflare_tunnel_auto.sh"
    echo ""
    echo -e "${YELLOW}Cloudflare API Token oluşturma:${NC}"
    echo "  1. Cloudflare Dashboard → My Profile → API Tokens"
    echo "  2. Create Token → Custom token"
    echo "  3. İzinler: Account → Cloudflare Tunnel → Edit"
    echo "  4. Token'ı kopyala ve export CF_API_TOKEN='token' yap"
    exit 1
fi

echo -e "${GREEN}✅ cloudflared bulundu${NC}"
echo -e "${GREEN}✅ jq bulundu${NC}"

# Tunnel adı
TUNNEL_NAME="novacore-siyahkare"
CONFIG_DIR="$HOME/.cloudflared"
CONFIG_FILE="$CONFIG_DIR/config.yml"

# Tunnel oluştur
echo -e "${YELLOW}🔨 Tunnel oluşturuluyor: $TUNNEL_NAME${NC}"
cloudflared tunnel create "$TUNNEL_NAME" 2>&1 | grep -v "already exists" || {
    echo -e "${YELLOW}⚠️  Tunnel zaten var, devam ediliyor...${NC}"
}

# Tunnel ID'yi al
TUNNEL_ID=$(cloudflared tunnel list --output json 2>/dev/null | jq -r ".[] | select(.name==\"$TUNNEL_NAME\") | .id" 2>/dev/null || echo "")

if [ -z "$TUNNEL_ID" ]; then
    echo -e "${RED}❌ Tunnel ID alınamadı!${NC}"
    echo -e "${YELLOW}💡 Tunnel listesi:${NC}"
    cloudflared tunnel list
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
cloudflared tunnel route dns "$TUNNEL_NAME" api.siyahkare.com 2>&1 | grep -v "already exists" || {
    echo -e "${YELLOW}⚠️  Backend route zaten var${NC}"
}

# Frontend Portal route
cloudflared tunnel route dns "$TUNNEL_NAME" portal.siyahkare.com 2>&1 | grep -v "already exists" || {
    echo -e "${YELLOW}⚠️  Frontend route zaten var${NC}"
}

echo -e "${GREEN}✅ DNS route'ları oluşturuldu${NC}"

# macOS için launchd plist oluştur
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo -e "${YELLOW}🍎 macOS için launchd service oluşturuluyor...${NC}"
    
    PLIST_FILE="$HOME/Library/LaunchAgents/com.cloudflare.tunnel.novacore.plist"
    
    cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.cloudflare.tunnel.novacore</string>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/homebrew/bin/cloudflared</string>
        <string>tunnel</string>
        <string>--config</string>
        <string>$CONFIG_FILE</string>
        <string>run</string>
        <string>$TUNNEL_NAME</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$HOME/.cloudflared/tunnel.log</string>
    <key>StandardErrorPath</key>
    <string>$HOME/.cloudflared/tunnel.error.log</string>
</dict>
</plist>
EOF

    echo -e "${GREEN}✅ Launchd plist oluşturuldu: $PLIST_FILE${NC}"
    echo -e "${YELLOW}📋 Service'i başlatmak için:${NC}"
    echo "   launchctl load $PLIST_FILE"
    echo ""
    echo -e "${YELLOW}📋 Service'i durdurmak için:${NC}"
    echo "   launchctl unload $PLIST_FILE"
fi

# Linux için systemd service oluştur
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
fi

# Test
echo -e "${YELLOW}🧪 Tunnel test ediliyor...${NC}"
sleep 2

if cloudflared tunnel info "$TUNNEL_NAME" &> /dev/null; then
    echo -e "${GREEN}✅ Tunnel başarıyla çalışıyor!${NC}"
else
    echo -e "${YELLOW}⚠️  Tunnel bilgisi alınamadı, ancak kurulum tamamlandı${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Cloudflare Tunnel kurulumu tamamlandı!${NC}"
echo ""
echo -e "${YELLOW}📋 Sonraki adımlar:${NC}"
echo "1. Backend'i başlat: uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo "2. Frontend'i başlat: cd apps/citizen-portal && npm run dev"
echo "3. Tunnel'ı başlat (eğer service başlamadıysa):"
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "   launchctl load $PLIST_FILE"
else
    echo "   sudo systemctl start cloudflared-tunnel"
fi
echo "4. Test et:"
echo "   - Backend: https://api.siyahkare.com/health"
echo "   - Frontend: https://portal.siyahkare.com"
echo ""
echo -e "${YELLOW}📚 Dokümantasyon: docs/CLOUDFLARE_TUNNEL_SETUP.md${NC}"

