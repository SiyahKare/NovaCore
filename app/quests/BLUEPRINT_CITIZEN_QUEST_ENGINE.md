# 🎯 Citizen Quest Engine - Blueprint & Code Skeleton

**Baron'un Devlet Ajandası - Aşama 1**

---

## 📋 Genel Bakış

Citizen Quest Engine, SiyahKare'nin **üretim motoru**dur.

**Mantık:**
- Her gün vatandaşa 3 slot görev (MONEY, SKILL, INTEGRITY)
- Vatandaş üretir → NovaScore sinyalleri → Marketplace'e otomatik gönderim
- Gerçek ekonomi döngüsü başlar

---

## 🏗️ Mimari

```
┌─────────────────┐
│  Telegram Bot   │
│  /tasks         │
│  /complete      │
│  /earnings      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Quest Router   │
│  /api/v1/...    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  QuestFactory   │
│  MVP Pack V1    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  UserQuest DB   │
│  (assigned)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Completion     │
│  + AbuseGuard   │
│  + RewardEngine │
│  + DRM          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Marketplace    │
│  Bridge         │
│  (AI 70+)       │
└─────────────────┘
```

---

## 📁 Dosya Yapısı

### Core Files

| Dosya | Açıklama |
|-------|----------|
| `mvp_pack_v1.py` | 7 görev tanımı (MONEY/SKILL/INTEGRITY) |
| `categories.py` | 6 ana kategori (PRODUCTION, RESEARCH, MODERATION, vb.) |
| `factory.py` | QuestFactory - günlük quest üretimi |
| `completion.py` | Quest tamamlama + RewardEngine entegrasyonu |
| `marketplace_bridge.py` | Marketplace'e otomatik gönderim (AI 70+) |
| `telegram_formatter.py` | Telegram mesaj formatı |

### Telegram Bot

| Dosya | Açıklama |
|-------|----------|
| `nasipquest_bot/handlers.py` | `/tasks`, `/complete`, `/earnings` komutları |
| `nasipquest_bot/api_client.py` | NovaCore API client |

---

## 🎮 Telegram Komutları

### `/tasks`

**Açıklama:** Bugünün görev listesi

**Çıktı:**
```
📌 Bugünkü NasipQuest görevlerin:

1) 💸 MONEY
   [daily_income_snapshot]
   👉 "Bugün cebine giren/çıkan parayı tek cümleyle yaz."

2) 🧠 SKILL
   [daily_micro_content]
   👉 "Nasip / Rızık / Gerçek temalı 1 cümlelik söz yaz."

3) 🧭 INTEGRITY
   [swamp_story_v1]
   👉 "Seni en çok ezen anını 3-5 cümlede anlat."
```

**Backend:** `GET /api/v1/telegram/quests/today`

---

### `/complete <quest_uuid>`

**Açıklama:** Quest proof gönderme

**Kullanım:**
```
/complete abc-123-def-456
```

**Backend:** `POST /api/v1/telegram/quests/submit`

**Akış:**
1. Proof gönderilir
2. AbuseGuard kontrolü
3. AI scoring (varsa)
4. RewardEngine ile ödül hesaplama
5. Marketplace bridge (AI 70+)
6. NCR + XP dağıtımı

---

### `/earnings`

**Açıklama:** NCR kazançları

**Çıktı:**
```
💰 NCR Kazançları

💵 Toplam Bakiye: 125.50 NCR
📅 Son 7 Gün: 45.20 NCR

Son Quest Ödülleri:
  • 10.50 NCR (2025-01-15)
  • 8.30 NCR (2025-01-14)
  ...
```

**Backend:** `GET /api/v1/wallet/me`

---

## 🔄 Quest Lifecycle

```
1. QuestFactory.generate_for_user()
   ↓
2. UserQuest (status=ASSIGNED) → DB'ye kaydet
   ↓
3. Kullanıcı /complete → Proof gönder
   ↓
4. submit_quest_proof()
   ├─ AbuseGuard kontrolü
   ├─ AI scoring
   ├─ RewardEngine (UserMultiplier × MacroMultiplier)
   └─ Marketplace bridge (AI 70+)
   ↓
5. NCR + XP dağıtımı
   ↓
6. NovaScore komponentleri güncellenir
```

---

## 💰 Ödül Hesaplama (RewardEngine v2)

```python
NCR_final = BaseNCR × UserMultiplier × MacroMultiplier

UserMultiplier = StreakFactor × SiyahFactor × RiskFactor × NovaFactor
MacroMultiplier = DRM (Dynamic Reward Multiplier)
```

**Örnek:**
- Base NCR: 10.0
- User Multiplier: 1.2 (iyi vatandaş)
- Macro Multiplier: 1.05 (normal mod)
- **Final NCR: 12.6**

---

## 🏪 Marketplace Bridge

**Kural:** AI Score 70+ → Marketplace'e otomatik gönderim

**Kategoriler:**
- ✅ PRODUCTION → Marketplace'e gidebilir
- ✅ RESEARCH → Marketplace'e gidebilir
- ❌ MODERATION → HITL görevleri, marketplace'e gitmez
- ❌ COMMUNITY → Marketplace'e gitmez
- ❌ LEARNING → Marketplace'e gitmez
- ❌ RITUAL → Marketplace'e gitmez

**Akış:**
```
Quest tamamlandı → AI Score 70+ → check_and_send_to_marketplace()
→ Marketplace item oluştur → %70 Vatandaşa, %30 Treasury
```

---

## 📊 NovaScore Sinyalleri

Her görev hangi komponentlere katkı yapar:

| Quest ID | ECO | REL | SOC | ID | CON |
|----------|-----|-----|-----|----|----|
| `daily_income_snapshot` | 0.3 | 0.2 | - | - | - |
| `micro_value_action` | 0.4 | - | - | 0.2 | 0.3 |
| `daily_micro_content` | - | - | 0.3 | - | 0.5 |
| `skill_xp_log` | - | 0.4 | - | - | 0.3 |
| `swamp_story_v1` | - | 0.3 | 0.2 | 0.5 | - |
| `nasip_oath_v1` | - | - | - | 0.6 | - |
| `trusted_friend_refer` | - | - | 0.2 | 0.3 | - |

---

## 🛡️ AbuseGuard Entegrasyonu

Her quest için:
- Min length kontrolü
- Spam detection
- Quality score threshold
- Duplicate check
- Risk score snapshot

**Özel Kurallar:**
- "hiç yok" dürüstlük bonusu → Integrity sinyali +
- Yemin ihlali takibi → RiskScore bonus artış
- CreatorAsset pipeline (AI 80+)

---

## 🎯 6 Ana Kategori (Genişletilmiş)

### A. PRODUCTION (Produksiyon)
- Mini içerik hook
- SEO cümleleri
- Ürün açıklaması
- Viral short script
- Foto caption
- Mikro çeviri

### B. RESEARCH (Araştırma)
- Trend analizi
- TikTok keşfet tarama
- Local niche araştırması
- Google Maps scraping

### C. MODERATION (Temizlik)
- Kötü içerik inceleme (HITL)
- Spam tespiti
- Toxic comment raporlama

### D. COMMUNITY (Topluluk)
- 1 referral
- 3 mesaj yardım
- Discord'da yardım
- Yeni vatandaş onboarding

### E. LEARNING (Öğrenme)
- Basic AI eğitim modülü
- Crypto basics quiz
- NovaCore onboarding

### F. RITUAL (Ritual)
- Sabah modu
- Akşam kapanış
- Cuma Raporu
- Streak Task

---

## 🚀 Sonraki Adımlar

### 1. Quest Submission Handler ✅
- Proof alıp AbuseGuard'a gönder → **TAMAMLANDI**

### 2. AI Scoring Service ⏳
- Her quest için kalite skoru hesapla
- OpenAI / Local model entegrasyonu

### 3. NovaScore Update ⏳
- Quest tamamlandığında komponentleri güncelle
- `nova_signals` dict'ini kullan

### 4. Marketplace Core ⏳
- Marketplace modülü oluştur
- Item listing, purchase flow
- Revenue share (%70 vatandaş, %30 treasury)

### 5. Telegram Bot Polish ⏳
- Inline keyboard iyileştirmeleri
- Proof gönderme UX'i
- Earnings grafikleri

---

## 📝 Kullanım Örnekleri

### Backend'de Quest Üretme

```python
from app.quests.factory import QuestFactory

quests = QuestFactory.generate_for_user(
    user_id=123,
    use_mvp_pack=True,
    completed_one_time_quests=["swamp_story_v1"],
)
```

### Quest Tamamlama

```python
from app.quests.completion import submit_quest_proof

uq = await submit_quest_proof(
    session=session,
    user_id=123,
    quest_uuid="abc-123",
    proof_type="text",
    proof_payload_ref="Bugün 200 TL harcadım",
    ai_score=75.0,
)
```

### Marketplace Bridge

```python
from app.quests.marketplace_bridge import check_and_send_to_marketplace

marketplace_id = await check_and_send_to_marketplace(
    session=session,
    user_quest=uq,
    ai_score=75.0,
)
```

---

## ✅ Tamamlanan Özellikler

- ✅ MVP Pack V1 (7 görev)
- ✅ Quest kategorileri (6 kategori)
- ✅ QuestFactory entegrasyonu
- ✅ RewardEngine v2 entegrasyonu
- ✅ DRM (Dynamic Reward Multiplier) entegrasyonu
- ✅ Marketplace bridge (placeholder)
- ✅ Telegram komutları (/tasks, /complete, /earnings)
- ✅ Telegram formatter

---

## ⏳ Eksik Özellikler

- ⏳ AI Scoring Service (gerçek implementasyon)
- ⏳ NovaScore update (quest tamamlandığında)
- ⏳ Marketplace Core modülü
- ⏳ 6 kategori için detaylı quest tanımları
- ⏳ DRM metrics toplama (cron job)

---

*Citizen Quest Engine v1.0 - Üretim motoru hazır, marketplace bekliyor*

