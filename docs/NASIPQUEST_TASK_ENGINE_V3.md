# NasipQuest Görev Motoru v3 — Mimari Dokümantasyon

## 1. Context

**NasipQuest Görev Motoru v3**, Telegram bot (`nasipquest_bot`) ile NovaCore backend arasında çalışan bir görev tamamlama ve ödül sistemi. Kullanıcılar Telegram bot üzerinden görevleri tamamlar, XP ve NCR (Nova Credit) ödülleri kazanır. Sistem idempotency, abuse koruması, event bonus'ları ve referral mekanizması içerir.

**Ana Bileşenler:**
- **Telegram Bot** (`nasipquest_bot/`): Kullanıcı arayüzü, komutlar, callback handler'ları
- **NovaCore API** (`app/telegram_gateway/`): Görev yönetimi, submission işleme, ödül dağıtımı
- **Database Models**: Task, TaskAssignment, TaskSubmission, TaskReward, ReferralReward
- **Services**: AbuseGuard (güvenlik), EventService (bonus), WalletService, XpLoyaltyService

---

## 2. Usage

### 2.1 API Endpoints

#### 2.1.1 Görev Listesi

**Endpoint:** `GET /api/v1/telegram/tasks`

**Headers:**
```
X-TG-BRIDGE-TOKEN: <bridge_token>
```

**Query Parameters:**
- `telegram_user_id` (int, required): Telegram kullanıcı ID'si

**Response:**
```json
{
  "tasks": [
    {
      "id": "daily_login",
      "title": "Günlük Giriş",
      "description": "Her gün bot'a giriş yap",
      "category": "daily",
      "difficulty": "easy",
      "task_type": "microtask",
      "proof_type": "none",
      "reward_xp": 10,
      "reward_ncr": "1.0",
      "status": "available",
      "cooldown_seconds": 0,
      "expires_at": null,
      "streak_required": 0,
      "max_completions_per_user": 1
    }
  ],
  "total_available": 1,
  "total_completed": 0
}
```

**Örnek İstek:**
```bash
curl -X GET "http://localhost:8000/api/v1/telegram/tasks?telegram_user_id=123456789" \
  -H "X-TG-BRIDGE-TOKEN: your-bridge-token"
```

---

#### 2.1.2 Görev Tamamlama

**Endpoint:** `POST /api/v1/telegram/tasks/{task_id}/submit`

**Headers:**
```
X-TG-BRIDGE-TOKEN: <bridge_token>
Content-Type: application/json
```

**Path Parameters:**
- `task_id` (string, required): Görev ID'si (örn: "daily_login")

**Query Parameters:**
- `telegram_user_id` (int, required): Telegram kullanıcı ID'si

**Request Body:**
```json
{
  "task_id": "daily_login",
  "proof": "https://example.com/screenshot.png",
  "metadata": {
    "external_id": "unique-submission-id-123",
    "source": "telegram_bot"
  }
}
```

**Response (Başarılı):**
```json
{
  "success": true,
  "task_id": "daily_login",
  "reward_xp": 15,
  "reward_ncr": "1.5",
  "message": "Görev tamamlandı! +15 XP, +1.5 NCR (Event bonus: +5 XP) (+0.5 NCR)",
  "new_balance": "150.5",
  "new_xp_total": 250
}
```

**Response (Onay Bekliyor):**
```json
{
  "success": true,
  "task_id": "daily_login",
  "reward_xp": 0,
  "reward_ncr": "0",
  "message": "Görev submit edildi, onay bekleniyor.",
  "new_balance": "0",
  "new_xp_total": 0
}
```

**Örnek İstek:**
```bash
curl -X POST "http://localhost:8000/api/v1/telegram/tasks/daily_login/submit?telegram_user_id=123456789" \
  -H "X-TG-BRIDGE-TOKEN: your-bridge-token" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "daily_login",
    "proof": null,
    "metadata": {
      "external_id": "submission-123"
    }
  }'
```

**Hata Yanıtları:**
- `400 Bad Request`: Görev bulunamadı, göreve erişim reddedildi
- `409 Conflict`: Duplicate submission, rate limit, cooldown aktif
- `404 Not Found`: Telegram account bulunamadı

---

#### 2.1.3 Referral Ödülü Talep Etme

**Endpoint:** `POST /api/v1/telegram/referral/claim`

**Headers:**
```
X-TG-BRIDGE-TOKEN: <bridge_token>
Content-Type: application/json
```

**Query Parameters:**
- `telegram_user_id` (int, required): Refer edilen kullanıcının Telegram ID'si

**Request Body:**
```json
{
  "referral_code": "REF-123"
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

**Örnek İstek:**
```bash
curl -X POST "http://localhost:8000/api/v1/telegram/referral/claim?telegram_user_id=123456789" \
  -H "X-TG-BRIDGE-TOKEN: your-bridge-token" \
  -H "Content-Type: application/json" \
  -d '{
    "referral_code": "REF-456"
  }'
```

**Hata Yanıtları:**
- `400 Bad Request`: Geçersiz referral code
- `409 Conflict`: Self-referral, duplicate referral, hesap yaşı yetersiz

---

#### 2.1.4 Leaderboard

**Endpoint:** `GET /api/v1/telegram/leaderboard`

**Headers:**
```
X-TG-BRIDGE-TOKEN: <bridge_token>
```

**Query Parameters:**
- `period` (string, optional): "daily", "weekly", "all_time" (default: "all_time")
- `limit` (int, optional): Sonuç sayısı (default: 10)

**Response:**
```json
{
  "entries": [
    {
      "rank": 1,
      "user_id": 123,
      "telegram_user_id": 123456789,
      "username": "johndoe",
      "display_name": "John Doe",
      "xp_total": 5000,
      "level": 15,
      "tier": "Gold",
      "tasks_completed": 150,
      "referrals_count": 25
    }
  ],
  "total_users": 1,
  "period": "all_time",
  "updated_at": "2025-12-02T10:00:00Z"
}
```

---

#### 2.1.5 Profil Kartı

**Endpoint:** `GET /api/v1/telegram/profile-card`

**Headers:**
```
X-TG-BRIDGE-TOKEN: <bridge_token>
```

**Query Parameters:**
- `telegram_user_id` (int, required)

**Response:**
```json
{
  "user_id": 123,
  "telegram_user_id": 123456789,
  "username": "johndoe",
  "display_name": "John Doe",
  "xp_total": 5000,
  "level": 15,
  "tier": "Gold",
  "tasks_completed": 150,
  "referrals_count": 25,
  "rank_all_time": 1,
  "rank_weekly": null,
  "achievements": ["Level 10", "50 Görev", "10 Referral"],
  "first_seen_at": "2025-01-01T00:00:00Z",
  "last_seen_at": "2025-12-02T10:00:00Z"
}
```

---

### 2.2 Environment Variables

**Zorunlu:**
```bash
# Telegram Bot Token (BotFather'dan alınır)
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# Bridge Token (Bot ↔ Backend güvenliği)
TELEGRAM_BRIDGE_TOKEN=your-secure-bridge-token-here

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/novacore
```

**Opsiyonel:**
```bash
# Start Param HMAC Secret (yoksa JWT_SECRET kullanılır)
TELEGRAM_LINK_SECRET=your-hmac-secret-here

# Environment
ENV=prod  # veya "dev"
```

**Güvenlik Notları:**
- `TELEGRAM_BRIDGE_TOKEN`: Prod'da zorunlu, dev'de opsiyonel
- `TELEGRAM_LINK_SECRET`: Opsiyonel, yoksa `JWT_SECRET` kullanılır
- Prod'da token yoksa hard fail (500 Internal Server Error)

---

## 3. Internal Flow

### 3.1 Görev Tamamlama Akışı

```
┌─────────────────┐
│  Telegram Bot   │
│  /complete cmd  │
└────────┬────────┘
         │
         │ POST /tasks/{task_id}/submit
         │ X-TG-BRIDGE-TOKEN: <token>
         │ telegram_user_id: 123456789
         │ { task_id, proof, metadata }
         ▼
┌─────────────────────────────────────┐
│  router.submit_telegram_task()      │
│  - verify_bridge_token()             │
│  - get_telegram_account()            │
└────────┬────────────────────────────┘
         │
         │ AbuseGuard.check_task_access()
         │ - Task var mı? Aktif mi?
         │ - Expires kontrolü
         │ - Assignment kontrolü
         ▼
┌─────────────────────────────────────┐
│  AbuseGuard.check_task_submission_  │
│  allowed()                          │
│  - Idempotency (external_id)        │
│  - Duplicate (user_id, task_id)    │
│  - Cooldown kontrolü                │
│  - Max completions kontrolü         │
│  - Rate limit (20/hour)             │
└────────┬────────────────────────────┘
         │
         │ TaskSubmission oluştur
         │ status = PENDING
         ▼
┌─────────────────────────────────────┐
│  Auto-approve kontrolü              │
│  if task.proof_type == "none":      │
│    status = APPROVED                 │
└────────┬────────────────────────────┘
         │
         │ if status == APPROVED:
         ▼
┌─────────────────────────────────────┐
│  EventService.apply_event_bonuses() │
│  - Aktif event'leri bul              │
│  - Multiplier'ları uygula           │
│  - Participation güncelle           │
│  Returns: (total_xp, total_ncr)     │
└────────┬────────────────────────────┘
         │
         │ XP Event oluştur
         │ XpLoyaltyService.create_xp_event()
         │
         │ NCR Reward
         │ WalletService.credit()
         │
         │ TaskReward kaydı oluştur
         │ status = REWARDED
         ▼
┌─────────────────────────────────────┐
│  Response döndür                     │
│  - reward_xp, reward_ncr             │
│  - new_balance, new_xp_total         │
│  - Bonus mesajı                      │
└─────────────────────────────────────┘
```

### 3.2 Referral Claim Akışı

```
┌─────────────────┐
│  Telegram Bot   │
│  /start REF-123 │
└────────┬────────┘
         │
         │ POST /referral/claim
         │ { referral_code: "REF-123" }
         ▼
┌─────────────────────────────────────┐
│  router.claim_referral()            │
│  - verify_bridge_token()            │
│  - get_telegram_account()           │
└────────┬────────────────────────────┘
         │
         │ Referrer user_id parse et
         │ (referral_code format: "REF-{user_id}")
         ▼
┌─────────────────────────────────────┐
│  AbuseGuard.check_referral_allowed()│
│  - Self-referral kontrolü           │
│  - Duplicate kontrolü               │
│  - Hesap yaşı kontrolü (1 saat)     │
└────────┬────────────────────────────┘
         │
         │ ReferralReward kaydı oluştur
         │
         │ XP Event (referrer için)
         │ XpLoyaltyService.create_xp_event()
         │
         │ NCR Reward (referrer için)
         │ WalletService.credit()
         │
         │ Reward kaydını güncelle
         │ (xp_event_id, wallet_tx_id)
         ▼
┌─────────────────────────────────────┐
│  Response döndür                     │
└─────────────────────────────────────┘
```

### 3.3 Service Dependencies

**AbuseGuard** (`app/telegram_gateway/abuse_guard.py`):
- `TaskSubmission` (duplicate, idempotency)
- `ReferralReward` (self-referral, duplicate)
- `Task` (access, cooldown, max_completions)
- `TaskAssignment` (expires check)

**EventService** (`app/telegram_gateway/event_service.py`):
- `Event` (aktif event'leri bul)
- `EventTask` (task-event bağlantısı)
- `EventParticipation` (skor güncelleme)

**WalletService** (`app/wallet/service.py`):
- `LedgerEntry` (NCR credit transaction)

**XpLoyaltyService** (`app/xp_loyalty/service.py`):
- `XpEvent` (XP event kaydı)
- `UserLoyalty` (XP total, level, tier)

**IdentityService** (`app/identity/service.py`):
- `User` (user oluşturma/bulma)
- `TelegramAccount` (telegram-user mapping)

---

## 4. Database Schema

### 4.1 Task Models

**`telegram_tasks` (Task):**
```sql
CREATE TABLE telegram_tasks (
    id VARCHAR(100) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT DEFAULT '',
    category VARCHAR(50) NOT NULL,
    difficulty VARCHAR(20) DEFAULT 'easy',
    task_type VARCHAR(20) DEFAULT 'microtask',
    proof_type VARCHAR(20) DEFAULT 'none',
    reward_xp INTEGER DEFAULT 0,
    reward_ncr VARCHAR(255) DEFAULT '0',
    cooldown_seconds INTEGER DEFAULT 0,
    expires_at TIMESTAMP,
    streak_required INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active',
    max_completions_per_user INTEGER DEFAULT 1,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_tasks_category ON telegram_tasks(category);
CREATE INDEX idx_tasks_status ON telegram_tasks(status);
CREATE INDEX idx_tasks_expires ON telegram_tasks(expires_at);
```

**`telegram_task_assignments` (TaskAssignment):**
```sql
CREATE TABLE telegram_task_assignments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    task_id VARCHAR(100) NOT NULL REFERENCES telegram_tasks(id),
    assigned_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, task_id),
    INDEX idx_assignments_user_active (user_id, is_active)
);
```

**`telegram_task_submissions` (TaskSubmission):**
```sql
CREATE TABLE telegram_task_submissions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    task_id VARCHAR(100) NOT NULL REFERENCES telegram_tasks(id),
    proof TEXT,
    proof_metadata JSONB DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'pending',
    reviewed_by INTEGER REFERENCES users(id),
    reviewed_at TIMESTAMP,
    rejection_reason TEXT,
    external_id VARCHAR(255) UNIQUE,
    submitted_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, task_id),
    INDEX idx_submissions_status (status, submitted_at),
    INDEX idx_submissions_external_id (external_id)
);
```

**`telegram_task_rewards` (TaskReward):**
```sql
CREATE TABLE telegram_task_rewards (
    id SERIAL PRIMARY KEY,
    submission_id INTEGER UNIQUE NOT NULL REFERENCES telegram_task_submissions(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    task_id VARCHAR(100) NOT NULL REFERENCES telegram_tasks(id),
    xp_amount INTEGER DEFAULT 0,
    ncr_amount VARCHAR(255) DEFAULT '0',
    wallet_tx_id INTEGER REFERENCES ledger_entries(id),
    xp_event_id INTEGER REFERENCES xp_events(id),
    rewarded_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_rewards_user (user_id),
    INDEX idx_rewards_task (task_id)
);
```

**`telegram_referral_rewards` (ReferralReward):**
```sql
CREATE TABLE telegram_referral_rewards (
    id SERIAL PRIMARY KEY,
    referrer_user_id INTEGER NOT NULL REFERENCES users(id),
    referred_user_id INTEGER NOT NULL REFERENCES users(id),
    referral_code VARCHAR(50) NOT NULL,
    xp_amount INTEGER DEFAULT 0,
    ncr_amount VARCHAR(255) DEFAULT '0',
    wallet_tx_id INTEGER REFERENCES ledger_entries(id),
    xp_event_id INTEGER REFERENCES xp_events(id),
    reward_metadata JSONB DEFAULT '{}',
    rewarded_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(referrer_user_id, referred_user_id),
    INDEX idx_referral_code (referral_code, rewarded_at)
);
```

---

## 5. Security & Idempotency

### 5.1 Bridge Token Authentication

**Header:** `X-TG-BRIDGE-TOKEN`

**Doğrulama:**
- Prod'da token zorunlu (yoksa 500 Internal Server Error)
- Dev'de opsiyonel (yoksa uyar ama geç)
- Token eşleşmezse 401 Unauthorized

**Kod:**
```python
async def verify_bridge_token(
    x_tg_bridge_token: str | None = Header(None, alias="X-TG-BRIDGE-TOKEN"),
) -> bool:
    expected_token = settings.TELEGRAM_BRIDGE_TOKEN
    if settings.is_prod and not expected_token:
        raise HTTPException(500, "TELEGRAM_BRIDGE_TOKEN not configured")
    if x_tg_bridge_token != expected_token:
        raise HTTPException(401, "Invalid bridge token")
    return True
```

### 5.2 HMAC Start Parameter

**Format:** `{payload_json}.{hmac_signature}`

**Payload:**
```json
{
  "telegram_user_id": 123456789,
  "user_hint": "web_123",
  "ts": 1701504000,
  "nonce": "abc123def456"
}
```

**Doğrulama:**
- HMAC SHA256 ile imza kontrolü
- Timestamp kontrolü (max 1 saat eski)
- `TELEGRAM_LINK_SECRET` veya `JWT_SECRET` kullanılır

**Kod:**
```python
def verify_start_param(start_param: str) -> tuple[bool, Optional[dict]]:
    payload_json, signature = start_param.rsplit('.', 1)
    secret = settings.TELEGRAM_LINK_SECRET or settings.JWT_SECRET
    expected_sig = hmac.new(secret.encode(), payload_json.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected_sig):
        return False, None
    payload = json.loads(payload_json)
    if time.time() - payload["ts"] > 3600:
        return False, None
    return True, payload
```

### 5.3 Idempotency Guards

**1. External ID (Task Submission):**
- `TaskSubmission.external_id` unique constraint
- Aynı `external_id` ile tekrar submit → 409 Conflict

**2. User-Task Pair (Task Submission):**
- `(user_id, task_id)` unique constraint
- Zaten `rewarded` ise → 409 Conflict
- `pending` ise → cooldown kontrolü

**3. Referral Pair:**
- `(referrer_user_id, referred_user_id)` unique constraint
- Self-referral → 409 Conflict
- Duplicate → 409 Conflict

---

## 6. Abuse Protection

### 6.1 Rate Limiting

**Task Submission:**
- Max 20 submission per hour per user
- Son 1 saatteki submission sayısı kontrol edilir

**Kod:**
```python
one_hour_ago = datetime.utcnow() - timedelta(hours=1)
recent_count = await session.execute(
    select(func.count(TaskSubmission.id)).where(
        and_(
            TaskSubmission.user_id == user_id,
            TaskSubmission.submitted_at >= one_hour_ago,
        )
    )
)
if recent_count.scalar_one() >= 20:
    return False, "Rate limit: Saatte maksimum 20 görev tamamlayabilirsin"
```

### 6.2 Cooldown Protection

**Task Cooldown:**
- `Task.cooldown_seconds` > 0 ise, son submission'dan bu kadar süre geçmeli
- Pending submission varsa, cooldown kontrol edilir

**Kod:**
```python
if task.cooldown_seconds > 0:
    elapsed = (datetime.utcnow() - submission.submitted_at).total_seconds()
    if elapsed < task.cooldown_seconds:
        remaining = int(task.cooldown_seconds - elapsed)
        return False, f"Cooldown aktif. {remaining} saniye sonra tekrar deneyebilirsin."
```

### 6.3 Max Completions

**Per-User Limit:**
- `Task.max_completions_per_user` > 0 ise, kullanıcı bu kadar kez tamamlayabilir
- `status == REWARDED` submission'lar sayılır

### 6.4 Referral Protection

**Hesap Yaşı:**
- Refer edilen kullanıcının hesabı en az 1 saat olmalı
- Spam koruması için

**Kod:**
```python
account_age = (datetime.utcnow() - referred_user.created_at).total_seconds()
if account_age < 3600:
    return False, "Refer edilen kullanıcının hesabı en az 1 saat olmalı"
```

---

## 7. Event Bonus System

### 7.1 Event-Task Mapping

**Event Model:**
- `Event`: Aktif event tanımı (starts_at, ends_at, status)
- `EventTask`: Event-task bağlantısı (reward_multiplier_xp, reward_multiplier_ncr)
- `EventParticipation`: Kullanıcının event'e katılımı (total_xp_earned, total_ncr_earned)

**Bonus Hesaplama:**
```python
# Event multiplier'ları al
xp_mult = event_task.reward_multiplier_xp or event.reward_multiplier_xp or 1.0
ncr_mult = event_task.reward_multiplier_ncr or event.reward_multiplier_ncr or 1.0

# Bonus hesapla
bonus_xp = int(base_xp * (xp_mult - 1.0))
bonus_ncr = base_ncr * (ncr_mult - 1.0)

total_xp = base_xp + bonus_xp
total_ncr = base_ncr + bonus_ncr
```

**Participation Güncelleme:**
- Her task tamamlandığında `EventParticipation` güncellenir
- `total_xp_earned`, `total_ncr_earned`, `tasks_completed` artırılır

---

## 8. TODO / Future Work

1. **Task Service Refactoring**
   - Şu an mock data dönen `/tasks` endpoint'i gerçek task service'ten çekmeli
   - Task assignment logic'i ayrı bir service'e taşınmalı
   - Task metadata validation (proof_type, task_type uyumluluğu)

2. **Admin Task Management**
   - Admin panel'den task oluşturma/düzenleme endpoint'leri
   - Task approval/rejection workflow (şu an sadece auto-approve var)
   - Task analytics (completion rate, average time, etc.)

3. **Proof Verification**
   - Screenshot verification (image analysis, OCR)
   - Link verification (domain whitelist, content check)
   - Onchain transaction verification (blockchain explorer integration)

4. **Advanced Rate Limiting**
   - Per-task rate limits (örn: daily_login günde 1 kez)
   - Per-category rate limits
   - Dynamic rate limiting (abuse detection'a göre)

5. **Referral System Enhancement**
   - Referral code generation service (şu an "REF-{user_id}" formatı)
   - Referral tracking (click tracking, conversion rate)
   - Multi-level referral (referrer'in referrer'ına da ödül)

6. **Event System Improvements**
   - Event leaderboard caching (Redis)
   - Event notifications (Telegram push)
   - Event rewards (top 10'a ekstra ödül)

7. **Analytics & Monitoring**
   - Task completion metrics (success rate, average time)
   - Abuse detection alerts (suspicious patterns)
   - Reward distribution analytics (total XP/NCR distributed)

---

## 9. Örnek Senaryolar

### Senaryo 1: Günlük Giriş Görevi

**1. Bot'tan görev listesi:**
```bash
GET /api/v1/telegram/tasks?telegram_user_id=123456789
```

**2. Kullanıcı `/complete daily_login` komutunu çalıştırır**

**3. Bot backend'e submit eder:**
```bash
POST /api/v1/telegram/tasks/daily_login/submit?telegram_user_id=123456789
{
  "task_id": "daily_login",
  "proof": null,
  "metadata": {
    "external_id": "daily_login_2025-12-02_123456789"
  }
}
```

**4. Backend işlemleri:**
- AbuseGuard: Duplicate kontrolü (ilk kez → OK)
- TaskSubmission oluştur (status: PENDING)
- Auto-approve (proof_type: none → status: APPROVED)
- EventService: Aktif event var mı? (varsa bonus uygula)
- XpLoyaltyService: XP event oluştur (10 XP + 5 XP bonus = 15 XP)
- WalletService: NCR credit (1.0 NCR + 0.5 NCR bonus = 1.5 NCR)
- TaskReward kaydı oluştur
- Response döndür

**5. Bot kullanıcıya mesaj gösterir:**
```
✅ Görev tamamlandı!
+15 XP, +1.5 NCR
(Event bonus: +5 XP) (+0.5 NCR)
```

### Senaryo 2: Referral Ödülü

**1. Kullanıcı `/start REF-456` ile bot'a katılır**

**2. Bot backend'e referral claim eder:**
```bash
POST /api/v1/telegram/referral/claim?telegram_user_id=123456789
{
  "referral_code": "REF-456"
}
```

**3. Backend işlemleri:**
- AbuseGuard: Self-referral kontrolü (123456789 ≠ 456 → OK)
- AbuseGuard: Duplicate kontrolü (ilk kez → OK)
- AbuseGuard: Hesap yaşı kontrolü (1 saat+ → OK)
- ReferralReward kaydı oluştur
- XpLoyaltyService: Referrer için XP event (100 XP)
- WalletService: Referrer için NCR credit (10.0 NCR)
- Response döndür

**4. Referrer kullanıcıya bildirim:**
```
🎉 Referral ödülü!
+100 XP, +10.0 NCR
```

---

## 10. Hata Senaryoları

### Senaryo 1: Duplicate Submission

**İstek:**
```bash
POST /api/v1/telegram/tasks/daily_login/submit?telegram_user_id=123456789
{
  "task_id": "daily_login",
  "metadata": {"external_id": "same-id-123"}
}
```

**İlk İstek:** ✅ Başarılı (200 OK)
**İkinci İstek:** ❌ 409 Conflict
```json
{
  "detail": "Bu submission zaten işlendi (idempotency)"
}
```

### Senaryo 2: Rate Limit

**İstek:** Son 1 saatte 20+ submission yapılmış

**Yanıt:** ❌ 409 Conflict
```json
{
  "detail": "Rate limit: Saatte maksimum 20 görev tamamlayabilirsin"
}
```

### Senaryo 3: Cooldown Aktif

**İstek:** Cooldown süresi dolmamış görev

**Yanıt:** ❌ 409 Conflict
```json
{
  "detail": "Cooldown aktif. 300 saniye sonra tekrar deneyebilirsin."
}
```

### Senaryo 4: Self-Referral

**İstek:**
```bash
POST /api/v1/telegram/referral/claim?telegram_user_id=123456789
{
  "referral_code": "REF-123456789"
}
```

**Yanıt:** ❌ 409 Conflict
```json
{
  "detail": "Kendini refer edemezsin"
}
```

---

## 11. Test Senaryoları

### Test 1: Idempotency

```python
# Aynı external_id ile 2 kez submit
response1 = submit_task(task_id="daily_login", external_id="test-123")
assert response1.status_code == 200

response2 = submit_task(task_id="daily_login", external_id="test-123")
assert response2.status_code == 409
assert "idempotency" in response2.json()["detail"]
```

### Test 2: Event Bonus

```python
# Event oluştur (2x XP multiplier)
event = create_event(xp_multiplier=2.0)

# Task submit et
response = submit_task(task_id="daily_login")
assert response.json()["reward_xp"] == 20  # 10 base * 2 = 20
```

### Test 3: Rate Limit

```python
# 21 kez submit et (1 saat içinde)
for i in range(21):
    response = submit_task(task_id=f"task_{i}")
    if i < 20:
        assert response.status_code == 200
    else:
        assert response.status_code == 409
        assert "Rate limit" in response.json()["detail"]
```

---

## 12. Monitoring & Logging

**Önemli Metrikler:**
- Task submission rate (per hour/day)
- Reward distribution (total XP/NCR)
- Abuse detection (rate limit hits, duplicate attempts)
- Event participation rate
- Referral conversion rate

**Log Points:**
- Task submission (user_id, task_id, status)
- Reward distribution (user_id, xp_amount, ncr_amount)
- Abuse guard hits (rate limit, duplicate, cooldown)
- Event bonus application (event_id, bonus_xp, bonus_ncr)

---

**Son Güncelleme:** 2025-12-02  
**Versiyon:** v3.0  
**Yazar:** NovaCore Team

