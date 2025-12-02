// AuroraEnforcementError.tsx
// Error handling component for Aurora enforcement 403 errors

import React from "react";

interface AuroraEnforcementErrorData {
  error: "AURORA_ENFORCEMENT_BLOCKED";
  message: string;
  regime: "NORMAL" | "SOFT_FLAG" | "PROBATION" | "RESTRICTED" | "LOCKDOWN";
  cp_value: number;
  action?: string;
}

interface AuroraEnforcementErrorProps {
  error: AuroraEnforcementErrorData;
  onDismiss?: () => void;
  showAppealLink?: boolean;
}

const regimeLabel: Record<AuroraEnforcementErrorData["regime"], string> = {
  NORMAL: "Normal",
  SOFT_FLAG: "Yumuşak Uyarı",
  PROBATION: "Gözaltı",
  RESTRICTED: "Kısıtlı",
  LOCKDOWN: "Kilitli",
};

const regimeColorClass: Record<AuroraEnforcementErrorData["regime"], string> = {
  NORMAL: "bg-emerald-100 text-emerald-800 border-emerald-300",
  SOFT_FLAG: "bg-yellow-100 text-yellow-800 border-yellow-300",
  PROBATION: "bg-orange-100 text-orange-800 border-orange-300",
  RESTRICTED: "bg-red-100 text-red-800 border-red-300",
  LOCKDOWN: "bg-red-900 text-red-100 border-red-700",
};

export const AuroraEnforcementError: React.FC<AuroraEnforcementErrorProps> = ({
  error,
  onDismiss,
  showAppealLink = true,
}) => {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="bg-slate-900 border border-red-500/50 rounded-2xl p-6 max-w-md w-full mx-4 shadow-2xl">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-full bg-red-500/20 flex items-center justify-center">
              <svg
                className="w-6 h-6 text-red-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
            </div>
            <div>
              <div className="text-sm font-semibold text-red-400">
                Aurora Adalet Engeli
              </div>
              <div className="text-xs text-slate-400">
                Bu işlem şu an gerçekleştirilemez
              </div>
            </div>
          </div>
          {onDismiss && (
            <button
              onClick={onDismiss}
              className="text-slate-400 hover:text-slate-200 transition-colors"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          )}
        </div>

        {/* Regime Badge */}
        <div className="mb-4">
          <div
            className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full border text-xs font-semibold ${regimeColorClass[error.regime]}`}
          >
            <span>Rejim:</span>
            <span>{regimeLabel[error.regime]}</span>
            <span className="ml-1">(CP: {error.cp_value})</span>
          </div>
        </div>

        {/* Message */}
        <div className="mb-4 text-sm text-slate-200 leading-relaxed">
          {error.message}
        </div>

        {/* Details */}
        <div className="mb-4 p-3 bg-slate-800/50 rounded-lg text-xs text-slate-400 space-y-1">
          <div className="flex justify-between">
            <span>Ceza Puanı (CP):</span>
            <span className="font-mono text-red-300">{error.cp_value}</span>
          </div>
          <div className="flex justify-between">
            <span>Rejim Seviyesi:</span>
            <span className="font-mono">{error.regime}</span>
          </div>
          {error.action && (
            <div className="flex justify-between">
              <span>Engellenen Aksiyon:</span>
              <span className="font-mono">{error.action}</span>
            </div>
          )}
        </div>

        {/* Info */}
        <div className="mb-4 text-xs text-slate-500 leading-relaxed">
          CP değeri zamanla otomatik olarak azalır. Yüksek CP değerleri ve
          LOCKDOWN rejimi, Ombudsman incelemesi gerektirir.
        </div>

        {/* Actions */}
        <div className="flex gap-2">
          {showAppealLink && (
            <a
              href="/admin/aurora/appeal"
              className="flex-1 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-sm font-medium transition-colors text-center"
            >
              İtiraz Et
            </a>
          )}
          <button
            onClick={onDismiss}
            className="flex-1 px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg text-sm font-medium transition-colors"
          >
            Anladım
          </button>
        </div>
      </div>
    </div>
  );
};

// Hook for handling enforcement errors
export const useAuroraEnforcementError = () => {
  const [error, setError] = React.useState<AuroraEnforcementErrorData | null>(
    null
  );

  const handleError = (err: any) => {
    // Check if it's an Aurora enforcement error
    if (
      err?.response?.status === 403 &&
      err?.response?.data?.error === "AURORA_ENFORCEMENT_BLOCKED"
    ) {
      setError(err.response.data);
      return true;
    }
    return false;
  };

  const clearError = () => {
    setError(null);
  };

  return {
    error,
    handleError,
    clearError,
  };
};

