// apps/citizen-portal/app/admin/aurora/growth/page.tsx
"use client";

import { useGrowthMetrics } from "@aurora/hooks";

export default function AuroraGrowthPage() {
  const { data, loading, error, refetch } = useGrowthMetrics({
    auto: true,
    pollIntervalMs: 60000, // 1 minute
  });

  if (loading && !data) {
    return (
      <div className="flex items-center justify-center py-20 text-sm text-gray-400">
        Growth metrics yükleniyor...
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center py-20 text-sm text-red-300">
        Growth metrics alınamadı.{" "}
        <button
          onClick={() => refetch()}
          className="ml-2 text-purple-300 hover:text-purple-200"
        >
          Tekrar dene
        </button>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  return (
    <div className="space-y-6">
      <header className="flex items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-gray-100">Growth & Education Metrics</h2>
          <p className="text-xs text-gray-400 max-w-xl">
            Onboarding, Academy engagement, Justice interactions ve aktif kullanıcı metrikleri.
            Son güncelleme: {new Date(data.generated_at).toLocaleString()}
          </p>
        </div>
        <button
          onClick={() => refetch()}
          className="rounded-lg border border-white/20 px-3 py-1.5 text-[11px] text-gray-200 hover:bg-white/5 transition"
        >
          Refresh
        </button>
      </header>

      {/* Onboarding Metrics */}
      <section className="rounded-2xl border border-white/10 bg-black/60 p-4 space-y-4">
        <h3 className="text-sm font-semibold text-purple-200">Onboarding</h3>
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-slate-900/60 border border-slate-700/70 rounded-xl p-3">
            <div className="text-xs text-slate-400 mb-1">Son 24 Saat</div>
            <div className="text-2xl font-bold text-emerald-400">{data.onboarding_last_24h}</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-700/70 rounded-xl p-3">
            <div className="text-xs text-slate-400 mb-1">Son 7 Gün</div>
            <div className="text-2xl font-bold text-sky-400">{data.onboarding_last_7d}</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-700/70 rounded-xl p-3">
            <div className="text-xs text-slate-400 mb-1">Toplam</div>
            <div className="text-2xl font-bold text-purple-400">{data.onboarding_total}</div>
          </div>
        </div>
      </section>

      {/* Academy Metrics */}
      <section className="rounded-2xl border border-white/10 bg-black/60 p-4 space-y-4">
        <h3 className="text-sm font-semibold text-purple-200">Academy Engagement</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-slate-900/60 border border-slate-700/70 rounded-xl p-3">
            <div className="text-xs text-slate-400 mb-1">Views (24h)</div>
            <div className="text-xl font-bold text-yellow-400">{data.academy_views_last_24h}</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-700/70 rounded-xl p-3">
            <div className="text-xs text-slate-400 mb-1">Views (7d)</div>
            <div className="text-xl font-bold text-yellow-300">{data.academy_views_last_7d}</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-700/70 rounded-xl p-3">
            <div className="text-xs text-slate-400 mb-1">Completions (24h)</div>
            <div className="text-xl font-bold text-emerald-400">
              {data.academy_module_completions_last_24h}
            </div>
          </div>
          <div className="bg-slate-900/60 border border-slate-700/70 rounded-xl p-3">
            <div className="text-xs text-slate-400 mb-1">Completions (7d)</div>
            <div className="text-xl font-bold text-emerald-300">
              {data.academy_module_completions_last_7d}
            </div>
          </div>
        </div>

        {/* Top Modules */}
        {data.top_modules.length > 0 && (
          <div className="mt-4 space-y-2">
            <div className="text-xs text-slate-400">En Çok Görüntülenen Modüller (7 gün):</div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              {data.top_modules.map((module) => (
                <div
                  key={module.module}
                  className="bg-slate-900/60 border border-slate-700/70 rounded-lg p-2 text-xs"
                >
                  <div className="font-semibold text-slate-200 capitalize">{module.module}</div>
                  <div className="text-slate-400">{module.views} views</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </section>

      {/* Justice Metrics */}
      <section className="rounded-2xl border border-white/10 bg-black/60 p-4 space-y-4">
        <h3 className="text-sm font-semibold text-purple-200">Justice Interactions</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-slate-900/60 border border-slate-700/70 rounded-xl p-3">
            <div className="text-xs text-slate-400 mb-1">Recall Requests (24h)</div>
            <div className="text-xl font-bold text-orange-400">{data.recall_requests_last_24h}</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-700/70 rounded-xl p-3">
            <div className="text-xs text-slate-400 mb-1">Recall Requests (Total)</div>
            <div className="text-xl font-bold text-orange-300">{data.recall_requests_total}</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-700/70 rounded-xl p-3">
            <div className="text-xs text-slate-400 mb-1">Appeals (24h)</div>
            <div className="text-xl font-bold text-red-400">{data.appeals_submitted_last_24h}</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-700/70 rounded-xl p-3">
            <div className="text-xs text-slate-400 mb-1">Appeals (Total)</div>
            <div className="text-xl font-bold text-red-300">{data.appeals_submitted_total}</div>
          </div>
        </div>
      </section>

      {/* Active Users */}
      <section className="rounded-2xl border border-white/10 bg-black/60 p-4 space-y-4">
        <h3 className="text-sm font-semibold text-purple-200">Active Users</h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-slate-900/60 border border-slate-700/70 rounded-xl p-3">
            <div className="text-xs text-slate-400 mb-1">Son 24 Saat</div>
            <div className="text-2xl font-bold text-cyan-400">{data.active_users_last_24h}</div>
          </div>
          <div className="bg-slate-900/60 border border-slate-700/70 rounded-xl p-3">
            <div className="text-xs text-slate-400 mb-1">Son 7 Gün</div>
            <div className="text-2xl font-bold text-cyan-300">{data.active_users_last_7d}</div>
          </div>
        </div>
      </section>
    </div>
  );
}

