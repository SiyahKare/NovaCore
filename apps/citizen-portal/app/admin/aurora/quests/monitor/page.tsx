'use client'

import { useState } from 'react'
import { useHitlQuests } from '@aurora/hooks'
import { HitlQuestCard } from '@/components/Ombudsman/HitlQuestCard'

export default function OmbudsmanQuestMonitorPage() {
  const [minRiskScore, setMinRiskScore] = useState(6.0)
  const { quests, isLoading, error, refetch } = useHitlQuests(minRiskScore)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-lg font-semibold text-gray-100">Ombudsman Quest Monitor</h2>
        <p className="text-xs text-gray-400 mt-1">
          RiskScore yüksek ve HITL (Human-In-The-Loop) kuyruğundaki quest'leri yönet
        </p>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <label className="text-xs text-gray-400">
          Minimum RiskScore:
          <input
            type="number"
            min="0"
            max="10"
            step="0.5"
            value={minRiskScore}
            onChange={(e) => setMinRiskScore(parseFloat(e.target.value) || 6.0)}
            className="ml-2 px-2 py-1 text-xs bg-black/40 border border-white/10 rounded text-gray-200 w-20"
          />
        </label>
        <button
          onClick={refetch}
          className="px-3 py-1 text-xs bg-purple-500/20 text-purple-300 border border-purple-500/50 rounded hover:bg-purple-500/30"
        >
          🔄 Yenile
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="rounded-lg border border-white/10 bg-black/40 p-3">
          <div className="text-xs text-gray-400">Toplam HITL</div>
          <div className="text-lg font-semibold text-gray-100">{quests.length}</div>
        </div>
        <div className="rounded-lg border border-white/10 bg-black/40 p-3">
          <div className="text-xs text-gray-400">Yüksek Risk (≥8.0)</div>
          <div className="text-lg font-semibold text-red-400">
            {quests.filter((q) => (q.abuse_risk_snapshot || 0) >= 8.0).length}
          </div>
        </div>
        <div className="rounded-lg border border-white/10 bg-black/40 p-3">
          <div className="text-xs text-gray-400">Orta Risk (6.0-7.9)</div>
          <div className="text-lg font-semibold text-orange-400">
            {quests.filter((q) => {
              const score = q.abuse_risk_snapshot || 0
              return score >= 6.0 && score < 8.0
            }).length}
          </div>
        </div>
      </div>

      {/* Quest List */}
      {isLoading && (
        <div className="text-center py-8 text-gray-400 text-sm">Yükleniyor...</div>
      )}

      {error && (
        <div className="rounded-lg border border-red-500/50 bg-red-500/10 p-4 text-red-300 text-sm">
          Hata: {error}
        </div>
      )}

      {!isLoading && !error && quests.length === 0 && (
        <div className="text-center py-8 text-gray-400 text-sm">
          HITL kuyruğunda quest yok. 🎉
        </div>
      )}

      {!isLoading && !error && quests.length > 0 && (
        <div className="space-y-4">
          {quests.map((quest) => (
            <HitlQuestCard key={quest.id} quest={quest} onDecision={refetch} />
          ))}
        </div>
      )}
    </div>
  )
}

