// apps/citizen-portal/components/RegimeAwareButton.tsx
"use client";

import { ReactNode } from "react";
import { useRegimeTheme } from "@aurora/hooks";

interface RegimeAwareButtonProps {
  children: ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  className?: string;
  actionType?: "message" | "call" | "withdraw" | "transfer" | "default";
}

export function RegimeAwareButton({
  children,
  onClick,
  disabled: externalDisabled,
  className = "",
  actionType = "default",
}: RegimeAwareButtonProps) {
  const theme = useRegimeTheme();

  // Determine if action should be locked based on regime and action type
  const isLockedByRegime = (() => {
    if (theme.regime === "LOCKDOWN") return true;
    if (theme.regime === "RESTRICTED") {
      // RESTRICTED: block critical actions
      return ["message", "call", "withdraw", "transfer"].includes(actionType);
    }
    if (theme.regime === "PROBATION") {
      // PROBATION: block financial actions
      return ["withdraw", "transfer"].includes(actionType);
    }
    return false;
  })();

  const disabled = externalDisabled || isLockedByRegime;

  const getLabel = () => {
    if (theme.regime === "LOCKDOWN") {
      return "LOCKDOWN · Action blocked";
    }
    if (theme.regime === "RESTRICTED" && isLockedByRegime) {
      return "Restricted · Limited access";
    }
    if (theme.regime === "PROBATION" && isLockedByRegime) {
      return "Probation · Action restricted";
    }
    return children;
  };

  const baseClasses = "rounded-xl px-4 py-2 text-sm font-semibold transition border";
  const lockedClasses =
    "bg-gray-900 text-gray-500 border-red-500/40 cursor-not-allowed";
  const activeClasses = "bg-purple-500 hover:bg-purple-400 text-white border-purple-400/60";

  return (
    <button
      onClick={disabled ? undefined : onClick}
      disabled={disabled}
      className={`${baseClasses} ${disabled ? lockedClasses : activeClasses} ${className}`}
      title={
        isLockedByRegime
          ? `Regime: ${theme.regime}. This action is blocked.`
          : undefined
      }
    >
      {getLabel()}
    </button>
  );
}

