# 🧪 Sistem Test Checklist

**Tarih:** 2025-01-XX  
**Durum:** Test ediliyor

---

## ✅ Backend Kontrolleri

### 1. Backend Başlatma
- [x] Uvicorn çalışıyor mu? (`ps aux | grep uvicorn`)
- [ ] Health endpoint çalışıyor mu? (`/api/v1/health`)
- [ ] API docs erişilebilir mi? (`http://localhost:8000/docs`)

### 2. Marketplace API
- [ ] `/api/v1/marketplace/items` → Liste dönüyor mu?
- [ ] `/api/v1/marketplace/items/{id}` → Item detayı dönüyor mu?
- [ ] `/api/v1/marketplace/my-items` → Creator items dönüyor mu?
- [ ] `/api/v1/marketplace/my-sales` → Sales stats dönüyor mu?

### 3. Agency API
- [ ] `/api/v1/agency/assets/viral` → Viral assets dönüyor mu?
- [ ] `/api/v1/agency/assets/{id}/use` → Asset kullanımı çalışıyor mu?

### 4. Quest API
- [ ] `/api/v1/telegram/quests/today` → Quest'ler dönüyor mu?
- [ ] `/api/v1/telegram/quests/submit` → Quest submission çalışıyor mu?
- [ ] `/api/v1/telegram/quests/active` → Aktif quest'ler dönüyor mu?

### 5. Justice API
- [ ] `/api/v1/admin/aurora/stats` → Stats dönüyor mu?
- [ ] `/api/v1/justice/cp/me` → CP state dönüyor mu?
- [ ] `/api/v1/nova-score/me` → NovaScore dönüyor mu?

---

## ✅ Frontend Kontrolleri

### 1. Citizen Portal Başlatma
- [ ] Next.js dev server çalışıyor mu? (`ps aux | grep next`)
- [ ] `http://localhost:3000` erişilebilir mi?
- [ ] Sayfalar yükleniyor mu?

### 2. Marketplace Sayfaları
- [ ] `/marketplace` → Liste görünüyor mu?
- [ ] `/marketplace/my-items` → Creator items görünüyor mu?
- [ ] Satın alma butonu çalışıyor mu?

### 3. Agency Sayfası
- [ ] `/agency` → Viral assets görünüyor mu?
- [ ] Filtreler çalışıyor mu?
- [ ] Asset kullanımı çalışıyor mu?

### 4. Ombudsman Sayfaları
- [ ] `/admin/aurora/ombudsman` → Dashboard açılıyor mu?
- [ ] `/admin/aurora/ombudsman/stats` → Stats görünüyor mu?
- [ ] `/admin/aurora/ombudsman/case/[userId]` → Case file görünüyor mu?

---

## 🔄 Tam Döngü Testleri

### Senaryo 1: Quest → Marketplace
1. [ ] Quest oluştur (`/api/v1/telegram/quests/today`)
2. [ ] Quest proof gönder (`/api/v1/telegram/quests/submit`)
3. [ ] AI Score 70+ kontrolü
4. [ ] MarketplaceItem oluştu mu?
5. [ ] `/marketplace` sayfasında görünüyor mu?

### Senaryo 2: Marketplace Purchase
1. [ ] Buyer user oluştur
2. [ ] NCR yükle (manual)
3. [ ] Marketplace'ten item satın al
4. [ ] NCR transferleri doğru mu? (buyer -100, creator +70, treasury +30)
5. [ ] Content delivery çalışıyor mu?

### Senaryo 3: Agency Integration
1. [ ] High-quality quest tamamla (AI Score 90+)
2. [ ] CreatorAsset oluştu mu?
3. [ ] `/agency` sayfasında görünüyor mu?
4. [ ] Asset kullanımı çalışıyor mu?

---

## 🐛 Bilinen Sorunlar

- [ ] Backend başlatma sorunları var mı?
- [ ] Frontend başlatma sorunları var mı?
- [ ] API endpoint'leri çalışıyor mu?
- [ ] Database bağlantısı var mı?

---

## 📝 Test Sonuçları

**Backend:**
- Status: ⏳ Test ediliyor
- Port: 8000
- Health: ⏳ Kontrol ediliyor

**Frontend:**
- Status: ⏳ Test ediliyor
- Port: 3000
- Erişim: ⏳ Kontrol ediliyor

---

**Test tamamlandığında bu checklist'i doldur.**

