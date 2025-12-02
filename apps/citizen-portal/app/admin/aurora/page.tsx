'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { AuroraStatsPanel } from '@aurora/ui'
import { useCurrentCitizen } from '@aurora/hooks'

export default function AuroraAdminOverviewPage() {
  const router = useRouter()
  const { citizen } = useCurrentCitizen()
  const [userId, setUserId] = useState('')

  const handleOpenCase = (e: React.FormEvent) => {
    e.preventDefault()
    if (!userId.trim()) return
    router.push(`/admin/aurora/case/${encodeURIComponent(userId.trim())}`)
  }

  return (
    <div className="space-y-8">
      {/* Quick stats */}
      <section className="space-y-3">
        <h2 className="text-sm font-semibold text-gray-100">Aurora State Snapshot</h2>
        <p className="text-xs text-gray-400">
          Consent, violations, CP ve regime dağılımı. Bu panel{' '}
          <span className="text-purple-300">/admin/aurora/stats</span> sayfasının condensed
          versiyonu.
        </p>

        <div className="rounded-2xl border border-white/10 bg-black/60 p-4">
          <AuroraStatsPanel />
        </div>
      </section>

      {/* Case search */}
      <section className="space-y-3">
        <h2 className="text-sm font-semibold text-gray-100">Quick Case Lookup</h2>
        <p className="text-xs text-gray-400">
          Herhangi bir Aurora citizen için komple case file aç. Ombudsman flow'unun giriş noktası.
        </p>

        <form
          onSubmit={handleOpenCase}
          className="flex flex-col md:flex-row gap-3 items-stretch md:items-center"
        >
          <input
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            placeholder="Örn: AUR-SIGMA, AUR-TROLLER, internal user_id..."
            className="flex-1 rounded-xl border border-white/15 bg-black/60 px-3 py-2 text-sm text-gray-100 placeholder:text-gray-500 focus:outline-none focus:border-purple-500/70 transition"
          />
          <button
            type="submit"
            className="rounded-xl bg-purple-500 px-4 py-2 text-sm font-semibold text-white hover:bg-purple-400 transition"
          >
            Open Case
          </button>
        </form>
      </section>

      {/* Admin info */}
      <section className="border-t border-white/10 pt-4 text-[11px] text-gray-500 flex justify-between">
        <div>
          Logged in as:{' '}
          <span className="text-gray-300">
            {citizen?.display_name || `Citizen ${citizen?.id || 'unknown'}`}{' '}
            {citizen?.is_admin ? '(admin)' : '(not admin)'}
          </span>
        </div>
        <div>
          Full stats &gt;{' '}
          <a
            href="/admin/aurora/stats"
            className="text-purple-300 hover:text-purple-200 transition"
          >
            Stats Panel
          </a>
        </div>
      </section>
    </div>
  )
}

