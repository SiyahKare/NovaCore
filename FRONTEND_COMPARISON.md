# Frontend Uygulamaları Karşılaştırması

## İki Farklı Frontend Var

### 1️⃣ `frontend/` - ⚠️ DEPRECATED

**Konum:** `/frontend/`  
**Durum:** **Kaldırıldı** - Tüm özellikler `apps/citizen-portal`'a taşındı

**Migration:** Tüm Justice Stack component'leri ve sayfaları `apps/citizen-portal/app/admin/aurora/ombudsman/` altına taşındı.

**Detaylar:** `docs/FRONTEND_MIGRATION.md` dosyasına bakın.

---

### 2️⃣ `apps/citizen-portal/` - Yeni Portal (Port 3001)

**Konum:** `/apps/citizen-portal/`  
**Teknoloji:** Next.js 14 (App Router) + TypeScript  
**Amaç:** Production-ready vatandaş portalı

**Özellikler:**
- Landing page (marketing)
- Onboarding wizard (3 adım)
- Dashboard (NovaScore, CP, Regime)
- Consent management
- Justice status
- Identity management

**Kullanım:**
```bash
cd apps/citizen-portal
npm run dev  # Port 3001 (veya 3000 boşsa)
```

**Durum:** Aktif geliştirme - Yeni özellikler buraya ekleniyor

---

## Farklar

| Özellik | `frontend/` | `apps/citizen-portal/` |
|---------|-------------|------------------------|
| **Framework** | Vite + React | Next.js 14 |
| **Routing** | React Router | Next.js App Router |
| **Build** | Vite | Next.js |
| **SSR** | ❌ | ✅ |
| **Shared Libraries** | ❌ | ✅ (@aurora/ui, @aurora/hooks) |
| **Monorepo** | ❌ | ✅ |
| **Production Ready** | ❌ (Demo) | ✅ |
| **Landing Page** | ❌ | ✅ |
| **Onboarding** | ❌ | ✅ |
| **Full Dashboard** | ❌ | ✅ |

---

## Hangi Ne Zaman Kullanılır?

### `frontend/` Kullan:
- Hızlı demo/test
- Ombudsman görünümü testi
- Stats panel testi
- Enforcement error testi

### `apps/citizen-portal/` Kullan:
- Production deployment
- Yeni özellik geliştirme
- Landing/onboarding
- Full citizen experience
- Shared component kullanımı

---

## ✅ Migration Tamamlandı

`frontend/` dizini **tamamen migrate edildi**:
- ✅ Component'ler → `packages/aurora-ui`
- ✅ Hooks → `packages/aurora-hooks`
- ✅ Justice Stack sayfaları → `apps/citizen-portal/app/admin/aurora/ombudsman/`
- ✅ Marketplace & Agency → `apps/citizen-portal/app/`

**Durum:** `frontend/` klasörü kaldırılabilir. Artık tek kaynak: **`apps/citizen-portal`**

---

## Hızlı Başlatma

```bash
# Eski demo (port 3000)
cd frontend && npm run dev

# Yeni portal (port 3001)
cd apps/citizen-portal && npm run dev
```

Her ikisi de aynı API'ye bağlanıyor: `http://localhost:8000/api/v1`

