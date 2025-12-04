"use client";

import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ConversationListItem } from "./ConversationListItem";
import type { Conversation, Lead, LeadSegment } from "@aurora/hooks";

interface Props {
  conversations: Conversation[];
  leads: Lead[];
  activeConversationId: string | null;
  onSelectConversation: (id: string) => void;
}

export function ConversationSidebar({
  conversations,
  leads,
  activeConversationId,
  onSelectConversation,
}: Props) {
  const getSegment = (c: Conversation): LeadSegment => c.segment;

  const filteredBySegment = (segment: LeadSegment | "all") =>
    segment === "all"
      ? conversations
      : conversations.filter((c) => getSegment(c) === segment);

  const renderList = (segment: LeadSegment | "all") => (
    <ScrollArea className="h-full">
      <div className="flex flex-col gap-1 p-2">
        {filteredBySegment(segment).map((conv) => {
          const lead = leads.find((l) => l.id === conv.leadId);
          return (
            <ConversationListItem
              key={conv.id}
              conversation={conv}
              lead={lead || null}
              active={conv.id === activeConversationId}
              onClick={() => onSelectConversation(conv.id)}
            />
          );
        })}
      </div>
    </ScrollArea>
  );

  return (
    <aside className="flex w-[280px] flex-col border-r border-slate-800 bg-slate-950/80">
      <div className="border-b border-slate-800 px-3 py-2">
        <div className="text-[11px] font-semibold uppercase tracking-wide text-slate-300">
          Telegram Inbox & Queues
        </div>
      </div>
      <Tabs defaultValue="all" className="flex h-full flex-col">
        <TabsList className="mx-2 mt-2 grid grid-cols-4 bg-slate-900">
          <TabsTrigger value="all" className="text-[10px]">
            📥
          </TabsTrigger>
          <TabsTrigger value="hot" className="text-[10px]">
            🔥
          </TabsTrigger>
          <TabsTrigger value="warm" className="text-[10px]">
            🌡
          </TabsTrigger>
          <TabsTrigger value="cold" className="text-[10px]">
            ❄
          </TabsTrigger>
        </TabsList>
        <div className="flex-1">
          <TabsContent value="all" className="m-0 h-full">
            {renderList("all")}
          </TabsContent>
          <TabsContent value="hot" className="m-0 h-full">
            {renderList("hot")}
          </TabsContent>
          <TabsContent value="warm" className="m-0 h-full">
            {renderList("warm")}
          </TabsContent>
          <TabsContent value="cold" className="m-0 h-full">
            {renderList("cold")}
          </TabsContent>
        </div>
      </Tabs>
    </aside>
  );
}

