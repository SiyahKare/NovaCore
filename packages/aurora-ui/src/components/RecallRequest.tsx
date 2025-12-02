import React, { useState } from 'react'

interface RecallRequestProps {
  onSubmit: (mode: 'ANONYMIZE' | 'FULL_EXCLUDE') => void
  onCancel?: () => void
  className?: string
}

export const RecallRequest: React.FC<RecallRequestProps> = ({
  onSubmit,
  onCancel,
  className = '',
}) => {
  const [mode, setMode] = useState<'ANONYMIZE' | 'FULL_EXCLUDE' | null>(null)

  return (
    <div className={`aurora-card max-w-lg mx-auto ${className}`}>
      <h2 className="text-xl font-bold text-slate-200 mb-4">Request Data Recall</h2>
      <p className="text-sm text-slate-400 mb-6">
        You have the right to request exclusion of your data from AI training. Choose your
        preference:
      </p>

      <div className="space-y-3 mb-6">
        <label
          className={`block p-4 rounded-lg border-2 cursor-pointer transition-all ${
            mode === 'ANONYMIZE'
              ? 'border-aurora-purple bg-aurora-purple/10'
              : 'border-slate-800 bg-slate-900/50 hover:border-slate-700'
          }`}
        >
          <input
            type="radio"
            name="mode"
            value="ANONYMIZE"
            checked={mode === 'ANONYMIZE'}
            onChange={() => setMode('ANONYMIZE')}
            className="mr-3"
          />
          <div>
            <span className="font-semibold text-slate-200">Anonymize</span>
            <p className="text-xs text-slate-400 mt-1">
              Your data will be anonymized but may still be used for training
            </p>
          </div>
        </label>

        <label
          className={`block p-4 rounded-lg border-2 cursor-pointer transition-all ${
            mode === 'FULL_EXCLUDE'
              ? 'border-aurora-purple bg-aurora-purple/10'
              : 'border-slate-800 bg-slate-900/50 hover:border-slate-700'
          }`}
        >
          <input
            type="radio"
            name="mode"
            value="FULL_EXCLUDE"
            checked={mode === 'FULL_EXCLUDE'}
            onChange={() => setMode('FULL_EXCLUDE')}
            className="mr-3"
          />
          <div>
            <span className="font-semibold text-slate-200">Full Exclusion</span>
            <p className="text-xs text-slate-400 mt-1">
              Your data will be completely excluded from all AI training processes
            </p>
          </div>
        </label>
      </div>

      <div className="flex gap-3">
        {onCancel && (
          <button onClick={onCancel} className="aurora-button-secondary flex-1">
            Cancel
          </button>
        )}
        <button
          onClick={() => mode && onSubmit(mode)}
          disabled={!mode}
          className="aurora-button flex-1 disabled:opacity-50"
        >
          Submit Request
        </button>
      </div>
    </div>
  )
}

