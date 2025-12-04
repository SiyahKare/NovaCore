'use client'

import { AuroraStatsPanel } from '@aurora/ui'

export default function OmbudsmanStatsPage() {
  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold text-gray-100">Aurora Justice Stats</h2>
        <p className="text-xs text-gray-400 max-w-xl">
          Consent sayıları, violation trend'leri, CP ortalaması ve regime dağılımı. Policy tuning
          ve operasyonel monitoring için kullanılır.
        </p>
      </div>

      <div className="mt-4">
        <AuroraStatsPanel />
      </div>
    </div>
  )
}

