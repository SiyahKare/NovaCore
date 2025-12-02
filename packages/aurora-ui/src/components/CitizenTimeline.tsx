'use client'

import type { CitizenState, ViolationItem } from '@aurora/hooks'

interface TimelineEvent {
  date: Date
  type: 'joined' | 'consent' | 'novascore' | 'violation' | 'regime_change' | 'recall'
  title: string
  description: string
  metadata?: Record<string, any>
}

interface CitizenTimelineProps {
  state: CitizenState
  className?: string
}

export function CitizenTimeline({ state, className = '' }: CitizenTimelineProps) {
  const events: TimelineEvent[] = []

  // Join date
  if (state.identity?.created_at) {
    events.push({
      date: new Date(state.identity.created_at),
      type: 'joined',
      title: 'Aurora Vatandaşlığı',
      description: 'Aurora devletine katıldın',
    })
  }

  // Consent signed
  if (state.privacy?.latest_consent_id && state.privacy.last_policy_updated_at) {
    events.push({
      date: new Date(state.privacy.last_policy_updated_at),
      type: 'consent',
      title: 'Consent İmzalandı',
      description: `Versiyon: ${state.privacy.contract_version || 'N/A'}`,
      metadata: { version: state.privacy.contract_version },
    })
  }

  // NovaScore milestones
  if (state.novaScore) {
    const score = state.novaScore.nova_score
    if (score >= 800) {
      events.push({
        date: new Date(), // Approximate
        type: 'novascore',
        title: 'NovaScore: Elite',
        description: `Skor: ${score.toFixed(0)}`,
        metadata: { score },
      })
    } else if (score >= 600) {
      events.push({
        date: new Date(),
        type: 'novascore',
        title: 'NovaScore: Yüksek',
        description: `Skor: ${score.toFixed(0)}`,
        metadata: { score },
      })
    }
  }

  // Violations
  state.violations.forEach((violation: ViolationItem) => {
    events.push({
      date: new Date(violation.created_at),
      type: 'violation',
      title: `İhlal: ${violation.category}`,
      description: `${violation.code} (+${violation.cp_delta} CP)`,
      metadata: { violation },
    })
  })

  // Regime changes (if CP state exists)
  if (state.cpState) {
    const cp = state.cpState.cp_value
    const regime = state.cpState.regime

    if (regime !== 'NORMAL' && cp > 0) {
      events.push({
        date: new Date(state.cpState.last_updated_at),
        type: 'regime_change',
        title: `Regime: ${regime}`,
        description: `CP: ${cp}`,
        metadata: { regime, cp },
      })
    }
  }

  // Recall request
  if (state.privacy?.recall_requested_at) {
    events.push({
      date: new Date(state.privacy.recall_requested_at),
      type: 'recall',
      title: 'Recall Talebi',
      description: state.privacy.recall_completed_at ? 'Tamamlandı' : 'İşleniyor',
      metadata: { mode: state.privacy.recall_mode },
    })
  }

  // Sort by date (newest first)
  events.sort((a, b) => b.date.getTime() - a.date.getTime())

  // Limit to last 10 events
  const recentEvents = events.slice(0, 10)

  if (recentEvents.length === 0) {
    return (
      <div className={`aurora-card ${className}`}>
        <h3 className="text-lg font-semibold text-slate-200 mb-4">Timeline</h3>
        <p className="text-sm text-gray-400">Henüz olay yok</p>
      </div>
    )
  }

  const getEventIcon = (type: TimelineEvent['type']) => {
    switch (type) {
      case 'joined':
        return '🎯'
      case 'consent':
        return '✓'
      case 'novascore':
        return '⭐'
      case 'violation':
        return '⚠️'
      case 'regime_change':
        return '🔒'
      case 'recall':
        return '🔄'
      default:
        return '•'
    }
  }

  const getEventColor = (type: TimelineEvent['type']) => {
    switch (type) {
      case 'joined':
        return 'text-emerald-300'
      case 'consent':
        return 'text-blue-300'
      case 'novascore':
        return 'text-purple-300'
      case 'violation':
        return 'text-red-300'
      case 'regime_change':
        return 'text-yellow-300'
      case 'recall':
        return 'text-cyan-300'
      default:
        return 'text-gray-300'
    }
  }

  const formatRelativeTime = (date: Date) => {
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

    if (diffDays === 0) {
      return 'Bugün'
    } else if (diffDays === 1) {
      return 'Dün'
    } else if (diffDays < 7) {
      return `${diffDays} gün önce`
    } else if (diffDays < 30) {
      const weeks = Math.floor(diffDays / 7)
      return `${weeks} hafta önce`
    } else {
      const months = Math.floor(diffDays / 30)
      return `${months} ay önce`
    }
  }

  return (
    <div className={`aurora-card ${className}`}>
      <h3 className="text-lg font-semibold text-slate-200 mb-4">Timeline</h3>
      <div className="space-y-3">
        {recentEvents.map((event, idx) => (
          <div
            key={idx}
            className="flex items-start gap-3 p-3 rounded-lg bg-slate-900/50 border border-slate-800 hover:border-slate-700 transition-colors"
          >
            <div className={`text-lg ${getEventColor(event.type)}`}>{getEventIcon(event.type)}</div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between mb-1">
                <h4 className="text-sm font-semibold text-slate-200">{event.title}</h4>
                <span className="text-xs text-gray-500">{formatRelativeTime(event.date)}</span>
              </div>
              <p className="text-xs text-gray-400">{event.description}</p>
              <p className="text-[10px] text-gray-500 mt-1">
                {event.date.toLocaleDateString('tr-TR', {
                  day: 'numeric',
                  month: 'short',
                  year: 'numeric',
                })}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

