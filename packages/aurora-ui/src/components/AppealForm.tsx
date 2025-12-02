import React, { useState } from 'react'

interface AppealFormProps {
  onSubmit: (appeal: { reason: string; details: string }) => void
  onCancel?: () => void
  className?: string
}

export const AppealForm: React.FC<AppealFormProps> = ({ onSubmit, onCancel, className = '' }) => {
  const [reason, setReason] = useState('')
  const [details, setDetails] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (reason.trim() && details.trim()) {
      onSubmit({ reason, details })
    }
  }

  return (
    <div className={`aurora-card max-w-lg mx-auto ${className}`}>
      <h2 className="text-xl font-bold text-slate-200 mb-4">Submit Appeal</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm text-slate-300 mb-2">Reason</label>
          <select
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            className="aurora-input"
            required
          >
            <option value="">Select a reason</option>
            <option value="false_positive">False Positive</option>
            <option value="extenuating_circumstances">Extenuating Circumstances</option>
            <option value="policy_disagreement">Policy Disagreement</option>
            <option value="other">Other</option>
          </select>
        </div>
        <div>
          <label className="block text-sm text-slate-300 mb-2">Details</label>
          <textarea
            value={details}
            onChange={(e) => setDetails(e.target.value)}
            rows={5}
            className="aurora-input"
            placeholder="Explain your appeal in detail..."
            required
          />
        </div>
        <div className="flex gap-3">
          {onCancel && (
            <button type="button" onClick={onCancel} className="aurora-button-secondary flex-1">
              Cancel
            </button>
          )}
          <button type="submit" className="aurora-button flex-1">
            Submit Appeal
          </button>
        </div>
      </form>
    </div>
  )
}

