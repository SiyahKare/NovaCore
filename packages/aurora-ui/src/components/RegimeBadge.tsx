import React from 'react'
import type { Regime } from '../types'

interface RegimeBadgeProps {
  regime: Regime
  size?: 'sm' | 'md' | 'lg'
  showLabel?: boolean
  className?: string
}

const regimeConfig: Record<Regime, { color: string; label: string; icon: string }> = {
  NORMAL: {
    color: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
    label: 'Normal',
    icon: '✓',
  },
  SOFT_FLAG: {
    color: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    label: 'Soft Flag',
    icon: '⚠',
  },
  PROBATION: {
    color: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
    label: 'Probation',
    icon: '⚡',
  },
  RESTRICTED: {
    color: 'bg-red-500/20 text-red-400 border-red-500/30',
    label: 'Restricted',
    icon: '🔒',
  },
  LOCKDOWN: {
    color: 'bg-purple-500/20 text-purple-400 border-purple-500/30 aurora-glow',
    label: 'Lockdown',
    icon: '🚫',
  },
}

export const RegimeBadge: React.FC<RegimeBadgeProps> = ({
  regime,
  size = 'md',
  showLabel = true,
  className = '',
}) => {
  const config = regimeConfig[regime]
  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-3 py-1',
    lg: 'text-base px-4 py-1.5',
  }

  return (
    <span
      className={`aurora-badge border ${config.color} ${sizeClasses[size]} ${className}`}
      title={`Regime: ${config.label}`}
    >
      <span className="mr-1">{config.icon}</span>
      {showLabel && config.label}
    </span>
  )
}

