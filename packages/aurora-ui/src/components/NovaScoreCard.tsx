import React from 'react'
import type { NovaScorePayload } from '../types'

interface NovaScoreCardProps {
  novaScore: NovaScorePayload
  showDetails?: boolean
  className?: string
}

export const NovaScoreCard: React.FC<NovaScoreCardProps> = ({
  novaScore,
  showDetails = true,
  className = '',
}) => {
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-emerald-400'
    if (score >= 60) return 'text-yellow-400'
    if (score >= 40) return 'text-orange-400'
    return 'text-red-400'
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-emerald-400'
    if (confidence >= 0.6) return 'text-yellow-400'
    return 'text-orange-400'
  }

  return (
    <div className={`aurora-card ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-slate-200">NovaScore</h3>
        <span className={`text-3xl font-bold ${getScoreColor(novaScore.value)}`}>
          {novaScore.value.toFixed(1)}
        </span>
      </div>

      <div className="space-y-3">
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-slate-400">Overall Confidence</span>
            <span className={getConfidenceColor(novaScore.confidence_overall)}>
              {(novaScore.confidence_overall * 100).toFixed(0)}%
            </span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-2">
            <div
              className="bg-aurora-purple h-2 rounded-full transition-all"
              style={{ width: `${novaScore.confidence_overall * 100}%` }}
            />
          </div>
        </div>

        {showDetails && (
          <div className="grid grid-cols-2 gap-3 pt-3 border-t border-slate-800">
            {Object.entries(novaScore.components).map(([key, component]) => (
              <div key={key} className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-400">{key}</span>
                  <span className="text-slate-200 font-medium">
                    {component.value.toFixed(1)}
                  </span>
                </div>
                <div className="w-full bg-slate-800 rounded-full h-1.5">
                  <div
                    className="bg-aurora-sky h-1.5 rounded-full"
                    style={{ width: `${component.value}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        )}

        {novaScore.explanation && (
          <p className="text-xs text-slate-400 mt-3 pt-3 border-t border-slate-800">
            {novaScore.explanation}
          </p>
        )}
      </div>
    </div>
  )
}

