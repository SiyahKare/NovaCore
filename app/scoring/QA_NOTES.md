# 🎯 AI Scoring Service - QA Notları

**Durum:** ✅ **HAZIR VE ÇALIŞIYOR**

---

## ✅ Tamamlanan Özellikler

1. **AI Scoring Service** (`app/scoring/service.py`)
   - ✅ OpenAI entegrasyonu (gpt-4o-mini)
   - ✅ Prompt engineering (Citizen Quest Judge)
   - ✅ Fallback mekanizması
   - ✅ Performance koruması (sadece PRODUCTION/RESEARCH)

2. **Quest Completion Entegrasyonu** (`app/quests/completion.py`)
   - ✅ AI Scoring otomatik çağrılıyor
   - ✅ Score + Flags + Tags döner
   - ✅ AbuseGuard entegrasyonu

3. **AbuseGuard Entegrasyonu**
   - ✅ `TOXIC_CONTENT` event type eklendi
   - ✅ `nsfw_or_toxic` flag → RiskScore +2
   - ✅ `low_quality` flag → RiskScore +1

---

## 🧪 Test Senaryoları

### 1. PRODUCTION Quest Scoring

**Adımlar:**
1. PRODUCTION kategorisinde bir quest tamamla
2. Proof gönder (text)
3. AI Scoring çağrılmalı

**Beklenen:**
- ✅ OpenAI API çağrısı yapılır
- ✅ Score (0-100) döner
- ✅ Flags ve tags döner
- ✅ `user_quest.final_score` güncellenir

**Test:**
```python
# Quest completion
POST /api/v1/telegram/quests/submit
{
  "quest_uuid": "...",
  "proof_type": "text",
  "proof_payload_ref": "Test içerik - viral hook örneği"
}
```

### 2. RESEARCH Quest Scoring

**Adımlar:**
1. RESEARCH kategorisinde bir quest tamamla
2. Proof gönder
3. AI Scoring çağrılmalı

**Beklenen:**
- ✅ OpenAI API çağrısı yapılır
- ✅ Score döner

### 3. MODERATION Quest (Basic Scoring)

**Adımlar:**
1. MODERATION kategorisinde bir quest tamamla
2. Proof gönder

**Beklenen:**
- ✅ OpenAI API çağrısı **YAPILMAZ**
- ✅ Basic scoring (uzunluk kontrolü)
- ✅ Default score: 70.0

### 4. Toxic Content Flag

**Adımlar:**
1. NSFW/toxic içerikli proof gönder
2. AI Scoring `nsfw_or_toxic` flag döner

**Beklenen:**
- ✅ `TOXIC_CONTENT` event oluşur
- ✅ RiskScore +2
- ✅ CP +10 (Justice modülü)

### 5. Low Quality Flag

**Adımlar:**
1. Çok kısa/boş proof gönder
2. AI Scoring `low_quality` flag döner
3. Score < 40

**Beklenen:**
- ✅ `LOW_QUALITY_BURST` event oluşur
- ✅ RiskScore +1

---

## 🔧 Configuration

**Environment Variables:**
```bash
OPENAI_API_KEY=sk-...  # OpenAI API key
OPENAI_MODEL=gpt-4o-mini  # Model name (default: gpt-4o-mini)
```

**Test için:**
```bash
# .env dosyasına ekle
OPENAI_API_KEY=sk-test-...
```

---

## ⚠️ Bilinen Limitler

1. **Proof Payload Çözme:**
   - Şu an `proof_payload_ref` direkt kullanılıyor
   - Gerçekte S3/DB'den payload çözülmeli
   - TODO: Proof storage service

2. **Image/Link Scoring:**
   - Şu an sadece text scoring var
   - Image ve link için özel prompt gerekli
   - TODO: Multi-modal scoring

3. **Cost Optimization:**
   - Her PRODUCTION/RESEARCH quest için API çağrısı
   - Batch scoring veya caching gerekebilir
   - TODO: Scoring cache layer

---

## ✅ QA Checklist

- [ ] PRODUCTION quest scoring çalışıyor
- [ ] RESEARCH quest scoring çalışıyor
- [ ] MODERATION quest basic scoring çalışıyor
- [ ] Toxic content flag → AbuseGuard entegrasyonu
- [ ] Low quality flag → AbuseGuard entegrasyonu
- [ ] Score 70+ → Marketplace'e gönderim
- [ ] Score < 40 → HITL queue
- [ ] Fallback scoring çalışıyor (OpenAI başarısız olursa)

---

*AI Scoring Service V1 - Hazır ve çalışıyor*

