# Telegram OAuth Domain Setup

## 🎯 Sorun

Telegram OAuth widget'ı için "Bot domain invalid" hatası alınıyor. Bu, bot'un domain'inin Telegram'a kayıtlı olmamasından kaynaklanır.

## ✅ Çözüm

### 1. Cloudflare Tunnel Kurulumu

Önce domain'i Cloudflare üzerinden ayağa kaldır:

```bash
# Cloudflare bilgilerini ayarla
export CF_ACCOUNT_ID='your-account-id'
export CF_API_TOKEN='your-api-token'

# Tunnel kurulumunu başlat
./scripts/setup_cloudflare_tunnel_auto.sh
```

### 2. Telegram Bot Domain Ayarları

#### BotFather'da Domain Kaydetme

1. Telegram'da [@BotFather](https://t.me/BotFather)'a git
2. `/mybots` → Bot'unu seç
3. **Bot Settings** → **Domain**
4. Domain'i gir: `portal.siyahkare.com` (veya `app.siyahkare.com`)
5. Telegram domain'i doğrulayacak

#### Domain Doğrulama

Telegram domain'i doğrulamak için şu dosyayı domain'in root'una koyar:
- `https://portal.siyahkare.com/.well-known/telegram-auth.txt`

Bu dosyayı oluştur:

```bash
# Backend'de static file serving için
mkdir -p static/.well-known
echo "8590435354" > static/.well-known/telegram-auth.txt
```

Veya Next.js'te:

```bash
# apps/citizen-portal/public/.well-known/telegram-auth.txt
mkdir -p apps/citizen-portal/public/.well-known
echo "8590435354" > apps/citizen-portal/public/.well-known/telegram-auth.txt
```

### 3. Environment Variables

**Frontend `.env.local`:**
```bash
NEXT_PUBLIC_TELEGRAM_BOT_ID=8590435354
NEXT_PUBLIC_AURORA_API_URL=https://api.siyahkare.com/api/v1
```

**Backend `.env`:**
```bash
TELEGRAM_BOT_TOKEN=your-bot-token
FRONTEND_URL=https://portal.siyahkare.com
```

### 4. Telegram OAuth Widget

Frontend'de Telegram OAuth widget'ı kullanırken:

```typescript
// apps/citizen-portal/app/identity/page.tsx
const botId = process.env.NEXT_PUBLIC_TELEGRAM_BOT_ID
const origin = process.env.NEXT_PUBLIC_AURORA_API_URL?.replace('/api/v1', '') || 'https://portal.siyahkare.com'

// Telegram OAuth URL
const telegramAuthUrl = `https://oauth.telegram.org/auth?bot_id=${botId}&origin=${encodeURIComponent(origin)}&request_access=write&return_to=${encodeURIComponent(`${origin}/identity`)}`
```

## 🔍 Test

### 1. Domain Doğrulama

```bash
# Telegram domain doğrulama dosyasını kontrol et
curl https://portal.siyahkare.com/.well-known/telegram-auth.txt
# Expected: 8590435354
```

### 2. Telegram OAuth Test

1. Browser'da `https://portal.siyahkare.com/identity` sayfasına git
2. "Telegram ile Giriş" butonuna tıkla
3. Telegram OAuth widget açılmalı
4. Giriş yap
5. Token alınmalı ve dashboard'a yönlendirilmeli

## 📝 Notlar

- **HTTPS Zorunlu**: Telegram OAuth sadece HTTPS üzerinden çalışır
- **Domain Kayıtlı Olmalı**: Bot'un domain'i BotFather'da kayıtlı olmalı
- **Origin Doğru Olmalı**: OAuth URL'deki `origin` parametresi domain ile eşleşmeli
- **Cloudflare Proxy**: Cloudflare proxy aktif olmalı (Orange Cloud)

## 🐛 Troubleshooting

### "Bot domain invalid" Hatası

1. BotFather'da domain kayıtlı mı kontrol et
2. Domain doğrulama dosyası var mı kontrol et: `/.well-known/telegram-auth.txt`
3. HTTPS çalışıyor mu kontrol et
4. Origin parametresi doğru mu kontrol et

### Domain Doğrulama Dosyası Bulunamıyor

```bash
# Frontend'de public klasörüne ekle
mkdir -p apps/citizen-portal/public/.well-known
echo "8590435354" > apps/citizen-portal/public/.well-known/telegram-auth.txt

# Build ve deploy
cd apps/citizen-portal
npm run build
npm start
```

### Cloudflare Tunnel Çalışmıyor

```bash
# Tunnel durumu
cloudflared tunnel info novacore-siyahkare

# Tunnel logları
tail -f ~/.cloudflared/tunnel.log
```

## 📚 Kaynaklar

- [Telegram Login Widget Documentation](https://core.telegram.org/widgets/login)
- [Telegram Bot Domain Setup](https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app)

