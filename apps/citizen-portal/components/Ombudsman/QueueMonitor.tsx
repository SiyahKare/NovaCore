"use client";

import { useOmbudsmanAppeals, useOmbudsmanViolations, type PendingAppeal, type PendingViolation } from "@aurora/hooks";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";

interface QueueMonitorProps {
  onSelectCase: (caseId: number, type: "appeal" | "violation", userId: string | number) => void;
  selectedCaseId?: number;
}

export function QueueMonitor({ onSelectCase, selectedCaseId }: QueueMonitorProps) {
  const { appeals, isLoading: appealsLoading } = useOmbudsmanAppeals();
  const { violations, isLoading: violationsLoading } = useOmbudsmanViolations();

  const totalPending = appeals.length + violations.length;
  const highRiskCount = violations.filter(v => (v.risk_score ?? 0) >= 8.0).length;

  return (
    <div className="flex h-full flex-col gap-4">
      {/* Quick Stats */}
      <Card className="border-slate-800 bg-slate-950">
        <CardHeader className="py-3">
          <CardTitle className="text-sm text-slate-100">📊 Queue Stats</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 py-2">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-400">Total Pending:</span>
            <Badge className="bg-slate-800 text-slate-100">{totalPending}</Badge>
          </div>
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-400">High Risk (≥8.0):</span>
            <Badge className="bg-red-500/20 text-red-300">{highRiskCount}</Badge>
          </div>
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-400">Appeals:</span>
            <Badge className="bg-amber-500/20 text-amber-300">{appeals.length}</Badge>
          </div>
        </CardContent>
      </Card>

      {/* HITL Queue */}
      <Card className="flex-1 border-slate-800 bg-slate-950">
        <CardHeader className="py-3">
          <CardTitle className="text-sm text-slate-100">🔍 HITL Queue</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <ScrollArea className="h-[300px]">
            {violationsLoading ? (
              <div className="p-4 text-center text-xs text-slate-400">Yükleniyor...</div>
            ) : violations.length === 0 ? (
              <div className="p-4 text-center text-xs text-slate-400">HITL kuyruğu boş</div>
            ) : (
              <div className="space-y-1 p-2">
                {violations.map((violation) => {
                  const violationId = typeof violation.id === 'string' ? parseInt(violation.id) || violation.id : violation.id;
                  const riskScore = violation.risk_score ?? 0;
                  const displayTitle = violation.title || violation.code || `Case ${violation.id}`;
                  const displayType = violation.type || (violation.score_ai ? "RiskEvent" : "Unknown");
                  
                  return (
                    <button
                      key={violation.id}
                      onClick={() => onSelectCase(Number(violationId), "violation", violation.user_id)}
                      className={cn(
                        "w-full rounded-md border p-2 text-left text-xs transition hover:bg-slate-900",
                        selectedCaseId === Number(violationId)
                          ? "border-cyan-500 bg-cyan-500/10"
                          : "border-slate-800 bg-slate-900/50"
                      )}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-medium text-slate-200">{displayTitle}</span>
                        <Badge
                          className={cn(
                            "text-[10px]",
                            riskScore >= 8.0
                              ? "bg-red-500/20 text-red-300"
                              : riskScore >= 6.0
                              ? "bg-amber-500/20 text-amber-300"
                              : "bg-slate-700 text-slate-200"
                          )}
                        >
                          {riskScore.toFixed(1)}
                        </Badge>
                      </div>
                      <div className="mt-1 text-[10px] text-slate-400">
                        {displayType} • User: {violation.user_id}
                        {violation.score_ai !== undefined && ` • AI: ${violation.score_ai.toFixed(1)}`}
                      </div>
                    </button>
                  );
                })}
              </div>
            )}
          </ScrollArea>
        </CardContent>
      </Card>

      {/* Appeal Queue */}
      <Card className="flex-1 border-slate-800 bg-slate-950">
        <CardHeader className="py-3">
          <CardTitle className="text-sm text-slate-100">⚖️ Appeal Queue</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <ScrollArea className="h-[300px]">
            {appealsLoading ? (
              <div className="p-4 text-center text-xs text-slate-400">Yükleniyor...</div>
            ) : appeals.length === 0 ? (
              <div className="p-4 text-center text-xs text-slate-400">İtiraz kuyruğu boş</div>
            ) : (
              <div className="space-y-1 p-2">
                {appeals.map((appeal) => (
                  <button
                    key={appeal.id}
                    onClick={() => onSelectCase(appeal.id, "appeal", appeal.user_id)}
                    className={cn(
                      "w-full rounded-md border p-2 text-left text-xs transition hover:bg-slate-900",
                      selectedCaseId === appeal.id
                        ? "border-cyan-500 bg-cyan-500/10"
                        : "border-slate-800 bg-slate-900/50"
                    )}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-slate-200">Appeal #{appeal.id}</span>
                      {appeal.risk_score !== undefined && (
                        <Badge
                          className={cn(
                            "text-[10px]",
                            appeal.risk_score >= 8.0
                              ? "bg-red-500/20 text-red-300"
                              : "bg-slate-700 text-slate-200"
                          )}
                        >
                          {appeal.risk_score.toFixed(1)}
                        </Badge>
                      )}
                    </div>
                    <div className="mt-1 line-clamp-2 text-[10px] text-slate-400">
                      {appeal.reason}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  );
}

