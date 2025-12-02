// SendMessageForm.tsx
// FlirtMarket message sending with Aurora enforcement integration
// Complete example: Backend 403 handling + Frontend error modal

import React, { useState } from "react";
import {
  useAuroraEnforcementError,
  AuroraEnforcementError,
} from "@/features/justice/AuroraEnforcementError";
import { RegimeBadge } from "@/features/justice/RegimeBadge";

interface SendMessageFormProps {
  recipientId: string;
  recipientName?: string;
  apiBaseUrl?: string;
  token?: string;
  onSuccess?: () => void;
}

interface MessageResponse {
  message_id: string;
  sent_at: string;
}

export const SendMessageForm: React.FC<SendMessageFormProps> = ({
  recipientId,
  recipientName,
  apiBaseUrl = "/api/v1",
  token,
  onSuccess,
}) => {
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { error: enforcementError, handleError, clearError } =
    useAuroraEnforcementError();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim()) return;

    setLoading(true);
    setError(null);
    clearError();

    try {
      const response = await fetch(`${apiBaseUrl}/flirtmarket/messages`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          recipient_id: recipientId,
          message: message.trim(),
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        // Try to handle as Aurora enforcement error
        const errorObj = {
          response: {
            status: response.status,
            data: data,
          },
        };
        if (handleError(errorObj)) {
          // Aurora enforcement error handled - modal will show
          setLoading(false);
          return;
        }

        // Other error
        throw new Error(data.detail || data.message || `HTTP ${response.status}`);
      }

      // Success
      setMessage("");
      if (onSuccess) onSuccess();
    } catch (err: any) {
      // Try to handle as Aurora enforcement error
      if (handleError(err)) {
        // Aurora enforcement error handled
        setLoading(false);
        return;
      }

      // Other error
      setError(err?.message || "Mesaj gönderilemedi");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Recipient Info */}
        <div className="flex items-center justify-between">
          <div>
            <div className="text-sm font-medium text-slate-200">
              {recipientName || `Kullanıcı ${recipientId}`}
            </div>
            <div className="text-xs text-slate-400">Alıcı</div>
          </div>
          {/* Regime badge would go here if we had user's regime */}
          {/* <RegimeBadge regime="NORMAL" size="sm" showTooltip /> */}
        </div>

        {/* Message Input */}
        <div>
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Mesajınızı yazın..."
            className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent resize-none"
            rows={4}
            disabled={loading}
          />
          <div className="mt-1 text-xs text-slate-500">
            {message.length} / 1000 karakter
          </div>
        </div>

        {/* Error Message (non-enforcement) */}
        {error && (
          <div className="p-3 bg-red-500/20 border border-red-500/50 rounded-lg text-sm text-red-400">
            {error}
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading || !message.trim()}
          className="w-full px-4 py-3 bg-sky-600 hover:bg-sky-700 disabled:bg-slate-700 disabled:text-slate-500 text-white font-medium rounded-lg transition-colors"
        >
          {loading ? "Gönderiliyor..." : "Mesaj Gönder"}
        </button>
      </form>

      {/* Aurora Enforcement Error Modal */}
      {enforcementError && (
        <AuroraEnforcementError
          error={enforcementError}
          onDismiss={clearError}
          showAppealLink={true}
        />
      )}
    </>
  );
};

