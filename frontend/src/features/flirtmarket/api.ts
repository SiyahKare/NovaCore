// api.ts
// FlirtMarket API client with Aurora enforcement error handling

import {
  useAuroraEnforcementError,
  AuroraEnforcementErrorData,
} from "@/features/justice/AuroraEnforcementError";

export interface SendMessageRequest {
  recipient_id: string;
  message: string;
}

export interface SendMessageResponse {
  message_id: string;
  sent_at: string;
}

export interface FlirtMarketApiError {
  error?: string;
  message?: string;
  regime?: string;
  cp_value?: number;
  action?: string;
}

/**
 * Check if error is Aurora enforcement error
 */
export function isAuroraEnforcementError(err: any): boolean {
  return (
    err?.response?.status === 403 &&
    err?.response?.data?.error === "AURORA_ENFORCEMENT_BLOCKED"
  );
}

/**
 * Extract Aurora enforcement error data
 */
export function extractAuroraEnforcementError(
  err: any
): AuroraEnforcementErrorData | null {
  if (isAuroraEnforcementError(err)) {
    return err.response.data as AuroraEnforcementErrorData;
  }
  return null;
}

/**
 * FlirtMarket API client with Aurora enforcement handling
 */
export class FlirtMarketApi {
  constructor(
    private baseUrl: string = "/api/v1",
    private token?: string
  ) {}

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(this.token ? { Authorization: `Bearer ${this.token}` } : {}),
        ...options.headers,
      },
    });

    const data = await response.json();

    if (!response.ok) {
      // Check for Aurora enforcement error
      if (
        response.status === 403 &&
        data.error === "AURORA_ENFORCEMENT_BLOCKED"
      ) {
        throw {
          response: {
            status: 403,
            data: data as AuroraEnforcementErrorData,
          },
        };
      }

      // Other error
      throw new Error(data.detail || data.message || `HTTP ${response.status}`);
    }

    return data;
  }

  /**
   * Send message with Aurora enforcement check
   */
  async sendMessage(
    request: SendMessageRequest
  ): Promise<SendMessageResponse> {
    return this.request<SendMessageResponse>("/flirtmarket/messages", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }

  /**
   * Start call with Aurora enforcement check
   */
  async startCall(recipientId: string): Promise<{ call_id: string }> {
    return this.request<{ call_id: string }>("/flirtmarket/calls/start", {
      method: "POST",
      body: JSON.stringify({ recipient_id: recipientId }),
    });
  }

  /**
   * Create flirt with Aurora enforcement check
   */
  async createFlirt(data: {
    performer_id: string;
    message?: string;
  }): Promise<{ flirt_id: string }> {
    return this.request<{ flirt_id: string }>("/flirtmarket/flirts", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }
}

