"use client";

import { 
  useTelegramConversation, 
  useTelegramLead,
  type Conversation,
  type Lead,
} from "@aurora/hooks";
import { ChatHeader } from "./ChatHeader";
import { MessageList } from "./MessageList";
import { ChatInput } from "./ChatInput";

interface Props {
  conversation: Conversation | null;
  lead: Lead | null;
  agentMode: "ai-only" | "hybrid" | "human-only";
}

export function ChatView({ conversation: propConversation, lead: propLead, agentMode }: Props) {
  // Use real API or fallback to props
  const { conversation: apiConversation } = useTelegramConversation(propConversation?.id || null);
  const { lead: apiLead } = useTelegramLead(propConversation?.leadId || null);
  
  const conversation = propConversation || apiConversation;
  const lead = propLead || apiLead;

  if (!conversation || !lead) {
    return (
      <div className="flex h-full flex-1 items-center justify-center text-xs text-slate-500">
        Bir konuşma seç.
      </div>
    );
  }

  return (
    <div className="flex h-full flex-1 flex-col">
      <ChatHeader conversation={conversation} lead={lead} agentMode={agentMode} />
      <MessageList conversation={conversation} />
      <ChatInput conversationId={conversation.id} agentMode={agentMode} />
    </div>
  );
}

