# 🤖 Bot Kurulumu - Gerekli Environment Variables

**Tarih:** 2025-12-04  
**Durum:** Bot token eksik

---

## ❌ Eksik Environment Variable

Bot çalışması için `.env` dosyasına şu değişkenler eklenmeli:

```bash
# Telegram Bot Token (BotFather'dan alınır)
TELEGRAM_BOT_TOKEN=your-bot-token-here

# NovaCore API URL (genelde localhost:8000)
NOVACORE_URL=http://localhost:8000

# Bridge Token (NovaCore .env'deki TELEGRAM_BRIDGE_TOKEN ile aynı olmalı)
TELEGRAM_BRIDGE_TOKEN=your-bridge-token-here

# Bot Debug Mode (opsiyonel)
BOT_DEBUG=false
```

---

## 🔧 Bot Token Alma Adımları

1. Telegram'da [@BotFather](https://t.me/botfather) ile konuş
2. `/newbot` komutunu gönder
3. Bot adını ve username'ini belirle
4. BotFather'dan gelen token'ı kopyala
5. `.env` dosyasına `TELEGRAM_BOT_TOKEN=...` olarak ekle

**Örnek Token Formatı:**
```
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

---

## ✅ Kontrol

Bot'u başlatmadan önce:

```bash
# .env dosyasında token var mı kontrol et
grep TELEGRAM_BOT_TOKEN .env

# Bot'u başlat
python -m nasipquest_bot.main
```

---

## 📝 Notlar

- `.env` dosyası `.gitignore`'da olmalı (token'ları commit etme!)
- `TELEGRAM_BRIDGE_TOKEN` NovaCore backend'in `.env` dosyasındaki ile aynı olmalı
- Bot çalışırken backend'in de çalışıyor olması gerekir (`uvicorn app.main:app --reload`)

---

**Bot Setup Required - Token eklenmeli!** 🔑

