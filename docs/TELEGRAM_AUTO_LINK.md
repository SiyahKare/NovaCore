# Telegram ↔ Web Panel Otomatik Bağlama

## 🎯 Özellik

Telegram kullanıcıları artık web panelinde **otomatik olarak** giriş yapabilir. 3 farklı yöntem mevcut:

## ✅ Yöntemler

### 1. Telegram WebApp (Otomatik - En İyi)

Telegram MiniApp içinde açıldığında **otomatik olarak** kullanıcı bilgileri gelir ve giriş yapılır.

**Nasıl Çalışır:**
- Telegram bot'tan `/panel` komutu ile web paneli açılır
- Telegram WebApp script'i yüklenir
- `window.Telegram.WebApp.initData` ile kullanıcı bilgileri alınır
- Backend'e `/api/v1/identity/telegram/auth` endpoint'ine gönderilir
- JWT token alınır ve localStorage'a kaydedilir
- Kullanıcı otomatik olarak giriş yapmış olur

**Kullanım:**
```bash
# Bot'ta
/panel
```

### 2. Bot Deep Link (URL Parametresi)

Bot'tan web paneline yönlendirme yapılırken URL'e `telegram_user_id` parametresi eklenir.

**Nasıl Çalışır:**
- Bot'ta `/panel` komutu çalıştırılır
- URL: `http://localhost:3000/onboarding?telegram_user_id=123456789`
- Frontend URL parametresini okur
- `/api/v1/dev/token/telegram?telegram_user_id=...` endpoint'ine istek atar
- Token alınır ve giriş yapılır

**Kullanım:**
```bash
# Bot'ta
/panel
```

### 3. Manuel Telegram User ID Girişi

Kullanıcı Telegram User ID'sini manuel olarak girer.

**Nasıl Çalışır:**
- Web panelinde "Telegram Quest'lerimi Gör" butonuna tıklanır
- Prompt'tan Telegram User ID girilir
- `/api/v1/dev/token/telegram?telegram_user_id=...` endpoint'ine istek atar
- Token alınır ve giriş yapılır

**Kullanım:**
1. Web panelinde `/onboarding` sayfasına git
2. "Telegram Quest'lerimi Gör" butonuna tıkla
3. Telegram User ID'ni gir

## 🔧 Teknik Detaylar

### Backend Endpoints

#### 1. Telegram Auth (Production)
```http
POST /api/v1/identity/telegram/auth
Content-Type: application/json

{
  "telegram_id": 123456789,
  "username": "johndoe",
  "first_name": "John",
  "last_name": "Doe",
  "photo_url": "https://...",
  "auth_date": 1234567890,
  "hash": "..."
}
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 604800,
  "user": { ... }
}
```

#### 2. Dev Token (Development)
```http
POST /api/v1/dev/token/telegram?telegram_user_id=123456789
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

### Frontend Implementation

#### Telegram WebApp Script
```typescript
// apps/citizen-portal/lib/telegram-webapp.ts
import { loadTelegramWebAppScript, getTelegramInitData, parseTelegramInitData } from '@/lib/telegram-webapp'

// Script'i yükle
await loadTelegramWebAppScript()

// InitData'yı al
const initData = getTelegramInitData()

// Parse et
const parsed = parseTelegramInitData(initData)

// Backend'e gönder
const res = await fetch('/api/v1/identity/telegram/auth', {
  method: 'POST',
  body: JSON.stringify(parsed)
})
```

#### URL Parameter Detection
```typescript
// apps/citizen-portal/app/onboarding/page.tsx
useEffect(() => {
  const params = new URLSearchParams(window.location.search)
  const telegramUserId = params.get('telegram_user_id')
  
  if (telegramUserId) {
    handleTelegramLinkFromUrl(telegramUserId)
  }
}, [])
```

## 📝 Bot Komutu

### `/panel` veya `/web`

Bot'ta web paneline yönlendiren komut:

```python
@router.message(Command("panel", "web"))
async def cmd_panel(message: Message):
    telegram_user_id = message.from_user.id
    panel_url = f"{config.FRONTEND_URL}/onboarding?telegram_user_id={telegram_user_id}"
    
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="🚀 Web Paneline Git", url=panel_url)
    
    await message.answer("Web paneline gitmek için butona tıkla", reply_markup=keyboard.as_markup())
```

## 🔐 Güvenlik

### Telegram WebApp Authentication
- Telegram'ın resmi WebApp script'i kullanılır
- `initData` içindeki `hash` parametresi ile imza doğrulanır (TODO: v0.2'de implement edilecek)
- Production'da mutlaka hash doğrulaması yapılmalı

### Dev Token
- Sadece dev mode'da çalışır
- Production'da devre dışı bırakılmalı
- `telegram_user_id` ile TelegramAccount bulunur ve User'a bağlanır

## 🚀 Kullanım Senaryoları

### Senaryo 1: Telegram MiniApp içinde
1. Bot'ta `/panel` komutu çalıştırılır
2. Telegram MiniApp içinde web paneli açılır
3. Otomatik olarak Telegram WebApp authentication çalışır
4. Kullanıcı giriş yapmış olur

### Senaryo 2: Normal web tarayıcısında
1. Bot'ta `/panel` komutu çalıştırılır
2. Normal web tarayıcısında web paneli açılır
3. URL'de `telegram_user_id` parametresi vardır
4. Frontend parametreyi okur ve token alır
5. Kullanıcı giriş yapmış olur

### Senaryo 3: Manuel giriş
1. Web panelinde `/onboarding` sayfasına git
2. "Telegram Quest'lerimi Gör" butonuna tıkla
3. Telegram User ID'ni gir
4. Token alınır ve giriş yapılır

## ⚙️ Konfigürasyon

### Backend (.env)
```bash
# Frontend URL (bot için)
FRONTEND_URL=http://localhost:3000

# Telegram Bot Token
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# Bridge Token
TELEGRAM_BRIDGE_TOKEN=your-secure-bridge-token-here
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_AURORA_API_URL=http://localhost:8000/api/v1
```

## 🐛 Troubleshooting

### Telegram WebApp çalışmıyor
- Telegram MiniApp içinde mi açıldığını kontrol et
- `window.Telegram?.WebApp` var mı kontrol et
- Browser console'da hata var mı kontrol et

### URL parametresi çalışmıyor
- URL'de `telegram_user_id` parametresi var mı kontrol et
- Backend'de `/api/v1/dev/token/telegram` endpoint'i çalışıyor mu kontrol et
- TelegramAccount var mı kontrol et (önce `/start` gönderilmeli)

### Manuel giriş çalışmıyor
- Telegram User ID doğru mu kontrol et
- Telegram'da `/start` komutu gönderilmiş mi kontrol et
- Backend log'larında hata var mı kontrol et

