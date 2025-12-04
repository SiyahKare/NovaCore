"use client";

import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import type { Lead } from "@aurora/hooks";

interface Props {
  lead: Lead;
}

const pipelineStages = [
  "New",
  "Contacted",
  "Qualified",
  "Proposal",
  "Won/Lost",
] as const;

export function PipelineCard({ lead }: Props) {
  const currentStageIndex = pipelineStages.findIndex(
    (stage) => stage.toLowerCase() === lead.status.replace("_", " "),
  );

  return (
    <Card className="border-slate-800 bg-slate-950">
      <CardHeader className="py-2">
        <CardTitle className="text-xs text-slate-100">Pipeline & Deal</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3 py-2">
        <div className="flex items-center gap-1 text-[10px]">
          {pipelineStages.map((stage, index) => (
            <div
              key={stage}
              className={`
                flex-1 rounded px-2 py-1 text-center
                ${
                  index === currentStageIndex
                    ? "bg-cyan-500/20 text-cyan-300 ring-1 ring-cyan-500/50"
                    : "bg-slate-800/50 text-slate-400"
                }
              `}
            >
              {stage}
            </div>
          ))}
        </div>
        <div className="flex flex-col gap-1">
          <Button size="sm" variant="outline" className="h-7 text-[10px]">
            Create Deal Draft
          </Button>
          <Button size="sm" variant="outline" className="h-7 text-[10px]">
            Schedule Demo
          </Button>
          <Button size="sm" variant="outline" className="h-7 text-[10px] text-red-300">
            Mark as Lost
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

