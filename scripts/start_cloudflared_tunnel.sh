#!/bin/bash

# Cloudflare Tunnel Başlatma Script'i
# Manuel başlatma için

set -e

CONFIG_FILE="$HOME/.cloudflared/config.yml"
TUNNEL_NAME="novacore-siyahkare"

# Config dosyası kontrolü
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Config dosyası bulunamadı: $CONFIG_FILE"
    echo "Önce setup_cloudflare_tunnel.sh çalıştırın"
    exit 1
fi

echo "🚀 Cloudflare Tunnel başlatılıyor..."
echo "📋 Config: $CONFIG_FILE"
echo "📋 Tunnel: $TUNNEL_NAME"
echo ""

# Tunnel'ı başlat
cloudflared tunnel --config "$CONFIG_FILE" run "$TUNNEL_NAME"

