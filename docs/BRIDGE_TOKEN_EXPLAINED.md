# TELEGRAM_BRIDGE_TOKEN Nedir?

## 🎯 Kısa Cevap

**`TELEGRAM_BRIDGE_TOKEN` bizim oluşturduğumuz bir güvenlik token'ı.**

- ❌ Telegram'dan gelmiyor
- ✅ Bizim backend'imizde tanımlıyoruz
- ✅ Bot ve NovaCore backend arasında güvenlik için kullanılıyor
- ✅ İki yerde de aynı olmalı (bot `.env` ve backend `.env`)

## 🔐 Ne İşe Yarar?

Bot → NovaCore API'ye istek yaparken, bu token ile kimlik doğrulaması yapılır.

**Güvenlik amacı:**
- Sadece token'ı bilen servisler (bot) API'ye erişebilir
- Rastgele istekler engellenir
- Bot ve backend arasında güvenli iletişim sağlanır

## 📝 Nasıl Oluşturulur?

**Manuel olarak sen oluşturuyorsun.** Herhangi bir rastgele string olabilir.

### Örnek Token'lar:

```bash
# Basit (dev için)
TELEGRAM_BRIDGE_TOKEN=dev-telegram-bridge-secret

# Güçlü (prod için)
TELEGRAM_BRIDGE_TOKEN=a7f3b9c2d4e8f1a6b5c9d2e7f3a8b1c4d6e9f2a5b8c1d4e7f0a3b6c9d2e5f8a1b4

# UUID benzeri
TELEGRAM_BRIDGE_TOKEN=550e8400-e29b-41d4-a716-446655440000
```

### Python ile Güçlü Token Oluşturma:

```python
import secrets

# 32 byte (256 bit) güçlü token
token = secrets.token_urlsafe(32)
print(f"TELEGRAM_BRIDGE_TOKEN={token}")
```

## 🔧 Nasıl Kullanılır?

### 1. Backend `.env` Dosyasına Ekle

```bash
# NovaCore backend .env
TELEGRAM_BRIDGE_TOKEN=dev-telegram-bridge-secret
```

### 2. Bot `.env` Dosyasına AYNI Token'ı Ekle

```bash
# Bot .env (veya aynı .env dosyası)
TELEGRAM_BRIDGE_TOKEN=dev-telegram-bridge-secret
```

**ÖNEMLİ:** İkisi de **tamamen aynı** olmalı!

## 🔄 Nasıl Çalışır?

### 1. Bot İstek Yaparken:

```python
# nasipquest_bot/api_client.py
headers = {
    "X-TG-BRIDGE-TOKEN": config.BRIDGE_TOKEN,  # Bot'tan gönderilen token
    "Content-Type": "application/json",
}
```

### 2. Backend Doğrularken:

```python
# app/telegram_gateway/router.py
async def verify_bridge_token(
    x_tg_bridge_token: str = Header(..., alias="X-TG-BRIDGE-TOKEN"),
):
    expected_token = settings.TELEGRAM_BRIDGE_TOKEN  # Backend'deki token
    
    if x_tg_bridge_token != expected_token:
        raise HTTPException(401, "Invalid token")
```

## ⚠️ Önemli Notlar

1. **Token'ı kimseyle paylaşma** - Bu token bot'un backend'e erişim anahtarı
2. **Prod'da güçlü token kullan** - Dev'de basit olabilir, prod'da mutlaka güçlü
3. **İki yerde de aynı olmalı** - Bot ve backend `.env` dosyalarında aynı token
4. **Git'e commit etme** - `.env` dosyası `.gitignore`'da olmalı

## 🚀 Hızlı Başlangıç

### Dev için:

```bash
# .env dosyasına ekle
TELEGRAM_BRIDGE_TOKEN=dev-telegram-bridge-secret-12345
```

### Prod için:

```bash
# Python ile güçlü token oluştur
python -c "import secrets; print('TELEGRAM_BRIDGE_TOKEN=' + secrets.token_urlsafe(32))"
```

Sonra çıkan token'ı hem backend hem bot `.env` dosyalarına ekle.

## 📚 İlgili Dosyalar

- `app/core/config.py` - Backend config (TELEGRAM_BRIDGE_TOKEN tanımlı)
- `app/telegram_gateway/router.py` - Token doğrulama (verify_bridge_token)
- `nasipquest_bot/config.py` - Bot config (BRIDGE_TOKEN tanımlı)
- `nasipquest_bot/api_client.py` - Token'ı header'da gönderir

## ✅ Özet

- **TELEGRAM_BRIDGE_TOKEN** = Bizim oluşturduğumuz secret
- **Amaç** = Bot ↔ Backend güvenliği
- **Nerede** = Backend `.env` ve Bot `.env` (ikisi de aynı)
- **Nasıl** = Manuel olarak eklenir (rastgele string)

