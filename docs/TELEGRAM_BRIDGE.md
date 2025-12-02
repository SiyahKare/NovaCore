# Telegram Bridge - Bot ↔ NovaCore Köprüsü

## 🎯 Durum: **v1 HAZIR**

Telegram bridge artık **tam çalışır durumda**. Bot'tan NovaCore'a tam entegrasyon mevcut.

## 📋 Checklist (Tamamlandı ✅)

- ✅ `TelegramAccount` modeli var
- ✅ `GET /api/v1/telegram/me` endpoint'i çalışıyor
- ✅ `GET /api/v1/telegram/tasks` endpoint'i çalışıyor
- ✅ `POST /api/v1/telegram/tasks/{id}/submit` endpoint'i çalışıyor
- ✅ `POST /api/v1/telegram/referral/claim` endpoint'i çalışıyor
- ✅ Bridge token güvenliği (`X-TG-BRIDGE-TOKEN` header)
- ✅ Otomatik user linking (`/link` endpoint)

## 🔐 Güvenlik

### Bridge Token

Bot → NovaCore arası servis token. `.env` dosyasına ekle:

```bash
TELEGRAM_BRIDGE_TOKEN=your-secret-token-here
```

**Tüm Telegram endpoint'leri bu token'ı `X-TG-BRIDGE-TOKEN` header'ında bekler.**

Dev mode'da token yoksa geçer (güvenlik riski - sadece dev için).

## 📡 API Endpoints

### 1. Link Telegram User

```http
POST /api/v1/telegram/link
X-TG-BRIDGE-TOKEN: your-token
Content-Type: application/json

{
  "telegram_user_id": 123456789,
  "username": "johndoe",
  "first_name": "John",
  "last_name": "Doe",
  "start_param": "optional-jwt-or-signature"
}
```

**Response:**
```json
{
  "success": true,
  "user_id": 1,
  "telegram_account_id": 1,
  "message": "Telegram account linked successfully"
}
```

### 2. Get User Profile

```http
GET /api/v1/telegram/me?telegram_user_id=123456789
X-TG-BRIDGE-TOKEN: your-token
```

**Response:**
```json
{
  "user_id": 1,
  "telegram_user_id": 123456789,
  "username": "johndoe",
  "display_name": "John Doe",
  "wallet_balance": "100.50",
  "xp_total": 500,
  "level": 5,
  "tier": "Silver",
  "xp_to_next_level": 200,
  "nova_score": 750,
  "cp_value": 0,
  "regime": "NORMAL",
  "first_seen_at": "2024-01-01T00:00:00Z",
  "last_seen_at": "2024-01-01T12:00:00Z"
}
```

### 3. Get Tasks

```http
GET /api/v1/telegram/tasks?telegram_user_id=123456789
X-TG-BRIDGE-TOKEN: your-token
```

**Response:**
```json
{
  "tasks": [
    {
      "id": "daily_login",
      "title": "Günlük Giriş",
      "description": "Her gün bot'a giriş yap",
      "category": "daily",
      "reward_xp": 10,
      "reward_ncr": "1.0",
      "status": "available",
      "expires_at": null
    }
  ],
  "total_available": 1,
  "total_completed": 0
}
```

### 4. Submit Task

```http
POST /api/v1/telegram/tasks/daily_login/submit?telegram_user_id=123456789
X-TG-BRIDGE-TOKEN: your-token
Content-Type: application/json

{
  "task_id": "daily_login",
  "proof": "screenshot_url_or_text",
  "metadata": {}
}
```

**Response:**
```json
{
  "success": true,
  "task_id": "daily_login",
  "reward_xp": 10,
  "reward_ncr": "1.0",
  "message": "Görev tamamlandı! +10 XP, +1.0 NCR",
  "new_balance": "101.50",
  "new_xp_total": 510
}
```

### 5. Claim Referral

```http
POST /api/v1/telegram/referral/claim?telegram_user_id=123456789
X-TG-BRIDGE-TOKEN: your-token
Content-Type: application/json

{
  "referral_code": "REF123"
}
```

**Response:**
```json
{
  "success": true,
  "reward_xp": 100,
  "reward_ncr": "10.0",
  "message": "Referral ödülü alındı! +100 XP, +10.0 NCR"
}
```

## 🤖 Bot Implementation (aiogram)

### Örnek Bot Kodu

```python
# nasipquest_bot/main.py
import asyncio
import httpx
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Config
BOT_TOKEN = "your-telegram-bot-token"
NOVACORE_URL = "http://localhost:8000"
BRIDGE_TOKEN = "your-bridge-token"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


async def call_novacore(endpoint: str, method: str = "GET", data: dict = None):
    """NovaCore API çağrısı."""
    headers = {
        "X-TG-BRIDGE-TOKEN": BRIDGE_TOKEN,
        "Content-Type": "application/json",
    }
    
    async with httpx.AsyncClient() as client:
        if method == "GET":
            response = await client.get(f"{NOVACORE_URL}{endpoint}", headers=headers)
        else:
            response = await client.post(f"{NOVACORE_URL}{endpoint}", headers=headers, json=data)
        
        return response.json()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Bot başlatma - Telegram user'ı NovaCore'a link et."""
    telegram_user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    
    # NovaCore'a link et
    link_data = {
        "telegram_user_id": telegram_user_id,
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
    }
    
    result = await call_novacore(
        f"/api/v1/telegram/link?telegram_user_id={telegram_user_id}",
        method="POST",
        data=link_data
    )
    
    if result.get("success"):
        await message.answer(
            f"✨ Hoş geldin! NovaCore'a bağlandın.\n"
            f"User ID: {result['user_id']}"
        )
    else:
        await message.answer("❌ Bağlantı hatası. Lütfen tekrar dene.")


@dp.message(Command("wallet"))
async def cmd_wallet(message: types.Message):
    """Cüzdan bilgisi."""
    telegram_user_id = message.from_user.id
    
    profile = await call_novacore(
        f"/api/v1/telegram/me?telegram_user_id={telegram_user_id}"
    )
    
    await message.answer(
        f"💰 **Cüzdan**\n"
        f"Bakiye: {profile['wallet_balance']} NCR\n"
        f"XP: {profile['xp_total']}\n"
        f"Seviye: {profile['level']} ({profile['tier']})\n"
        f"Sonraki seviye: {profile['xp_to_next_level']} XP kaldı"
    )


@dp.message(Command("tasks"))
async def cmd_tasks(message: types.Message):
    """Görev listesi."""
    telegram_user_id = message.from_user.id
    
    tasks_data = await call_novacore(
        f"/api/v1/telegram/tasks?telegram_user_id={telegram_user_id}"
    )
    
    tasks = tasks_data.get("tasks", [])
    
    if not tasks:
        await message.answer("📋 Şu an aktif görev yok.")
        return
    
    text = "📋 **Aktif Görevler**\n\n"
    for task in tasks:
        text += f"• {task['title']}\n"
        text += f"  {task['description']}\n"
        text += f"  Ödül: +{task['reward_xp']} XP, +{task['reward_ncr']} NCR\n\n"
    
    await message.answer(text)


@dp.message(Command("complete"))
async def cmd_complete(message: types.Message):
    """Görev tamamlama (örnek: daily_login)."""
    telegram_user_id = message.from_user.id
    
    submit_data = {
        "task_id": "daily_login",
        "proof": "completed_via_bot",
    }
    
    result = await call_novacore(
        f"/api/v1/telegram/tasks/daily_login/submit?telegram_user_id={telegram_user_id}",
        method="POST",
        data=submit_data
    )
    
    if result.get("success"):
        await message.answer(
            f"✅ {result['message']}\n"
            f"Yeni bakiye: {result['new_balance']} NCR\n"
            f"Yeni XP: {result['new_xp_total']}"
        )
    else:
        await message.answer("❌ Görev tamamlanamadı.")


async def main():
    """Bot'u başlat."""
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
```

## 🗄️ Database Migration

Telegram bridge için migration oluştur:

```bash
alembic revision --autogenerate -m "Add telegram_accounts table"
alembic upgrade head
```

**Oluşacak tablo:**
- `telegram_accounts` (TelegramAccount model)

## 🧪 Test Senaryosu

1. **Bot'u başlat:**
   ```bash
   python nasipquest_bot/main.py
   ```

2. **Telegram'da `/start` gönder:**
   - Bot → NovaCore `/link` çağrısı yapar
   - User oluşturulur/bağlanır

3. **`/wallet` komutu:**
   - Bot → NovaCore `/me` çağrısı yapar
   - Wallet, XP, NovaScore, CP bilgileri gösterilir

4. **`/tasks` komutu:**
   - Bot → NovaCore `/tasks` çağrısı yapar
   - Görev listesi gösterilir

5. **`/complete` komutu:**
   - Bot → NovaCore `/tasks/{id}/submit` çağrısı yapar
   - XP ve NCR ödülü verilir

## ✅ "Bridge v1 Bitti" Kriterleri

- 🟢 Telegram'dan gelen user, NovaCore DB'de tekil user ile bağlı
- 🟢 Bot üzerinden balance/görev/XP çekilebiliyor
- 🟢 En az 1 tip görev tam akış çalışıyor:
  - Görev al → yap → submit → onay → token mint → balance update

**Durum: ✅ TAMAMLANDI**

---

**Telegram Bridge v1 = HAYATTA** 🚀

