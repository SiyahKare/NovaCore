#!/bin/bash

# Cloudflare Tunnel Başlatma Script'i
# Tunnel'ı background'da başlatır

set -e

TUNNEL_NAME="novacore-siyahkare"
CONFIG_FILE="$HOME/.cloudflared/config.yml"

echo "🚀 Cloudflare Tunnel başlatılıyor: $TUNNEL_NAME"

# Config dosyası kontrolü
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Config dosyası bulunamadı: $CONFIG_FILE"
    echo "Önce connect_cloudflare_tunnel.sh çalıştırın"
    exit 1
fi

# Tunnel'ı başlat (background)
echo "📋 Config: $CONFIG_FILE"
echo "📋 Tunnel: $TUNNEL_NAME"
echo ""
echo "💡 Tunnel çalışıyor. Durmak için: pkill cloudflared"
echo ""

# Background'da başlat
cloudflared tunnel --config "$CONFIG_FILE" run "$TUNNEL_NAME" > ~/.cloudflared/tunnel.log 2>&1 &

echo "✅ Tunnel başlatıldı (PID: $!)"
echo "📋 Loglar: ~/.cloudflared/tunnel.log"
echo ""
echo "🧪 Test:"
echo "   curl https://api.siyahkare.com/health"
echo "   curl https://portal.siyahkare.com"

