# 🎯 Quest Submission Pipeline - Vatandaş Aksiyon → Sistem Hafızası

**"Vatandaş bir şey yazdığında bu nasıl proof olur, nereye kaydolur, nasıl skorlanır?"**

---

## 📋 Pipeline Özeti

```
Vatandaş → Text Gönderir → QuestProof Kaydı → AI Scoring → AbuseGuard → Reward → NovaScore Update
```

---

## 1️⃣ Backend Core

### QuestProof Model (`app/quests/proof_models.py`)

**Amaç:** Her proof submission'ın kalıcı kaydı.

**Alanlar:**
- `user_id`, `user_quest_id` - İlişki
- `source` - telegram | web | api | mobile
- `message_id` - Telegram message_id tracking
- `proof_type` - text | photo | link | mixed
- `content` - Proof içeriği (text veya JSON)
- `ai_score`, `ai_flags`, `ai_tags` - AI scoring sonuçları

### Quest Submission API (`app/quests/router.py`)

**Endpoint:**
```http
POST /api/v1/telegram/quests/submit
```

**Payload:**
```json
{
  "quest_uuid": "abc-123-def",
  "proof_type": "text",
  "proof_payload_ref": "telegram_msg_123456",
  "proof_content": "Bugün 200 TL yol + kahve yaktım, 0 TL kazandım.",
  "source": "telegram",
  "message_id": "123456",
  "ai_score": null
}
```

**Pipeline:**
1. Quest bul ve kontrol et (expired, status)
2. AbuseGuard pre-check (cooldown, risk)
3. **QuestProof kaydı oluştur**
4. AI Scoring (PRODUCTION/RESEARCH için)
5. AbuseGuard post-check (flags → events)
6. RewardEngine v2 ile NCR/XP hesapla
7. Treasury Cap uygula
8. Wallet + XP service'e yaz
9. Marketplace Bridge (AI Score 70+)
10. Quest finalize (APPROVED / UNDER_REVIEW / REJECTED)

---

## 2️⃣ Telegram Bot Entegrasyonu

### `/görevler` veya `/tasks` Komutu

**Handler:** `nasipquest_bot/handlers.py::cmd_tasks`

**Akış:**
1. `GET /api/v1/telegram/quests/today` → Günlük quest'leri getir
2. Quest'leri formatla ve göster
3. Inline keyboard ile quest seçimi

### Text Yakalama Handler

**Handler:** `nasipquest_bot/handlers_quest_proof.py::handle_proof_text`

**MVP Mantık:**
- Kullanıcı text gönderdiğinde (command değilse)
- Aktif quest'i bul (bugün için ASSIGNED durumunda ilk quest)
- Proof gönder
- Sonuç mesajı göster

**State Tracking:**
- `_user_active_quest` dict (telegram_user_id → quest_uuid)
- MVP: Memory-based (ileride Redis/DB)

---

## 3️⃣ AI Scoring Entegrasyonu

**Service:** `app/scoring/service.py::score_quest()`

**Kullanım:**
- PRODUCTION / RESEARCH quest'leri için full scoring
- Diğer kategoriler için auto-pass (70.0)

**Sonuç:**
- Score (0-100)
- Flags (nsfw_or_toxic, low_quality, cliche)
- Suggested tags

**QuestProof'a Kayıt:**
- `quest_proof.ai_score`
- `quest_proof.ai_flags` (comma-separated)
- `quest_proof.ai_tags` (comma-separated)

---

## 4️⃣ AbuseGuard Entegrasyonu

**Pre-Check:**
- Cooldown kontrolü (RiskScore 9+)
- Quest expired kontrolü

**Post-Check:**
- `nsfw_or_toxic` flag → `TOXIC_CONTENT` event → RiskScore +2
- `low_quality` flag + score < 40 → `LOW_QUALITY_BURST` event → RiskScore +1
- Score < 50 → `AUTO_REJECT` event → HITL queue

**Quest Status:**
- Score < 50 veya hitl_required → `UNDER_REVIEW`
- Score >= 50 ve low risk → `APPROVED`

---

## 5️⃣ Reward Calculation

**Engine:** `RewardEngine v2` + `DRM`

**Formül:**
```
Final_NCR = BaseNCR × UserMultiplier × MacroMultiplier
Final_XP = BaseXP × UserMultiplier
```

**UserMultiplier:**
- Level, Streak, NovaScore, Citizen Level

**MacroMultiplier:**
- DRM (Dynamic Reward Multiplier)
- Economy Mode (Growth / Stabilization / Recovery)

**Treasury Cap:**
- Günlük emission limit kontrolü
- Limit aşılırsa ödül kırpılır

---

## 6️⃣ Marketplace Bridge

**Koşul:** AI Score >= 70 ve PRODUCTION/RESEARCH kategorisi

**Akış:**
1. Quest kategorisinden item_type çıkar
2. Fiyat hesapla (AI score'a göre)
3. `MarketplaceItem` oluştur (ACTIVE)
4. Tags ve preview_text ekle

---

## 7️⃣ Kullanım Senaryoları

### Senaryo 1: Basit Text Proof

**Vatandaş:**
```
/görevler
→ Quest listesi görünür

"Bugün 200 TL yol + kahve yaktım, 0 TL kazandım."
→ Text yakalama handler çalışır
→ İlk ASSIGNED quest'e bağlanır
→ Proof gönderilir
→ AI scoring yapılır
→ Sonuç mesajı gösterilir
```

**Backend:**
1. QuestProof kaydı oluşturulur
2. AI Scoring çağrılır (score: 75)
3. AbuseGuard kontrolü (flags yok)
4. Reward hesaplanır (10 NCR × 1.2 multiplier = 12 NCR)
5. Wallet'a yazılır
6. Marketplace'e gönderilir (score 75 >= 70)

### Senaryo 2: Toxic Content

**Vatandaş:**
```
"Kötü içerik..."
→ AI Scoring: score 30, flag: nsfw_or_toxic
```

**Backend:**
1. QuestProof kaydı oluşturulur
2. AI Scoring: score 30, flag: nsfw_or_toxic
3. AbuseGuard: `TOXIC_CONTENT` event → RiskScore +2
4. Quest status: `UNDER_REVIEW` (HITL)
5. Reward: 0 NCR (rejected)

---

## 8️⃣ API Client Methods

**`nasipquest_bot/api_client.py`:**

```python
# Quest gönder
await api_client.submit_quest(
    telegram_user_id=123,
    quest_uuid="abc-123",
    proof_type="text",
    proof_payload_ref="telegram_msg_456",
    proof_content="Proof text content",
    message_id="456",
    ai_score=None,
)

# Aktif quest getir
active_quest = await api_client.get_next_assignable_quest(telegram_user_id)
```

---

## 9️⃣ Sonraki Adımlar

1. ✅ QuestProof modeli oluşturuldu
2. ✅ AI Scoring entegrasyonu tamamlandı
3. ✅ AbuseGuard entegrasyonu tamamlandı
4. ✅ Telegram text yakalama handler eklendi
5. ⏳ NovaScore update fonksiyonu (sonraki sprint)
6. ⏳ `/myscore` ve `/history` komutları (sonraki sprint)

---

## 🔥 Test Senaryosu

**1. Quest oluştur:**
```bash
# Backend'de quest oluşturulur (QuestFactory)
GET /api/v1/telegram/quests/today?telegram_user_id=123
```

**2. Text gönder:**
```
Telegram: "Bugün çok çalıştım"
→ Bot: handle_proof_text() çalışır
→ API: POST /api/v1/telegram/quests/submit
```

**3. Sonuç:**
```
✅ Gönderin Onaylandı!
💰 Ödül: +25 XP, +12.5 NCR
⭐ Kalite Skoru: 75
```

---

**Quest Submission Pipeline hazır ve çalışıyor!** 🎉

