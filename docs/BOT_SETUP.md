# NasipQuest Bot Kurulum ve Çalıştırma Rehberi

## 🎯 Hızlı Başlangıç

### 1. Bot Token Alma

1. Telegram'da [@BotFather](https://t.me/botfather) ile konuş
2. `/newbot` komutunu gönder
3. Bot adını belirle (örn: "NasipQuest Bot")
4. Bot username'ini belirle (örn: "nasipquest_bot")
5. BotFather'dan gelen token'ı kopyala

### 2. Environment Variables

`.env` dosyasına ekle:

```bash
# Telegram Bot Token (BotFather'dan aldığın token)
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# NovaCore API URL (backend'in çalıştığı adres)
NOVACORE_URL=http://localhost:8000

# Bridge Token (NovaCore .env'deki TELEGRAM_BRIDGE_TOKEN ile aynı olmalı)
# BU TOKEN BİZİM OLUŞTURDUĞUMUZ BİR SECRET - Telegram'dan gelmiyor!
# İstediğin rastgele bir string olabilir (örn: "dev-secret-123" veya daha güçlü bir token)
TELEGRAM_BRIDGE_TOKEN=dev-telegram-bridge-secret

# Bot Debug Mode (opsiyonel, true/false)
BOT_DEBUG=false
```

**ÖNEMLİ:** `TELEGRAM_BRIDGE_TOKEN` NovaCore backend'inin `.env` dosyasındaki ile **tamamen aynı** olmalı!

### 3. Bağımlılıkları Yükle

```bash
# Bot bağımlılıklarını yükle
pip install aiogram httpx

# veya pyproject.toml'dan
pip install -e ".[bot]"
```

### 4. NovaCore Backend'i Çalıştır

Bot'un çalışması için NovaCore backend'inin çalışıyor olması gerekir:

```bash
# NovaCore dizininde
uvicorn app.main:app --reload
```

Backend'in `http://localhost:8000` adresinde çalıştığını kontrol et:

```bash
curl http://localhost:8000/health
```

### 5. Bot'u Çalıştır

```bash
# Proje root dizininde
python -m nasipquest_bot.main
```

veya:

```bash
cd nasipquest_bot
python main.py
```

## ✅ Test Et

1. Telegram'da bot'unu bul (BotFather'dan verdiğin username ile)
2. `/start` komutunu gönder
3. Bot "Hoş geldin!" mesajı göndermeli
4. `/help` komutu ile tüm komutları gör
5. `/profile` ile profil bilgilerini kontrol et

## 📋 Bot Komutları

### Temel Komutlar

- `/start` - Bot'u başlat ve NovaCore'a bağlan
- `/help` - Yardım menüsü
- `/profile` veya `/wallet` - Profil ve cüzdan bilgisi

### Görev Komutları

- `/tasks` - Aktif görevleri listele
- `/complete <task_id>` - Görevi tamamla (örn: `/complete daily_login`)

### Event Komutları

- `/events` - Aktif event'leri göster
- `/nasipfriday` - Nasip Friday event'i
- `/war` - Quest War leaderboard

### Sosyal Komutlar

- `/leaderboard` veya `/top` - Global leaderboard
- `/me` - Detaylı profil kartı
- `/refer <code>` - Referral ödülü talep et

## 🔧 Geliştirme

### Debug Mode

Detaylı log'lar için:

```bash
BOT_DEBUG=true python -m nasipquest_bot.main
```

### Yeni Komut Ekleme

`nasipquest_bot/handlers.py` dosyasına yeni handler ekle:

```python
@router.message(Command("mycommand"))
async def cmd_mycommand(message: Message):
    """Yeni komut açıklaması."""
    telegram_user_id = message.from_user.id
    
    try:
        # NovaCore API çağrısı
        result = await api_client.call("/api/v1/telegram/me", params={"telegram_user_id": telegram_user_id})
        
        await message.answer(f"Sonuç: {result}")
    except Exception as e:
        await message.answer(f"❌ Hata: {str(e)}")
```

## 🐛 Troubleshooting

### "TELEGRAM_BOT_TOKEN is required" hatası

- `.env` dosyasında `TELEGRAM_BOT_TOKEN` tanımlı olduğundan emin ol
- Token'ın doğru kopyalandığından emin ol (boşluk yok)

### "NovaCore API error" hatası

1. **NovaCore backend çalışıyor mu?**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Bridge token eşleşiyor mu?**
   - Bot `.env`'deki `TELEGRAM_BRIDGE_TOKEN`
   - NovaCore `.env`'deki `TELEGRAM_BRIDGE_TOKEN`
   - İkisi de **tamamen aynı** olmalı!

3. **NovaCore URL doğru mu?**
   - `NOVACORE_URL=http://localhost:8000` (backend'in çalıştığı adres)
   - Eğer farklı bir port kullanıyorsan, onu da belirt

### Bot mesaj göndermiyor

1. Bot token'ının doğru olduğunu kontrol et
2. BotFather'dan bot'un aktif olduğunu kontrol et (`/mybots`)
3. Log'ları kontrol et (`BOT_DEBUG=true`)
4. Bot'un block edilmediğinden emin ol

### "Connection refused" hatası

- NovaCore backend'inin çalıştığından emin ol
- `NOVACORE_URL`'in doğru olduğunu kontrol et
- Firewall/proxy ayarlarını kontrol et

## 📚 Daha Fazla Bilgi

- [Telegram Bridge Documentation](./TELEGRAM_BRIDGE.md)
- [NovaCore API Documentation](../README.md)
- [Bot README](../nasipquest_bot/README.md)

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

Aktif et:

```bash
sudo systemctl enable nasipquest-bot
sudo systemctl start nasipquest-bot
sudo systemctl status nasipquest-bot
```

### Docker (Opsiyonel)

`nasipquest_bot/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY nasipquest_bot/ ./nasipquest_bot/
COPY pyproject.toml ./

RUN pip install --no-cache-dir -e ".[bot]"

CMD ["python", "-m", "nasipquest_bot.main"]
```

Build ve run:

```bash
docker build -t nasipquest-bot -f nasipquest_bot/Dockerfile .
docker run --env-file .env nasipquest-bot
```

