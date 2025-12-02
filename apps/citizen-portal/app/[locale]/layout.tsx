import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { NextIntlClientProvider } from 'next-intl'
import { getMessages } from 'next-intl/server'
import { notFound } from 'next/navigation'
import '../globals.css'
import { AuroraShell } from '@/components/AuroraShell'
import { locales } from '@/i18n'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Aurora Citizen Portal',
  description: 'Your gateway to the Aurora State Network',
}

export function generateStaticParams() {
  return locales.map((locale) => ({ locale }))
}

export default async function LocaleLayout({
  children,
  params: { locale },
}: {
  children: React.ReactNode
  params: { locale: string }
}) {
  // Validate locale
  if (!locales.includes(locale as any)) {
    notFound()
  }

  // Providing all messages to the client
  // side is the easiest way to get started
  const messages = await getMessages()

  return (
    <html lang={locale} className="dark">
      <body className={inter.className}>
        <NextIntlClientProvider messages={messages}>
          <AuroraShell>{children}</AuroraShell>
        </NextIntlClientProvider>
      </body>
    </html>
  )
}

