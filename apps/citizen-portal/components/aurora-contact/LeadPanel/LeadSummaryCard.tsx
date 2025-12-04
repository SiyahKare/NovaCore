"use client";

import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { Lead } from "@aurora/hooks";

interface Props {
  lead: Lead;
}

export function LeadSummaryCard({ lead }: Props) {
  return (
    <Card className="border-slate-800 bg-slate-950">
      <CardHeader className="py-2">
        <CardTitle className="text-xs text-slate-100">Lead Snapshot</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2 py-2 text-[11px]">
        <div className="font-semibold text-slate-100">{lead.businessName}</div>
        {lead.telegramUsername && (
          <div className="text-slate-400">@{lead.telegramUsername}</div>
        )}
        <div className="flex flex-wrap gap-1 pt-1">
          <Badge className="bg-slate-800 text-[10px]">
            Score: {lead.score}/100
          </Badge>
          <Badge className="bg-slate-800 text-[10px] capitalize">
            Segment: {lead.segment}
          </Badge>
          <Badge className="bg-slate-800 text-[10px]">
            Priority: {lead.priority.toUpperCase()}
          </Badge>
          <Badge className="bg-slate-800 text-[10px]">
            Risk: {lead.risk.toUpperCase()}
          </Badge>
        </div>
        <div className="pt-1 text-slate-300">
          <div>Sektör: {lead.sector}</div>
          {lead.city && <div>Şehir: {lead.city}</div>}
          {lead.monthlyMsgVolumeEst && (
            <div>Mesaj hacmi: {lead.monthlyMsgVolumeEst}</div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

