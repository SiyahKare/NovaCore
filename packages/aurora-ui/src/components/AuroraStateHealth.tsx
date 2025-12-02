'use client'

import { usePolicy } from '@aurora/hooks'
import type { PolicyParams } from '@aurora/ui'

interface AuroraStateHealthProps {
  className?: string
}

export function AuroraStateHealth({ className = '' }: AuroraStateHealthProps) {
  const { policy, loading } = usePolicy()

  if (loading) {
    return (
      <div className={`aurora-card ${className}`}>
        <div className="text-gray-400 text-sm">Yükleniyor...</div>
      </div>
    )
  }

  if (!policy) {
    return (
      <div className={`aurora-card border-yellow-500/30 ${className}`}>
        <p className="text-yellow-300 text-sm">Policy bilgisi yüklenemedi</p>
      </div>
    )
  }

  const policyData = policy as PolicyParams

  return (
    <div className={`aurora-card border-purple-500/50 bg-gradient-to-br from-purple-950/20 to-black ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-slate-200 flex items-center gap-2">
          <span className="text-purple-400">⚡</span>
          Aurora State Health
        </h3>
        <div className="px-2 py-1 rounded text-xs bg-purple-500/20 text-purple-300 border border-purple-500/50">
          v{policyData.version || '1.0'}
        </div>
      </div>

      <div className="space-y-3">
        {/* DAO Status */}
        <div className="flex items-center justify-between p-2 rounded-lg bg-slate-900/50 border border-slate-800">
          <span className="text-xs text-gray-400">DAO Status</span>
          <span className="text-xs font-semibold text-emerald-300">
            {policyData.onchain_address ? 'On-Chain' : 'Off-Chain'}
          </span>
        </div>

        {/* Policy Version */}
        <div className="flex items-center justify-between p-2 rounded-lg bg-slate-900/50 border border-slate-800">
          <span className="text-xs text-gray-400">Active Policy</span>
          <span className="text-xs font-mono text-purple-300">{policyData.version}</span>
        </div>

        {/* Constitution Hash (placeholder) */}
        <div className="flex items-center justify-between p-2 rounded-lg bg-slate-900/50 border border-slate-800">
          <span className="text-xs text-gray-400">Constitution</span>
          <span className="text-xs font-mono text-gray-300">Aurora-DataEthics-v1.0</span>
        </div>

        {/* Last Sync */}
        {policyData.synced_at && (
          <div className="flex items-center justify-between p-2 rounded-lg bg-slate-900/50 border border-slate-800">
            <span className="text-xs text-gray-400">Last Sync</span>
            <span className="text-xs text-gray-300">
              {new Date(policyData.synced_at).toLocaleDateString('tr-TR')}
            </span>
          </div>
        )}

        {/* On-chain Info */}
        {policyData.onchain_address && (
          <div className="mt-3 pt-3 border-t border-slate-800">
            <div className="flex items-center justify-between p-2 rounded-lg bg-slate-900/50 border border-slate-800">
              <span className="text-xs text-gray-400">Contract</span>
              <span className="text-xs font-mono text-purple-300 truncate max-w-[120px]">
                {policyData.onchain_address.slice(0, 10)}...
              </span>
            </div>
            {policyData.onchain_block && (
              <div className="flex items-center justify-between p-2 rounded-lg bg-slate-900/50 border border-slate-800 mt-2">
                <span className="text-xs text-gray-400">Block</span>
                <span className="text-xs font-mono text-gray-300">#{policyData.onchain_block}</span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

