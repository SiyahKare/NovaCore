# MVP Citizen Quest Pack V1

**Her gün vatandaşa 3 slot görev: MONEY, SKILL, INTEGRITY**

---

## 🎯 Temel Mantık

Her gün vatandaşa 3 tip görev göster:

1. **MONEY** – Ekonomi / üretim / iş tarafı
2. **SKILL** – Öğrenme / üretim / beceri
3. **INTEGRITY** – Ahlak / şeffaflık / tribe

Bunlar hem **NovaScore komponentlerine** sinyal verir, hem de **AbuseGuard'ın eline veri** verir.

---

## 📋 Görev Listesi

### MONEY Slot

| Quest ID | Başlık | Base NCR | Base XP | Tek Seferlik? |
|----------|--------|----------|---------|---------------|
| `daily_income_snapshot` | Günün Para Raporu | 5.0 | 15 | ❌ |
| `micro_value_action` | Küçük Ticari Hamle | 8.0 | 25 | ❌ |

### SKILL Slot

| Quest ID | Başlık | Base NCR | Base XP | Tek Seferlik? |
|----------|--------|----------|---------|---------------|
| `daily_micro_content` | 1 Dakika Nasip Üretimi | 10.0 | 30 | ❌ |
| `skill_xp_log` | Skill XP (Mikro Öğrenme Log'u) | 6.0 | 20 | ❌ |

### INTEGRITY Slot

| Quest ID | Başlık | Base NCR | Base XP | Tek Seferlik? | HITL? |
|----------|--------|----------|---------|---------------|-------|
| `swamp_story_v1` | Bataklık Kaydı | 15.0 | 50 | ✅ | ✅ |
| `nasip_oath_v1` | Nasip Yemin Kartı | 5.0 | 20 | ✅ | ❌ |
| `trusted_friend_refer` | Tribe Ping | 3.0 | 15 | ❌ | ❌ |

---

## 🔗 NovaScore Sinyalleri

Her görev hangi NovaScore komponentlerine katkı yapar:

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

## 🛡️ AbuseGuard Kuralları

Her görev için özel AbuseGuard kuralları:

### `daily_income_snapshot`
- Min length: 10 karakter
- Min quality score: 30
- Spam detection: ✅
- Duplicate check: ✅

### `micro_value_action`
- Min length: 10 karakter
- Min quality score: 40
- Spam detection: ✅
- **Özel:** "hiç yok" yazarsa → düşük NCR ama Integrity bonus

### `daily_micro_content`
- Min length: 15 karakter
- Min quality score: 50
- Spam detection: ✅
- Originality check: ✅
- **Özel:** AI Score 80+ → CreatorAsset pipeline'a girebilir

### `skill_xp_log`
- Min length: 10 karakter
- Min quality score: 35
- Spam detection: ✅
- Concreteness check: ✅ (somut şeyler daha yüksek score)

### `swamp_story_v1`
- Min length: 50 karakter (3-5 cümle)
- Min quality score: 40
- **Her zaman HITL** (insan moderasyon)
- Emotional depth check: ✅

### `nasip_oath_v1`
- Exact match check: ✅ ("Kabul ediyorum" dışında → flag)
- **Özel:** Yemin sonrası ihlal → RiskScore bonus artış

### `trusted_friend_refer`
- Min length: 2 karakter
- Min quality score: 20
- Spam detection: ✅

---

## 💻 Kullanım Örnekleri

### Backend'de Quest Üretme

```python
from app.quests.factory import QuestFactory
from app.quests.mvp_pack_v1 import QuestSlot

# Kullanıcı için günlük quest seti
quests = QuestFactory.generate_for_user(
    user_id=123,
    use_mvp_pack=True,  # MVP Pack V1 kullan
    completed_one_time_quests=["swamp_story_v1"],  # Tamamlanmış tek seferlikler
)

# Her gün 3 quest döner (MONEY, SKILL, INTEGRITY)
for quest in quests:
    print(f"{quest.key}: {quest.title} - {quest.base_ncr} NCR")
```

### Telegram Bot'ta Gösterme

```python
from app.quests.telegram_formatter import format_daily_quests_for_telegram

# Quest'leri Telegram formatına çevir
message = format_daily_quests_for_telegram(quests)
# Bot'a gönder
bot.send_message(chat_id, message)
```

**Çıktı:**
```
📌 Bugünkü NasipQuest görevlerin:

1) 💸 MONEY
   [daily_income_snapshot]
   👉 "Bugün cebine giren/çıkana dair **tek bir cümle** yaz:..."

2) 🧠 SKILL
   [daily_micro_content]
   👉 "Bugün 'Nasip / Rızık / Gerçek' temalı **1 cümlelik**..."

3) 🧭 INTEGRITY
   [trusted_friend_refer]
   👉 "Hayatında **gerçekten güvendiğin** 1 kişinin adını..."
```

### Quest Tanımına Erişim

```python
from app.quests.mvp_pack_v1 import get_quest_by_id

quest_def = get_quest_by_id("daily_income_snapshot")

print(f"Slot: {quest_def.slot}")
print(f"Nova Signals: {quest_def.nova_signals}")
print(f"Abuse Rules: {quest_def.abuse_rules}")
print(f"Requires HITL: {quest_def.requires_hitl}")
```

---

## 🔄 Quest Lifecycle

```
1. QuestFactory.generate_for_user() → RuntimeQuest listesi
2. UserQuest tablosuna kaydet (status=ASSIGNED)
3. Kullanıcı proof gönder → status=SUBMITTED
4. AbuseGuard + AI scoring → status=APPROVED/REJECTED
5. NovaScore komponentleri güncellenir
6. Ödül dağıtılır (RewardEngine ile)
```

---

## 📊 Özel Kurallar

### "hiç yok" Dürüstlük Bonusu

`micro_value_action` ve `skill_xp_log` görevlerinde:
- Kullanıcı "hiç yok" veya benzeri dürüst cevap verirse
- NCR düşük (2.0) ama **Integrity sinyali +0.5** artar
- Bu dürüstlük kaydı NovaScore'a pozitif etki eder

### CreatorAsset Pipeline

`daily_micro_content` görevinde:
- AI Score 80+ ise → CreatorAsset pipeline'a girebilir
- Bu içerik Viral Agency tarafına da bağlanabilir

### Yemin İhlali Takibi

`nasip_oath_v1` görevinde:
- Kullanıcı "Kabul ediyorum" yazar
- Sonra spam/proof hilesi yaparsa → **RiskScore bonus artış**
- Bu IntegrityScore, CP tavanı, NovaScore ceiling'i etkiler

---

## 🎯 Sonraki Adımlar

1. **Quest Submission Handler** → Proof alıp AbuseGuard'a gönder
2. **AI Scoring Service** → Her quest için kalite skoru hesapla
3. **NovaScore Update** → Quest tamamlandığında komponentleri güncelle
4. **Telegram Bot Integration** → `/görevler` komutu ile göster

---

*MVP Pack V1 - Her gün 3 slot, NovaScore sinyalleri, AbuseGuard uyumlu*

