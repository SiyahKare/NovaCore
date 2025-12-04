'use client'

import { useState } from 'react'
import { useAuroraAPI } from '@aurora/hooks'
import type { HitlQuest } from '@aurora/hooks'

interface HitlQuestCardProps {
  quest: HitlQuest
  onDecision: () => void
}

export function HitlQuestCard({ quest, onDecision }: HitlQuestCardProps) {
  const { fetchAPI } = useAuroraAPI()
  const [isProcessing, setIsProcessing] = useState(false)
  const [decisionReason, setDecisionReason] = useState('')

  const handleDecision = async (decision: 'APPROVED' | 'REJECTED') => {
    if (isProcessing) return
    
    setIsProcessing(true)
    
    try {
      const { data, error } = await fetchAPI(
        `/admin/quests/${quest.id}/hitl-decision`,
        {
          method: 'POST',
          body: JSON.stringify({
            decision,
            reason: decisionReason || undefined,
          }),
        }
      )
      
      if (error) {
        alert(`Hata: ${error.detail || 'Karar verilemedi'}`)
      } else {
        alert(`Quest ${decision === 'APPROVED' ? 'onaylandı' : 'reddedildi'}`)
        onDecision()
      }
    } catch (err) {
      alert(`Hata: ${err instanceof Error ? err.message : 'Bilinmeyen hata'}`)
    } finally {
      setIsProcessing(false)
      setDecisionReason('')
    }
  }

  const riskScore = quest.abuse_risk_snapshot || 0
  const riskColor = riskScore >= 8.0 ? 'text-red-400' : riskScore >= 6.0 ? 'text-orange-400' : 'text-yellow-400'

  return (
    <div className="rounded-lg border border-white/10 bg-black/40 p-4 space-y-3">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h3 className="text-sm font-semibold text-gray-100">{quest.title}</h3>
          <p className="text-xs text-gray-400 mt-1">{quest.description}</p>
          <p className="text-xs text-gray-500 mt-1">ID: {quest.quest_uuid.slice(0, 8)}...</p>
        </div>
        <div className="text-right">
          <p className={`text-sm font-bold ${riskColor}`}>
            RiskScore: {riskScore.toFixed(1)}
          </p>
          {quest.final_score !== null && (
            <p className="text-xs text-gray-400">AI Score: {quest.final_score.toFixed(1)}</p>
          )}
        </div>
      </div>

      {/* Creator Info */}
      <div className="flex items-center gap-3 text-xs text-gray-400">
        <span>Creator ID: {quest.user_id}</span>
        <span>•</span>
        <span>Type: {quest.quest_type}</span>
      </div>

      {/* Rewards */}
      <div className="flex items-center gap-4 text-xs">
        <div>
          <span className="text-gray-400">Base: </span>
          <span className="text-gray-200">
            {quest.base_reward_xp} XP, {quest.base_reward_ncr} NCR
          </span>
        </div>
        {quest.final_reward_ncr !== null && quest.final_reward_xp !== null && (
          <div>
            <span className="text-gray-400">Final: </span>
            <span className="text-gray-200">
              {quest.final_reward_xp} XP, {quest.final_reward_ncr} NCR
            </span>
          </div>
        )}
      </div>

      {/* Proof */}
      {quest.proof_payload_ref && (
        <div className="text-xs">
          <span className="text-gray-400">Kanıt: </span>
          <span className="text-gray-200">{quest.proof_type || 'N/A'}</span>
          {quest.proof_payload_ref && (
            <a
              href={quest.proof_payload_ref}
              target="_blank"
              rel="noopener noreferrer"
              className="ml-2 text-purple-400 hover:text-purple-300 underline"
            >
              Görüntüle
            </a>
          )}
        </div>
      )}

      {/* Timestamps */}
      <div className="text-xs text-gray-500">
        <div>Atandı: {new Date(quest.assigned_at).toLocaleString('tr-TR')}</div>
        {quest.submitted_at && (
          <div>Gönderildi: {new Date(quest.submitted_at).toLocaleString('tr-TR')}</div>
        )}
      </div>

      {/* Decision Input */}
      <div className="space-y-2 pt-2 border-t border-white/10">
        <textarea
          value={decisionReason}
          onChange={(e) => setDecisionReason(e.target.value)}
          placeholder="Karar nedeni (opsiyonel)"
          className="w-full px-3 py-2 text-xs bg-black/40 border border-white/10 rounded text-gray-200 placeholder-gray-500 focus:outline-none focus:border-purple-500/50"
          rows={2}
        />
        
        <div className="flex gap-2">
          <button
            onClick={() => handleDecision('APPROVED')}
            disabled={isProcessing}
            className="flex-1 px-4 py-2 text-xs font-medium bg-green-500/20 text-green-300 border border-green-500/50 rounded hover:bg-green-500/30 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            ✅ Onayla (Ödül Ver)
          </button>
          <button
            onClick={() => handleDecision('REJECTED')}
            disabled={isProcessing}
            className="flex-1 px-4 py-2 text-xs font-medium bg-red-500/20 text-red-300 border border-red-500/50 rounded hover:bg-red-500/30 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            ❌ Reddet (Ceza Ver)
          </button>
        </div>
      </div>
    </div>
  )
}

