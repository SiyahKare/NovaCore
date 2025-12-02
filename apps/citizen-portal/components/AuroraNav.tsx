'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useCurrentCitizen } from '@aurora/hooks'
import { RegimeBadge } from '@aurora/ui'
import { clearToken } from '@/lib/auth'
import { NAV_ITEMS } from '@/lib/constants'

export function AuroraNav() {
  const pathname = usePathname()
  const { citizen, loading } = useCurrentCitizen()

  const handleLogout = () => {
    clearToken()
    window.location.href = '/'
  }

  return (
    <nav className="flex items-center justify-between py-4 mb-6 border-b border-white/10">
      <Link href="/" className="flex items-center gap-4">
        <div className="w-8 h-8 bg-aurora-gradient rounded-lg flex items-center justify-center">
          <span className="text-white font-bold text-sm">A</span>
        </div>
        <span className="font-semibold tracking-wide text-purple-300">
          Aurora Citizen Portal
        </span>
      </Link>

      <div className="flex gap-6 text-sm items-center">
        {NAV_ITEMS.map((item) => {
          const isActive = pathname === item.href || (item.href === '/academy' && pathname?.startsWith('/academy'))
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`transition-colors ${
                isActive
                  ? 'text-aurora-purple font-medium'
                  : 'text-gray-300 hover:text-white'
              }`}
            >
              {item.label}
            </Link>
          )
        })}
        {citizen ? (
          <div className="flex items-center gap-3">
            {citizen.is_admin && (
              <Link
                href="/admin/aurora"
                className="rounded-lg border border-purple-500/60 px-2 py-1 text-[10px] text-purple-200 hover:bg-purple-500/10 transition"
              >
                Admin
              </Link>
            )}
            <div className="text-right text-xs">
              <div className="text-gray-300 font-medium">
                {citizen.display_name || `Citizen ${citizen.id}`}
              </div>
              <div className="text-gray-500 text-[10px]">ID: {citizen.id}</div>
            </div>
            <button
              onClick={handleLogout}
              className="rounded-lg border border-red-500/40 px-2 py-1 text-[10px] text-red-300 hover:bg-red-500/10 transition"
            >
              Logout
            </button>
          </div>
        ) : (
          <Link
            href="/onboarding"
            className="rounded-lg border border-purple-500/60 px-3 py-1 text-xs text-purple-200 hover:bg-purple-500/10 transition"
          >
            Become a Citizen
          </Link>
        )}
      </div>
    </nav>
  )
}

