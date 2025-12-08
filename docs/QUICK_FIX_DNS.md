# Hızlı DNS Çözümü

## 🚀 Hızlı Çözüm

### 1. DNS Cache Temizle (Terminal'de çalıştır)

```bash
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder
```

### 2. Frontend'i Başlat

```bash
cd apps/citizen-portal
npm run dev
```

### 3. Browser'da Test Et

DNS cache sorunu genellikle browser'da olmaz:

- https://portal.siyahkare.com
- https://api.siyahkare.com/health

### 4. Alternatif: Hosts Dosyası (Geçici)

```bash
echo "104.21.34.130 portal.siyahkare.com" | sudo tee -a /etc/hosts
echo "104.21.34.130 api.siyahkare.com" | sudo tee -a /etc/hosts
```

## ✅ Durum

- ✅ Tunnel çalışıyor
- ✅ DNS kayıtları var
- ✅ Config doğru
- ⚠️ DNS cache sorunu (terminal'de)
- ⚠️ Frontend çalışmıyor olabilir

## 🧪 Test

```bash
# Browser'da aç
open https://portal.siyahkare.com
open https://api.siyahkare.com/docs
```

