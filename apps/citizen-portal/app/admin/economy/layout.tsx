'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { ReactNode } from 'react'
import { ProtectedView } from '@/components/ProtectedView'

const tabs = [
  { href: '/admin/aurora', label: 'Aurora' },
  { href: '/admin/economy', label: 'Economy' },
]

export default function EconomyAdminLayout({ children }: { children: ReactNode }) {
  const pathname = usePathname()

  return (
    <ProtectedView requireAdmin>
      <div className="max-w-7xl mx-auto px-4 py-8 space-y-6">
        <header className="flex items-center justify-between gap-4">
          <div>
            <div className="text-xs uppercase tracking-[0.2em] text-purple-300">
              Admin Panel
            </div>
            <h1 className="text-2xl font-semibold text-gray-100">NasipQuest Economy</h1>
            <p className="text-xs text-gray-400 mt-1">
              NCR fiyatı, Treasury durumu ve ekonomi metrikleri
            </p>
          </div>

          <Link
            href="/dashboard"
            className="rounded-lg border border-white/15 px-3 py-1.5 text-[11px] text-gray-200 hover:bg-white/5 transition"
          >
            ← Citizen View
          </Link>
        </header>

        <nav className="flex gap-3 border-b border-white/10 pb-2 text-xs">
          {tabs.map((tab) => {
            const active = pathname?.startsWith(tab.href)
            return (
              <Link
                key={tab.href}
                href={tab.href}
                className={`rounded-lg px-3 py-1.5 transition ${
                  active
                    ? 'bg-purple-500/20 text-purple-100 border border-purple-500/50'
                    : 'text-gray-400 hover:text-gray-200 hover:bg-white/5 border border-transparent'
                }`}
              >
                {tab.label}
              </Link>
            )
          })}
        </nav>

        <div>{children}</div>
      </div>
    </ProtectedView>
  )
}

