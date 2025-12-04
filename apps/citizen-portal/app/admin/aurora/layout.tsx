'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { ReactNode } from 'react'
import { ProtectedView } from '@/components/ProtectedView'

const tabs = [
  { href: '/admin/aurora', label: 'Overview' },
  { href: '/admin/aurora/users', label: 'Users' },
  { href: '/admin/aurora/stats', label: 'Stats' },
  { href: '/admin/aurora/violations', label: 'Violations' },
  { href: '/admin/aurora/events', label: 'Events' },
  { href: '/admin/aurora/growth', label: 'Growth' },
  { href: '/admin/aurora/policy', label: 'Policy' },
  { href: '/admin/aurora/quests/monitor', label: 'HITL Monitor' },
  { href: '/admin/aurora/ombudsman', label: 'Ombudsman' },
  { href: '/admin/aurora/telegram-dashboard', label: 'Telegram Dashboard' },
  { href: '/admin/economy', label: 'Economy' },
]

export default function AuroraAdminLayout({ children }: { children: ReactNode }) {
  const pathname = usePathname()

  return (
    <ProtectedView requireAdmin>
      <div className="max-w-6xl mx-auto px-4 py-8 space-y-6">
        <header className="flex items-center justify-between gap-4">
          <div>
            <div className="text-xs uppercase tracking-[0.2em] text-purple-300">
              Aurora Justice Control Room
            </div>
            <h1 className="text-2xl font-semibold text-gray-100">NovaCore Admin Panel</h1>
            <p className="text-xs text-gray-400 mt-1">
              Case yönetimi, ceza rejimi ve politika görünümü.
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
            const active = pathname === tab.href
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

