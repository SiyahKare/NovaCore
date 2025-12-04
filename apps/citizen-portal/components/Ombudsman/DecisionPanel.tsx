"use client";

import { useState } from "react";
import { useOmbudsmanDecision } from "@aurora/hooks";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";

interface DecisionPanelProps {
  caseId: number;
  userId: string | number;
  currentRiskScore?: number;
  onDecisionSubmitted?: () => void;
}

export function DecisionPanel({
  caseId,
  userId,
  currentRiskScore,
  onDecisionSubmitted,
}: DecisionPanelProps) {
  const [note, setNote] = useState("");
  const { submitDecision, isSubmitting } = useOmbudsmanDecision();

  const handleSubmitDecision = async (decision: "APPROVE" | "REJECT") => {
    if (!note && decision === "REJECT") {
      alert("Red kararı için not girmek zorunludur.");
      return;
    }

    try {
      const result = await submitDecision(caseId, decision, note || undefined);

      if (result?.success) {
        alert(
          `Karar işlendi: ${decision}\n` +
          (result.risk_score_after !== undefined
            ? `Yeni RiskScore: ${result.risk_score_after.toFixed(1)}`
            : "")
        );
        setNote("");
        onDecisionSubmitted?.();
      } else {
        alert("Karar işlenirken hata oluştu.");
      }
    } catch (error) {
      alert(
        `Hata: ${error instanceof Error ? error.message : "Bilinmeyen hata"}`
      );
    }
  };

  return (
    <Card className="border-2 border-slate-700 bg-slate-900">
      <CardHeader className="py-3">
        <CardTitle className="text-lg font-bold text-red-400">
          ⚖️ NASIPCOURT KARAR BÖLÜMÜ
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4 py-4">
        {/* RiskScore Display */}
        {currentRiskScore !== undefined && (
          <div>
            <label className="block text-sm text-slate-300 mb-1">
              RiskScore Güncel Durum:
            </label>
            <Badge
              className={
                currentRiskScore >= 8.0
                  ? "bg-red-500/20 text-red-300"
                  : currentRiskScore >= 6.0
                  ? "bg-amber-500/20 text-amber-300"
                  : "bg-slate-700 text-slate-200"
              }
            >
              {currentRiskScore.toFixed(1)}
            </Badge>
            <p className="text-xs text-yellow-500 mt-1">
              REJECT olursa: RiskScore +2.0, MANUAL_FLAG loglanır.
            </p>
          </div>
        )}

        {/* Note Textarea */}
        <div>
          <label className="block text-sm text-slate-300 mb-1">
            Gerekçe ve Notlar:
          </label>
          <Textarea
            value={note}
            onChange={(e) => setNote(e.target.value)}
            placeholder="Gerekçe ve notlarınızı buraya girin (Red kararı için zorunludur)..."
            className="min-h-[100px] bg-slate-800 border-slate-700 text-sm text-slate-100 placeholder:text-slate-500"
            rows={4}
          />
        </div>

        {/* Decision Buttons */}
        <div className="flex justify-between gap-3">
          <Button
            onClick={() => handleSubmitDecision("APPROVE")}
            disabled={isSubmitting}
            className="flex-1 bg-green-700 hover:bg-green-600 text-white font-bold py-2 px-4 rounded transition disabled:opacity-50"
          >
            ✅ ONAYLA (Ödül Ver)
          </Button>
          <Button
            onClick={() => handleSubmitDecision("REJECT")}
            disabled={isSubmitting || !note.trim()}
            className="flex-1 bg-red-700 hover:bg-red-600 text-white font-bold py-2 px-4 rounded transition disabled:opacity-50"
          >
            ❌ REDDET (Ceza Uygula)
          </Button>
        </div>

        {/* Enforcement Preview */}
        <div className="rounded-md border border-slate-700 bg-slate-800/50 p-2 text-xs text-slate-400">
          <div className="font-semibold text-slate-300 mb-1">
            Enforcement Preview:
          </div>
          <div className="space-y-1">
            <div>• APPROVE: Ödül verilir, RiskScore azalabilir</div>
            <div>• REJECT: RiskScore +2.0, MANUAL_FLAG loglanır</div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

