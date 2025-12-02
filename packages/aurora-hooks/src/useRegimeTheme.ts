// packages/aurora-hooks/src/useRegimeTheme.ts
import { useMemo } from "react";
import { useJustice } from "./useJustice";

export type AuroraRegime =
  | "NORMAL"
  | "SOFT_FLAG"
  | "PROBATION"
  | "RESTRICTED"
  | "LOCKDOWN";

export interface RegimeTheme {
  regime: AuroraRegime;
  intensity: number; // 0.0 - 1.0
  bgClass: string;
  borderClass: string;
  glowClass: string;
  accentClass: string;
  warningLevel: "none" | "soft" | "hard" | "critical";
}

export function useRegimeTheme(): RegimeTheme {
  const { cpState } = useJustice();

  const regime = (cpState?.regime ?? "NORMAL") as AuroraRegime;

  return useMemo<RegimeTheme>(() => {
    switch (regime) {
      case "SOFT_FLAG":
        return {
          regime,
          intensity: 0.2,
          bgClass:
            "bg-gradient-to-br from-slate-900 via-slate-950 to-purple-950",
          borderClass: "border-yellow-500/40",
          glowClass: "shadow-[0_0_26px_rgba(234,179,8,0.25)]",
          accentClass: "text-yellow-300",
          warningLevel: "soft",
        };

      case "PROBATION":
        return {
          regime,
          intensity: 0.5,
          bgClass:
            "bg-gradient-to-br from-slate-950 via-purple-950 to-rose-950",
          borderClass: "border-orange-500/45",
          glowClass: "shadow-[0_0_32px_rgba(249,115,22,0.35)]",
          accentClass: "text-orange-300",
          warningLevel: "hard",
        };

      case "RESTRICTED":
        return {
          regime,
          intensity: 0.75,
          bgClass:
            "bg-gradient-to-br from-black via-rose-950 to-red-950 saturate-150",
          borderClass: "border-red-500/55",
          glowClass: "shadow-[0_0_40px_rgba(239,68,68,0.5)]",
          accentClass: "text-red-300",
          warningLevel: "hard",
        };

      case "LOCKDOWN":
        return {
          regime,
          intensity: 1,
          bgClass:
            "bg-[radial-gradient(circle_at_top,_#05010f_0,_#02010a_45%,_#000_100%)]",
          borderClass: "border-red-500/70",
          glowClass: "shadow-[0_0_55px_rgba(248,113,113,0.7)]",
          accentClass: "text-red-300",
          warningLevel: "critical",
        };

      case "NORMAL":
      default:
        return {
          regime: "NORMAL",
          intensity: 0,
          bgClass:
            "bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950",
          borderClass: "border-purple-500/30",
          glowClass: "shadow-[0_0_24px_rgba(168,85,247,0.3)]",
          accentClass: "text-purple-300",
          warningLevel: "none",
        };
    }
  }, [regime]);
}

