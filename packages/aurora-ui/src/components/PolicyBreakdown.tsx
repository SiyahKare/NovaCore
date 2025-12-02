import React from 'react'
import type { PolicyParams } from '../types'

interface PolicyBreakdownProps {
  policy: PolicyParams
  className?: string
}

export const PolicyBreakdown: React.FC<PolicyBreakdownProps> = ({
  policy,
  className = '',
}) => {
  return (
    <div className={`aurora-card ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-slate-200">Policy Parameters</h3>
        <span className="text-xs text-slate-400">v{policy.version}</span>
      </div>

      <div className="space-y-4">
        {/* Decay */}
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-slate-400">Decay per Day</span>
            <span className="text-slate-200 font-medium">{policy.decay_per_day} CP</span>
          </div>
        </div>

        {/* Base Weights */}
        <div>
          <p className="text-xs text-slate-400 mb-2">Base CP Weights</p>
          <div className="grid grid-cols-2 gap-2">
            <div className="bg-slate-900/50 rounded p-2">
              <span className="text-xs text-slate-400">EKO</span>
              <span className="block text-sm font-semibold text-slate-200">
                {policy.base_eko}
              </span>
            </div>
            <div className="bg-slate-900/50 rounded p-2">
              <span className="text-xs text-slate-400">COM</span>
              <span className="block text-sm font-semibold text-slate-200">
                {policy.base_com}
              </span>
            </div>
            <div className="bg-slate-900/50 rounded p-2">
              <span className="text-xs text-slate-400">SYS</span>
              <span className="block text-sm font-semibold text-slate-200">
                {policy.base_sys}
              </span>
            </div>
            <div className="bg-slate-900/50 rounded p-2">
              <span className="text-xs text-slate-400">TRUST</span>
              <span className="block text-sm font-semibold text-slate-200">
                {policy.base_trust}
              </span>
            </div>
          </div>
        </div>

        {/* Thresholds */}
        <div>
          <p className="text-xs text-slate-400 mb-2">Regime Thresholds</p>
          <div className="space-y-1">
            <div className="flex justify-between text-xs">
              <span className="text-yellow-400">SOFT_FLAG</span>
              <span className="text-slate-300">{policy.threshold_soft_flag}</span>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-orange-400">PROBATION</span>
              <span className="text-slate-300">{policy.threshold_probation}</span>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-red-400">RESTRICTED</span>
              <span className="text-slate-300">{policy.threshold_restricted}</span>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-purple-400">LOCKDOWN</span>
              <span className="text-slate-300">{policy.threshold_lockdown}</span>
            </div>
          </div>
        </div>

        {policy.onchain_block && (
          <div className="pt-3 border-t border-slate-800">
            <p className="text-xs text-slate-400">
              Synced from chain at block {policy.onchain_block}
            </p>
            <p className="text-xs text-slate-500 mt-1">
              {new Date(policy.synced_at).toLocaleString()}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

