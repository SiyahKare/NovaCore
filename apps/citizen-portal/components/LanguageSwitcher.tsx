'use client'

import { useLocale } from 'next-intl'
import { usePathname, useRouter } from '@/navigation'
import { locales, type Locale } from '@/i18n'

const localeNames: Record<Locale, string> = {
  tr: 'Türkçe',
  en: 'English',
  ru: 'Русский',
}

export function LanguageSwitcher() {
  const locale = useLocale() as Locale
  const router = useRouter()
  const pathname = usePathname()

  const switchLocale = (newLocale: Locale) => {
    // usePathname() from next-intl returns locale-aware pathname (e.g., '/ru/academy')
    // We need to extract the path without locale and rebuild with new locale
    let pathWithoutLocale = pathname
    
    // Remove current locale prefix
    if (pathname.startsWith(`/${locale}/`)) {
      pathWithoutLocale = pathname.slice(`/${locale}/`.length)
    } else if (pathname === `/${locale}` || pathname === `/${locale}/`) {
      pathWithoutLocale = '/'
    } else if (pathname.startsWith(`/${locale}`)) {
      pathWithoutLocale = pathname.slice(`/${locale}`.length)
    }
    
    // Build new absolute path with new locale
    const newPath = pathWithoutLocale === '/' 
      ? `/${newLocale}` 
      : `/${newLocale}${pathWithoutLocale.startsWith('/') ? '' : '/'}${pathWithoutLocale}`
    
    router.push(newPath)
  }

  return (
    <div className="flex items-center gap-2">
      {locales.map((loc) => (
        <button
          key={loc}
          onClick={() => switchLocale(loc)}
          className={`px-3 py-1 rounded text-sm transition-colors ${
            locale === loc
              ? 'bg-blue-600 text-white'
              : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
          }`}
        >
          {localeNames[loc]}
        </button>
      ))}
    </div>
  )
}

