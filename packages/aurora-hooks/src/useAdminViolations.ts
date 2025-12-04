// packages/aurora-hooks/src/useAdminViolations.ts
import { useEffect, useState, useCallback } from "react";
import { useAuroraAPI } from "./useAuroraAPI";

export type ViolationCategory = "EKO" | "COM" | "SYS" | "TRUST";

export interface AdminViolation {
  id: string;
  user_id: string;
  category: ViolationCategory | string;
  code: string;
  severity: number;
  cp_delta: number;
  regime_after?: string | null;
  source?: string | null;
  message_preview?: string | null;
  meta?: Record<string, any>;
  created_at: string;
}

export interface AdminViolationFilters {
  category?: ViolationCategory | "";
  severityMin?: number;
  severityMax?: number;
}

interface ResponseShape {
  items: AdminViolation[];
  total: number;
  limit: number;
  offset: number;
}

export function useAdminViolations(opts?: {
  auto?: boolean;
  pollIntervalMs?: number;
  initialFilters?: AdminViolationFilters;
}) {
  const api = useAuroraAPI();
  const [data, setData] = useState<AdminViolation[]>([]);
  const [total, setTotal] = useState(0);
  const [limit, setLimit] = useState(50);
  const [offset, setOffset] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<AdminViolationFilters>(
    opts?.initialFilters ?? {}
  );

  const fetchData = useCallback(
    async (override?: { offset?: number; limit?: number }) => {
      setLoading(true);
      setError(null);

      try {
        const params: Record<string, any> = {
          limit: override?.limit ?? limit,
          offset: override?.offset ?? offset,
        };

        if (filters.category) params.category = filters.category;
        if (filters.severityMin !== undefined)
          params.severity_min = filters.severityMin;
        if (filters.severityMax !== undefined)
          params.severity_max = filters.severityMax;

        // Build query string
        const queryString = new URLSearchParams(
          Object.entries(params).reduce((acc, [key, value]) => {
            if (value !== undefined && value !== null) {
              acc[key] = String(value);
            }
            return acc;
          }, {} as Record<string, string>)
        ).toString();

        const endpoint = `/admin/aurora/violations${queryString ? `?${queryString}` : ""}`;
        const { data: res, error: apiError } = await api.fetchAPI<ResponseShape>(
          endpoint
        );

        if (apiError) {
          setError("VIOLATION_FETCH_FAILED");
          return;
        }

        if (res) {
          setData(res.items);
          setTotal(res.total);
          setLimit(res.limit);
          setOffset(res.offset);
        }
      } catch (err: any) {
        setError("VIOLATION_FETCH_FAILED");
      } finally {
        setLoading(false);
      }
    },
    [api, filters, limit, offset]
  );

  // Auto load
  useEffect(() => {
    if (opts?.auto ?? true) {
      fetchData();
    }
  }, [fetchData, opts?.auto]);

  // Polling - filters değiştiğinde yeniden başlat, ama fetchData'ya bağlı değil
  // Page Visibility API ile sayfa görünür değilken polling'i durdur
  useEffect(() => {
    if (!opts?.pollIntervalMs) return;
    
    // İlk fetch'i hemen yap
    const doFetch = () => {
      // Sayfa görünür değilse polling yapma
      if (document.hidden) return;
      
      setLoading(true);
      setError(null);
      
      const params: Record<string, any> = {
        limit: limit,
        offset: 0,
      };
      
      if (filters.category) params.category = filters.category;
      if (filters.severityMin !== undefined) params.severity_min = filters.severityMin;
      if (filters.severityMax !== undefined) params.severity_max = filters.severityMax;
      
      const queryString = new URLSearchParams(
        Object.entries(params).reduce((acc, [key, value]) => {
          if (value !== undefined && value !== null) {
            acc[key] = String(value);
          }
          return acc;
        }, {} as Record<string, string>)
      ).toString();
      
      const endpoint = `/admin/aurora/violations${queryString ? `?${queryString}` : ""}`;
      
      api.fetchAPI<ResponseShape>(endpoint).then(({ data: res, error: apiError }) => {
        if (apiError) {
          setError("VIOLATION_FETCH_FAILED");
          return;
        }
        if (res) {
          setData(res.items);
          setTotal(res.total);
          setLimit(res.limit);
          setOffset(0);
        }
      }).catch(() => {
        setError("VIOLATION_FETCH_FAILED");
      }).finally(() => {
        setLoading(false);
      });
    };
    
    const id = setInterval(doFetch, opts.pollIntervalMs);
    return () => clearInterval(id);
  }, [api, filters, limit, opts?.pollIntervalMs]); // fetchData'yı dependency'den çıkardık

  return {
    data,
    total,
    limit,
    offset,
    loading,
    error,
    filters,
    setFilters,
    refetch: () => fetchData({ offset: 0 }),
  };
}

