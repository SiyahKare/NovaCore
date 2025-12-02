// Root layout - redirects to locale-based layout
import { redirect } from 'next/navigation'
import { defaultLocale } from '@/i18n'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  // Redirect to default locale
  redirect(`/${defaultLocale}`)
}
