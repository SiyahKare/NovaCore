import { useTranslations } from 'next-intl'
import { redirect } from 'next/navigation'

export default function HomePage({
  params: { locale },
}: {
  params: { locale: string }
}) {
  // Redirect to dashboard for now
  redirect(`/${locale}/dashboard`)
}

