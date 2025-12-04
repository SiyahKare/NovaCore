"use client";

import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface Props {
  totalCallsToday?: number;
  hotCount?: number;
  warmCount?: number;
  coldCount?: number;
  agentMode: "ai-only" | "hybrid" | "human-only";
  onAgentModeChange: (mode: Props["agentMode"]) => void;
}

export function TopBar({
  totalCallsToday,
  hotCount,
  warmCount,
  coldCount,
  agentMode,
  onAgentModeChange,
}: Props) {
  return (
    <header className="flex items-center justify-between border-b border-slate-800 bg-slate-950/80 px-4 py-2 text-xs backdrop-blur">
      <div className="flex items-center gap-2">
        <div className="h-6 w-6 rounded-md bg-gradient-to-br from-cyan-400 to-violet-500" />
        <div>
          <div className="text-[11px] font-semibold tracking-wide text-slate-100">
            AURORA CONTACT
          </div>
          <div className="text-[10px] uppercase text-slate-400">Telegram Console</div>
        </div>
        <Badge variant="outline" className="ml-2 border-emerald-500/60 text-[10px] text-emerald-300">
          🟢 AI Hunter: Active
        </Badge>
      </div>

      <div className="hidden items-center gap-4 md:flex">
        <div className="flex items-center gap-2 text-slate-300">
          <span>Bugün aranan:</span>
          <span className="font-semibold text-slate-100">{totalCallsToday ?? 0}</span>
        </div>
        <div className="flex items-center gap-2 text-[11px]">
          <Badge className="bg-red-500/20 text-red-300">Hot {hotCount ?? 0}</Badge>
          <Badge className="bg-amber-500/20 text-amber-300">Warm {warmCount ?? 0}</Badge>
          <Badge className="bg-slate-700 text-slate-200">Cold {coldCount ?? 0}</Badge>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <ModeChip
          label="AI ONLY"
          active={agentMode === "ai-only"}
          onClick={() => onAgentModeChange("ai-only")}
        />
        <ModeChip
          label="HYBRID"
          active={agentMode === "hybrid"}
          onClick={() => onAgentModeChange("hybrid")}
        />
        <ModeChip
          label="HUMAN"
          active={agentMode === "human-only"}
          onClick={() => onAgentModeChange("human-only")}
        />
        <Button variant="ghost" size="icon" className="h-7 w-7 text-slate-400">
          ⚙
        </Button>
      </div>
    </header>
  );
}

function ModeChip({
  label,
  active,
  onClick,
}: {
  label: string;
  active?: boolean;
  onClick?: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "rounded-full px-2 py-1 text-[10px] uppercase tracking-wide",
        "border border-slate-700 text-slate-300 hover:border-cyan-500/70 hover:text-cyan-200",
        active && "border-cyan-400 bg-cyan-400/10 text-cyan-100",
      )}
    >
      {label}
    </button>
  );
}

