# Telegram ↔ Web Panel Kullanıcı Eşleştirme

## 🔗 Sorun

Telegram'da quest tamamlayan kullanıcı ile web panelinde giriş yapan kullanıcı farklı `user_id`'lere sahip olabilir.

## ✅ Çözüm

### Yöntem 1: Dev Token ile Telegram User ID Kullanma

Telegram'da quest tamamlayan kullanıcının `telegram_user_id`'sini kullanarak web panelinde token al:

```bash
POST /api/v1/dev/token/telegram?telegram_user_id=YOUR_TELEGRAM_USER_ID
```

**Response:**
```json
{
  "token": "eyJ...",
  "token_type": "bearer",
  "user_id": 13,
  "telegram_id": 123456789,
  "telegram_user_id": 123456789,
  "display_name": "Test User",
  "username": "test"
}
```

### Yöntem 2: Telegram User ID'yi Bulma

Telegram'da quest tamamlayan kullanıcının `telegram_user_id`'sini bulmak için:

1. **Bot'tan:** `/start` komutunu gönderdiğinde bot log'larında `telegram_user_id` görünür
2. **Database'den:** `telegram_accounts` tablosunda `telegram_user_id` kolonunu kontrol et
3. **API'den:** `/api/v1/telegram/me?telegram_user_id=...` endpoint'ini kullan

### Yöntem 3: Frontend'de Token Alma

Web panelinde, Telegram user ID'si ile token almak için:

```typescript
// apps/citizen-portal/lib/auth.ts veya component içinde
const telegramUserId = 123456789 // Telegram'dan alınan user ID
const res = await fetch(`${AURORA_API_URL}/dev/token/telegram?telegram_user_id=${telegramUserId}`, {
  method: 'POST',
})
const { token } = await res.json()
setToken(token) // localStorage'a kaydet
```

## 📝 Adımlar

1. **Telegram'da quest tamamla** → Bot'tan `telegram_user_id`'yi not et
2. **Web panelinde:** `http://localhost:3000/onboarding` sayfasına git
3. **Dev Mode:** "Dev Mode" butonuna tıkla (veya direkt API çağrısı yap)
4. **Telegram User ID ile token al:** 
   ```bash
   curl -X POST "http://localhost:8000/api/v1/dev/token/telegram?telegram_user_id=YOUR_TELEGRAM_USER_ID"
   ```
5. **Token'ı localStorage'a kaydet** ve sayfayı yenile
6. **Quest History sayfasına git:** `/quests/history`

## 🔍 Kontrol

Quest'lerin görünüp görünmediğini kontrol et:

```bash
# Backend'den direkt kontrol
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/quests/me/history"
```

## ⚠️ Notlar

- Bu endpoint sadece **dev mode**'da çalışır
- Production'da Telegram WebApp authentication kullanılmalı
- `telegram_user_id` Telegram'da `/start` komutunu gönderdiğinde oluşturulan ID'dir

