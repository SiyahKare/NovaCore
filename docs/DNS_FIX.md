# DNS Çözümleme Sorunu - Çözüm

## 🔍 Durum

- ✅ DNS kayıtları var (`dig` ile çözümleniyor)
- ✅ Tunnel çalışıyor
- ✅ Config dosyası doğru
- ❌ `curl` ile bağlanılamıyor (DNS cache sorunu)

## ✅ Çözüm Adımları

### 1. DNS Cache Temizleme (macOS)

Terminal'de şu komutu çalıştır:

```bash
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder
```

### 2. Alternatif: Farklı DNS Server Kullan

```bash
# Google DNS ile test et
curl https://portal.siyahkare.com/.well-known/telegram-auth.txt --resolve portal.siyahkare.com:443:104.21.34.130

# veya hosts dosyasına ekle (geçici)
echo "104.21.34.130 portal.siyahkare.com" | sudo tee -a /etc/hosts
```

### 3. Frontend'i Başlat

Tunnel çalışıyor ama frontend localhost:3000'de çalışmıyor olabilir:

```bash
cd apps/citizen-portal
npm run dev
```

### 4. Browser'da Test Et

DNS cache sorunu genellikle browser'da olmaz:

```
https://portal.siyahkare.com
https://api.siyahkare.com/health
```

## 🧪 Test Komutları

```bash
# DNS çözümleme
dig portal.siyahkare.com
nslookup portal.siyahkare.com 8.8.8.8

# HTTPS bağlantı testi
curl -v https://portal.siyahkare.com/.well-known/telegram-auth.txt

# Tunnel durumu
cloudflared tunnel info novacore-siyahkare
```

## 📋 Checklist

- [ ] DNS cache temizlendi
- [ ] Frontend çalışıyor (localhost:3000)
- [ ] Tunnel çalışıyor
- [ ] Browser'da test edildi

## 💡 Notlar

- DNS propagation 5-10 dakika sürebilir
- Cloudflare DNS genellikle hızlıdır ama local DNS cache sorunlu olabilir
- Browser DNS cache'i farklıdır, browser'da çalışabilir

