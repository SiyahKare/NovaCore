# 🧪 Marketplace QA Test Senaryoları

**Tarih:** 2025-12-04  
**Versiyon:** V1.0  
**Durum:** Ready for Testing

---

## 🎯 Test Hedefleri

1. ✅ **Quest → Marketplace Bridge** çalışıyor mu?
2. ✅ **AI Scoring** kalite filtresi aktif mi?
3. ✅ **Satın alma akışı** (NCR transfer) doğru mu?
4. ✅ **Content delivery** buyer'a ulaşıyor mu?
5. ✅ **Double purchase** koruması var mı?
6. ✅ **Telegram bot** komutları çalışıyor mu?

---

## 📋 Kritik Test Senaryoları

### Senaryo 1: Happy Path Purchase ✅

**Amaç:** Normal satın alma akışını test et

**Adımlar:**

1. **Quest Tamamla:**
   ```
   /tasks → PRODUCTION quest seç
   /complete <quest_uuid> → Kaliteli içerik gönder
   ```

2. **AI Scoring Kontrolü:**
   - Backend log'da `ai_score >= 70` görünmeli
   - `MarketplaceItem` oluşmuş mu? (DB kontrol)
   - Status: `ACTIVE` olmalı

3. **Marketplace'te Görünürlük:**
   ```
   /market → Yeni item listede görünmeli
   ```

4. **Satın Alma:**
   ```
   💳 Satın al → NCR transfer olmalı
   ```

5. **Doğrulama:**
   - Buyer wallet: NCR düştü mü?
   - Creator wallet: %70 eklendi mi?
   - Treasury: %30 eklendi mi?
   - `MarketplacePurchase` kaydı var mı?
   - Content buyer'a gönderildi mi?

**Beklenen Sonuç:** ✅ Tüm adımlar başarılı

---

### Senaryo 2: Insufficient Balance 🚫

**Amaç:** Yetersiz bakiye kontrolü

**Adımlar:**

1. **Düşük NCR'lı user:**
   - Wallet'da 0 veya çok az NCR

2. **Satın Alma Denemesi:**
   ```
   /market → Item seç → 💳 Satın al
   ```

3. **Beklenen:**
   - `InsufficientFundsError` exception
   - Telegram: "🚫 NCR bakiyen yetersiz" mesajı
   - NCR transfer olmamalı
   - `MarketplacePurchase` kaydı oluşmamalı

**Beklenen Sonuç:** ✅ Hata mesajı gösterildi, transfer olmadı

---

### Senaryo 3: Double Purchase 🔄

**Amaç:** Aynı item'i iki kere alma koruması

**Adımlar:**

1. **İlk Satın Alma:**
   ```
   /buy 12 → Başarılı
   ```

2. **İkinci Satın Alma Denemesi:**
   ```
   /buy 12 → Tekrar dene
   ```

3. **Beklenen:**
   - `AlreadyPurchasedError` exception
   - Telegram: "ℹ️ Bu ürünü zaten almışsın" mesajı
   - İkinci transfer olmamalı
   - `MarketplacePurchase` kaydı tekrar oluşmamalı

**Beklenen Sonuç:** ✅ Double purchase engellendi

---

### Senaryo 4: Item Status Changes 📦

**Amaç:** Disabled/Archived item'lerin satın alınamaması

**Adımlar:**

1. **Item Status Değiştir:**
   - DB'den bir item'ı `DISABLED` yap

2. **Marketplace Listesi:**
   ```
   /market → Disabled item görünmemeli
   ```

3. **Direkt Satın Alma Denemesi:**
   ```
   /buy <disabled_item_id> → API çağrısı
   ```

4. **Beklenen:**
   - `404 Not Found` veya `400 Bad Request`
   - "Bu ürün artık mevcut değil" mesajı
   - Transfer olmamalı

**Beklenen Sonuç:** ✅ Disabled item satın alınamadı

---

## 🔍 Detaylı Kontrol Listesi

### Backend API Testleri

- [ ] `GET /api/v1/marketplace/items` → Liste dönüyor mu?
- [ ] `GET /api/v1/marketplace/items/{id}` → Detay dönüyor mu?
- [ ] `POST /api/v1/marketplace/items/{id}/purchase` → Satın alma çalışıyor mu?
- [ ] `GET /api/v1/marketplace/my-items` → Creator items görünüyor mu?
- [ ] `GET /api/v1/marketplace/my-sales` → Sales stats doğru mu?

### Telegram Bot Testleri

- [ ] `/market` → TOP 10 item listesi gösteriliyor mu?
- [ ] `💳 Satın al` → Inline button çalışıyor mu?
- [ ] `/buy <id>` → Text komutu çalışıyor mu?
- [ ] `/my_items` → Creator items gösteriliyor mu?
- [ ] `/my_sales` → Sales stats gösteriliyor mu?

### Content Delivery Testleri

- [ ] Satın alma sonrası content gönderiliyor mu?
- [ ] Content formatı doğru mu? (JSON parse edilebiliyor mu?)
- [ ] Farklı item type'lar için format doğru mu?
- [ ] Content yoksa fallback mesajı gösteriliyor mu?

### NCR Transfer Testleri

- [ ] Buyer wallet'tan NCR düşüyor mu?
- [ ] Creator wallet'a %70 ekleniyor mu?
- [ ] Treasury'ye %30 ekleniyor mu?
- [ ] Transaction kayıtları doğru mu?

### AI Scoring Testleri

- [ ] PRODUCTION quest → AI scoring çalışıyor mu?
- [ ] RESEARCH quest → AI scoring çalışıyor mu?
- [ ] MODERATION quest → Auto-pass (70) çalışıyor mu?
- [ ] Score < 40 → AbuseGuard'a sinyal gidiyor mu?
- [ ] Score >= 70 → Marketplace'e gönderiliyor mu?

---

## 🐛 Bilinen Sorunlar / Edge Cases

### 1. Content Delivery Format

**Sorun:** `format_content_for_delivery()` farklı item type'lar için format belirsiz

**Çözüm:** Item type'a göre format belirle:
- `VIRAL_HOOK` → Plain text listesi
- `CAPTION_PACK` → JSON array → numaralı liste
- `HASHTAG_SET` → Comma-separated → hashtag formatı

### 2. Telegram Bot Import Hatası

**Sorun:** `from app.marketplace.delivery import format_content_for_delivery` bot içinde çalışmayabilir

**Çözüm:** Delivery logic'i bot handler içine taşı veya API response'a formatted content ekle

### 3. Double Purchase Check

**Sorun:** Şu an idempotent mi kontrol et

**Çözüm:** `MarketplaceService.purchase_item()` içinde `already_purchased` kontrolü ekle

---

## 📊 Test Metrikleri

### Başarı Kriterleri

- ✅ Quest → Marketplace bridge: %100 başarı
- ✅ AI Scoring: %95+ doğruluk
- ✅ Satın alma akışı: %100 başarı
- ✅ Content delivery: %100 başarı
- ✅ Double purchase koruması: %100 başarı

### Performans Hedefleri

- API response time: < 500ms
- Telegram bot response: < 2s
- Content delivery: < 1s

---

## 🚀 Test Sonrası Checklist

- [ ] Tüm kritik senaryolar test edildi
- [ ] Edge case'ler kontrol edildi
- [ ] Performance metrikleri ölçüldü
- [ ] Hata mesajları kullanıcı dostu mu?
- [ ] Log'lar yeterli mi?
- [ ] Database transaction'ları doğru mu?

---

## 📝 Test Raporu Şablonu

```markdown
### Test Tarihi: YYYY-MM-DD
### Test Eden: [İsim]

#### Senaryo 1: Happy Path Purchase
- [ ] Başarılı / [ ] Başarısız
- Notlar: ...

#### Senaryo 2: Insufficient Balance
- [ ] Başarılı / [ ] Başarısız
- Notlar: ...

#### Senaryo 3: Double Purchase
- [ ] Başarılı / [ ] Başarısız
- Notlar: ...

#### Senaryo 4: Item Status Changes
- [ ] Başarılı / [ ] Başarısız
- Notlar: ...

#### Genel Notlar:
...
```

---

**Son Güncelleme:** 2025-12-04  
**Test Durumu:** Ready for QA
