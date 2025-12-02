import React from 'react'
import type { EnforcementError } from '../types'
import { RegimeBadge } from './RegimeBadge'

interface EnforcementErrorModalProps {
  error: EnforcementError
  onClose: () => void
  onAppeal?: () => void
}

export const EnforcementErrorModal: React.FC<EnforcementErrorModalProps> = ({
  error,
  onClose,
  onAppeal,
}) => {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm">
      <div className="aurora-card max-w-md w-full mx-4 border-2 border-red-500/30">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h2 className="text-xl font-bold text-red-400 mb-2">Aurora Enforcement</h2>
            <RegimeBadge regime={error.regime} size="md" />
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-200 transition-colors"
          >
            ✕
          </button>
        </div>

        <p className="text-slate-300 mb-4">{error.detail}</p>

        <div className="bg-slate-900/50 rounded-lg p-3 mb-4">
          <p className="text-xs text-slate-400 mb-1">Action:</p>
          <p className="text-sm font-mono text-slate-200">{error.action}</p>
        </div>

        {error.allowed_actions && error.allowed_actions.length > 0 && (
          <div className="mb-4">
            <p className="text-xs text-slate-400 mb-2">Allowed Actions:</p>
            <div className="flex flex-wrap gap-2">
              {error.allowed_actions.map((action) => (
                <span
                  key={action}
                  className="text-xs px-2 py-1 bg-emerald-500/20 text-emerald-400 rounded"
                >
                  {action}
                </span>
              ))}
            </div>
          </div>
        )}

        <div className="flex gap-3">
          <button onClick={onClose} className="aurora-button-secondary flex-1">
            Close
          </button>
          {onAppeal && error.appeal_url && (
            <button onClick={onAppeal} className="aurora-button flex-1">
              Appeal
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

