import React from 'react'
import type { Regime } from '../types'
import { RegimeBadge } from './RegimeBadge'

export interface RegimeBannerProps {
  regime: Regime
  cpValue: number
  message?: string
  className?: string
}

const regimeMessages: Record<Regime, string> = {
  NORMAL: 'You are in good standing with Aurora.',
  SOFT_FLAG: 'You have been flagged. Please review your recent activity.',
  PROBATION: 'You are on probation. Some actions may be restricted.',
  RESTRICTED: 'Your account is restricted. Contact support for assistance.',
  LOCKDOWN: 'Your account is locked. All actions are blocked. Appeal required.',
}

export const RegimeBanner: React.FC<RegimeBannerProps> = ({
  regime,
  cpValue,
  message,
  className = '',
}) => {
  const bannerConfig: Record<Regime, { bg: string; border: string }> = {
    NORMAL: {
      bg: 'bg-emerald-500/10',
      border: 'border-emerald-500/30',
    },
    SOFT_FLAG: {
      bg: 'bg-yellow-500/10',
      border: 'border-yellow-500/30',
    },
    PROBATION: {
      bg: 'bg-orange-500/10',
      border: 'border-orange-500/30',
    },
    RESTRICTED: {
      bg: 'bg-red-500/10',
      border: 'border-red-500/30',
    },
    LOCKDOWN: {
      bg: 'bg-purple-500/10',
      border: 'border-purple-500/30',
      // Add glow for lockdown
    },
  }

  const config = bannerConfig[regime]
  const displayMessage = message || regimeMessages[regime]

  return (
    <div
      className={`${config.bg} ${config.border} border rounded-lg p-4 ${className} ${
        regime === 'LOCKDOWN' ? 'aurora-glow' : ''
      }`}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <RegimeBadge regime={regime} size="md" />
          <div>
            <p className="text-sm text-slate-200">{displayMessage}</p>
            <p className="text-xs text-slate-400 mt-1">CP: {cpValue}</p>
          </div>
        </div>
      </div>
    </div>
  )
}

