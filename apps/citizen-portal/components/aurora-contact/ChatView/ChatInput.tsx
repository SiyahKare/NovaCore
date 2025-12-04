"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useAuroraAPI } from "@aurora/hooks";

interface Props {
  conversationId: string;
  agentMode: "ai-only" | "hybrid" | "human-only";
}

export function ChatInput({ conversationId, agentMode }: Props) {
  const { fetchAPI } = useAuroraAPI();
  const [message, setMessage] = useState("");
  const [isSending, setIsSending] = useState(false);

  const handleSend = async () => {
    if (!message.trim() || isSending) return;
    
    setIsSending(true);
    
    try {
      const { data, error } = await fetchAPI(
        `/admin/telegram/conversations/${conversationId}/send-message?text=${encodeURIComponent(message)}&agent_mode=${agentMode}`,
        {
          method: "POST",
        }
      );
      
      if (error) {
        alert(`Hata: ${error.detail || 'Mesaj gönderilemedi'}`);
      } else {
        // Success - mesaj gönderildi
        setMessage("");
        // TODO: Conversation'ı yeniden yükle
      }
    } catch (err) {
      alert(`Hata: ${err instanceof Error ? err.message : 'Bilinmeyen hata'}`);
    } finally {
      setIsSending(false);
    }
  };

  const placeholder =
    agentMode === "ai-only"
      ? "Aurora'ya yönerge yaz (örn: 'kısa cevap, fiyat söyleme')"
      : agentMode === "human-only"
        ? "Manuel mesaj yaz..."
        : "Nurella için not + Aurora'ya yönerge yaz...";

  return (
    <div className="border-t border-slate-800 bg-slate-950/70 p-3">
      <div className="flex items-end gap-2">
        <Textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder={placeholder}
          className="min-h-[60px] resize-none bg-slate-900 text-sm text-slate-100 placeholder:text-slate-500"
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSend();
            }
          }}
        />
        <Button
          onClick={handleSend}
          disabled={isSending}
          size="sm"
          className="h-[60px] bg-cyan-500/20 text-cyan-100 hover:bg-cyan-500/30 disabled:opacity-50"
        >
          {isSending ? "Gönderiliyor..." : "Gönder"}
        </Button>
      </div>
      <div className="mt-2 flex items-center gap-2 text-[10px] text-slate-400">
        <span>Mode: {agentMode.toUpperCase()}</span>
        <span>•</span>
        <span>AI Reply / Manual Reply</span>
      </div>
    </div>
  );
}

