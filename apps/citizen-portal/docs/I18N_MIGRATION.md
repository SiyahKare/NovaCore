# i18n Migration Guide

## ✅ Tamamlanan Adımlar

1. ✅ `next-intl` paketi eklendi
2. ✅ `i18n.ts` yapılandırma dosyası oluşturuldu
3. ✅ `middleware.ts` eklendi (locale routing için)
4. ✅ Dil dosyaları oluşturuldu (`messages/tr.json`, `messages/en.json`, `messages/ru.json`)
5. ✅ `[locale]` layout oluşturuldu
6. ✅ `LanguageSwitcher` bileşeni eklendi
7. ✅ `NovaCoreNav` güncellendi (dil değiştirici eklendi)

## 📋 Yapılması Gerekenler

### 1. Mevcut Sayfaları `[locale]` Klasörüne Taşıma

Tüm sayfaları `app/[locale]/` altına taşımanız gerekiyor:

```bash
# Örnek: Dashboard sayfası
mv app/dashboard app/[locale]/dashboard
mv app/identity app/[locale]/identity
mv app/consent app/[locale]/consent
mv app/justice app/[locale]/justice
mv app/onboarding app/[locale]/onboarding
mv app/admin app/[locale]/admin
mv app/academy app/[locale]/academy
# ... diğer sayfalar
```

### 2. Sayfalarda `useTranslations` Kullanımı

Her sayfada çevirileri kullanmak için:

```tsx
'use client'

import { useTranslations } from 'next-intl'

export default function MyPage() {
  const t = useTranslations('nav') // veya 'auth', 'dashboard', vb.
  
  return (
    <div>
      <h1>{t('dashboard')}</h1>
    </div>
  )
}
```

### 3. Link'lerde Locale Desteği

Link'lerde locale'i korumak için:

```tsx
import { useLocale } from 'next-intl'
import Link from 'next/link'

function MyComponent() {
  const locale = useLocale()
  
  return (
    <Link href={`/${locale}/dashboard`}>
      Dashboard
    </Link>
  )
}
```

Veya `next-intl`'in `Link` bileşenini kullanın:

```tsx
import { Link } from '@/navigation'

<Link href="/dashboard">Dashboard</Link>
```

### 4. Server Components'te Çeviri

Server component'lerde:

```tsx
import { getTranslations } from 'next-intl/server'

export default async function MyPage() {
  const t = await getTranslations('dashboard')
  
  return <h1>{t('title')}</h1>
}
```

## 🎯 Hızlı Başlangıç

### 1. Paket Kurulumu

```bash
cd apps/citizen-portal
npm install
```

### 2. Test

```bash
npm run dev
```

Ardından şu URL'leri test edin:
- http://localhost:3000/tr (Türkçe)
- http://localhost:3000/en (English)
- http://localhost:3000/ru (Русский)

### 3. Yeni Çeviri Ekleme

`messages/tr.json`, `messages/en.json`, `messages/ru.json` dosyalarına yeni anahtarlar ekleyin:

```json
{
  "mySection": {
    "myKey": "Değer"
  }
}
```

Kullanım:

```tsx
const t = useTranslations('mySection')
t('myKey') // "Değer"
```

## 📝 Örnek Sayfa Dönüşümü

### Önce (i18n olmadan):

```tsx
export default function DashboardPage() {
  return (
    <div>
      <h1>Kontrol Paneli</h1>
      <p>Hoş geldiniz</p>
    </div>
  )
}
```

### Sonra (i18n ile):

```tsx
'use client'

import { useTranslations } from 'next-intl'

export default function DashboardPage() {
  const t = useTranslations('dashboard')
  
  return (
    <div>
      <h1>{t('title')}</h1>
      <p>{t('welcome')}</p>
    </div>
  )
}
```

## 🔧 Sorun Giderme

### "Cannot find module '@/i18n'"

`tsconfig.json`'da path alias kontrol edin:

```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./*"]
    }
  }
}
```

### Middleware çalışmıyor

`middleware.ts` dosyasının root'ta olduğundan emin olun (`apps/citizen-portal/middleware.ts`).

### Locale değişmiyor

`LanguageSwitcher` bileşeninin doğru çalıştığından emin olun. `usePathname()` ve `useRouter()` hook'larını kullanıyor.

## 📚 Kaynaklar

- [next-intl Documentation](https://next-intl-docs.vercel.app/)
- [Next.js App Router i18n](https://next-intl-docs.vercel.app/docs/next-13/app-router)

