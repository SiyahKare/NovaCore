'use client'

import { usePolicy } from '@aurora/hooks'
import { PolicyBreakdown, DAOChangeLog } from '@aurora/ui'

export default function AuroraPolicyPage() {
  const { policy, loading } = usePolicy()

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20 text-sm text-gray-400">
        Loading policy data...
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-gray-100">Policy & DAO Governance</h2>
        <p className="text-xs text-gray-400 max-w-xl">
          CP ağırlıkları, decay oranları, regime threshold'ları ve DAO'dan gelen aktif policy
          versiyonu. Şimdilik read-only; ileride proposal flow eklenebilir.
        </p>
      </div>

      <div className="grid md:grid-cols-[3fr,2fr] gap-6">
        <div className="rounded-2xl border border-white/10 bg-black/60 p-4">
          {policy ? (
            <PolicyBreakdown policy={policy} />
          ) : (
            <div className="text-sm text-gray-400">Policy data not available</div>
          )}
        </div>
        <div className="rounded-2xl border border-white/10 bg-black/60 p-4 text-xs text-gray-300">
          <div className="flex items-center justify-between mb-2">
            <span className="font-semibold text-gray-100">Policy History</span>
            {policy && 'onchain_address' in policy && (policy as any).onchain_address && (
              <span className="text-[10px] text-purple-300">
                {String((policy as any).onchain_address).slice(0, 6)}...{String((policy as any).onchain_address).slice(-4)}
              </span>
            )}
          </div>
          <DAOChangeLog changes={[]} />
        </div>
      </div>
    </div>
  )
}

