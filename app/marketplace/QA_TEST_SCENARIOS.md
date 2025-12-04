# 🧪 Marketplace QA Test Senaryoları

**"Bu sistem gerçekten para üretir mi?" - Lokal QA Checklist**

---

## ✅ Test Senaryoları

### 1. Happy Path - Satın Alma Akışı

**Adımlar:**
1. NCR bakiyesi olan bir user ile login
2. `GET /api/v1/marketplace/items` → Item listesi getir
3. Bir item seç (örn: ID=1)
4. `POST /api/v1/marketplace/items/1/purchase` → Satın al

**Beklenen Sonuçlar:**

**Backend:**
- ✅ Buyer wallet: NCR düşer (price_ncr kadar)
- ✅ Creator wallet: %70 eklenir (price_ncr * 0.70)
- ✅ Treasury: %30 eklenir (price_ncr * 0.30)
- ✅ `MarketplacePurchase` kaydı oluşur
- ✅ Item `purchase_count` +1
- ✅ Item `total_revenue_ncr` güncellenir

**Frontend:**
- ✅ "Satın al" → Success toast gösterilir
- ✅ Item "Purchased" state'ine düşer (buton disable olur veya "Satın Alındı" yazısı)

**Test Komutları:**
```bash
# 1. Item listesi
curl -X GET "http://localhost:8000/api/v1/marketplace/items" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 2. Satın alma
curl -X POST "http://localhost:8000/api/v1/marketplace/items/1/purchase" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 2. Yetersiz Bakiye (Low NCR)

**Adımlar:**
1. Cüzdanda 0 veya çok az NCR olan user ile login
2. Item fiyatından daha az NCR'ı olan bir item seç
3. `POST /api/v1/marketplace/items/{id}/purchase` → Satın alma dene

**Beklenen Sonuçlar:**

**Backend:**
- ✅ HTTP 400 Bad Request
- ✅ Error message: "Yetersiz bakiye. Mevcut: X NCR, Gerekli: Y NCR"
- ✅ Hiçbir wallet transaction oluşmaz
- ✅ `MarketplacePurchase` kaydı oluşmaz

**Frontend:**
- ✅ Net uyarı gösterilir: "Yetersiz NCR, önce görev tamamla."
- ✅ "Satın Al" butonu disable olur (bakiye yetersizse)

**Test Komutları:**
```bash
# Bakiye kontrolü
curl -X GET "http://localhost:8000/api/v1/wallet/me" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Satın alma denemesi (yetersiz bakiye)
curl -X POST "http://localhost:8000/api/v1/marketplace/items/1/purchase" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 3. Double Purchase (Aynı Item'i İki Kere Alma)

**Adımlar:**
1. Bir item satın al
2. Aynı item'i tekrar satın alma dene

**Beklenen Sonuçlar:**

**Seçenek A: Backend Engeller (İdeal)**
- ✅ HTTP 400 Bad Request
- ✅ Error: "Bu item zaten satın alındı" veya "Duplicate purchase"
- ✅ İkinci purchase loglanmaz

**Seçenek B: İdempotent (Alternatif)**
- ✅ İkinci purchase aynı `MarketplacePurchase` kaydını döndürür
- ✅ Wallet transaction tekrar oluşmaz

**Şu An Durum:**
- ⚠️ **Double spend bug riski var** - Backend kontrolü yok
- 🔧 **TODO:** `MarketplaceService.purchase_item()` içine duplicate check ekle

**Test Komutları:**
```bash
# İlk satın alma
curl -X POST "http://localhost:8000/api/v1/marketplace/items/1/purchase" \
  -H "Authorization: Bearer YOUR_TOKEN"

# İkinci satın alma (duplicate)
curl -X POST "http://localhost:8000/api/v1/marketplace/items/1/purchase" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 4. Item Status Değişimleri

**Test Senaryoları:**

#### 4.1. ACTIVE Item Görünürlüğü

**Adımlar:**
1. `status = ACTIVE` olan item'leri listele
2. `GET /api/v1/marketplace/items?status=active`

**Beklenen:**
- ✅ Sadece ACTIVE item'ler döner
- ✅ Frontend'de görünür

#### 4.2. DISABLED Item Görünürlüğü

**Adımlar:**
1. Bir item'i `status = DISABLED` yap
2. `GET /api/v1/marketplace/items` → Listele

**Beklenen:**
- ✅ DISABLED item'ler listede görünmez **VEYA**
- ✅ Görünür ama "Satın Al" butonu disable
- ✅ `POST /purchase` reddedilir (400 Bad Request)

#### 4.3. ARCHIVED Item Görünürlüğü

**Adımlar:**
1. Bir item'i `status = ARCHIVED` yap
2. `GET /api/v1/marketplace/items` → Listele

**Beklenen:**
- ✅ ARCHIVED item'ler listede görünmez
- ✅ Purchase reddedilir

**Test Komutları:**
```bash
# ACTIVE items
curl -X GET "http://localhost:8000/api/v1/marketplace/items?status=active" \
  -H "Authorization: Bearer YOUR_TOKEN"

# DISABLED item purchase (reddedilmeli)
curl -X POST "http://localhost:8000/api/v1/marketplace/items/{disabled_id}/purchase" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🐛 Bilinen Bug'lar

### 1. Double Purchase Kontrolü Yok

**Durum:** ⚠️ Aynı user aynı item'i iki kere satın alabilir

**Çözüm:**
```python
# app/marketplace/service.py
async def purchase_item(...):
    # Duplicate check ekle
    existing_purchase = await session.execute(
        select(MarketplacePurchase).where(
            MarketplacePurchase.buyer_id == buyer_id,
            MarketplacePurchase.item_id == item_id,
        )
    )
    if existing_purchase.scalar_one_or_none():
        raise ValueError("Bu item zaten satın alındı")
```

---

## 📊 Seed Data Kontrolü

**Seed Script Çalıştırma:**
```bash
cd /Users/onur/code/DeltaNova_System/NovaCore
python -m app.marketplace.seed
```

**Beklenen:**
- ✅ 9 seed item oluşturulur
- ✅ 3 creator (Burak, Betül, Random Genç)
- ✅ AI score'lar: 75-91 arası
- ✅ Fiyatlar: 2.0-11.0 NCR arası
- ✅ Tüm item'ler ACTIVE status

**Frontend Kontrolü:**
- `/marketplace` açıldığında 9 item görünmeli
- Grid layout çalışmalı
- Item detay modal açılmalı

---

## ✅ QA Checklist

- [ ] Happy path satın alma çalışıyor
- [ ] Yetersiz bakiye kontrolü çalışıyor
- [ ] Double purchase engelleniyor (veya idempotent)
- [ ] ACTIVE item'ler görünüyor
- [ ] DISABLED item'ler görünmüyor/disable
- [ ] ARCHIVED item'ler görünmüyor
- [ ] Seed data yüklendi
- [ ] Frontend'de "Satın Al" butonu çalışıyor
- [ ] Success toast gösteriliyor
- [ ] Wallet transaction'ları doğru

---

## 🚀 Sonraki Adımlar

1. **Double Purchase Bug Fix** → `MarketplaceService.purchase_item()` duplicate check
2. **AI Scoring Test** → Gerçek quest completion ile scoring test
3. **Telegram Bot** → `/market`, `/buy` komutları
4. **Agency Panel** → Aurora Contact entegrasyonu

---

*Marketplace QA v1.0 - "Bu sistem gerçekten para üretir mi?" test senaryoları*

