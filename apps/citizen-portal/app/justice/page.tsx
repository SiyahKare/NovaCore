'use client'

import { ProtectedView } from '@/components/ProtectedView'
import { useJustice, useAuroraEvents } from '@aurora/hooks'
import { RegimeBadge, RegimeBanner } from '@aurora/ui'
import { AppealForm } from '@aurora/ui'
import { useState } from 'react'
import type { CpState } from '@aurora/ui'

export default function JusticePage() {
  return (
    <ProtectedView>
      <JusticeInner />
    </ProtectedView>
  )
}

function JusticeInner() {
  const { cpState, violations, loading } = useJustice()
  const { track } = useAuroraEvents()
  const [showAppeal, setShowAppeal] = useState(false)

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-gray-400">Loading justice status...</div>
      </div>
    )
  }

  if (!cpState) {
    return (
      <div className="aurora-card">
        <p className="text-slate-400">No justice data available</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold mb-2">Justice & Appeals</h1>
        <p className="text-gray-400 max-w-xl">
          View your case file, CP status, and submit appeals if needed.
        </p>
      </div>

      {/* Regime Banner */}
      <RegimeBanner
        regime={cpState.regime}
        cpValue={cpState.cp_value}
        message={
          cpState.regime === 'LOCKDOWN'
            ? 'Your account is locked. All actions are blocked. Appeal required.'
            : undefined
        }
      />

      {/* CP Status */}
      <div className="aurora-card">
        <h2 className="text-xl font-semibold text-slate-200 mb-4">CP Status</h2>
        <div className="grid md:grid-cols-3 gap-4">
          <div>
            <p className="text-sm text-slate-400 mb-1">Current CP</p>
            <p className="text-3xl font-bold text-aurora-purple">{cpState.cp_value}</p>
          </div>
          <div>
            <p className="text-sm text-slate-400 mb-1">Regime</p>
            <RegimeBadge regime={cpState.regime} size="md" showLabel={true} />
          </div>
          <div>
            <p className="text-sm text-slate-400 mb-1">Last Updated</p>
            <p className="text-sm text-slate-300">
              {new Date(cpState.last_updated_at).toLocaleString()}
            </p>
          </div>
        </div>
      </div>

      {/* Violations */}
      {violations && violations.length > 0 && (
        <div className="aurora-card">
          <h2 className="text-xl font-semibold text-slate-200 mb-4">Recent Violations</h2>
          <div className="space-y-2">
            {violations.slice(0, 5).map((violation) => (
              <div
                key={violation.id}
                className="p-3 bg-slate-900/50 rounded-lg border border-slate-800"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-semibold text-slate-200">{violation.code}</p>
                    <p className="text-xs text-slate-400 mt-1">
                      {violation.category} • Severity: {violation.severity}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-semibold text-red-400">+{violation.cp_delta} CP</p>
                    <p className="text-xs text-slate-500">
                      {new Date(violation.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Appeal Section */}
      {cpState.regime !== 'NORMAL' && (
        <div className="aurora-card border-aurora-purple/30">
          <h2 className="text-xl font-semibold text-slate-200 mb-4">Submit Appeal</h2>
          {!showAppeal ? (
            <div>
              <p className="text-slate-300 mb-4">
                If you believe your regime status is incorrect, you can submit an appeal for review.
              </p>
              <button
                onClick={() => setShowAppeal(true)}
                className="aurora-button"
              >
                Submit Appeal
              </button>
            </div>
          ) : (
            <AppealForm
              onSubmit={async (appeal) => {
                // Track appeal submission
                await track('appeal_submitted', {
                  regime: cpState?.regime,
                  cp_value: cpState?.cp_value,
                  reason: appeal.reason,
                })
                // TODO: Implement appeal API call
                console.log('Appeal submitted:', appeal)
                setShowAppeal(false)
              }}
              onCancel={() => setShowAppeal(false)}
            />
          )}
        </div>
      )}
    </div>
  )
}

