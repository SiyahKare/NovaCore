"use client";

import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import type { HandoffEvent } from "@aurora/hooks";

interface Props {
  handoffs: HandoffEvent[];
}

export function HandoffHistory({ handoffs }: Props) {
  if (handoffs.length === 0) {
    return (
      <Card className="border-slate-800 bg-slate-950">
        <CardHeader className="py-2">
          <CardTitle className="text-xs text-slate-100">Handoff History</CardTitle>
        </CardHeader>
        <CardContent className="py-2 text-[10px] text-slate-400">
          Henüz handoff yok.
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-slate-800 bg-slate-950">
      <CardHeader className="py-2">
        <CardTitle className="text-xs text-slate-100">Handoff History</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2 py-2">
        {handoffs.map((handoff) => (
          <div key={handoff.id} className="text-[10px] text-slate-300">
            <div className="flex items-center gap-1">
              <span className="text-slate-400">
                {new Date(handoff.at).toLocaleTimeString("tr-TR", {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </span>
              <span className="text-slate-500">–</span>
              <span className="capitalize">{handoff.from}</span>
              <span className="text-slate-500">→</span>
              <span className="capitalize">{handoff.to}</span>
            </div>
            <div className="mt-1 text-slate-400">{handoff.reason}</div>
            {handoff.note && (
              <div className="mt-1 text-slate-500 italic">{handoff.note}</div>
            )}
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

