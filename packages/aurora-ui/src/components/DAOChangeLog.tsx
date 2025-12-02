import React from 'react'

interface PolicyChange {
  version: string
  changed_at: string
  changed_by: string
  change_type: 'dao_vote' | 'admin_update' | 'sync'
  onchain_tx?: string | null
}

interface DAOChangeLogProps {
  changes: PolicyChange[]
  className?: string
}

export const DAOChangeLog: React.FC<DAOChangeLogProps> = ({ changes, className = '' }) => {
  if (!changes || changes.length === 0) {
    return (
      <div className={`aurora-card ${className}`}>
        <p className="text-sm text-slate-400">No policy changes recorded</p>
      </div>
    )
  }

  return (
    <div className={`aurora-card ${className}`}>
      <h3 className="text-lg font-semibold text-slate-200 mb-4">Policy Change History</h3>
      <div className="space-y-3">
        {changes.map((change, index) => (
          <div
            key={index}
            className="bg-slate-900/50 rounded-lg p-3 border border-slate-800"
          >
            <div className="flex items-start justify-between mb-2">
              <div>
                <span className="text-sm font-semibold text-aurora-purple">v{change.version}</span>
                <span className="text-xs text-slate-400 ml-2">
                  {new Date(change.changed_at).toLocaleString()}
                </span>
              </div>
              <span className="text-xs px-2 py-0.5 bg-slate-800 rounded text-slate-300">
                {change.change_type}
              </span>
            </div>
            <p className="text-xs text-slate-400">Changed by: {change.changed_by}</p>
            {change.onchain_tx && (
              <a
                href={`#tx-${change.onchain_tx}`}
                className="text-xs text-aurora-sky hover:underline mt-1 block"
              >
                View on-chain: {change.onchain_tx.slice(0, 10)}...
              </a>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

