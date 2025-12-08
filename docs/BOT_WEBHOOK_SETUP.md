# Telegram Bot Webhook Kurulumu

## 📋 Genel Bakış

Şu anda bot **polling** modunda çalışıyor (localhost'ta çalışabilir). Production için **webhook** moduna geçiş yapabilirsin.

## 🔄 Polling vs Webhook

### Polling (Şu Anki Durum)
- ✅ Localhost'ta çalışır
- ✅ Public domain gerekmez
- ✅ Development için ideal
- ❌ Sürekli API çağrısı yapar (kaynak kullanımı)
- ❌ Production'da ölçeklenebilir değil

### Webhook (Production İçin)
- ✅ Telegram mesajları direkt bot'a gönderir
- ✅ Daha verimli (kaynak kullanımı düşük)
- ✅ Production için önerilen yöntem
- ❌ Public HTTPS domain gerekir
- ❌ SSL sertifikası gerekir

## 🚀 Webhook'a Geçiş Adımları

### 1. Public Domain ve HTTPS

Bot'un çalışacağı bir domain/subdomain hazırla:
- Örnek: `https://bot.siyahkare.com` veya `https://nasipquest.siyahkare.com`
- HTTPS sertifikası gerekli (Let's Encrypt ücretsiz)

### 2. Webhook Endpoint Oluştur

`nasipquest_bot/main.py` dosyasına webhook desteği ekle:

```python
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

async def setup_webhook(bot: Bot, webhook_url: str):
    """Webhook'u Telegram'a kaydet."""
    await bot.set_webhook(
        url=webhook_url,
        allowed_updates=["message", "callback_query"]
    )
    logger.info(f"Webhook set to: {webhook_url}")

async def create_webhook_app(bot: Bot, dp: Dispatcher) -> web.Application:
    """Webhook için aiohttp app oluştur."""
    app = web.Application()
    
    # Webhook handler
    webhook_path = "/webhook"
    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    ).register(app, path=webhook_path)
    
    # Health check
    async def health_check(request):
        return web.json_response({"status": "ok"})
    
    app.router.add_get("/health", health_check)
    
    return app

# main() fonksiyonunu güncelle:
async def main():
    """Bot'u başlat."""
    # ... config kontrolleri ...
    
    bot = Bot(token=config.BOT_TOKEN, ...)
    dp = Dispatcher()
    # ... router'ları ekle ...
    
    # Webhook modu
    if config.WEBHOOK_URL:
        webhook_url = f"{config.WEBHOOK_URL}/webhook"
        await setup_webhook(bot, webhook_url)
        
        app = await create_webhook_app(bot, dp)
        web.run_app(app, host="0.0.0.0", port=config.WEBHOOK_PORT or 8443)
    else:
        # Polling modu (development)
        await dp.start_polling(bot, ...)
```

### 3. Environment Variables

`.env` dosyasına ekle:

```bash
# Webhook modu için
WEBHOOK_URL=https://bot.siyahkare.com
WEBHOOK_PORT=8443

# Polling modu için (webhook yoksa)
# WEBHOOK_URL boş bırakılırsa polling kullanılır
```

### 4. Reverse Proxy (Nginx Örneği)

Nginx config (`/etc/nginx/sites-available/bot.siyahkare.com`):

```nginx
server {
    listen 80;
    server_name bot.siyahkare.com;
    
    # HTTP'den HTTPS'e yönlendir
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name bot.siyahkare.com;
    
    ssl_certificate /etc/letsencrypt/live/bot.siyahkare.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/bot.siyahkare.com/privkey.pem;
    
    location /webhook {
        proxy_pass http://localhost:8443;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /health {
        proxy_pass http://localhost:8443;
    }
}
```

### 5. SSL Sertifikası (Let's Encrypt)

```bash
sudo certbot --nginx -d bot.siyahkare.com
```

### 6. Systemd Service (Opsiyonel)

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

## 🔍 Webhook Kontrolü

### Webhook Durumunu Kontrol Et

```python
# Python script ile
import asyncio
from aiogram import Bot

async def check_webhook():
    bot = Bot(token="YOUR_BOT_TOKEN")
    webhook_info = await bot.get_webhook_info()
    print(webhook_info)

asyncio.run(check_webhook())
```

### Webhook'u Kaldır (Polling'e Dön)

```python
async def remove_webhook():
    bot = Bot(token="YOUR_BOT_TOKEN")
    await bot.delete_webhook()
    print("Webhook removed, bot will use polling")

asyncio.run(remove_webhook())
```

## 📝 Notlar

1. **Development**: Polling kullan (localhost)
2. **Production**: Webhook kullan (public domain)
3. **Geçiş**: Webhook URL'i ayarladığında otomatik geçiş yapılır
4. **Güvenlik**: Webhook endpoint'ine rate limiting ekle
5. **Monitoring**: Health check endpoint'i ile bot durumunu izle

## 🐛 Troubleshooting

### "Webhook URL must be HTTPS"
- SSL sertifikası kurulu olmalı
- Let's Encrypt kullanabilirsin

### "Webhook failed"
- Domain'in DNS'i doğru mu?
- Port açık mı? (443)
- Firewall kuralları?

### "Bot mesaj almıyor"
- Webhook URL'i doğru mu?
- `/webhook` path'i doğru mu?
- Log'larda hata var mı?

## 🔗 Kaynaklar

- [Aiogram Webhook Docs](https://docs.aiogram.dev/en/latest/dispatcher/webhook.html)
- [Telegram Bot API - Webhooks](https://core.telegram.org/bots/api#setwebhook)

