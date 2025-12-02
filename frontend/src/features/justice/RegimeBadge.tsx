// RegimeBadge.tsx
// Reusable regime badge component for user profiles, cards, etc.

import React from "react";

export type Regime = "NORMAL" | "SOFT_FLAG" | "PROBATION" | "RESTRICTED" | "LOCKDOWN";

interface RegimeBadgeProps {
  regime: Regime;
  cp?: number;
  size?: "sm" | "md" | "lg";
  showTooltip?: boolean;
}

const regimeLabel: Record<Regime, string> = {
  NORMAL: "Normal",
  SOFT_FLAG: "Yumuşak Uyarı",
  PROBATION: "Gözaltı",
  RESTRICTED: "Kısıtlı",
  LOCKDOWN: "Kilitli",
};

const regimeColorClass: Record<Regime, string> = {
  NORMAL: "bg-emerald-100 text-emerald-800 border-emerald-300",
  SOFT_FLAG: "bg-yellow-100 text-yellow-800 border-yellow-300",
  PROBATION: "bg-orange-100 text-orange-800 border-orange-300",
  RESTRICTED: "bg-red-100 text-red-800 border-red-300",
  LOCKDOWN: "bg-red-900 text-red-100 border-red-700",
};

const sizeClasses = {
  sm: "px-2 py-0.5 text-xs",
  md: "px-3 py-1 text-sm",
  lg: "px-4 py-1.5 text-base",
};

const regimeTooltip: Record<Regime, string> = {
  NORMAL: "Normal rejim - Tüm haklar aktif",
  SOFT_FLAG: "Yumuşak uyarı - Davranışlar izleniyor",
  PROBATION: "Gözaltı - Bazı kısıtlamalar aktif",
  RESTRICTED: "Kısıtlı - Ağır limitler uygulanıyor",
  LOCKDOWN: "Kilitli - Tüm aksiyonlar engellendi, Ombudsman incelemesi gereklidir",
};

export const RegimeBadge: React.FC<RegimeBadgeProps> = ({
  regime,
  cp,
  size = "md",
  showTooltip = false,
}) => {
  const badge = (
    <span
      className={`inline-flex items-center gap-1 rounded-full border font-semibold ${regimeColorClass[regime]} ${sizeClasses[size]}`}
    >
      <span>{regimeLabel[regime]}</span>
      {cp !== undefined && <span className="font-mono">(CP: {cp})</span>}
    </span>
  );

  if (showTooltip) {
    return (
      <div className="group relative inline-block">
        {badge}
        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block z-50">
          <div className="bg-slate-900 text-white text-xs rounded-lg py-2 px-3 shadow-xl border border-slate-700 max-w-xs">
            {regimeTooltip[regime]}
            {cp !== undefined && (
              <div className="mt-1 text-slate-400">
                Ceza Puanı: {cp}
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  return badge;
};

// Helper function for getting regime style
export const getRegimeStyle = (regime: Regime) => {
  return {
    label: regimeLabel[regime],
    colorClass: regimeColorClass[regime],
    tooltip: regimeTooltip[regime],
  };
};

