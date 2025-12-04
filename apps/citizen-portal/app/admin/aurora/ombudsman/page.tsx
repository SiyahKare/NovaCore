"use client";

import { useState } from "react";
import { QueueMonitor } from "@/components/Ombudsman/QueueMonitor";
import { CaseView } from "@/components/Ombudsman/CaseView";
import { DecisionPanel } from "@/components/Ombudsman/DecisionPanel";

export default function OmbudsmanDashboardPage() {
  const [selectedCaseId, setSelectedCaseId] = useState<number | undefined>();
  const [selectedCaseType, setSelectedCaseType] = useState<"appeal" | "violation">("violation");
  const [selectedUserId, setSelectedUserId] = useState<string | number | undefined>();

  const handleSelectCase = (
    caseId: number,
    type: "appeal" | "violation",
    userId: string | number
  ) => {
    setSelectedCaseId(caseId);
    setSelectedCaseType(type);
    setSelectedUserId(userId);
  };

  const handleDecisionSubmitted = () => {
    // Refresh queues after decision
    setSelectedCaseId(undefined);
    setSelectedUserId(undefined);
  };

  return (
    <div className="flex h-[calc(100vh-12rem)] flex-col bg-slate-950 text-slate-50 rounded-lg border border-slate-800 overflow-hidden">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-950/80 px-6 py-4 flex-shrink-0">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-slate-100">
              ⚖️ Ombudsman Kokpiti - NasipCourt DAO v1.0
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Validator/HITL ve Appeal karar verme paneli
            </p>
          </div>
          <div className="flex gap-2">
            <a
              href="/admin/aurora/ombudsman/stats"
              className="rounded-lg border border-white/15 px-3 py-1.5 text-[11px] text-gray-200 hover:bg-white/5 transition"
            >
              Justice Stats
            </a>
            <a
              href="/admin/aurora/stats"
              className="rounded-lg border border-white/15 px-3 py-1.5 text-[11px] text-gray-200 hover:bg-white/5 transition"
            >
              Full Stats
            </a>
          </div>
        </div>
      </header>

      {/* 3-Column Layout */}
      <div className="flex flex-1 overflow-hidden">
        {/* Column 1: Queue Monitor */}
        <aside className="w-[320px] border-r border-slate-800 bg-slate-950/90 p-4 overflow-y-auto">
          <QueueMonitor
            onSelectCase={handleSelectCase}
            selectedCaseId={selectedCaseId}
          />
        </aside>

        {/* Column 2: Case File & Evidence */}
        <main className="flex-1 border-r border-slate-800 bg-slate-950/90 overflow-y-auto">
          {selectedCaseId && selectedUserId ? (
            <CaseView
              caseId={selectedCaseId}
              caseType={selectedCaseType}
              userId={selectedUserId}
            />
          ) : (
            <div className="flex h-full items-center justify-center text-xs text-slate-500">
              Bir vaka seçin
            </div>
          )}
        </main>

        {/* Column 3: Decision Panel */}
        <aside className="w-[400px] bg-slate-950/90 p-4 overflow-y-auto">
          {selectedCaseId && selectedUserId ? (
            <DecisionPanel
              caseId={selectedCaseId}
              userId={selectedUserId}
              currentRiskScore={undefined} // TODO: Get from case data
              onDecisionSubmitted={handleDecisionSubmitted}
            />
          ) : (
            <div className="flex h-full items-center justify-center text-xs text-slate-500">
              Karar vermek için bir vaka seçin
            </div>
          )}
        </aside>
      </div>
    </div>
  );
}

