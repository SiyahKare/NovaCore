"use client";

import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";
import type { Conversation, Message } from "@aurora/hooks";

interface Props {
  conversation: Conversation;
}

export function MessageList({ conversation }: Props) {
  return (
    <ScrollArea className="flex-1">
      <div className="flex flex-col gap-3 p-4">
        {conversation.messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
      </div>
    </ScrollArea>
  );
}

function MessageBubble({ message }: { message: Message }) {
  const isUser = message.from === "user";
  const isSystem = message.from === "system";
  const isAI = message.from === "ai";
  const isHuman = message.from === "human_agent";

  if (isSystem) {
    return (
      <div className="flex justify-center">
        <div className="rounded-full bg-slate-800/50 px-3 py-1 text-[10px] text-slate-400">
          {message.text}
        </div>
      </div>
    );
  }

  return (
    <div
      className={cn(
        "flex w-full",
        isUser ? "justify-end" : "justify-start",
      )}
    >
      <div
        className={cn(
          "max-w-[70%] rounded-lg px-3 py-2 text-xs",
          isUser
            ? "bg-cyan-500/20 text-cyan-100"
            : isAI
              ? "bg-slate-800 text-slate-100"
              : "bg-purple-500/20 text-purple-100",
        )}
      >
        <div className="mb-1 text-[10px] text-slate-400">
          {isUser ? "User" : isAI ? "Aurora Contact • AI" : "Nurella • Human"}
        </div>
        <div>{message.text}</div>
        {message.meta?.action === "tool_call" && (
          <div className="mt-1 text-[10px] text-slate-400">
            Tool: {message.meta.toolName} ✔
          </div>
        )}
        <div className="mt-1 text-[10px] text-slate-500">
          {new Date(message.createdAt).toLocaleTimeString("tr-TR", {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </div>
      </div>
    </div>
  );
}

