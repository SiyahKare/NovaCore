# Telegram Token'ları - Farkları ve Kullanımları

## 🔑 İki Farklı Token

`.env` dosyasında iki farklı Telegram token'ı var:

### 1. `TELEGRAM_BOT_TOKEN` 
### 2. `TELEGRAM_BRIDGE_TOKEN`

## 📋 Detaylı Açıklama

### 🤖 TELEGRAM_BOT_TOKEN

**Nereden gelir:** Telegram BotFather'dan alınır

**Ne işe yarar:** Bot'un Telegram API'ye bağlanması için gerekli

**Kim kullanır:** Sadece Telegram Bot (nasipquest_bot)

**Nasıl alınır:**
1. Telegram'da [@BotFather](https://t.me/botfather) ile konuş
2. `/newbot` komutunu gönder
3. Bot adını ve username'ini belirle
4. BotFather'dan gelen token'ı kopyala

**Örnek:**
```bash
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

**Nerede kullanılır:**
- `nasipquest_bot/main.py` - Bot'u başlatırken
- Telegram API'ye mesaj göndermek için

---

### 🔐 TELEGRAM_BRIDGE_TOKEN

**Nereden gelir:** Bizim oluşturduğumuz secret (Telegram'dan gelmiyor!)

**Ne işe yarar:** Bot ↔ NovaCore backend arasında güvenlik için

**Kim kullanır:** Hem Bot hem Backend (ikisi de aynı token'ı kullanır)

**Nasıl oluşturulur:** Manuel olarak sen oluşturuyorsun (rastgele string)

**Örnek:**
```bash
TELEGRAM_BRIDGE_TOKEN=dev-telegram-bridge-secret
```

**Nerede kullanılır:**
- `nasipquest_bot/api_client.py` - Bot'tan backend'e istek yaparken header'da gönderilir
- `app/telegram_gateway/router.py` - Backend'de istekleri doğrularken kontrol edilir

---

## 🔄 Karşılaştırma Tablosu

| Özellik | TELEGRAM_BOT_TOKEN | TELEGRAM_BRIDGE_TOKEN | TELEGRAM_LINK_SECRET |
|---------|-------------------|----------------------|---------------------|
| **Kaynak** | Telegram BotFather | Bizim oluşturduğumuz | Bizim oluşturduğumuz |
| **Amaç** | Bot ↔ Telegram API | Bot ↔ NovaCore Backend | Start param imzalama |
| **Kim kullanır** | Sadece Bot | Bot + Backend (ikisi de) | Backend (imzalama/doğrulama) |
| **Nerede** | Bot `.env` | Bot `.env` + Backend `.env` | Backend `.env` |
| **Zorunlu mu?** | Evet (bot çalışması için) | Evet (güvenlik için) | ❌ Opsiyonel (yoksa JWT_SECRET kullanılır) |
| **Değiştirilebilir mi?** | BotFather'dan yeni token alınır | İstediğin zaman değiştirebilirsin | İstediğin zaman değiştirebilirsin |

---

## 📝 .env Dosyası Örneği

```bash
# Telegram Bot Token (BotFather'dan alınır)
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# Bridge Token (Bizim oluşturduğumuz - Bot ve Backend'de aynı olmalı)
TELEGRAM_BRIDGE_TOKEN=dev-telegram-bridge-secret

# Link Secret (Opsiyonel - Start param imzalama için, yoksa JWT_SECRET kullanılır)
TELEGRAM_LINK_SECRET=your-hmac-secret-here
```

---

## 🎯 Özet

### TELEGRAM_BOT_TOKEN
- ✅ Telegram'dan gelir (BotFather)
- ✅ Bot'un Telegram'a bağlanması için
- ✅ Sadece bot kullanır
- ✅ Zorunlu

### TELEGRAM_BRIDGE_TOKEN
- ✅ Bizim oluştururuz
- ✅ Bot ↔ Backend güvenliği için
- ✅ Hem bot hem backend kullanır (aynı token)
- ✅ Zorunlu

### TELEGRAM_LINK_SECRET
- ✅ Bizim oluştururuz (opsiyonel)
- ✅ Start parameter imzalama için (deep link güvenliği)
- ✅ Sadece backend kullanır
- ❌ Opsiyonel (yoksa JWT_SECRET kullanılır)

---

## ⚠️ Önemli Notlar

1. **TELEGRAM_BOT_TOKEN** → Telegram'dan alınır, bot çalışması için zorunlu
2. **TELEGRAM_BRIDGE_TOKEN** → Bizim oluştururuz, güvenlik için zorunlu
3. **TELEGRAM_BRIDGE_TOKEN** → Bot ve Backend `.env` dosyalarında **aynı** olmalı
4. İkisi de farklı amaçlar için kullanılır, birbirinin yerine geçmez

---

## 🚀 Hızlı Kurulum

### 1. Bot Token (Telegram'dan)
```bash
# BotFather'dan al
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

### 2. Bridge Token (Bizim oluşturuyoruz)
```bash
# Python ile güçlü token oluştur
python -c "import secrets; print('TELEGRAM_BRIDGE_TOKEN=' + secrets.token_urlsafe(32))"

# Çıkan token'ı hem bot hem backend .env'lerine ekle
TELEGRAM_BRIDGE_TOKEN=TsaMy4tv21P_56mGDvkhDMAJyYqkb-V0E_t-03drMcU
```

