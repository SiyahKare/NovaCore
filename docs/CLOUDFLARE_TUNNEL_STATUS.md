# Cloudflare Tunnel Durumu

## ✅ Kurulum Tamamlandı

### Tunnel Bilgileri
- **Tunnel Adı:** `novacore-siyahkare`
- **Tunnel ID:** `78dd4f2b-b2ae-4152-92a5-caedf7bc057d`
- **Config Dosyası:** `~/.cloudflared/config.yml`

### DNS Route'ları
- ✅ `api.siyahkare.com` → `http://localhost:8000`
- ✅ `portal.siyahkare.com` → `http://localhost:3000`

## 🚀 Tunnel'ı Başlatma

### Manuel Başlatma (Foreground)
```bash
cloudflared tunnel --config ~/.cloudflared/config.yml run novacore-siyahkare
```

### Background'da Başlatma
```bash
# Script ile
./scripts/start_tunnel.sh

# veya manuel
cloudflared tunnel --config ~/.cloudflared/config.yml run novacore-siyahkare > ~/.cloudflared/tunnel.log 2>&1 &
```

### macOS Launchd Service (Önerilen)
```bash
# Service oluştur
launchctl load ~/Library/LaunchAgents/com.cloudflare.tunnel.novacore.plist

# Service durumu
launchctl list | grep cloudflare

# Service'i durdur
launchctl unload ~/Library/LaunchAgents/com.cloudflare.tunnel.novacore.plist
```

## 🧪 Test

### Backend Test
```bash
curl https://api.siyahkare.com/health
# Expected: {"status":"ok"}
```

### Frontend Test
```bash
curl https://portal.siyahkare.com
# Expected: HTML content
```

### Browser Test
- Backend: https://api.siyahkare.com/docs
- Frontend: https://portal.siyahkare.com

## 📋 Gereksinimler

Tunnel'ın çalışması için:

1. **Backend çalışıyor olmalı:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

2. **Frontend çalışıyor olmalı:**
   ```bash
   cd apps/citizen-portal
   npm run dev
   ```

3. **Tunnel çalışıyor olmalı:**
   ```bash
   cloudflared tunnel --config ~/.cloudflared/config.yml run novacore-siyahkare
   ```

## 🔍 Troubleshooting

### Tunnel Bağlantısı Yok
```bash
# Tunnel durumu
cloudflared tunnel info novacore-siyahkare

# Tunnel logları
tail -f ~/.cloudflared/tunnel.log
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

## 📚 Kaynaklar

- [Cloudflare Tunnel Documentation](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [Tunnel Setup Guide](./docs/CLOUDFLARE_TUNNEL_SETUP.md)

