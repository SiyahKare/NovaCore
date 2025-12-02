// packages/aurora-hooks/src/useGrowthMetrics.ts
import { useEffect, useState } from "react";
import { useAuroraAPI } from "./useAuroraAPI";

export interface GrowthMetrics {
  onboarding_last_24h: number;
  onboarding_last_7d: number;
  onboarding_total: number;
  academy_views_last_24h: number;
  academy_views_last_7d: number;
  academy_module_completions_last_24h: number;
  academy_module_completions_last_7d: number;
  top_modules: Array<{ module: string; views: number }>;
  recall_requests_last_24h: number;
  recall_requests_total: number;
  appeals_submitted_last_24h: number;
  appeals_submitted_total: number;
  active_users_last_24h: number;
  active_users_last_7d: number;
  generated_at: string;
}

export function useGrowthMetrics(opts?: { auto?: boolean; pollIntervalMs?: number }) {
  const api = useAuroraAPI();
  const [data, setData] = useState<GrowthMetrics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);

    try {
      const { data: res, error: apiError } = await api.fetchAPI<GrowthMetrics>(
        "/admin/aurora/growth"
      );

      if (apiError) {
        setError("GROWTH_FETCH_FAILED");
        return;
      }

      if (res) {
        setData(res);
      }
    } catch (err: any) {
      setError("GROWTH_FETCH_FAILED");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (opts?.auto ?? true) {
      fetchData();
    }
  }, []);

  // Polling
  useEffect(() => {
    if (!opts?.pollIntervalMs) return;
    const id = setInterval(() => {
      fetchData();
    }, opts.pollIntervalMs);
    return () => clearInterval(id);
  }, [opts?.pollIntervalMs]);

  return {
    data,
    loading,
    error,
    refetch: fetchData,
  };
}

