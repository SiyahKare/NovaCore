# Telegram OAuth Domain Fix - Hızlı Çözüm

## 🎯 Sorun

Telegram OAuth widget'ı "Bot domain invalid" hatası veriyor.

## ✅ Çözüm Adımları

### 1. Cloudflare Tunnel Kurulumu

```bash
# Cloudflare bilgilerini ayarla
export CF_ACCOUNT_ID='your-account-id'
export CF_API_TOKEN='your-api-token'

# Tunnel kurulumunu başlat
./scripts/setup_cloudflare_tunnel_auto.sh
```

### 2. Telegram Bot Domain Kaydı

1. Telegram'da [@BotFather](https://t.me/BotFather)'a git
2. `/mybots` → Bot'unu seç (8590435354)
3. **Bot Settings** → **Domain**
4. Domain'i gir: `portal.siyahkare.com`
5. Telegram domain'i doğrulayacak

### 3. Domain Doğrulama Dosyası

✅ **Zaten oluşturuldu:** `apps/citizen-portal/public/.well-known/telegram-auth.txt`

Bu dosya Cloudflare üzerinden erişilebilir olmalı:
- `https://portal.siyahkare.com/.well-known/telegram-auth.txt`
- İçeriği: `8590435354`

### 4. Environment Variables

**Frontend `.env.local`:**
```bash
NEXT_PUBLIC_TELEGRAM_BOT_ID=8590435354
NEXT_PUBLIC_AURORA_API_URL=https://api.siyahkare.com/api/v1
```

### 5. Test

```bash
# Domain doğrulama dosyasını kontrol et
curl https://portal.siyahkare.com/.well-known/telegram-auth.txt
# Expected: 8590435354

# Telegram OAuth test
# Browser: https://portal.siyahkare.com/identity
```

## 📋 Checklist

- [ ] Cloudflare Tunnel kuruldu
- [ ] Domain `portal.siyahkare.com` çalışıyor
- [ ] BotFather'da domain kayıtlı
- [ ] Domain doğrulama dosyası erişilebilir
- [ ] Environment variables ayarlandı
- [ ] Frontend rebuild edildi

## 🐛 Troubleshooting

### "Bot domain invalid" Hatası Devam Ediyor

1. **BotFather'da domain kayıtlı mı?**
   - `/mybots` → Bot → Bot Settings → Domain
   - `portal.siyahkare.com` kayıtlı olmalı

2. **Domain doğrulama dosyası erişilebilir mi?**
   ```bash
   curl https://portal.siyahkare.com/.well-known/telegram-auth.txt
   ```
   - `8590435354` dönmeli

3. **HTTPS çalışıyor mu?**
   - Telegram OAuth sadece HTTPS üzerinden çalışır
   - Cloudflare proxy aktif olmalı (Orange Cloud)

4. **Frontend rebuild edildi mi?**
   ```bash
   cd apps/citizen-portal
   npm run build
   ```

## 📚 Detaylı Dokümantasyon

- [Telegram OAuth Setup](./docs/TELEGRAM_OAUTH_SETUP.md)
- [Cloudflare Tunnel Setup](./docs/CLOUDFLARE_TUNNEL_SETUP.md)

