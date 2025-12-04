"use client";

import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import type { Conversation, Lead } from "@aurora/hooks";

interface Props {
  conversation: Conversation;
  lead: Lead | null;
  active?: boolean;
  onClick?: () => void;
}

export function ConversationListItem({ conversation, lead, active, onClick }: Props) {
  const title =
    lead?.businessName && lead?.telegramUsername
      ? `${lead.businessName} • @${lead.telegramUsername}`
      : lead?.businessName || conversation.title;

  return (
    <button
      onClick={onClick}
      className={cn(
        "flex w-full flex-col gap-1 rounded-md px-2 py-2 text-left text-xs",
        "hover:bg-slate-900/80",
        active && "bg-slate-900/80 ring-1 ring-cyan-500/60",
      )}
    >
      <div className="flex items-center justify-between gap-1">
        <div className="truncate text-[11px] font-medium text-slate-100">{title}</div>
        <Badge
          className={cn(
            "ml-1 h-4 min-w-[40px] justify-center px-1 text-[10px]",
            conversation.segment === "hot" && "bg-red-500/20 text-red-300",
            conversation.segment === "warm" && "bg-amber-500/20 text-amber-300",
            conversation.segment === "cold" && "bg-slate-700 text-slate-200",
          )}
        >
          {conversation.score}
        </Badge>
      </div>
      <div className="flex items-center justify-between gap-1 text-[10px] text-slate-400">
        <span className="truncate">
          {lead?.lastMessagePreview ?? "Son mesaj yok"}
        </span>
        <span>{/* buraya "3 dk önce" relative time gelebilir */}</span>
      </div>
    </button>
  );
}

