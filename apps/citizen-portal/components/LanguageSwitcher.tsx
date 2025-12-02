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
    // Replace the locale in the pathname
    const segments = pathname.split('/')
    if (segments[1] && locales.includes(segments[1] as Locale)) {
      segments[1] = newLocale
    } else {
      segments.splice(1, 0, newLocale)
    }
    router.push(segments.join('/'))
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

