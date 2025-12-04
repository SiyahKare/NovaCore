# 🧪 Marketplace Uçtan Uca Test Planı

**"Vatandaş çalışır → ürün olur → KOBİ alır → hazine dolar"**

---

## 📋 Test Senaryoları

### Senaryo 1: Vatandaş İçerik Üretip Vitrinde Görünür

**Amaç:** Quest → Marketplace köprüsünün çalıştığını doğrula.

**Adımlar:**

1. **Citizen User Oluştur**
   ```sql
   -- DB'de test user oluştur
   INSERT INTO users (telegram_id, username) VALUES (123456, 'test_citizen');
   ```

2. **Quest Oluştur ve Tamamla**
   ```
   Telegram: /görevler
   → PRODUCTION/RESEARCH kategorisinde bir quest seç
   → Örn: "daily_micro_content" veya "micro_value_action"
   ```

3. **Kaliteli Proof Gönder**
   ```
   Telegram: "Bugün kuaför salonum için 5 viral hook yazdım:
   1. 'Bu saç kesimi seni 10 yaş genç gösterecek'
   2. 'Müşterilerim bana neden bu kadar güveniyor?'
   3. '3 dakikada saç rengini değiştiren teknik'
   4. 'Yıllarca yanlış yaptığımız şey'
   5. 'Müşteri memnuniyeti %100 nasıl olur?'"
   ```

4. **Backend Kontrolleri**
   ```python
   # app/quests/completion.py sonrası kontrol
   - UserQuest.final_score >= 70? ✅
   - QuestProof.content kaydedildi mi? ✅
   - MarketplaceItem oluştu mu? ✅
   - MarketplaceItem.status == "active"? ✅
   - MarketplaceItem.content == QuestProof.content? ✅
   ```

5. **Telegram Market Kontrolü**
   ```
   Telegram: /market
   → Ürün listesinde gözüküyor mu? ✅
   → Preview text doğru mu? ✅
   → Fiyat mantıklı mı? ✅
   ```

**Beklenen Sonuç:**
- Quest tamamlandı
- AI Score 70+
- MarketplaceItem oluşturuldu (status=ACTIVE)
- `/market` komutunda görünüyor

---

### Senaryo 2: KOBİ / Buyer Satın Alma

**Amaç:** Purchase flow'unun çalıştığını ve revenue share'in doğru dağıtıldığını doğrula.

**Adımlar:**

1. **Buyer User Oluştur ve NCR Yükle**
   ```sql
   -- DB'de buyer user oluştur
   INSERT INTO users (telegram_id, username) VALUES (789012, 'test_buyer');
   
   -- NCR yükle (manual top-up)
   INSERT INTO wallet_ledger (user_id, amount, token, type, source_app)
   VALUES (789012, 100.0, 'NCR', 'EARN', 'admin_topup');
   ```

2. **Marketplace'ten Satın Al**
   ```
   Telegram (buyer hesabından): /market
   → TOP item'lerden birine "💳 Satın al" tıkla
   ```

3. **Backend Kontrolleri**
   ```python
   # app/marketplace/service.py::purchase_item() sonrası
   - Buyer balance düştü mü? ✅
   - Creator balance arttı mı? (%70) ✅
   - Treasury balance arttı mı? (%30) ✅
   - MarketplacePurchase kaydı oluştu mu? ✅
   - MarketplaceItem.purchase_count arttı mı? ✅
   - MarketplaceItem.total_revenue_ncr arttı mı? ✅
   ```

4. **Content Delivery Kontrolü**
   ```
   Telegram: Satın alma sonrası content gönderildi mi? ✅
   - Hook Pack ise → Liste formatında
   - Caption Pack ise → Numaralı liste
   - Script ise → Formatlanmış script
   ```

**Beklenen Sonuç:**
- Purchase başarılı
- NCR transferleri doğru (buyer -100, creator +70, treasury +30)
- Content buyer'a gönderildi
- İstatistikler güncellendi

---

### Senaryo 3: Double Purchase Koruması

**Amaç:** Aynı item'i 2 kez satın almayı engelle.

**Adımlar:**

1. **İlk Purchase**
   ```
   Telegram: /market → Item satın al
   → Başarılı ✅
   ```

2. **İkinci Purchase Denemesi**
   ```
   Telegram: Aynı item'e tekrar "💳 Satın al" tıkla
   → "ℹ️ Bu ürünü zaten daha önce almışsın" mesajı ✅
   ```

3. **Backend Kontrolü**
   ```python
   # Duplicate purchase kontrolü
   - AlreadyPurchasedError raise edildi mi? ✅
   - İkinci purchase kaydı oluşmadı mı? ✅
   - NCR transferi tekrar yapılmadı mı? ✅
   ```

**Beklenen Sonuç:**
- İdempotent behavior
- Hata mesajı gösterildi
- Duplicate purchase engellendi

---

### Senaryo 4: Yetersiz Bakiye

**Amaç:** Yetersiz bakiye durumunu handle et.

**Adımlar:**

1. **Düşük Bakiye**
   ```sql
   -- Buyer'a sadece 5 NCR yükle
   INSERT INTO wallet_ledger (user_id, amount, token, type, source_app)
   VALUES (789012, 5.0, 'NCR', 'EARN', 'admin_topup');
   ```

2. **Pahalı Item Satın Alma Denemesi**
   ```
   Telegram: /market → 50 NCR'lık item'e "💳 Satın al" tıkla
   → "🚫 NCR bakiyen yetersiz" mesajı ✅
   ```

3. **Backend Kontrolü**
   ```python
   # InsufficientFundsError raise edildi mi? ✅
   - Purchase kaydı oluşmadı mı? ✅
   - NCR transferi yapılmadı mı? ✅
   ```

**Beklenen Sonuç:**
- Hata mesajı gösterildi
- Purchase engellendi
- Bakiye değişmedi

---

## 🔍 Test Komutları

### Backend Test (Python)

```python
# Test 1: Quest → Marketplace Bridge
from app.quests.completion import submit_quest_proof
from app.quests.models import UserQuest
from sqlmodel import select

# Quest'i bul
stmt = select(UserQuest).where(UserQuest.user_id == 123)
quest = await session.execute(stmt).scalar_one()

# Marketplace item kontrolü
from app.marketplace.models import MarketplaceItem
item_stmt = select(MarketplaceItem).where(
    MarketplaceItem.source_quest_id == quest.id
)
item = await session.execute(item_stmt).scalar_one()

assert item.status == "active"
assert item.ai_score >= 70
assert item.content is not None
```

### Telegram Bot Test

```bash
# Test 1: Quest oluştur
curl -X GET "http://localhost:8000/api/v1/telegram/quests/today?telegram_user_id=123456"

# Test 2: Quest submit
curl -X POST "http://localhost:8000/api/v1/telegram/quests/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "quest_uuid": "abc-123",
    "proof_type": "text",
    "proof_payload_ref": "test_ref",
    "proof_content": "Test content",
    "source": "telegram",
    "message_id": "123"
  }'

# Test 3: Marketplace list
curl -X GET "http://localhost:8000/api/v1/marketplace/items?telegram_user_id=123456&status=active"

# Test 4: Purchase
curl -X POST "http://localhost:8000/api/v1/marketplace/items/1/purchase?telegram_user_id=789012"
```

---

## ✅ Test Checklist

- [ ] Senaryo 1: Quest → Marketplace köprüsü çalışıyor
- [ ] Senaryo 2: Purchase flow çalışıyor
- [ ] Senaryo 2: Revenue share doğru dağıtılıyor (%70 creator, %30 treasury)
- [ ] Senaryo 2: Content delivery çalışıyor
- [ ] Senaryo 3: Double purchase koruması çalışıyor
- [ ] Senaryo 4: Yetersiz bakiye kontrolü çalışıyor
- [ ] MarketplaceItem istatistikleri güncelleniyor
- [ ] Telegram bot mesajları doğru gösteriliyor

---

## 🐛 Bilinen Sorunlar / Eksikler

1. **Content Delivery Formatı**
   - Şu an basit text formatı
   - İleride JSON schema validation eklenebilir

2. **Purchase Notification**
   - Creator'a satış bildirimi yok (ileride eklenebilir)

3. **Refund Sistemi**
   - Şu an yok, admin panelden manuel iade gerekli

---

**Test tamamlandığında bu checklist'i doldur ve sonuçları dokümante et.**

