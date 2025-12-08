# 🚀 Hızlı Test Rehberi

## Sistem Durumu

✅ **Backend:** `http://localhost:8000` (Uvicorn çalışıyor)  
✅ **Frontend:** `http://localhost:3000` (Next.js çalışıyor)

---

## 🔍 Hızlı Kontroller

### 1. Backend API Test

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Marketplace items
curl 'http://localhost:8000/api/v1/marketplace/items?limit=5&status=active'

# Agency assets
curl 'http://localhost:8000/api/v1/agency/assets/viral?limit=5'

# Aurora stats
curl 'http://localhost:8000/api/v1/admin/aurora/stats'
```

### 2. Frontend Sayfaları

Tarayıcıda aç:
- `http://localhost:3000` → Landing page
- `http://localhost:3000/marketplace` → Marketplace
- `http://localhost:3000/agency` → Agency
- `http://localhost:3000/admin/aurora/ombudsman` → Ombudsman Dashboard
- `http://localhost:3000/admin/aurora/ombudsman/stats` → Justice Stats

### 3. API Docs

- `http://localhost:8000/docs` → Swagger UI
- `http://localhost:8000/redoc` → ReDoc

---

## 🧪 Test Senaryoları

### Senaryo 1: Marketplace Listesi
1. Tarayıcıda `/marketplace` sayfasını aç
2. Ürün listesi görünüyor mu?
3. Satın alma butonu çalışıyor mu?

### Senaryo 2: Agency Panel
1. Tarayıcıda `/agency` sayfasını aç
2. Viral assets görünüyor mu?
3. Filtreler çalışıyor mu?

### Senaryo 3: Ombudsman Dashboard
1. Tarayıcıda `/admin/aurora/ombudsman` sayfasını aç
2. Queue monitor görünüyor mu?
3. Stats linki çalışıyor mu?

---

## 🐛 Sorun Giderme

### Backend çalışmıyor
```bash
# Port kontrolü
lsof -ti:8000

# Yeniden başlat
cd /Users/onur/code/DeltaNova_System/NovaCore
source .venv/bin/activate
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend çalışmıyor
```bash
# Port kontrolü
lsof -ti:3000

# Yeniden başlat
cd /Users/onur/code/DeltaNova_System/NovaCore/apps/citizen-portal
npm run dev
```

### Database bağlantı sorunu
```bash
# PostgreSQL çalışıyor mu?
pg_isready

# Docker Compose ile başlat
docker-compose up -d
```

---

**Test sonuçlarını `TEST_CHECKLIST.md` dosyasına kaydet.**

