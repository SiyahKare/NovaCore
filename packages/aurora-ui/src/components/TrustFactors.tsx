'use client'

import type { CitizenState } from '@aurora/hooks'

interface TrustFactorsProps {
  state: CitizenState
  className?: string
}

export function TrustFactors({ state, className = '' }: TrustFactorsProps) {
  const factors: Array<{
    label: string
    value: string | number
    status: 'good' | 'warning' | 'bad' | 'neutral'
    description?: string
  }> = []

  // Account Age
  if (state.identity?.created_at) {
    const accountAge = Math.floor(
      (new Date().getTime() - new Date(state.identity.created_at).getTime()) / (1000 * 60 * 60 * 24)
    )
    factors.push({
      label: 'Hesap Yaşı',
      value: `${accountAge} gün`,
      status: accountAge >= 30 ? 'good' : accountAge >= 7 ? 'warning' : 'neutral',
      description: accountAge >= 30 ? 'Güvenilir hesap' : accountAge >= 7 ? 'Yeni hesap' : 'Çok yeni',
    })
  }

  // Violation Frequency
  const violationCount = state.violations.length
  const violationRate = violationCount > 0 ? (violationCount / 30).toFixed(1) : 0
  factors.push({
    label: 'İhlal Sıklığı',
    value: `${violationCount} ihlal`,
    status: violationCount === 0 ? 'good' : violationCount <= 2 ? 'warning' : 'bad',
    description: violationCount === 0 ? 'Temiz kayıt' : violationCount <= 2 ? 'Düşük risk' : 'Yüksek risk',
  })

  // Behavior Risk Score (based on CP and NovaScore)
  let behaviorRisk = 'Düşük'
  let behaviorStatus: 'good' | 'warning' | 'bad' | 'neutral' = 'good'
  if (state.cpState && state.novaScore) {
    const cp = state.cpState.cp_value
    const score = state.novaScore.nova_score
    if (cp >= 60 || score < 400) {
      behaviorRisk = 'Yüksek'
      behaviorStatus = 'bad'
    } else if (cp >= 30 || score < 600) {
      behaviorRisk = 'Orta'
      behaviorStatus = 'warning'
    }
  }
  factors.push({
    label: 'Davranış Riski',
    value: behaviorRisk,
    status: behaviorStatus,
    description:
      state.cpState && state.novaScore
        ? `CP: ${state.cpState.cp_value}, Score: ${state.novaScore.nova_score.toFixed(0)}`
        : 'Hesaplanamadı',
  })

  // Redline Compliance
  if (state.privacy) {
    const hasRedline = state.privacy.recall_requested_at !== null
    factors.push({
      label: 'Redline Uyumu',
      value: hasRedline ? 'Recall Talebi Var' : 'Uyumlu',
      status: hasRedline ? 'warning' : 'good',
      description: hasRedline ? 'Veri geri çekme talebi aktif' : 'Tüm veriler kullanımda',
    })
  }

  // Consent Status
  if (state.privacy) {
    factors.push({
      label: 'Consent Durumu',
      value: state.privacy.latest_consent_id ? 'İmzalı' : 'İmzasız',
      status: state.privacy.latest_consent_id ? 'good' : 'bad',
      description: state.privacy.latest_consent_id
        ? `v${state.privacy.contract_version || 'N/A'}`
        : 'Consent imzalanmamış',
    })
  }

  // XP Level (if available)
  if (state.loyalty) {
    factors.push({
      label: 'Loyalty Seviyesi',
      value: `Level ${state.loyalty.level} (${state.loyalty.tier})`,
      status: state.loyalty.level >= 10 ? 'good' : state.loyalty.level >= 5 ? 'warning' : 'neutral',
      description: `${state.loyalty.xp_total} XP`,
    })
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'good':
        return 'text-emerald-300 border-emerald-500/50 bg-emerald-500/10'
      case 'warning':
        return 'text-yellow-300 border-yellow-500/50 bg-yellow-500/10'
      case 'bad':
        return 'text-red-300 border-red-500/50 bg-red-500/10'
      default:
        return 'text-gray-300 border-gray-500/50 bg-gray-500/10'
    }
  }

  return (
    <div className={`aurora-card ${className}`}>
      <h3 className="text-lg font-semibold text-slate-200 mb-4">Trust Factors</h3>
      <div className="space-y-2">
        {factors.map((factor, idx) => (
          <div
            key={idx}
            className={`p-3 rounded-lg border ${getStatusColor(factor.status)}`}
          >
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs text-gray-400">{factor.label}</span>
              <span className="text-sm font-semibold">{factor.value}</span>
            </div>
            {factor.description && (
              <p className="text-[10px] text-gray-500 mt-1">{factor.description}</p>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

