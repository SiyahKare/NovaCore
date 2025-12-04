# Frontend Migration - Justice Stack → Citizen Portal

**Tarih:** 2025-01-XX  
**Durum:** ✅ Tamamlandı

---

## 🎯 Migration Özeti

**`frontend/`** klasörü artık kullanılmıyor. Tüm Justice Stack component'leri ve sayfaları **`apps/citizen-portal`**'a taşındı.

---

## 📦 Taşınan Component'ler

### 1. Justice Stack Component'leri

**Eski Konum:** `frontend/src/features/justice/`  
**Yeni Konum:** `packages/aurora-ui/` (shared package)

- ✅ `AuroraCaseView` → `@aurora/ui`
- ✅ `AuroraStatsPanel` → `@aurora/ui`
- ✅ `RegimeBadge` → `@aurora/ui`
- ✅ `RegimeBanner` → `@aurora/ui`
- ✅ `EnforcementErrorModal` → `@aurora/ui`

### 2. Justice Stack Sayfaları

**Eski Konum:** `frontend/src/App.tsx` (routes)  
**Yeni Konum:** `apps/citizen-portal/app/admin/aurora/ombudsman/`

- ✅ **Stats Panel** → `/admin/aurora/ombudsman/stats`
- ✅ **Case File Viewer** → `/admin/aurora/ombudsman/case/[userId]`
- ✅ **Ombudsman Dashboard** → `/admin/aurora/ombudsman/` (zaten vardı)

---

## 🔄 Yeni Yapı

```
apps/citizen-portal/
├── app/
│   ├── admin/
│   │   └── aurora/
│   │       ├── ombudsman/
│   │       │   ├── page.tsx              # Ombudsman Dashboard
│   │       │   ├── stats/
│   │       │   │   └── page.tsx         # Justice Stats Panel
│   │       │   └── case/
│   │       │       └── [userId]/
│   │       │           └── page.tsx      # Case File Viewer
│   │       ├── stats/
│   │       │   └── page.tsx              # Full Stats (genel)
│   │       └── case/
│   │           └── [userId]/
│   │               └── page.tsx          # Case File (genel)
│   ├── marketplace/                      # Marketplace (yeni)
│   └── agency/                           # Agency (yeni)
└── ...

packages/aurora-ui/                        # Shared components
└── src/
    ├── components/
    │   ├── AuroraCaseView.tsx
    │   ├── AuroraStatsPanel.tsx
    │   ├── RegimeBadge.tsx
    │   ├── RegimeBanner.tsx
    │   └── EnforcementErrorModal.tsx
    └── ...
```

---

## 🗑️ Kaldırılan Klasör

**`frontend/`** klasörü artık kullanılmıyor ve kaldırılabilir.

**Kaldırma Adımları:**

```bash
# 1. Backup (isteğe bağlı)
cp -r frontend frontend.backup

# 2. Kaldır
rm -rf frontend/
```

---

## 📝 Kullanım Örnekleri

### Yeni Import Yöntemi

**Eski:**
```tsx
import { AuroraCaseView } from '../features/justice/AuroraCaseView'
```

**Yeni:**
```tsx
import { AuroraCaseView } from '@aurora/ui'
```

### Yeni Route'lar

**Eski:**
- `/stats` → `frontend/` içinde
- `/case/:userId` → `frontend/` içinde

**Yeni:**
- `/admin/aurora/ombudsman/stats` → Ombudsman altında stats
- `/admin/aurora/ombudsman/case/[userId]` → Ombudsman altında case
- `/admin/aurora/stats` → Genel stats (admin panel)
- `/admin/aurora/case/[userId]` → Genel case (admin panel)

---

## ✅ Migration Checklist

- [x] Component'ler `@aurora/ui` paketine taşındı
- [x] Sayfalar `apps/citizen-portal`'a eklendi
- [x] Navigation güncellendi
- [x] README güncellendi
- [x] Migration dokümantasyonu oluşturuldu
- [ ] `frontend/` klasörü kaldırıldı (manuel)

---

## 🚀 Sonraki Adımlar

1. **`frontend/` klasörünü kaldır** (artık kullanılmıyor)
2. **Eski import'ları kontrol et** (varsa güncelle)
3. **CI/CD pipeline'ları güncelle** (frontend build'i kaldır)

---

**Migration tamamlandı!** Artık tek kaynak: **`apps/citizen-portal`**

