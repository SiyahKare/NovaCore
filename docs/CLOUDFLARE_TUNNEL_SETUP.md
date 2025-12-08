# Cloudflare Tunnel (cloudflared) Otomatik Kurulum

## 🎯 Amaç

Cloudflare Tunnel kullanarak NovaCore sistemini `siyahkare.com` altında otomatik olarak yayınlamak.

## 📋 Gereksinimler

1. **Cloudflare hesabı** (ücretsiz)
2. **Cloudflare API Token** (gerekli izinler: `Account.Cloudflare Tunnel.Edit`)
3. **cloudflared** kurulu
4. **jq** kurulu (JSON parsing için)

## 🚀 Otomatik Kurulum

### 1. cloudflared Kurulumu

#### macOS
```bash
brew install cloudflared
```

#### Linux
```bash
# Debian/Ubuntu
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# veya
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared
chmod +x cloudflared
sudo mv cloudflared /usr/local/bin/
```

#### Windows
```powershell
# Chocolatey
choco install cloudflared

# veya manuel
# https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/
```

### 2. Cloudflare API Token Oluşturma

1. Cloudflare Dashboard → **My Profile** → **API Tokens**
2. **Create Token** → **Custom token**
3. İzinler:
   - **Account** → **Cloudflare Tunnel** → **Edit**
4. Account Resources:
   - **Include** → **All accounts**
5. Token'ı kopyala ve güvenli bir yerde sakla

### 3. Otomatik Kurulum Script'i

```bash
# Script'i çalıştırılabilir yap
chmod +x scripts/setup_cloudflare_tunnel.sh

# Kurulumu başlat
./scripts/setup_cloudflare_tunnel.sh
```

Script şunları yapar:
- ✅ Tunnel oluşturur (`novacore-siyahkare`)
- ✅ Config dosyası oluşturur (`~/.cloudflared/config.yml`)
- ✅ DNS route'ları oluşturur (`api.siyahkare.com`, `portal.siyahkare.com`)
- ✅ Systemd service oluşturur (Linux için)
- ✅ Tunnel'ı başlatır

### 4. Manuel Kurulum (Alternatif)

#### Tunnel Oluşturma
```bash
cloudflared tunnel create novacore-siyahkare
```

#### Config Dosyası Oluşturma
```bash
mkdir -p ~/.cloudflared
cp scripts/cloudflared_config.yml.example ~/.cloudflared/config.yml
nano ~/.cloudflared/config.yml  # Tunnel ID'yi güncelle
```

#### DNS Route Oluşturma
```bash
cloudflared tunnel route dns novacore-siyahkare api.siyahkare.com
cloudflared tunnel route dns novacore-siyahkare portal.siyahkare.com
```

#### Tunnel'ı Başlatma
```bash
# Manuel
cloudflared tunnel --config ~/.cloudflared/config.yml run novacore-siyahkare

# veya script ile
chmod +x scripts/start_cloudflared_tunnel.sh
./scripts/start_cloudflared_tunnel.sh
```

## ⚙️ Systemd Service (Linux)

Script otomatik olarak systemd service oluşturur:

```bash
# Service durumu
sudo systemctl status cloudflared-tunnel

# Service logları
sudo journalctl -u cloudflared-tunnel -f

# Service'i yeniden başlat
sudo systemctl restart cloudflared-tunnel

# Service'i durdur
sudo systemctl stop cloudflared-tunnel
```

## 🔧 Konfigürasyon

### Config Dosyası Yapısı

`~/.cloudflared/config.yml`:

```yaml
tunnel: YOUR_TUNNEL_ID
credentials-file: /home/user/.cloudflared/YOUR_TUNNEL_ID.json

ingress:
  # Backend API
  - hostname: api.siyahkare.com
    service: http://localhost:8000
  
  # Frontend Portal
  - hostname: portal.siyahkare.com
    service: http://localhost:3000
  
  # Catch-all (404)
  - service: http_status:404
```

### Environment Variables

Backend `.env`:
```bash
ENV=prod
CORS_ORIGINS=https://portal.siyahkare.com,https://app.siyahkare.com
NOVACORE_URL=https://api.siyahkare.com
FRONTEND_URL=https://portal.siyahkare.com
BACKEND_URL=https://api.siyahkare.com
```

Frontend `.env.local`:
```bash
NEXT_PUBLIC_AURORA_API_URL=https://api.siyahkare.com/api/v1
NEXT_PUBLIC_AURORA_ENV=prod
```

## 🧪 Test

### Tunnel Durumu
```bash
cloudflared tunnel info novacore-siyahkare
cloudflared tunnel list
```

### Backend Test
```bash
curl https://api.siyahkare.com/health
# Expected: {"status":"ok"}
```

### Frontend Test
```bash
# Browser'da aç
https://portal.siyahkare.com
```

### Telegram Webhook Test
```bash
curl -X POST "https://api.telegram.org/bot<BOT_TOKEN>/setWebhook" \
  -d "url=https://api.siyahkare.com/api/v1/telegram/webhook"

# Webhook durumu
curl "https://api.telegram.org/bot<BOT_TOKEN>/getWebhookInfo"
```

## 🔍 Troubleshooting

### Tunnel Başlamıyor
```bash
# Logları kontrol et
cloudflared tunnel --config ~/.cloudflared/config.yml run novacore-siyahkare --loglevel debug

# Systemd logları
sudo journalctl -u cloudflared-tunnel -f
```

### DNS Çözümleme Hatası
```bash
# DNS kayıtlarını kontrol et
dig api.siyahkare.com
dig portal.siyahkare.com

# Cloudflare DNS'de kayıtlar var mı kontrol et
cloudflared tunnel route dns list
```

### Backend/Frontend Erişilemiyor
```bash
# Localhost'ta çalışıyor mu kontrol et
curl http://localhost:8000/health
curl http://localhost:3000

# Tunnel config'deki service URL'leri kontrol et
cat ~/.cloudflared/config.yml
```

### SSL Hatası
- Cloudflare otomatik SSL sağlar
- Tunnel üzerinden gelen istekler HTTPS olarak gelir
- Backend'de SSL certificate gerekmez

## 📚 Kaynaklar

- [Cloudflare Tunnel Documentation](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [cloudflared CLI Reference](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/tunnel-guide/)
- [Cloudflare API Tokens](https://developers.cloudflare.com/fundamentals/api/get-started/create-token/)

## 🎉 Sonuç

Kurulum tamamlandıktan sonra:
- ✅ `https://api.siyahkare.com` → Backend API
- ✅ `https://portal.siyahkare.com` → Frontend Portal
- ✅ Otomatik SSL (Cloudflare)
- ✅ DDoS Protection (Cloudflare)
- ✅ CDN Cache (Cloudflare)

Tüm trafik Cloudflare üzerinden güvenli bir şekilde VPS'e yönlendirilir.

