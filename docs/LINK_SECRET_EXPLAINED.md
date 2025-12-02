# TELEGRAM_LINK_SECRET Nedir?

## 🎯 Kısa Cevap

**`TELEGRAM_LINK_SECRET` start parameter (HMAC) imzalama için kullanılan secret.**

- ✅ Bizim oluşturduğumuz bir secret
- ✅ Start parameter'ları imzalamak için kullanılır
- ✅ Opsiyonel (yoksa `JWT_SECRET` kullanılır)
- ✅ Güvenlik için önerilir

## 🔐 Ne İşe Yarar?

Telegram bot'unda `/start` komutuna parametre eklediğinde (örn: `/start abc123`), bu parametrenin **gerçekten bizim gönderdiğimiz** olduğunu doğrulamak için kullanılır.

**Güvenlik amacı:**
- Start parameter'ların manipüle edilmesini engeller
- Sadece bizim imzaladığımız parametreler geçerli olur
- Client-side oynanabilir kimlik riskini azaltır

## 📝 Nasıl Çalışır?

### 1. Start Parameter Oluşturma (Backend)

```python
# app/telegram_gateway/start_param.py
from app.telegram_gateway.start_param import generate_start_param

# Start parameter oluştur
start_param = generate_start_param(
    telegram_user_id=123456789,
    user_hint="user_123",
    nonce="random123"
)

# Sonuç: "{"telegram_user_id":123456789,"user_hint":"user_123",...}.HMAC_SIGNATURE"
```

### 2. Bot'ta Kullanım

```python
# Bot'ta deep link oluştur
from telegram import InlineKeyboardButton

button = InlineKeyboardButton(
    text="Bot'a Katıl",
    url=f"https://t.me/your_bot?start={start_param}"
)
```

### 3. Doğrulama (Backend)

```python
# app/telegram_gateway/router.py
from app.telegram_gateway.start_param import verify_start_param

# Start param doğrula
is_valid, payload = verify_start_param(start_param)

if is_valid:
    # Güvenli - parametre bizim imzaladığımız
    telegram_user_id = payload["telegram_user_id"]
else:
    # Güvensiz - parametre manipüle edilmiş
    raise HTTPException(400, "Invalid start parameter")
```

## 🔧 Nasıl Kullanılır?

### Opsiyonel - Varsayılan: JWT_SECRET

Eğer `.env` dosyasında `TELEGRAM_LINK_SECRET` tanımlı değilse, otomatik olarak `JWT_SECRET` kullanılır:

```python
# app/telegram_gateway/start_param.py
secret = getattr(settings, "TELEGRAM_LINK_SECRET", None) or settings.JWT_SECRET
```

### Önerilen: Ayrı Secret

Güvenlik için ayrı bir secret kullanmak daha iyi:

```bash
# .env dosyasına ekle
TELEGRAM_LINK_SECRET=your-hmac-secret-here
```

veya güçlü token oluştur:

```bash
python -c "import secrets; print('TELEGRAM_LINK_SECRET=' + secrets.token_urlsafe(32))"
```

## 📋 Örnek Kullanım Senaryosu

### Senaryo: Deep Link ile Bot'a Yönlendirme

1. **Web sitesinde:**
   ```html
   <a href="https://t.me/your_bot?start=SIGNED_PARAM">Bot'a Katıl</a>
   ```

2. **Backend'de start param oluştur:**
   ```python
   start_param = generate_start_param(
       telegram_user_id=user.telegram_user_id,
       user_hint=f"web_{user.id}"
   )
   ```

3. **Kullanıcı link'e tıklar:**
   - Telegram açılır
   - Bot `/start SIGNED_PARAM` komutunu alır

4. **Bot backend'e gönderir:**
   ```python
   await api_client.link_user(
       telegram_user_id=123456789,
       start_param="SIGNED_PARAM"
   )
   ```

5. **Backend doğrular:**
   - HMAC signature kontrol edilir
   - Geçerliyse → User link edilir
   - Geçersizse → Hata döner

## ⚠️ Önemli Notlar

1. **Opsiyonel:** Yoksa `JWT_SECRET` kullanılır (ama ayrı secret önerilir)
2. **Güvenlik:** Start parameter'ların manipüle edilmesini engeller
3. **Kullanım:** Deep link'lerde, referral link'lerde, web'den bot'a yönlendirmede kullanılır
4. **Zorunlu değil:** Basit bot kullanımında gerekli olmayabilir

## 🔄 Üç Token Karşılaştırması

| Token | Kaynak | Amaç | Zorunlu mu? |
|-------|--------|------|-------------|
| **TELEGRAM_BOT_TOKEN** | Telegram BotFather | Bot ↔ Telegram API | ✅ Evet |
| **TELEGRAM_BRIDGE_TOKEN** | Bizim oluşturduğumuz | Bot ↔ Backend güvenliği | ✅ Evet |
| **TELEGRAM_LINK_SECRET** | Bizim oluşturduğumuz | Start param imzalama | ❌ Opsiyonel |

## 🚀 Hızlı Kurulum

### Basit (JWT_SECRET kullan):

```bash
# .env dosyasında hiçbir şey ekleme
# Otomatik olarak JWT_SECRET kullanılır
```

### Güvenli (Ayrı secret):

```bash
# Güçlü token oluştur
python -c "import secrets; print('TELEGRAM_LINK_SECRET=' + secrets.token_urlsafe(32))"

# .env dosyasına ekle
TELEGRAM_LINK_SECRET=TsaMy4tv21P_56mGDvkhDMAJyYqkb-V0E_t-03drMcU
```

## 📚 İlgili Dosyalar

- `app/core/config.py` - Config tanımı (TELEGRAM_LINK_SECRET)
- `app/telegram_gateway/start_param.py` - HMAC imzalama/doğrulama
- `app/telegram_gateway/router.py` - Start param doğrulama kullanımı

## ✅ Özet

- **TELEGRAM_LINK_SECRET** = Start parameter imzalama için secret
- **Amaç** = Deep link güvenliği
- **Zorunlu mu?** = Hayır (yoksa JWT_SECRET kullanılır)
- **Ne zaman gerekli?** = Deep link, referral link, web'den bot'a yönlendirme kullanıyorsan

