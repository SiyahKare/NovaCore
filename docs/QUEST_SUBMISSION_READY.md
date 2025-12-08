# ✅ Quest Submission Pipeline - Hazır Durum

**Tarih:** 2025-12-04  
**Versiyon:** V2.0  
**Durum:** ✅ Ready for Testing

---

## 🎯 Tamamlanan Özellikler

### 1. Backend Core ✅

- ✅ **QuestProof Model** (`app/quests/proof_models.py`)
  - Proof submission kayıtları
  - AI scoring sonuçları (score, flags, tags)
  - Source tracking (telegram, web, api, mobile)

- ✅ **Quest Submission API** (`app/quests/router.py`)
  - `POST /api/v1/telegram/quests/submit`
  - `QuestSubmitResponse` model (status, reason, rewards, marketplace_item_id)
  - Pipeline entegrasyonu

- ✅ **Quest Completion Pipeline** (`app/quests/completion.py`)
  - 10 adımlı pipeline
  - AbuseGuard pre/post-check
  - AI Scoring entegrasyonu
  - RewardEngine v2
  - Marketplace Bridge

### 2. Telegram Bot Entegrasyonu ✅

- ✅ **`/görevler` veya `/tasks` Komutu**
  - Günlük quest'leri getir
  - Inline keyboard ile quest seçimi

- ✅ **Text Yakalama Handler** (`nasipquest_bot/handlers_quest_proof.py`)
  - Kullanıcı text gönderdiğinde aktif quest'e bağla
  - MVP: Bugün için ASSIGNED durumunda olan ilk quest

- ✅ **Response Handling**
  - Status'a göre mesaj gösterimi
  - Ödül bilgisi gösterimi
  - Hata mesajları

### 3. AI Scoring Service ✅

- ✅ **AI Scoring** (`app/scoring/service.py`)
  - OpenAI entegrasyonu
  - PRODUCTION/RESEARCH için full scoring
  - MODERATION/RITUAL için auto-pass
  - Flags ve tags döndürme

### 4. Marketplace Bridge ✅

- ✅ **Otomatik Marketplace Gönderimi**
  - AI Score 70+ → Marketplace'e gönder
  - Item type inference
  - Dynamic pricing
  - Content delivery

---

## 📋 Pipeline Akışı

```
1. Vatandaş text gönderir
   ↓
2. Telegram bot → aktif quest bul
   ↓
3. POST /api/v1/telegram/quests/submit
   ↓
4. Quest bul ve kontrol et
   ↓
5. AbuseGuard pre-check (cooldown)
   ↓
6. QuestProof kaydı oluştur
   ↓
7. AI Scoring (PRODUCTION/RESEARCH)
   ↓
8. AbuseGuard post-check (flags → events)
   ↓
9. RewardEngine v2 → NCR/XP hesapla
   ↓
10. Treasury Cap uygula
   ↓
11. Wallet + XP service'e yaz (APPROVED ise)
   ↓
12. Marketplace Bridge (AI Score 70+)
   ↓
13. Quest finalize (APPROVED / UNDER_REVIEW / REJECTED)
   ↓
14. Response döndür (status, rewards, marketplace_item_id)
```

---

## 🔧 API Kullanımı

### Request

```http
POST /api/v1/telegram/quests/submit
Content-Type: application/json

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

### Response

```json
{
  "status": "approved",
  "quest_uuid": "abc-123-def",
  "quest_id": 42,
  "reason": "approved",
  "risk_delta": null,
  "ai_score": 85.0,
  "final_reward_ncr": 12.5,
  "final_reward_xp": 150,
  "final_score": 85.0,
  "marketplace_item_id": 123
}
```

---

## 📊 Status Mapping

| Status | Reason | Açıklama |
|--------|--------|----------|
| `pending_review` | `queued_for_ai_scoring` | AI scoring bekleniyor (artık kullanılmıyor, sync yapılıyor) |
| `approved` | `approved` | Quest onaylandı, ödül verildi |
| `rejected` | `abuse_guard_block` | AbuseGuard tarafından reddedildi |
| `rejected` | `auto_reject` | AI score < 50 |
| `under_review` | `under_review` | HITL (Human-in-the-Loop) gerekli |

---

## 🧪 Test Senaryoları

### Senaryo 1: Happy Path ✅

```
1. /görevler → Quest seç
2. Text gönder → Proof kaydedildi
3. AI Scoring → Score 85
4. AbuseGuard → Risk OK
5. Reward → NCR + XP verildi
6. Marketplace → Item oluşturuldu
7. Response → status="approved", marketplace_item_id=123
```

### Senaryo 2: Low Quality

```
1. Text gönder → Proof kaydedildi
2. AI Scoring → Score 35
3. AbuseGuard → LOW_QUALITY_BURST event
4. Quest → UNDER_REVIEW
5. Response → status="under_review"
```

### Senaryo 3: Toxic Content

```
1. Text gönder → Proof kaydedildi
2. AI Scoring → Score 20, flag="nsfw_or_toxic"
3. AbuseGuard → TOXIC_CONTENT event, RiskScore +2
4. Quest → REJECTED
5. Response → status="rejected", reason="abuse_guard_block"
```

---

## 🚀 Sonraki Adımlar

1. ✅ **Quest Submission Pipeline** (Tamamlandı)
2. ✅ **Telegram `/görevler` + text yakalama** (Tamamlandı)
3. 🔜 **NovaScore update fonksiyonu** (Sonraki sprint)
4. 🔜 **AI Scoring Worker** (Async worker'a taşıma - opsiyonel)
5. 🔜 **`/myscore` ve `/history` komutları** (Sonraki sprint)

---

## 📝 Notlar

- **AI Scoring:** Şu an sync olarak `submit_quest_proof()` içinde yapılıyor. İleride async worker'a taşınabilir.
- **Marketplace Item ID:** Response'da marketplace_item_id döndürülüyor, ancak quest APPROVED ve AI Score 70+ ise.
- **Risk Delta:** Şu an response'da `null` döndürülüyor, AbuseGuard'dan risk_delta çekilebilir.

---

**Pipeline hazır ve çalışıyor!** 🚀

Test için:
1. Telegram bot'u başlat
2. `/görevler` komutuyla quest al
3. Text gönder → Proof kaydedilir ve işlenir
4. Response'u kontrol et

