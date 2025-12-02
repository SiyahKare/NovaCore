// packages/aurora-hooks/src/useAuroraEvents.ts
import { useCallback } from "react";
import { useAuroraAPI } from "./useAuroraAPI";

export interface TelemetryEventPayload {
  event: string;
  payload?: Record<string, any>;
  session_id?: string;
  source?: string;
}

export function useAuroraEvents() {
  const api = useAuroraAPI();

  const track = useCallback(
    async (event: string, payload?: Record<string, any>, options?: { session_id?: string; source?: string }) => {
      try {
        const eventData: TelemetryEventPayload = {
          event,
          payload: payload || {},
          session_id: options?.session_id,
          source: options?.source || "citizen-portal",
        };

        await api.fetchAPI("/telemetry/events", {
          method: "POST",
          body: JSON.stringify(eventData),
        });

        // Silently fail - don't break UI if telemetry fails
      } catch (err) {
        // Silently fail
        console.debug("Telemetry event failed:", event, err);
      }
    },
    [api]
  );

  return { track };
}

