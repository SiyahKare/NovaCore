# 🏪 Marketplace Core - SiyahKare Viral Market

**Baron'un Devlet Ajandası - Aşama 2**

**19 Satılabilir Dijital Asset**

---

## 🎯 Ne Yapıyor?

Basit gerçek:

- **Input:** Citizen Quest Engine'den çıkan *yüksek kaliteli görevler* (AI ≥ 70)
- **Storage:** Bunları "satılabilir asset" olarak kaydediyor
- **Output:** KOBİ / creator gelip **NCR ile satın alıyor**
- **Split:** %70 vatandaşa, %30 Treasury

---

## 📦 Ürün Kataloğu V1 (19 Ürün)

### En Çok Satacak İlk 5 (Türkiye Pazarı)

1. **Viral Hook** (1.5-3.0 NCR) - 3-12 kelimelik çarpıcı giriş cümlesi
2. **Hashtag Set** (2.0-4.0 NCR) - 15-25 tane hashtag
3. **Caption Pack** (3.0-5.0 NCR) - 5'li hazır yazı paketi
4. **TikTok Trend Report** (6.0-12.0 NCR) - Günlük trend raporu
5. **Local Niche Pack** (8.0-15.0 NCR) - Şehir bazlı içerik paketi

### Kategoriler

**A) HOOK & CONTENT PACKS (8 ürün)**
- Viral Hook, Short Script, Caption Pack, Story Pack
- SEO Video Description, Keyword Cluster Pack
- Hashtag Set, TikTok Trend Report

**B) VISUAL / PROMPT VARLIKLARI (3 ürün)**
- Premium Prompt Pack, Reels Thumbnail Prompt
- Storyboard Mini

**C) RESEARCH-LEVEL ASSETS (4 ürün)**
- Competitor Research, Trend Opportunity Report
- Nano-Industry Report, Local Niche Pack

**D) MODERATION & TRUST (3 ürün)**
- Toxic Comment Cleaner, Spam Detection Report
- Shadowban Risk Check

**E) COMMUNITY & RITUAL (1 ürün)**
- Social Value Pack

**Detaylı katalog:** `app/marketplace/catalog.py` ve `catalog_v1.json`

---

## 💰 Fiyatlandırma Politikası V1

**Dinamik Fiyatlandırma:**
```python
price = min_price + (max_price - min_price) * ((ai_score - 70) / 30)
```

**AI Score Etkisi:**
- AI Score 70 → min_price
- AI Score 100 → max_price
- Linear interpolation

**Quest Ödülü Etkisi:**
- Base quest reward × 0.1 (max %20 etki)
- Yüksek kaliteli quest'ler daha pahalı

**Örnek:**
```
Viral Hook:
- AI Score 70 → 1.5 NCR
- AI Score 85 → 2.25 NCR
- AI Score 100 → 3.0 NCR
```

---

## 📊 Data Model

### MarketplaceItem

```python
- id: int
- creator_id: int (NovaCore user_id)
- source_quest_id: int (UserQuest.id referansı)
- title: str
- description: str
- item_type: str (hook, caption_pack, script, prompt, research_pack, other)
- price_ncr: float
- ai_score: float (0-100)
- status: str (draft, active, disabled, archived)
- revenue_share_creator: float (0.70 = %70)
- revenue_share_treasury: float (0.30 = %30)
- purchase_count: int
- total_revenue_ncr: float
```

### MarketplacePurchase

```python
- id: int
- item_id: int
- buyer_id: int
- creator_id: int (cache)
- price_ncr: float
- creator_share_ncr: float
- treasury_share_ncr: float
```

---

## 🔄 Akış

```
1. Vatandaş Quest tamamlar
   ↓
2. AI Score 70+ → Marketplace Bridge
   ↓
3. MarketplaceItem oluştur (status=ACTIVE)
   ↓
4. KOBİ / Creator satın alır
   ↓
5. NCR Transfer:
   - Buyer'dan çıkar (SPEND)
   - Creator'a ver (EARN) - %70
   - Treasury'ye ver (EARN) - %30
   ↓
6. MarketplacePurchase kaydı oluştur
```

---

## 🌐 API Endpoints

### `GET /api/v1/marketplace/items`

**Açıklama:** Marketplace item'lerini listele

**Query Parameters:**
- `item_type`: Filtreleme için item tipi
- `limit`: Sayfa boyutu (default: 20)
- `offset`: Sayfa offset'i (default: 0)
- `status`: Durum filtresi (default: active)

**Response:**
```json
[
  {
    "id": 1,
    "title": "Viral Hook Pack",
    "description": "...",
    "item_type": "hook",
    "price_ncr": 30.0,
    "ai_score": 85.0,
    "creator_id": 123,
    "purchase_count": 5,
    "total_revenue_ncr": 150.0
  }
]
```

---

### `GET /api/v1/marketplace/items/{item_id}`

**Açıklama:** Tek bir marketplace item detayını getir

**Response:**
```json
{
  "id": 1,
  "title": "Viral Hook Pack",
  "description": "...",
  "item_type": "hook",
  "price_ncr": 30.0,
  "ai_score": 85.0,
  "preview_text": "...",
  "creator_id": 123,
  "purchase_count": 5,
  "total_revenue_ncr": 150.0
}
```

---

### `POST /api/v1/marketplace/items/{item_id}/purchase`

**Açıklama:** Marketplace item satın al

**Auth:** Required (JWT)

**Response:**
```json
{
  "id": 1,
  "item_id": 1,
  "buyer_id": 456,
  "creator_id": 123,
  "price_ncr": 30.0,
  "creator_share_ncr": 21.0,
  "treasury_share_ncr": 9.0,
  "created_at": "2025-01-15T10:00:00Z"
}
```

---

### `GET /api/v1/marketplace/my-items`

**Açıklama:** Giriş yapan kullanıcının marketplace item'lerini getir

**Auth:** Required (JWT)

**Query Parameters:**
- `limit`: Sayfa boyutu (default: 20)
- `offset`: Sayfa offset'i (default: 0)

---

### `GET /api/v1/marketplace/my-sales`

**Açıklama:** Satış istatistiklerimi getir

**Auth:** Required (JWT)

**Response:**
```json
{
  "creator_id": 123,
  "total_sales": 10,
  "total_revenue_ncr": 210.0,
  "purchases": [...]
}
```

---

## 🔗 Quest → Marketplace Bridge

**Dosya:** `app/quests/marketplace_bridge.py`

**Fonksiyon:** `check_and_send_to_marketplace()`

**Koşullar:**
1. Quest kategorisi PRODUCTION veya RESEARCH
2. AI Score ≥ 70

**Fiyatlama:**
```python
base_price = (quest.final_reward_ncr or quest.base_reward_ncr) * 3.0
```

**Item Tipi:**
- `hook` → MarketplaceItemType.HOOK
- `caption` → MarketplaceItemType.CAPTION_PACK
- `script` → MarketplaceItemType.SCRIPT
- `prompt` → MarketplaceItemType.PROMPT
- `research` → MarketplaceItemType.RESEARCH_PACK
- Diğer → MarketplaceItemType.OTHER

---

## 💰 Revenue Share

**Varsayılan:**
- Creator: %70
- Treasury: %30

**Örnek:**
```
Item fiyatı: 30 NCR
Creator payı: 21 NCR (70%)
Treasury payı: 9 NCR (30%)
```

---

## 📈 İstatistikler

Her MarketplaceItem'de:
- `purchase_count`: Toplam satış sayısı
- `total_revenue_ncr`: Toplam gelir (NCR)

Her satışta bu değerler otomatik güncellenir.

---

## 🚀 Sonraki Adımlar

### 1. Telegram Bot Komutları ⏳
- `/market` → TOP 10 item listesi
- `/buy <id>` → API purchase call

### 2. Aurora Contact Dashboard ⏳
- `GET /marketplace/items?item_type=hook` → KOBİ'ye hazır paket göster

### 3. Creator Dashboard ⏳
- `/my_items` → Vatandaşın marketplace'e düşen asset'leri
- `/my_sales` → Kazandığı NCR breakdown

### 4. Dynamic Pricing ⏳
- AI Score'a göre fiyat ayarlama
- Popülerlik bazlı fiyat artışı

---

## ✅ Tamamlanan Özellikler

- ✅ MarketplaceItem & MarketplacePurchase modelleri
- ✅ MarketplaceService (list, get, create_from_quest, purchase)
- ✅ Quest → Marketplace Bridge (otomatik gönderim)
- ✅ API Router (5 endpoint)
- ✅ Revenue share (%70 creator, %30 treasury)
- ✅ NCR transfer entegrasyonu
- ✅ İstatistik takibi (purchase_count, total_revenue)

---

*Marketplace Core v1.0 - Gerçek ekonomi döngüsü başladı*

