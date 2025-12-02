# NasipQuest Bot Kurulum Rehberi

## 🚀 Hızlı Kurulum (5 Adım)

### 1️⃣ Bot Token Al (Telegram BotFather'dan)

1. Telegram'da [@BotFather](https://t.me/botfather) ile konuş
2. `/newbot` komutunu gönder
3. Bot adını belirle (örn: "NasipQuest Bot")
4. Bot username'ini belirle (örn: "nasipquest_bot")
5. BotFather'dan gelen token'ı kopyala

**Örnek token:**
```
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

---

### 2️⃣ Bağımlılıkları Yükle

```bash
# Proje root dizininde
pip install aiogram httpx
```

veya:

```bash
pip install -e ".[bot]"
```

---

### 3️⃣ .env Dosyasını Hazırla

Proje root dizinindeki `.env` dosyasına ekle:

```bash
# Telegram Bot Token (BotFather'dan aldığın token)
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# NovaCore API URL (backend'in çalıştığı adres)
NOVACORE_URL=http://localhost:8000

# Bridge Token (Bot ve Backend'de AYNI olmalı!)
# Python ile güçlü token oluştur:
# python -c "import secrets; print('TELEGRAM_BRIDGE_TOKEN=' + secrets.token_urlsafe(32))"
TELEGRAM_BRIDGE_TOKEN=dev-telegram-bridge-secret

# Link Secret (Opsiyonel - deep link kullanmıyorsan gerekli değil)
TELEGRAM_LINK_SECRET=your-hmac-secret-here
```

**ÖNEMLİ:** `TELEGRAM_BRIDGE_TOKEN` hem bot hem backend `.env` dosyalarında **tamamen aynı** olmalı!

---

### 4️⃣ NovaCore Backend'i Çalıştır

Bot'un çalışması için NovaCore backend'inin çalışıyor olması gerekir:

```bash
# Proje root dizininde
uvicorn app.main:app --reload
```

Backend'in çalıştığını kontrol et:

```bash
curl http://localhost:8000/health
```

---

### 5️⃣ Bot'u Çalıştır

```bash
# Proje root dizininde
python -m nasipquest_bot.main
```

veya:

```bash
cd nasipquest_bot
python main.py
```

---

## ✅ Test Et

1. Telegram'da bot'unu bul (BotFather'dan verdiğin username ile)
2. `/start` komutunu gönder
3. Bot "Hoş geldin!" mesajı göndermeli
4. `/help` komutu ile tüm komutları gör
5. `/profile` ile profil bilgilerini kontrol et

---

## 🔧 Detaylı Kurulum

### Adım 1: Bot Token Alma

1. Telegram'da [@BotFather](https://t.me/botfather) ile konuş
2. `/newbot` komutunu gönder
3. Bot adını belirle (örn: "NasipQuest Bot")
4. Bot username'ini belirle (örn: "nasipquest_bot")
5. BotFather'dan gelen token'ı kopyala

**Token formatı:**
```
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

---

### Adım 2: Python Bağımlılıkları

```bash
# Virtual environment aktif et (eğer kullanıyorsan)
source .venv/bin/activate

# Bot bağımlılıklarını yükle
pip install aiogram httpx
```

**Kontrol et:**
```bash
python -c "import aiogram; print('✅ aiogram OK')"
python -c "import httpx; print('✅ httpx OK')"
```

---

### Adım 3: Environment Variables

`.env` dosyasına ekle (yoksa oluştur):

```bash
# Telegram Bot Token (BotFather'dan alınır)
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# NovaCore API URL
NOVACORE_URL=http://localhost:8000

# Bridge Token (Bot ↔ Backend güvenliği için)
# Python ile güçlü token oluştur:
python -c "import secrets; print('TELEGRAM_BRIDGE_TOKEN=' + secrets.token_urlsafe(32))"

# Çıkan token'ı ekle (hem bot hem backend .env'lerine aynı token)
TELEGRAM_BRIDGE_TOKEN=TsaMy4tv21P_56mGDvkhDMAJyYqkb-V0E_t-03drMcU

# Link Secret (Opsiyonel - deep link kullanmıyorsan gerekli değil)
TELEGRAM_LINK_SECRET=your-hmac-secret-here
```

**ÖNEMLİ NOTLAR:**
- `TELEGRAM_BOT_TOKEN` → BotFather'dan alınır
- `TELEGRAM_BRIDGE_TOKEN` → Bizim oluştururuz, **bot ve backend'de aynı olmalı**
- `TELEGRAM_LINK_SECRET` → Opsiyonel (yoksa JWT_SECRET kullanılır)

---

### Adım 4: NovaCore Backend Kontrolü

Backend'in çalıştığından emin ol:

```bash
# Backend'i başlat (eğer çalışmıyorsa)
uvicorn app.main:app --reload

# Başka terminal'de kontrol et
curl http://localhost:8000/health
```

**Beklenen çıktı:**
```json
{"status": "ok"}
```

---

### Adım 5: Bot'u Başlat

```bash
# Proje root dizininde
python -m nasipquest_bot.main
```

**Beklenen çıktı:**
```
INFO - Starting NasipQuest Bot...
INFO - NovaCore URL: http://localhost:8000
INFO - Debug mode: False
INFO - Bot is running...
```

---

## 🧪 Test Senaryosu

### 1. Bot'u Başlat

```bash
python -m nasipquest_bot.main
```

### 2. Telegram'da Test Et

1. Telegram'da bot'unu bul (BotFather'dan verdiğin username ile)
2. `/start` komutunu gönder
3. Bot "Hoş geldin!" mesajı göndermeli

### 3. Komutları Test Et

- `/help` → Yardım menüsü
- `/profile` → Profil bilgisi
- `/tasks` → Görev listesi
- `/events` → Aktif event'ler

---

## 🐛 Troubleshooting

### "TELEGRAM_BOT_TOKEN is required" hatası

**Çözüm:**
- `.env` dosyasında `TELEGRAM_BOT_TOKEN` tanımlı olduğundan emin ol
- Token'ın doğru kopyalandığından emin ol (boşluk yok)

### "NovaCore API error" hatası

**Kontrol listesi:**
1. ✅ NovaCore backend çalışıyor mu?
   ```bash
   curl http://localhost:8000/health
   ```

2. ✅ Bridge token eşleşiyor mu?
   - Bot `.env`'deki `TELEGRAM_BRIDGE_TOKEN`
   - Backend `.env`'deki `TELEGRAM_BRIDGE_TOKEN`
   - İkisi de **tamamen aynı** olmalı!

3. ✅ NovaCore URL doğru mu?
   - `NOVACORE_URL=http://localhost:8000` (backend'in çalıştığı adres)

### Bot mesaj göndermiyor

**Kontrol listesi:**
1. ✅ Bot token doğru mu? (BotFather'dan kontrol et)
2. ✅ Bot aktif mi? (`/mybots` komutu ile kontrol et)
3. ✅ Log'ları kontrol et (`BOT_DEBUG=true` ile çalıştır)
4. ✅ Bot block edilmedi mi?

### "Connection refused" hatası

**Çözüm:**
- NovaCore backend'inin çalıştığından emin ol
- `NOVACORE_URL`'in doğru olduğunu kontrol et
- Firewall/proxy ayarlarını kontrol et

---

## 📋 Komutlar

Bot'ta kullanılabilir komutlar:

- `/start` - Bot'u başlat ve NovaCore'a bağlan
- `/help` - Yardım menüsü
- `/profile` veya `/wallet` - Profil ve cüzdan bilgisi
- `/tasks` - Aktif görevleri listele
- `/complete <task_id>` - Görevi tamamla
- `/events` - Aktif event'leri göster
- `/nasipfriday` - Nasip Friday event'i
- `/war` - Quest War leaderboard
- `/leaderboard` veya `/top` - Global leaderboard
- `/me` - Detaylı profil kartı

---

## 🚀 Production Deployment

### Systemd Service (Linux)

`/etc/systemd/system/nasipquest-bot.service`:

```ini
[Unit]
Description=NasipQuest Telegram Bot
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/NovaCore
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python -m nasipquest_bot.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Aktif et:**
```bash
sudo systemctl enable nasipquest-bot
sudo systemctl start nasipquest-bot
sudo systemctl status nasipquest-bot
```

---

## 📚 Daha Fazla Bilgi

- [Bot README](../nasipquest_bot/README.md)
- [Telegram Bridge Documentation](./TELEGRAM_BRIDGE.md)
- [Token Açıklamaları](./TELEGRAM_TOKENS_EXPLAINED.md)
- [Bridge Token Açıklaması](./BRIDGE_TOKEN_EXPLAINED.md)
- [Link Secret Açıklaması](./LINK_SECRET_EXPLAINED.md)

---

## ✅ Kurulum Checklist

- [ ] Bot token alındı (BotFather'dan)
- [ ] Bağımlılıklar yüklendi (`aiogram`, `httpx`)
- [ ] `.env` dosyası hazırlandı
- [ ] `TELEGRAM_BOT_TOKEN` eklendi
- [ ] `TELEGRAM_BRIDGE_TOKEN` eklendi (bot ve backend'de aynı)
- [ ] NovaCore backend çalışıyor
- [ ] Bot başlatıldı
- [ ] Telegram'da `/start` komutu test edildi
- [ ] Bot çalışıyor ✅

---

**Bot kurulumu tamamlandı! 🎉**

