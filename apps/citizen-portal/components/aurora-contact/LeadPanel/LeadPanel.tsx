"use client";

import { LeadSummaryCard } from "./LeadSummaryCard";
import { PipelineCard } from "./PipelineCard";
import { NotesCard } from "./NotesCard";
import { HandoffHistory } from "./HandoffHistory";
import type { Lead, HandoffEvent } from "@aurora/hooks";

interface Props {
  lead: Lead | null;
  handoffs: HandoffEvent[];
}

export function LeadPanel({ lead, handoffs }: Props) {
  if (!lead) {
    return (
      <div className="flex h-full items-center justify-center text-xs text-slate-500">
        Lead seçildiğinde istihbarat burada görünecek.
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col gap-2 bg-slate-950/90 p-2 text-xs">
      <LeadSummaryCard lead={lead} />
      <PipelineCard lead={lead} />
      <NotesCard leadId={lead.id} />
      <HandoffHistory handoffs={handoffs} />
    </div>
  );
}

