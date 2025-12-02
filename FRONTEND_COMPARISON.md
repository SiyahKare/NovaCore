# Frontend Uygulamaları Karşılaştırması

## İki Farklı Frontend Var

### 1️⃣ `frontend/` - Eski Demo (Port 3000)

**Konum:** `/frontend/`  
**Teknoloji:** Vite + React + TypeScript  
**Amaç:** Aurora Justice Stack demo ve test arayüzü

**Özellikler:**
- Aurora Case View (Ombudsman görünümü)
- Aurora Stats Panel
- Regime Badge/Banner
- Enforcement Error Modal
- FlirtMarket entegrasyon örneği

**Kullanım:**
```bash
cd frontend
npm run dev  # Port 3000
```

**Durum:** Legacy - Yeni geliştirmeler için kullanılmıyor

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

## Gelecek Planı

`frontend/` dizini **migrate edilecek**:
- Component'ler → `packages/aurora-ui`
- Hooks → `packages/aurora-hooks`
- App → `apps/citizen-portal` veya `apps/admin-panel`

**Öneri:** Yeni geliştirmeler için sadece `apps/citizen-portal/` kullan.

---

## Hızlı Başlatma

```bash
# Eski demo (port 3000)
cd frontend && npm run dev

# Yeni portal (port 3001)
cd apps/citizen-portal && npm run dev
```

Her ikisi de aynı API'ye bağlanıyor: `http://localhost:8000/api/v1`

