'use client'

import { AuroraStatsPanel } from '@aurora/ui'

export default function AuroraStatsPage() {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-gray-100">Aurora Justice Metrics & Stats</h2>
      <p className="text-xs text-gray-400 max-w-xl">
        Consent sayıları, violation trend'leri, CP ortalaması ve regime dağılımı. Policy tuning
        ve operasyonel monitoring için kullanılır. <strong className="text-purple-300">Justice Overview</strong> metrikleri
        NasipCourt DAO v1.0 sistem sağlığını ve adalet kalitesini ölçer.
      </p>

      <div className="mt-4">
        <AuroraStatsPanel />
      </div>
    </div>
  )
}

