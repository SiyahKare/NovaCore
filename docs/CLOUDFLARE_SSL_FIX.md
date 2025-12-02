# Cloudflare SSL/TLS Hata Çözümü

## 🔴 Hata: ERR_SSL_VERSION_OR_CIPHER_MISMATCH

Bu hata genellikle Cloudflare Dashboard'daki SSL/TLS ayarlarından kaynaklanır.

## ✅ Çözüm Adımları

### 1. Cloudflare Dashboard'a Git

1. [Cloudflare Dashboard](https://dash.cloudflare.com/) → `siyahkare.com` domain'ini seç
2. Sol menüden **SSL/TLS** → **Overview**

### 2. SSL/TLS Encryption Mode'u Değiştir

**ÖNEMLİ:** Tunnel kullanırken **"Full"** veya **"Full (strict)"** modunu kullanmalısın.

**Şu anki mod:** Muhtemelen "Flexible" veya "Off"

**Değiştir:**
1. **SSL/TLS** → **Overview**
2. **Encryption mode** → **Full** seç
3. **Save** butonuna tıkla

**Açıklama:**
- **Flexible**: Cloudflare ↔ Browser arası SSL, Cloudflare ↔ Origin arası HTTP (Tunnel için uygun değil)
- **Full**: Cloudflare ↔ Browser arası SSL, Cloudflare ↔ Origin arası SSL (Tunnel için uygun)
- **Full (strict)**: Full + sertifika doğrulama (Tunnel için ideal)

### 3. Always Use HTTPS

1. **SSL/TLS** → **Edge Certificates**
2. **Always Use HTTPS** → **On** yap
3. **Automatic HTTPS Rewrites** → **On** yap

### 4. DNS Kayıtlarını Kontrol Et

1. **DNS** → **Records**
2. `api.novacore.siyahkare.com` kaydını kontrol et:
   - **Type**: CNAME
   - **Target**: `novacore-tunnel.cfargotunnel.com` (veya tunnel'ın otomatik oluşturduğu CNAME)
   - **Proxy status**: ✅ **Proxied** (Orange cloud) olmalı

3. `novacore.siyahkare.com` kaydını kontrol et:
   - **Type**: CNAME
   - **Target**: `novacore-tunnel.cfargotunnel.com`
   - **Proxy status**: ✅ **Proxied** (Orange cloud) olmalı

### 5. Tunnel Route'larını Kontrol Et

```bash
# Tunnel route'larını listele
cloudflared tunnel route dns list novacore-tunnel

# Eğer route yoksa ekle
cloudflared tunnel route dns novacore-tunnel api.novacore.siyahkare.com
cloudflared tunnel route dns novacore-tunnel novacore.siyahkare.com
```

### 6. Tunnel'ı Yeniden Başlat

```bash
# Mevcut tunnel'ı durdur
pkill -f "cloudflared tunnel"

# Yeniden başlat
cd /Users/onur/code/DeltaNova_System/NovaCore
cloudflared tunnel --config cloudflare-tunnel.yml run novacore-tunnel
```

### 7. DNS Propagation Bekle

DNS değişikliklerinin yayılması 5-10 dakika sürebilir. Bekle ve tekrar dene.

## 🔍 Test

```bash
# SSL sertifikasını kontrol et
openssl s_client -connect api.novacore.siyahkare.com:443 -servername api.novacore.siyahkare.com < /dev/null 2>&1 | grep -E "subject|issuer|Verify"

# HTTP test (SSL bypass)
curl -k https://api.novacore.siyahkare.com/health

# Normal test
curl https://api.novacore.siyahkare.com/health
```

## 🐛 Yaygın Sorunlar

### Sorun 1: "Flexible" Mode

**Belirti:** SSL hatası, tunnel çalışıyor ama bağlantı kurulamıyor

**Çözüm:** SSL/TLS mode'unu "Full" veya "Full (strict)" yap

### Sorun 2: DNS Proxy Kapalı

**Belirti:** DNS kaydı var ama proxy (orange cloud) kapalı

**Çözüm:** DNS kaydında "Proxy status" → "Proxied" yap

### Sorun 3: Tunnel Route Eksik

**Belirti:** Tunnel çalışıyor ama domain'e bağlanamıyor

**Çözüm:** `cloudflared tunnel route dns` komutu ile route ekle

### Sorun 4: Backend Çalışmıyor

**Belirti:** SSL bağlantısı kuruluyor ama 502/503 hatası

**Çözüm:** Backend'in `http://localhost:8000` adresinde çalıştığından emin ol

## 📊 Durum Kontrolü

```bash
# Backend kontrolü
curl http://localhost:8000/health

# Tunnel kontrolü
ps aux | grep cloudflared | grep -v grep

# DNS kontrolü
dig api.novacore.siyahkare.com +short
dig novacore.siyahkare.com +short
```

## ✅ Başarılı Kurulum Checklist

- [ ] SSL/TLS mode: **Full** veya **Full (strict)**
- [ ] Always Use HTTPS: **On**
- [ ] DNS kayıtları: **Proxied** (Orange cloud)
- [ ] Tunnel route'ları: Eklendi
- [ ] Backend çalışıyor: `http://localhost:8000`
- [ ] Tunnel çalışıyor: Process aktif
- [ ] DNS propagation: Tamamlandı (5-10 dakika)

## 🔗 Kaynaklar

- [Cloudflare SSL/TLS Settings](https://developers.cloudflare.com/ssl/ssl-modes/)
- [Cloudflare Tunnel Troubleshooting](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/troubleshooting/)

