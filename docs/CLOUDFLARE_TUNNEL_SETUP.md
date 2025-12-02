# Cloudflare Tunnel Kurulum Rehberi

NovaCore'u `novacore.siyahkare.com` altında Cloudflare Tunnel ile yayına alma rehberi.

## 🎯 Genel Bakış

Cloudflare Tunnel, sisteminizi Cloudflare'in edge network'ü üzerinden güvenli bir şekilde yayınlar. Bu sayede:
- ✅ SSL/TLS otomatik (Cloudflare tarafından)
- ✅ DDoS koruması
- ✅ Firewall kuralları
- ✅ Analytics ve monitoring
- ✅ Public IP gerekmez

## 📋 Gereksinimler

1. Cloudflare hesabı (ücretsiz)
2. `siyahkare.com` domain'i Cloudflare'de yönetiliyor olmalı
3. `cloudflared` CLI aracı
4. Backend ve Frontend çalışıyor olmalı

---

## 1️⃣ Cloudflare Tunnel Oluşturma

### Adım 1: Cloudflare Dashboard'a Git

1. [Cloudflare Dashboard](https://dash.cloudflare.com/) → `siyahkare.com` domain'ini seç
2. Sol menüden **Zero Trust** → **Networks** → **Tunnels**
3. **Create a tunnel** butonuna tıkla
4. Tunnel adı: `novacore-tunnel`
5. **Save tunnel** butonuna tıkla

### Adım 2: Token Alma

1. Tunnel oluşturulduktan sonra **Configure** butonuna tıkla
2. **Quick Tunnel** yerine **Private Network** seç
3. **Install connector** bölümünde **Linux** seç
4. Token'ı kopyala (şu formatta: `eyJ...`)

**ÖNEMLİ:** Bu token'ı güvenli bir yerde sakla, `.env` dosyasına ekleyeceğiz.

---

## 2️⃣ cloudflared Kurulumu

### Linux (Ubuntu/Debian)

```bash
# cloudflared kurulumu
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb -o cloudflared.deb
sudo dpkg -i cloudflared.deb
```

### macOS

```bash
brew install cloudflared
```

### Docker (Alternatif)

```bash
docker pull cloudflare/cloudflared:latest
```

---

## 3️⃣ Tunnel Yapılandırması

### Adım 1: Credentials Dosyası Oluştur

```bash
# Credentials dizinini oluştur
mkdir -p ~/.cloudflared

# Credentials dosyasını oluştur (token'ı buraya yapıştır)
cat > ~/.cloudflared/credentials.json << EOF
{
  "AccountTag": "YOUR_ACCOUNT_TAG",
  "TunnelSecret": "YOUR_TUNNEL_SECRET",
  "TunnelID": "YOUR_TUNNEL_ID"
}
EOF
```

**Not:** Bu bilgileri Cloudflare Dashboard'dan alabilirsin, ya da token ile otomatik oluşturabilirsin.

### Adım 2: Token ile Otomatik Yapılandırma (Önerilen)

```bash
# Token'ı kullanarak tunnel'ı yapılandır
cloudflared tunnel login

# Tunnel oluştur (eğer dashboard'dan oluşturmadıysan)
cloudflared tunnel create novacore-tunnel

# Route ekle
cloudflared tunnel route dns novacore-tunnel novacore.siyahkare.com
cloudflared tunnel route dns novacore-tunnel api.novacore.siyahkare.com
```

### Adım 3: Yapılandırma Dosyası

`cloudflare-tunnel.yml` dosyası zaten hazır. 

**Token kullanıyorsan:**
- `credentials-file` satırını yorum satırı yap
- Environment variable olarak token kullan: `CLOUDFLARE_TUNNEL_TOKEN`

**Credentials file kullanıyorsan:**
- `credentials-file` satırını aktif et
- `~/.cloudflared/credentials.json` dosyasını oluştur

Yapılandırma dosyasını kontrol et:

```bash
cat cloudflare-tunnel.yml
```

---

## 4️⃣ Environment Variables Güncelleme

### Backend `.env` Dosyası

```bash
# CORS origins - Cloudflare domain'lerini ekle
CORS_ORIGINS=https://novacore.siyahkare.com,https://api.novacore.siyahkare.com

# API URL (opsiyonel - frontend için)
AURORA_API_URL=https://api.novacore.siyahkare.com
```

### Frontend `.env` Dosyası

`apps/citizen-portal/.env.local`:

```bash
NEXT_PUBLIC_AURORA_API_URL=https://api.novacore.siyahkare.com
NEXT_PUBLIC_AURORA_ENV=production
```

---

## 5️⃣ Tunnel'ı Çalıştırma

### Manuel Çalıştırma (Test)

```bash
# Backend ve frontend'i başlat (ayrı terminal'lerde)
# Terminal 1: Backend
cd /Users/onur/code/DeltaNova_System/NovaCore
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd apps/citizen-portal
npm run dev

# Terminal 3: Cloudflare Tunnel
cloudflared tunnel --config cloudflare-tunnel.yml run novacore-tunnel
```

### Systemd Service (Production)

`/etc/systemd/system/cloudflared-tunnel.service`:

```ini
[Unit]
Description=Cloudflare Tunnel for NovaCore
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/Users/onur/code/DeltaNova_System/NovaCore
ExecStart=/usr/local/bin/cloudflared tunnel --config /Users/onur/code/DeltaNova_System/NovaCore/cloudflare-tunnel.yml run novacore-tunnel
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Aktif et:**

```bash
sudo systemctl enable cloudflared-tunnel
sudo systemctl start cloudflared-tunnel
sudo systemctl status cloudflared-tunnel
```

### Docker Compose (Alternatif)

`docker-compose.tunnel.yml`:

```yaml
version: '3.8'

services:
  cloudflared:
    image: cloudflare/cloudflared:latest
    container_name: novacore-cloudflared
    restart: unless-stopped
    command: tunnel --config /etc/cloudflared/config.yml run novacore-tunnel
    volumes:
      - ./cloudflare-tunnel.yml:/etc/cloudflared/config.yml:ro
      - ~/.cloudflared:/root/.cloudflared:ro
    network_mode: host
```

**Çalıştır:**

```bash
docker-compose -f docker-compose.tunnel.yml up -d
```

---

## 6️⃣ DNS Kayıtları

Cloudflare Tunnel otomatik olarak DNS kayıtlarını oluşturur. Eğer manuel eklemek istersen:

1. Cloudflare Dashboard → DNS → Records
2. **A** record ekle:
   - Name: `novacore`
   - Type: `CNAME`
   - Target: `novacore-tunnel.cfargotunnel.com`
   - Proxy: ✅ (Orange cloud)
3. **A** record ekle:
   - Name: `api.novacore`
   - Type: `CNAME`
   - Target: `novacore-tunnel.cfargotunnel.com`
   - Proxy: ✅ (Orange cloud)

---

## 7️⃣ CORS Ayarları

Backend'de CORS ayarlarını güncelle:

`app/core/config.py`:

```python
CORS_ORIGINS = [
    "https://novacore.siyahkare.com",
    "https://api.novacore.siyahkare.com",
    "http://localhost:3000",  # Dev için
    "http://localhost:8000",  # Dev için
]
```

---

## 8️⃣ SSL/TLS Ayarları

Cloudflare Dashboard → SSL/TLS:

1. **Encryption mode**: Full (strict) seç
2. **Always Use HTTPS**: ✅ Aktif et
3. **Automatic HTTPS Rewrites**: ✅ Aktif et

---

## 9️⃣ Test Etme

### Backend Test

```bash
curl https://api.novacore.siyahkare.com/health
```

**Beklenen çıktı:**
```json
{"status": "ok"}
```

### Frontend Test

Tarayıcıda aç:
- https://novacore.siyahkare.com

---

## 🔧 Troubleshooting

### Tunnel bağlanmıyor

1. **Token kontrolü:**
   ```bash
   cloudflared tunnel list
   ```

2. **Log kontrolü:**
   ```bash
   journalctl -u cloudflared-tunnel -f
   ```

3. **Manuel test:**
   ```bash
   cloudflared tunnel --config cloudflare-tunnel.yml run novacore-tunnel --loglevel debug
   ```

### Backend erişilemiyor

1. Backend'in çalıştığından emin ol:
   ```bash
   curl http://localhost:8000/health
   ```

2. Port kontrolü:
   ```bash
   netstat -tulpn | grep 8000
   ```

### Frontend erişilemiyor

1. Frontend'in çalıştığından emin ol:
   ```bash
   curl http://localhost:3000
   ```

2. Port kontrolü:
   ```bash
   netstat -tulpn | grep 3000
   ```

### CORS hatası

1. Backend `.env` dosyasında `CORS_ORIGINS` kontrol et
2. Frontend `.env.local` dosyasında `NEXT_PUBLIC_AURORA_API_URL` kontrol et
3. Browser console'da hata mesajını kontrol et

---

## 📊 Monitoring

### Cloudflare Dashboard

1. **Analytics** → **Traffic** → Tunnel trafiğini gör
2. **Analytics** → **Security** → DDoS saldırılarını gör
3. **Zero Trust** → **Networks** → **Tunnels** → Tunnel durumunu gör

### Logs

```bash
# Systemd service logları
journalctl -u cloudflared-tunnel -f

# Docker logları
docker logs -f novacore-cloudflared
```

---

## 🚀 Production Checklist

- [ ] Cloudflare Tunnel oluşturuldu
- [ ] DNS kayıtları eklendi
- [ ] SSL/TLS Full (strict) mod aktif
- [ ] CORS ayarları güncellendi
- [ ] Environment variables güncellendi
- [ ] Systemd service kuruldu ve aktif
- [ ] Backend çalışıyor (`http://localhost:8000`)
- [ ] Frontend çalışıyor (`http://localhost:3000`)
- [ ] Tunnel çalışıyor
- [ ] `https://novacore.siyahkare.com` erişilebilir
- [ ] `https://api.novacore.siyahkare.com` erişilebilir
- [ ] Health check endpoint'leri çalışıyor

---

## 📚 Kaynaklar

- [Cloudflare Tunnel Docs](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [cloudflared CLI Reference](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/tunnel-guide/)
- [Zero Trust Dashboard](https://one.dash.cloudflare.com/)

---

**Hazır!** 🎉

Sisteminiz artık `https://novacore.siyahkare.com` adresinden erişilebilir.

