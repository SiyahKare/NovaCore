#!/bin/bash
# Cloudflare Tunnel Kurulum Scripti
# Bu script Cloudflare Tunnel'ı kurar ve yapılandırır

set -e

echo "🚀 NovaCore Cloudflare Tunnel Kurulumu"
echo "========================================"
echo ""

# 1. cloudflared kurulumu kontrolü
echo "📦 cloudflared kontrol ediliyor..."
if ! command -v cloudflared &> /dev/null; then
    echo "❌ cloudflared bulunamadı. Kurulum yapılıyor..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb -o /tmp/cloudflared.deb
        sudo dpkg -i /tmp/cloudflared.deb
        rm /tmp/cloudflared.deb
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if ! command -v brew &> /dev/null; then
            echo "❌ Homebrew bulunamadı. Lütfen manuel olarak kurun: brew install cloudflared"
            exit 1
        fi
        brew install cloudflared
    else
        echo "❌ Desteklenmeyen işletim sistemi. Lütfen manuel olarak cloudflared kurun."
        exit 1
    fi
else
    echo "✅ cloudflared zaten kurulu: $(cloudflared --version)"
fi

echo ""

# 2. Credentials dizini oluştur
echo "📁 Credentials dizini oluşturuluyor..."
mkdir -p ~/.cloudflared
echo "✅ Dizin hazır: ~/.cloudflared"

echo ""

# 3. Cloudflare'e login ol (eğer daha önce olmadıysa)
echo "🔐 Cloudflare authentication kontrol ediliyor..."
if [ ! -f ~/.cloudflared/cert.pem ]; then
    echo "📝 Cloudflare'e login olunuyor..."
    echo "   (Tarayıcı açılacak, oradan login olun)"
    cloudflared tunnel login
    echo "✅ Cloudflare login tamamlandı"
else
    echo "✅ Cloudflare authentication mevcut"
fi

echo ""

# 4. Tunnel oluştur (eğer yoksa)
echo "🌐 Tunnel kontrol ediliyor..."
if ! cloudflared tunnel list 2>/dev/null | grep -q "novacore-tunnel"; then
    echo "📝 Tunnel oluşturuluyor..."
    cloudflared tunnel create novacore-tunnel
    echo "✅ Tunnel oluşturuldu: novacore-tunnel"
else
    echo "✅ Tunnel zaten var: novacore-tunnel"
fi

echo ""

# 5. DNS route'ları ekle
echo "🔗 DNS route'ları ekleniyor..."
cloudflared tunnel route dns novacore-tunnel novacore.siyahkare.com 2>/dev/null || echo "⚠️  novacore.siyahkare.com route'u zaten var veya eklenemedi"
cloudflared tunnel route dns novacore-tunnel api.novacore.siyahkare.com 2>/dev/null || echo "⚠️  api.novacore.siyahkare.com route'u zaten var veya eklenemedi"
echo "✅ DNS route'ları işlendi"

echo ""

# 6. Yapılandırma dosyasını otomatik oluştur (eğer yoksa)
echo "📄 Yapılandırma dosyası kontrol ediliyor..."
if [ ! -f "cloudflare-tunnel.yml" ]; then
    echo "📝 Yapılandırma dosyası oluşturuluyor..."
    cat > cloudflare-tunnel.yml << 'EOF'
# Cloudflare Tunnel Configuration
# Bu dosya cloudflared ile tunnel yapılandırması için kullanılır
# 
# Credentials file otomatik oluşur (~/.cloudflared/cert.pem)

tunnel: novacore-tunnel

ingress:
  # Backend API (FastAPI)
  - hostname: api.novacore.siyahkare.com
    service: http://localhost:8000
    originRequest:
      noHappyEyeballs: true
      connectTimeout: 30s
      tcpKeepAlive: 30s
      keepAliveConnections: 100
      keepAliveTimeout: 90s
      httpHostHeader: api.novacore.siyahkare.com

  # Frontend (Next.js)
  - hostname: novacore.siyahkare.com
    service: http://localhost:3000
    originRequest:
      noHappyEyeballs: true
      connectTimeout: 30s
      tcpKeepAlive: 30s
      keepAliveConnections: 100
      keepAliveTimeout: 90s
      httpHostHeader: novacore.siyahkare.com

  # Catch-all (404)
  - service: http_status:404
EOF
    echo "✅ Yapılandırma dosyası oluşturuldu: cloudflare-tunnel.yml"
else
    echo "✅ Yapılandırma dosyası zaten var: cloudflare-tunnel.yml"
fi

echo ""

# 7. Systemd service oluştur (Linux)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "⚙️  Systemd service oluşturuluyor..."
    
    SERVICE_FILE="/etc/systemd/system/cloudflared-tunnel.service"
    WORK_DIR=$(pwd)
    
    # Config file ile çalıştır (credentials file otomatik kullanılır)
    EXEC_START="/usr/local/bin/cloudflared tunnel --config $WORK_DIR/cloudflare-tunnel.yml run novacore-tunnel"
    
    sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=Cloudflare Tunnel for NovaCore
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$WORK_DIR
ExecStart=$EXEC_START
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    echo "✅ Systemd service oluşturuldu: $SERVICE_FILE"
    echo ""
    echo "Service'i aktif etmek için:"
    echo "  sudo systemctl daemon-reload"
    echo "  sudo systemctl enable cloudflared-tunnel"
    echo "  sudo systemctl start cloudflared-tunnel"
fi

echo ""
echo "✅ Kurulum tamamlandı!"
echo ""
echo "📋 Sonraki adımlar:"
echo "1. Backend'i başlat: uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo "2. Frontend'i başlat: cd apps/citizen-portal && npm run dev"
echo "3. Tunnel'ı başlat: cloudflared tunnel --config cloudflare-tunnel.yml run novacore-tunnel"
echo ""
echo "🌐 Erişim adresleri:"
echo "  - Frontend: https://novacore.siyahkare.com"
echo "  - Backend API: https://api.novacore.siyahkare.com"
echo ""
echo "💡 Otomatik başlatma için: ./scripts/start-production.sh"
echo ""
