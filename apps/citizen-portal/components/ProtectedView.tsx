'use client'

import { ReactNode } from 'react'
import { useCurrentCitizen } from '@aurora/hooks'
import { getToken } from '@/lib/auth'
import Link from 'next/link'

interface ProtectedViewProps {
  children: ReactNode
  requireAdmin?: boolean
}

export function ProtectedView({ children, requireAdmin = false }: ProtectedViewProps) {
  const { citizen, loading, error, isAuthenticated } = useCurrentCitizen()
  const hasToken = getToken() !== null

  if (loading) {
    return (
      <div className="flex justify-center py-20 text-sm text-gray-400">
        Aurora identity kontrol ediliyor...
      </div>
    )
  }

  if (error || !isAuthenticated) {
    // Token varsa ama authentication başarısızsa (expired/invalid token)
    if (hasToken) {
      return (
        <div className="max-w-md mx-auto py-16 text-center space-y-4">
          <h2 className="text-xl font-semibold text-gray-100">Oturum sona erdi.</h2>
          <p className="text-sm text-gray-400">
            Token&apos;ın süresi dolmuş veya geçersiz. Lütfen tekrar giriş yap.
          </p>
          <Link
            href="/onboarding"
            className="inline-flex rounded-xl bg-purple-500 px-4 py-2 text-sm font-semibold text-white hover:bg-purple-400 transition"
          >
            Connect Citizen
          </Link>
        </div>
      )
    }

    // Token yoksa - yeni kullanıcı
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
          Dashboard&apos;a Dön
        </Link>
      </div>
    )
  }

  return <>{children}</>
}

