import React from 'react'
import type { NovaScorePayload } from '../types'

interface NovaScoreCardProps {
  novaScore: NovaScorePayload | { nova_score?: number; value?: number; [key: string]: any }
  showDetails?: boolean
  className?: string
}

export const NovaScoreCard: React.FC<NovaScoreCardProps> = ({
  novaScore,
  showDetails = true,
  className = '',
}) => {
  // Support both formats: { value: number } and { nova_score: number }
  // Backend returns nova_score (0-1000), frontend expects value (0-100)
  const rawScore = (novaScore as any).value ?? (novaScore as any).nova_score ?? 0
  // Normalize: if score > 100, assume it's 0-1000 scale and convert to 0-100
  const normalizedScore = rawScore > 100 ? rawScore / 10 : rawScore
  
  // Get confidence - support both formats
  const confidence = (novaScore as any).confidence_overall ?? 0.5
  
  // Get components - support both formats
  const components = (novaScore as any).components ?? {}

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-emerald-400'
    if (score >= 60) return 'text-yellow-400'
    if (score >= 40) return 'text-orange-400'
    return 'text-red-400'
  }

  const getConfidenceColor = (conf: number) => {
    if (conf >= 0.8) return 'text-emerald-400'
    if (conf >= 0.6) return 'text-yellow-400'
    return 'text-orange-400'
  }

  // Safety check: if score is invalid, show placeholder
  if (!novaScore || (normalizedScore === 0 && rawScore === 0 && !components)) {
    return (
      <div className={`aurora-card ${className}`}>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-slate-200">NovaScore</h3>
          <span className="text-3xl font-bold text-gray-500">—</span>
        </div>
        <p className="text-sm text-slate-400">NovaScore verisi yükleniyor...</p>
      </div>
    )
  }

  return (
    <div className={`aurora-card ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-slate-200">NovaScore</h3>
        <span className={`text-3xl font-bold ${getScoreColor(normalizedScore)}`}>
          {normalizedScore.toFixed(1)}
        </span>
      </div>

      <div className="space-y-3">
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-slate-400">Overall Confidence</span>
            <span className={getConfidenceColor(confidence)}>
              {(confidence * 100).toFixed(0)}%
            </span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-2">
            <div
              className="bg-aurora-purple h-2 rounded-full transition-all"
              style={{ width: `${confidence * 100}%` }}
            />
          </div>
        </div>

        {showDetails && components && Object.keys(components).length > 0 && (
          <div className="grid grid-cols-2 gap-3 pt-3 border-t border-slate-800">
            {Object.entries(components).map(([key, component]: [string, any]) => {
              const compValue = component?.value ?? 0
              const normalizedCompValue = compValue > 100 ? compValue / 10 : compValue
              return (
                <div key={key} className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span className="text-slate-400">{key}</span>
                    <span className="text-slate-200 font-medium">
                      {normalizedCompValue.toFixed(1)}
                    </span>
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-1.5">
                    <div
                      className="bg-aurora-sky h-1.5 rounded-full"
                      style={{ width: `${Math.min(normalizedCompValue, 100)}%` }}
                    />
                  </div>
                </div>
              )
            })}
          </div>
        )}

        {(novaScore as any).explanation && (
          <p className="text-xs text-slate-400 mt-3 pt-3 border-t border-slate-800">
            {(novaScore as any).explanation}
          </p>
        )}
      </div>
    </div>
  )
}

