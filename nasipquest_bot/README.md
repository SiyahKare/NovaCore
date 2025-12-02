# NasipQuest Telegram Bot

NovaCore Telegram Bridge bot implementation.

## 🚀 Kurulum

### 1. Bağımlılıkları Yükle

```bash
pip install aiogram httpx
```

veya `pyproject.toml`'a ekle:

```toml
[project.optional-dependencies]
bot = ["aiogram>=3.0.0", "httpx>=0.25.0"]
```

Sonra:

```bash
pip install -e ".[bot]"
```

### 2. Environment Variables

`.env` dosyasına ekle:

```bash
# Telegram Bot Token (BotFather'dan alınır)
TELEGRAM_BOT_TOKEN=your-bot-token-here

# NovaCore API URL
NOVACORE_URL=http://localhost:8000

# Bridge Token (NovaCore .env'deki TELEGRAM_BRIDGE_TOKEN ile aynı olmalı)
TELEGRAM_BRIDGE_TOKEN=your-bridge-token-here

# Bot Debug Mode (opsiyonel)
BOT_DEBUG=false
```

### 3. Bot Token Alma

1. Telegram'da [@BotFather](https://t.me/botfather) ile konuş
2. `/newbot` komutunu gönder
3. Bot adını ve username'ini belirle
4. BotFather'dan gelen token'ı `.env` dosyasına ekle

### 4. NovaCore Backend'i Çalıştır

Bot'un çalışması için NovaCore backend'inin çalışıyor olması gerekir:

```bash
# NovaCore dizininde
uvicorn app.main:app --reload
```

## 🏃 Çalıştırma

```bash
# Bot dizininde
python -m nasipquest_bot.main
```

veya direkt:

```bash
python nasipquest_bot/main.py
```

## 📋 Komutlar

- `/start` - Bot'u başlat ve NovaCore'a bağlan
- `/help` - Yardım menüsü
- `/profile` veya `/wallet` - Profil ve cüzdan bilgisi
- `/tasks` - Aktif görevleri listele
- `/complete <task_id>` - Görevi tamamla
- `/events` - Aktif event'leri göster
- `/nasipfriday` - Nasip Friday event'i
- `/war` - Quest War leaderboard
- `/leaderboard` veya `/top` - Global leaderboard
- `/me` - Detaylı profil kartı
- `/refer <code>` - Referral ödülü talep et

## 🔧 Geliştirme

### Debug Mode

```bash
BOT_DEBUG=true python nasipquest_bot/main.py
```

### Yeni Komut Ekleme

`nasipquest_bot/handlers.py` dosyasına yeni handler ekle:

```python
@router.message(Command("mycommand"))
async def cmd_mycommand(message: Message):
    # Handler logic
    pass
```

## 🐛 Troubleshooting

### "TELEGRAM_BOT_TOKEN is required" hatası

`.env` dosyasında `TELEGRAM_BOT_TOKEN` tanımlı olduğundan emin ol.

### "NovaCore API error" hatası

1. NovaCore backend'inin çalıştığından emin ol (`http://localhost:8000`)
2. `TELEGRAM_BRIDGE_TOKEN`'ın NovaCore `.env`'deki ile aynı olduğunu kontrol et
3. NovaCore API'nin erişilebilir olduğunu kontrol et

### Bot mesaj göndermiyor

1. Bot token'ının doğru olduğunu kontrol et
2. BotFather'dan bot'un aktif olduğunu kontrol et
3. Log'ları kontrol et (`BOT_DEBUG=true`)

## 📚 Daha Fazla Bilgi

- [Telegram Bridge Documentation](../docs/TELEGRAM_BRIDGE.md)
- [NovaCore API Documentation](../README.md)

