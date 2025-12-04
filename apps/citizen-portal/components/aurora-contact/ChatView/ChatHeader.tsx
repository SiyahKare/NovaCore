"use client";

import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useAuroraAPI, type Conversation, type Lead } from "@aurora/hooks";

interface Props {
  conversation: Conversation;
  lead: Lead;
  agentMode: "ai-only" | "hybrid" | "human-only";
}

export function ChatHeader({ conversation, lead }: Props) {
  const { fetchAPI } = useAuroraAPI();

  const handleHandoff = async () => {
    try {
      const { data, error } = await fetchAPI(
        `/admin/telegram/conversations/${conversation.id}/handoff?reason=manual_handoff`,
        {
          method: "POST",
        }
      );
      
      if (error) {
        alert(`Hata: ${error.detail || 'Handoff tetiklenemedi'}`);
      } else {
        alert("Human handoff tetiklendi!");
      }
    } catch (err) {
      alert(`Hata: ${err instanceof Error ? err.message : 'Bilinmeyen hata'}`);
    }
  };
  return (
    <div className="flex items-center justify-between border-b border-slate-800 bg-slate-950/70 px-3 py-2 text-xs">
      <div>
        <div className="text-[11px] font-semibold text-slate-100">
          {lead.businessName} {lead.telegramUsername && `• @${lead.telegramUsername}`}
        </div>
        <div className="text-[10px] text-slate-400">
          Sektör: {lead.sector} {lead.city ? `• ${lead.city}` : ""}
        </div>
      </div>
      <div className="flex items-center gap-2">
        <Badge className="bg-slate-800 text-[10px]">
          Segment: {conversation.segment.toUpperCase()}
        </Badge>
        <Badge className="bg-slate-800 text-[10px]">Score: {conversation.score}</Badge>
        <Button size="sm" variant="outline" className="h-7 text-[11px]" onClick={handleHandoff}>
          👩‍🦰 Nurella Devral
        </Button>
        <Button size="sm" variant="outline" className="h-7 text-[11px]">
          📞 Arama
        </Button>
      </div>
    </div>
  );
}

