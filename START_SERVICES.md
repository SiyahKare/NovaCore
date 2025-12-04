# 🚀 Servisleri Başlatma Rehberi

## Backend (NovaCore API)

```bash
cd /Users/onur/code/DeltaNova_System/NovaCore
source .venv/bin/activate
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Kontrol:**
```bash
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/docs
```

---

## Frontend (Citizen Portal)

```bash
cd /Users/onur/code/DeltaNova_System/NovaCore/apps/citizen-portal
npm run dev
```

**Kontrol:**
```bash
curl http://localhost:3000
```

---

## Port Kontrolü

Eğer portlar doluysa:

```bash
# Backend portunu temizle
lsof -ti:8000 | xargs kill -9

# Frontend portunu temizle
lsof -ti:3000 | xargs kill -9
```

---

## Servis Durumu

- **Backend:** `http://localhost:8000`
- **Frontend:** `http://localhost:3000`
- **API Docs:** `http://localhost:8000/docs`

---

**Her iki servis de çalıştığında sistem hazır!** ✅

