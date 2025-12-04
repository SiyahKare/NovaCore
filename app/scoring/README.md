# 🎯 AI Scoring Service V1 - Quest Kalite Filtresi

**Baron'un Devlet Ajandası - Kalite Gate**

---

## 🎯 Ne Yapıyor?

**Basit gerçek:**

- Vatandaş Quest tamamlar → AI Scoring → Kalite skoru (0-100)
- Score 70+ → Marketplace'e düşer
- Score < 40 → AbuseGuard'a sinyal
- Score 85+ & flag yok → CreatorAsset candidate

**Kalite filtresi olmadan marketplace çöplük olur.**

---

## 📊 Scoring Kriterleri

| Score Aralığı | Anlam | Marketplace | AbuseGuard |
|---------------|-------|-------------|------------|
| 0-39 | Çöp / spam / alakasız | ❌ | RiskScore +1 |
| 40-69 | Orta, geliştirilebilir | ❌ | - |
| 70-84 | Marketplace'e gidebilir | ✅ | - |
| 85-100 | Premium, viral potansiyelli | ✅ | CreatorAsset candidate |

---

## 🚩 Flags

- `nsfw_or_toxic` → RiskScore +2, CP +10
- `low_quality` → RiskScore +1 (score < 40 ise)
- `cliche` → Uyarı
- `spam` → Uyarı

---

## 🔄 Akış

```
1. Quest tamamlandı
   ↓
2. AI Scoring Service çağrılır
   ↓
3. OpenAI API (gpt-4o-mini) ile puanlama
   ↓
4. Score + Flags + Tags döner
   ↓
5. AbuseGuard entegrasyonu:
   - nsfw_or_toxic → RiskScore +2
   - low_quality → RiskScore +1
   ↓
6. RewardEngine → ai_score kullanır
   ↓
7. Marketplace Bridge → ai_score >= 70 ise item açar
```

---

## ⚙️ Configuration

**Environment Variables:**
```bash
OPENAI_API_KEY=sk-...  # OpenAI API key
OPENAI_MODEL=gpt-4o-mini  # Model name (default: gpt-4o-mini)
```

**Config (`app/core/config.py`):**
```python
OPENAI_API_KEY: str | None = None
OPENAI_MODEL: str = "gpt-4o-mini"
```

---

## 📝 Kullanım

### Quest Completion'da Otomatik

```python
# app/quests/completion.py
scoring_result = await score_quest(
    QuestScoringInput(
        user_id=user_id,
        quest_key=uq.key,
        category=quest_category.value,
        proof_type=proof_type,
        proof_payload=proof_payload,
        lang="tr",
    )
)

final_ai_score = scoring_result.score
scoring_flags = scoring_result.flags
suggested_tags = scoring_result.suggested_tags
```

---

## 🎯 Performance / Cost Koruması

**Sadece PRODUCTION / RESEARCH için full scoring:**

```python
if input_data.category not in ["PRODUCTION", "RESEARCH"]:
    return self._basic_scoring(input_data)  # Model çağrısı yok
```

**MODERATION / COMMUNITY / LEARNING / RITUAL:**
- Basic length + spam check
- Model çağrısı yok
- Default score: 70.0

---

## 🔧 Fallback Mekanizması

**OpenAI çağrısı başarısız olursa:**

1. **Fallback Scoring:**
   - Uzunluk bazlı heuristik
   - Score: 40-80 arası
   - Flag: low_quality (çok kısa ise)

2. **Logging:**
   - Hata loglanır
   - Quest yine de tamamlanır (fallback score ile)

---

## 📊 Prompt Engineering

**System Prompt:**
```
Sen bir "Citizen Quest Judge"sın.

Görevin: Vatandaşın ürettiği içeriği 0-100 arası puanlamak.

Kriterlerin:
- 40 altı: Çöp / spam / alakasız
- 40-69: Orta, geliştirilebilir
- 70-84: Marketplace'e gidebilir
- 85-100: Premium, viral potansiyelli

Ek kontroller:
- NSFW, nefret, scam, kumar → "nsfw_or_toxic"
- Çok kısa/boş → "low_quality"
- Çok klişe → "cliche"
- Spam pattern → "spam"
```

**Temperature:** 0.3 (daha tutarlı sonuçlar)

---

## ✅ Tamamlanan Özellikler

- ✅ QuestScoringInput / QuestScoringOutput modelleri
- ✅ ScoringService (OpenAI entegrasyonu)
- ✅ Prompt engineering
- ✅ Fallback mekanizması
- ✅ Performance koruması (sadece PRODUCTION/RESEARCH)
- ✅ AbuseGuard entegrasyonu
- ✅ Quest completion pipeline entegrasyonu

---

## ⏳ Sonraki Adımlar

- ⏳ Telegram `/market` & `/buy` komutları
- ⏳ Dynamic pricing (AI score bazlı)
- ⏳ Featured items (Score 85+)
- ⏳ Aurora Contact dashboard entegrasyonu

---

*AI Scoring Service V1 - Kalite gate aktif, marketplace çöplükten korunuyor*

