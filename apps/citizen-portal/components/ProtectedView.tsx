'use client'

import { ReactNode } from 'react'
import { useCurrentCitizen } from '@aurora/hooks'
import Link from 'next/link'

interface ProtectedViewProps {
  children: ReactNode
  requireAdmin?: boolean
}

export function ProtectedView({ children, requireAdmin = false }: ProtectedViewProps) {
  const { citizen, loading, error, isAuthenticated } = useCurrentCitizen()

  if (loading) {
    return (
      <div className="flex justify-center py-20 text-sm text-gray-400">
        Aurora identity kontrol ediliyor...
      </div>
    )
  }

  if (error || !isAuthenticated) {
    return (
      <div className="max-w-md mx-auto py-16 text-center space-y-4">
        <h2 className="text-xl font-semibold text-gray-100">Aurora vatandaşlığı gerekli.</h2>
        <p className="text-sm text-gray-400">
          Bu alan sadece doğrulanmış Aurora vatandaşlarına açık. Önce onboarding akışını tamamlaman
          ve giriş yapman gerekiyor.
        </p>
        <Link
          href="/onboarding"
          className="inline-flex rounded-xl bg-purple-500 px-4 py-2 text-sm font-semibold text-white hover:bg-purple-400 transition"
        >
          Become a Citizen
        </Link>
      </div>
    )
  }

  if (requireAdmin && !citizen?.is_admin) {
    return (
      <div className="max-w-md mx-auto py-16 text-center space-y-4">
        <h2 className="text-xl font-semibold text-gray-100">Admin yetkisi gerekli.</h2>
        <p className="text-sm text-gray-400">
          Bu alan sadece Aurora admin kullanıcılarına açık. Admin yetkisi olmayan hesaplar bu
          sayfaya erişemez.
        </p>
        <Link
          href="/dashboard"
          className="inline-flex rounded-xl bg-purple-500 px-4 py-2 text-sm font-semibold text-white hover:bg-purple-400 transition"
        >
          Dashboard'a Dön
        </Link>
      </div>
    )
  }

  return <>{children}</>
}

