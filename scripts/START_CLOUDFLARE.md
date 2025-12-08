# Cloudflare Tunnel Başlatma

## Hızlı Başlangıç

### 1. Cloudflare Bilgilerini Ayarla

```bash
# Cloudflare Account ID (Dashboard → Sağ üst köşeden kopyala)
export CF_ACCOUNT_ID='your-account-id'

# Cloudflare API Token (My Profile → API Tokens → Create Token)
export CF_API_TOKEN='your-api-token'
```

### 2. Otomatik Kurulum (Non-Interactive)

```bash
./scripts/setup_cloudflare_tunnel_auto.sh
```

### 3. Interaktif Kurulum

```bash
./scripts/setup_cloudflare_tunnel.sh
```

## Cloudflare API Token Oluşturma

1. Cloudflare Dashboard → **My Profile** → **API Tokens**
2. **Create Token** → **Custom token**
3. İzinler:
   - **Account** → **Cloudflare Tunnel** → **Edit**
4. Account Resources:
   - **Include** → **All accounts**
5. Token'ı kopyala ve `export CF_API_TOKEN='token'` yap

## Tunnel'ı Başlatma

### macOS (Launchd)

```bash
# Service'i başlat
launchctl load ~/Library/LaunchAgents/com.cloudflare.tunnel.novacore.plist

# Service durumu
launchctl list | grep cloudflare

# Service'i durdur
launchctl unload ~/Library/LaunchAgents/com.cloudflare.tunnel.novacore.plist
```

### Linux (Systemd)

```bash
# Service'i başlat
sudo systemctl start cloudflared-tunnel

# Service durumu
sudo systemctl status cloudflared-tunnel

# Service logları
sudo journalctl -u cloudflared-tunnel -f
```

### Manuel Başlatma

```bash
./scripts/start_cloudflared_tunnel.sh
```

## Test

```bash
# Tunnel durumu
cloudflared tunnel info novacore-siyahkare

# Backend test
curl https://api.siyahkare.com/health

# Frontend test
# Browser: https://portal.siyahkare.com
```

