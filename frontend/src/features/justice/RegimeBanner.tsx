// RegimeBanner.tsx
// UX Spice: Contextual banners based on regime

import React from "react";
import { Regime, RegimeBadge } from "./RegimeBadge";

interface RegimeBannerProps {
  regime: Regime;
  cp?: number;
  onDismiss?: () => void;
}

const regimeBannerConfig: Record<
  Regime,
  { color: string; icon: string; message: string }
> = {
  NORMAL: {
    color: "bg-emerald-500/10 border-emerald-500/30 text-emerald-300",
    icon: "✓",
    message: "Normal rejim - Tüm haklarınız aktif",
  },
  SOFT_FLAG: {
    color: "bg-yellow-500/10 border-yellow-500/30 text-yellow-300",
    icon: "⚠",
    message: "Yumuşak uyarı - Davranışlarınız Adalet Motoru tarafından izleniyor",
  },
  PROBATION: {
    color: "bg-orange-500/10 border-orange-500/30 text-orange-300",
    icon: "⚡",
    message: "Gözaltı rejimi - Bazı kısıtlamalar aktif, davranışlarınız sıkı takipte",
  },
  RESTRICTED: {
    color: "bg-red-500/10 border-red-500/30 text-red-300",
    icon: "🔒",
    message: "Kısıtlı rejim - Ağır limitler uygulanıyor, bazı aksiyonlar engellendi",
  },
  LOCKDOWN: {
    color: "bg-red-900/30 border-red-700/50 text-red-200",
    icon: "🚫",
    message:
      "Aurora Adalet Rejimi: LOCKDOWN – Tüm aksiyonlar engellendi. Ombudsman incelemesi gereklidir.",
  },
};

export const RegimeBanner: React.FC<RegimeBannerProps> = ({
  regime,
  cp,
  onDismiss,
}) => {
  // Only show banner for non-NORMAL regimes
  if (regime === "NORMAL") {
    return null;
  }

  const config = regimeBannerConfig[regime];

  return (
    <div
      className={`relative border rounded-lg p-4 ${config.color} ${
        regime === "LOCKDOWN" ? "border-l-4" : ""
      }`}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3 flex-1">
          <div className="text-xl">{config.icon}</div>
          <div className="flex-1">
            <div className="text-sm font-medium mb-1">{config.message}</div>
            {cp !== undefined && (
              <div className="text-xs opacity-75">
                Ceza Puanı (CP): {cp} | Rejim: {regime}
              </div>
            )}
          </div>
        </div>
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="text-current opacity-60 hover:opacity-100 transition-opacity"
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
      {regime === "LOCKDOWN" && (
        <div className="mt-3 pt-3 border-t border-red-700/30">
          <a
            href="/admin/aurora/appeal"
            className="text-xs underline hover:no-underline"
          >
            İtiraz et veya Ombudsman'a başvur →
          </a>
        </div>
      )}
    </div>
  );
};

