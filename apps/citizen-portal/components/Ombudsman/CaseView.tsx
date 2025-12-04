"use client";

import { useState, useEffect } from "react";
import { useAuroraAPI } from "@aurora/hooks";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";

interface CaseViewProps {
  caseId: number;
  caseType: "appeal" | "violation";
  userId: string | number;
}

export function CaseView({ caseId, caseType, userId }: CaseViewProps) {
  const { fetchAPI } = useAuroraAPI();
  const [caseData, setCaseData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadCase = async () => {
      setIsLoading(true);
      setError(null);

      try {
        // Get case file
        const { data, error: apiError } = await fetchAPI(
          `/justice/case/${userId}`
        );

        if (apiError) {
          setError(apiError.detail || "Failed to load case");
          setCaseData(null);
        } else {
          setCaseData(data);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
        setCaseData(null);
      } finally {
        setIsLoading(false);
      }
    };

    if (userId) {
      loadCase();
    }
  }, [userId, fetchAPI]);

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center text-xs text-slate-400">
        Yükleniyor...
      </div>
    );
  }

  if (error || !caseData) {
    return (
      <div className="flex h-full items-center justify-center text-xs text-red-400">
        {error || "Case data not found"}
      </div>
    );
  }

  const cpState = caseData.cp_state;
  const regime = cpState?.regime || "NORMAL";
  const cpValue = cpState?.cp_value || 0;
  const isLockdown = regime === "LOCKDOWN";
  const isRestricted = regime === "RESTRICTED";

  return (
    <ScrollArea className="h-full">
      <div className="space-y-4 p-4">
        {/* CP / Regime Warning */}
        {(isLockdown || isRestricted) && (
          <Card className={cn(
            "border-2",
            isLockdown ? "border-red-500 bg-red-500/10" : "border-amber-500 bg-amber-500/10"
          )}>
            <CardHeader className="py-3">
              <CardTitle className="text-sm text-red-300">
                ⚠️ {isLockdown ? "LOCKDOWN" : "RESTRICTED"} REGIME
              </CardTitle>
            </CardHeader>
            <CardContent className="py-2">
              <div className="text-xs text-slate-300">
                CP Value: <span className="font-bold text-red-400">{cpValue}</span>
              </div>
              <div className="mt-1 text-[10px] text-slate-400">
                Kullanıcı {isLockdown ? "tam kısıtlama" : "kısmi kısıtlama"} durumunda.
              </div>
            </CardContent>
          </Card>
        )}

        {/* User Snapshot */}
        <Card className="border-slate-800 bg-slate-950">
          <CardHeader className="py-3">
            <CardTitle className="text-sm text-slate-100">👤 User Snapshot</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 py-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="text-slate-400">User ID:</span>
              <span className="text-slate-200">{userId}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-400">CP Value:</span>
              <Badge
                className={cn(
                  cpValue >= 100
                    ? "bg-red-500/20 text-red-300"
                    : cpValue >= 50
                    ? "bg-amber-500/20 text-amber-300"
                    : "bg-slate-700 text-slate-200"
                )}
              >
                {cpValue}
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Regime:</span>
              <Badge
                className={cn(
                  regime === "LOCKDOWN"
                    ? "bg-red-500/20 text-red-300"
                    : regime === "RESTRICTED"
                    ? "bg-amber-500/20 text-amber-300"
                    : "bg-slate-700 text-slate-200"
                )}
              >
                {regime}
              </Badge>
            </div>
            {caseData.nova_score && (
              <div className="flex items-center justify-between">
                <span className="text-slate-400">NovaScore:</span>
                <span className="text-slate-200">{caseData.nova_score.value}</span>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Violator Stats */}
        <Card className="border-slate-800 bg-slate-950">
          <CardHeader className="py-3">
            <CardTitle className="text-sm text-slate-100">📊 Violator Stats</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 py-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="text-slate-400">RiskScore:</span>
              <Badge className="bg-slate-700 text-slate-200">
                {caseData.risk_score || "N/A"}
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Recent Violations:</span>
              <span className="text-slate-200">
                {caseData.recent_violations?.length || 0}
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Proof / Evidence */}
        <Card className="border-slate-800 bg-slate-950">
          <CardHeader className="py-3">
            <CardTitle className="text-sm text-slate-100">📎 Proof / Evidence</CardTitle>
          </CardHeader>
          <CardContent className="py-2">
            <div className="text-xs text-slate-400">
              Proof payload reference will be displayed here.
            </div>
            {/* TODO: Display actual proof (image, text, etc.) */}
          </CardContent>
        </Card>
      </div>
    </ScrollArea>
  );
}

