'use client'

import { useParams, useRouter } from 'next/navigation'
import { AuroraCaseView } from '@aurora/ui'

export default function OmbudsmanCaseDetailPage() {
  const params = useParams<{ userId: string }>()
  const router = useRouter()
  const userId = decodeURIComponent(params.userId)

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-gray-100">Case File · {userId}</h2>
          <p className="text-xs text-gray-400">
            Privacy profile, CP/Regime state, NovaScore bileşenleri ve son violation'lar tek
            ekranda.
          </p>
        </div>
        <button
          onClick={() => router.push('/admin/aurora/ombudsman')}
          className="rounded-lg border border-white/15 px-3 py-1.5 text-[11px] text-gray-200 hover:bg-white/5 transition"
        >
          ← Ombudsman
        </button>
      </div>

      <div className="rounded-2xl border border-white/10 bg-black/60 p-3">
        <AuroraCaseView userId={userId} />
      </div>
    </div>
  )
}

