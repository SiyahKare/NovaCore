"use client";

import { useState, useMemo } from "react";
import { 
  useTelegramConversations, 
  useTelegramStats,
  type Conversation,
  type Lead,
  type HandoffEvent,
} from "@aurora/hooks";
import { TopBar } from "./TopBar";
import { ConversationSidebar } from "./ConversationSidebar/ConversationSidebar";
import { ChatView } from "./ChatView/ChatView";
import { LeadPanel } from "./LeadPanel/LeadPanel";

interface Props {
  conversations?: Conversation[];
  leads?: Lead[];
  handoffs?: HandoffEvent[];
}

export function TelegramConsoleLayout({ 
  conversations: propConversations, 
  leads: propLeads, 
  handoffs: propHandoffs 
}: Props) {
  // Use real API or fallback to props
  const { conversations: apiConversations, isLoading: conversationsLoading } = useTelegramConversations();
  const { stats } = useTelegramStats();
  
  const conversations = propConversations || apiConversations || [];
  const leads = propLeads || [];
  const handoffs = propHandoffs || [];
  const [activeConversationId, setActiveConversationId] = useState<string | null>(
    conversations[0]?.id ?? null,
  );
  const [agentMode, setAgentMode] = useState<"ai-only" | "hybrid" | "human-only">("hybrid");

  const activeConversation = useMemo(
    () => conversations.find((c) => c.id === activeConversationId) || null,
    [conversations, activeConversationId],
  );

  const activeLead = useMemo(() => {
    if (!activeConversation) return null;
    return leads.find((l) => l.id === activeConversation.leadId) || null;
  }, [activeConversation, leads]);

  const activeHandoffs = useMemo(() => {
    if (!activeConversation) return [];
    return handoffs.filter((h) => h.id.startsWith(activeConversation.id));
  }, [handoffs, activeConversation]);

  return (
    <div className="flex h-screen flex-col bg-slate-950 text-slate-50">
      <TopBar
        totalCallsToday={stats?.totalCallsToday}
        hotCount={stats?.hotCount}
        warmCount={stats?.warmCount}
        coldCount={stats?.coldCount}
        agentMode={agentMode}
        onAgentModeChange={setAgentMode}
      />
      <div className="flex flex-1 overflow-hidden">
        <ConversationSidebar
          conversations={conversations}
          leads={leads}
          activeConversationId={activeConversationId}
          onSelectConversation={setActiveConversationId}
        />

        <div className="flex min-w-0 flex-[2] border-l border-slate-800">
          <ChatView
            conversation={activeConversation}
            lead={activeLead}
            agentMode={agentMode}
          />
        </div>

        <div className="hidden w-[360px] border-l border-slate-800 lg:block">
          <LeadPanel lead={activeLead} handoffs={activeHandoffs} />
        </div>
      </div>
    </div>
  );
}

