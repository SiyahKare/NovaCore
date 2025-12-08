#!/bin/bash

# DNS Cache Temizleme Script'i
# macOS için DNS cache'i temizler

echo "🔧 DNS Cache temizleniyor..."

# macOS DNS cache temizleme
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 macOS DNS cache temizleniyor..."
    sudo dscacheutil -flushcache
    sudo killall -HUP mDNSResponder
    echo "✅ DNS cache temizlendi"
else
    echo "⚠️  Bu script sadece macOS için. Linux için: sudo systemd-resolve --flush-caches"
fi

echo ""
echo "🧪 Test:"
echo "  dig portal.siyahkare.com"
echo "  curl https://portal.siyahkare.com/.well-known/telegram-auth.txt"

