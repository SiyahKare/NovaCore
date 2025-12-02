// AuroraStatsPanel.tsx
// Simple admin stats panel for Aurora Justice Stack

import React, { useEffect, useState } from "react";

interface RegimeDistribution {
  NORMAL: number;
  SOFT_FLAG: number;
  PROBATION: number;
  RESTRICTED: number;
  LOCKDOWN: number;
}

interface ViolationBreakdown {
  EKO: number;
  COM: number;
  SYS: number;
  TRUST: number;
}

interface AuroraStats {
  total_consent_records: number;
  total_privacy_profiles: number;
  recall_requests_count: number;
  recall_requests_last_24h: number;
  consent_signatures_last_24h: number;
  total_violations: number;
  violations_last_24h: number;
  violations_last_7d: number;
  violation_breakdown: ViolationBreakdown;
  average_cp: number;
  regime_distribution: RegimeDistribution;
  lockdown_users_count: number;
  generated_at: string;
}

interface AuroraStatsPanelProps {
  apiBaseUrl?: string;
  token?: string;
}

const regimeColors: Record<keyof RegimeDistribution, string> = {
  NORMAL: "bg-emerald-500",
  SOFT_FLAG: "bg-yellow-500",
  PROBATION: "bg-orange-500",
  RESTRICTED: "bg-red-500",
  LOCKDOWN: "bg-red-900",
};

const categoryColors: Record<keyof ViolationBreakdown, string> = {
  EKO: "bg-blue-500",
  COM: "bg-purple-500",
  SYS: "bg-pink-500",
  TRUST: "bg-indigo-500",
};

export const AuroraStatsPanel: React.FC<AuroraStatsPanelProps> = ({
  apiBaseUrl = "/api/v1",
  token,
}) => {
  const [stats, setStats] = useState<AuroraStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`${apiBaseUrl}/admin/aurora/stats`, {
          headers: {
            "Content-Type": "application/json",
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
        });

        if (!res.ok) {
          throw new Error(`HTTP ${res.status}`);
        }

        const data = (await res.json()) as AuroraStats;
        setStats(data);
      } catch (err: any) {
        setError(err?.message || "Stats yüklenemedi");
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
    // Auto-refresh every 60 seconds
    const interval = setInterval(fetchStats, 60000);
    return () => clearInterval(interval);
  }, [apiBaseUrl, token]);

  if (loading && !stats) {
    return (
      <div className="p-6 text-sm text-slate-400">Aurora istatistikleri yükleniyor...</div>
    );
  }

  if (error) {
    return (
      <div className="p-6 text-sm text-red-500">
        Hata: {error}
      </div>
    );
  }

  if (!stats) {
    return null;
  }

  const regimeTotal = Object.values(stats.regime_distribution).reduce((a, b) => a + b, 0);
  const violationTotal = Object.values(stats.violation_breakdown).reduce((a, b) => a + b, 0);

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-slate-100">Aurora Justice Stack Stats</h2>
          <p className="text-xs text-slate-400">
            Son güncelleme: {new Date(stats.generated_at).toLocaleString()}
          </p>
        </div>
        <div className="text-xs text-slate-500">
          Auto-refresh: 60s
        </div>
      </div>

      {/* Quick Stats Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-900/60 border border-slate-700/70 rounded-xl p-4">
          <div className="text-xs text-slate-400 mb-1">Toplam Consent</div>
          <div className="text-2xl font-bold text-emerald-400">{stats.total_consent_records}</div>
        </div>
        <div className="bg-slate-900/60 border border-slate-700/70 rounded-xl p-4">
          <div className="text-xs text-slate-400 mb-1">Son 24h Violation</div>
          <div className="text-2xl font-bold text-orange-400">{stats.violations_last_24h}</div>
        </div>
        <div className="bg-slate-900/60 border border-slate-700/70 rounded-xl p-4">
          <div className="text-xs text-slate-400 mb-1">Ortalama CP</div>
          <div className="text-2xl font-bold text-sky-400">{stats.average_cp.toFixed(1)}</div>
        </div>
        <div className="bg-slate-900/60 border border-slate-700/70 rounded-xl p-4">
          <div className="text-xs text-slate-400 mb-1">LOCKDOWN</div>
          <div className="text-2xl font-bold text-red-600">{stats.lockdown_users_count}</div>
        </div>
      </div>

      {/* Grid: 3 columns */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Column 1: Consent & Privacy */}
        <div className="bg-slate-900/60 border border-slate-700/70 rounded-2xl p-4 space-y-3">
          <div className="text-xs font-semibold uppercase text-slate-400">
            Consent & Privacy
          </div>
          <div className="space-y-2 text-sm text-slate-200">
            <div className="flex justify-between">
              <span className="text-slate-400">Toplam Consent:</span>
              <span className="font-mono">{stats.total_consent_records}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Privacy Profilleri:</span>
              <span className="font-mono">{stats.total_privacy_profiles}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Recall İstekleri:</span>
              <span className="font-mono">{stats.recall_requests_count}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Son 24h Recall:</span>
              <span className="font-mono text-yellow-400">
                {stats.recall_requests_last_24h}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Son 24h İmza:</span>
              <span className="font-mono text-emerald-400">
                {stats.consent_signatures_last_24h}
              </span>
            </div>
          </div>
        </div>

        {/* Column 2: Justice & CP */}
        <div className="bg-slate-900/60 border border-slate-700/70 rounded-2xl p-4 space-y-3">
          <div className="text-xs font-semibold uppercase text-slate-400">
            Justice & CP
          </div>
          <div className="space-y-2 text-sm text-slate-200">
            <div className="flex justify-between">
              <span className="text-slate-400">Toplam Violation:</span>
              <span className="font-mono">{stats.total_violations}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Son 24h:</span>
              <span className="font-mono text-orange-400">
                {stats.violations_last_24h}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Son 7 Gün:</span>
              <span className="font-mono text-red-400">
                {stats.violations_last_7d}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Ortalama CP:</span>
              <span className="font-mono text-sky-400">
                {stats.average_cp.toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">LOCKDOWN Kullanıcı:</span>
              <span className="font-mono text-red-600">
                {stats.lockdown_users_count}
              </span>
            </div>
          </div>
        </div>

        {/* Column 3: Regime Distribution */}
        <div className="bg-slate-900/60 border border-slate-700/70 rounded-2xl p-4 space-y-3">
          <div className="text-xs font-semibold uppercase text-slate-400">
            Rejim Dağılımı
          </div>
          <div className="space-y-2">
            {Object.entries(stats.regime_distribution).map(([regime, count]) => {
              const percentage = regimeTotal > 0 ? (count / regimeTotal) * 100 : 0;
              return (
                <div key={regime} className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span className="text-slate-300">{regime}</span>
                    <span className="font-mono text-slate-400">
                      {count} ({percentage.toFixed(1)}%)
                    </span>
                  </div>
                  <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${regimeColors[regime as keyof RegimeDistribution]}`}
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Violation Breakdown */}
      <div className="bg-slate-900/60 border border-slate-700/70 rounded-2xl p-4 space-y-3">
        <div className="text-xs font-semibold uppercase text-slate-400">
          Violation Kategori Dağılımı
        </div>
        <div className="grid grid-cols-4 gap-4">
          {Object.entries(stats.violation_breakdown).map(([category, count]) => {
            const percentage =
              violationTotal > 0 ? (count / violationTotal) * 100 : 0;
            return (
              <div key={category} className="space-y-2">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-300">{category}</span>
                  <span className="font-mono text-slate-400">
                    {count} ({percentage.toFixed(1)}%)
                  </span>
                </div>
                <div className="h-3 bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${categoryColors[category as keyof ViolationBreakdown]}`}
                    style={{ width: `${percentage}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

