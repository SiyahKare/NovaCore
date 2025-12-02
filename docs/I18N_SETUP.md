# 🌍 Çoklu Dil Desteği (i18n) Kurulumu

## ✅ Tamamlanan İşlemler

### 1. API Hatası Düzeltildi
- ✅ `EmailLoginRequest` ve `EmailRegisterRequest` schemas eklendi
- ✅ `IdentityService`'e `register_email` ve `login_email` metodları eklendi
- ✅ Password hashing (bcrypt) implementasyonu tamamlandı

### 2. i18n Altyapısı Kuruldu
- ✅ `next-intl` paketi eklendi
- ✅ 3 dil desteği: **Türkçe (tr)**, **İngilizce (en)**, **Rusça (ru)**
- ✅ Middleware yapılandırması (locale routing)
- ✅ Dil dosyaları oluşturuldu (`messages/tr.json`, `messages/en.json`, `messages/ru.json`)
- ✅ `LanguageSwitcher` bileşeni eklendi
- ✅ Navigation helper'ları oluşturuldu

## 📁 Yeni Dosyalar

```
apps/citizen-portal/
├── i18n.ts                    # i18n yapılandırması
├── middleware.ts              # Locale routing middleware
├── navigation.ts              # Locale-aware navigation helpers
├── messages/
│   ├── tr.json                # Türkçe çeviriler
│   ├── en.json                # İngilizce çeviriler
│   └── ru.json                # Rusça çeviriler
├── app/
│   ├── [locale]/              # Locale-based routing
│   │   ├── layout.tsx         # Locale layout
│   │   ├── page.tsx           # Home page (redirects to dashboard)
│   │   └── dashboard/         # Dashboard (örnek)
│   └── layout.tsx             # Root layout (redirects to default locale)
└── components/
    └── LanguageSwitcher.tsx   # Dil değiştirme bileşeni
```

## 🚀 Kullanım

### 1. Paket Kurulumu

```bash
cd apps/citizen-portal
npm install
```

### 2. Geliştirme

```bash
npm run dev
```

URL'ler:
- http://localhost:3000/tr (Türkçe - varsayılan)
- http://localhost:3000/en (English)
- http://localhost:3000/ru (Русский)

### 3. Sayfalarda Çeviri Kullanımı

```tsx
'use client'

import { useTranslations } from 'next-intl'

export default function MyPage() {
  const t = useTranslations('dashboard')
  
  return (
    <div>
      <h1>{t('title')}</h1>
      <p>{t('welcome')}</p>
    </div>
  )
}
```

### 4. Link'lerde Locale Desteği

```tsx
import { Link } from '@/navigation'

<Link href="/dashboard">Dashboard</Link>
```

## 📝 Sonraki Adımlar

### Mevcut Sayfaları Taşıma

Tüm sayfaları `app/[locale]/` altına taşımanız gerekiyor:

```bash
# Örnek komutlar
mv app/dashboard app/[locale]/dashboard
mv app/identity app/[locale]/identity
mv app/consent app/[locale]/consent
mv app/justice app/[locale]/justice
mv app/onboarding app/[locale]/onboarding
mv app/admin app/[locale]/admin
mv app/academy app/[locale]/academy
```

### Çeviri Ekleme

Yeni çeviriler için `messages/*.json` dosyalarına anahtarlar ekleyin:

```json
{
  "mySection": {
    "myKey": "Değer"
  }
}
```

Detaylı rehber için: `apps/citizen-portal/docs/I18N_MIGRATION.md`

## 🔧 Yapılandırma

### Desteklenen Diller

`apps/citizen-portal/i18n.ts` dosyasında:

```typescript
export const locales = ['tr', 'en', 'ru'] as const
export const defaultLocale: Locale = 'tr'
```

### Yeni Dil Ekleme

1. `i18n.ts`'e yeni locale ekleyin
2. `messages/[locale].json` dosyası oluşturun
3. Çevirileri ekleyin

## 📚 Kaynaklar

- [next-intl Documentation](https://next-intl-docs.vercel.app/)
- [Migration Guide](./apps/citizen-portal/docs/I18N_MIGRATION.md)

