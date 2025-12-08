// apps/citizen-portal/app/admin/aurora/violations/page.tsx
"use client";

import { useRouter } from 'next/navigation';
import { useState } from "react";
import { useAdminViolations } from "@aurora/hooks";
import { RegimeBadge } from "@aurora/ui";

const CATEGORY_OPTIONS = [
  { value: "", label: "All" },
  { value: "COM", label: "COM · Communication" },
  { value: "EKO", label: "EKO · Economy" },
  { value: "SYS", label: "SYS · System" },
  { value: "TRUST", label: "TRUST · Identity" },
];

export default function AuroraViolationsPage() {
  const router = useRouter();
  const [severityRange, setSeverityRange] = useState<[number, number]>([1, 5]);

  const {
    data,
    loading,
    error,
    filters,
    setFilters,
    total,
    refetch,
  } = useAdminViolations({
    auto: true,
    pollIntervalMs: 30000, // 30 saniye - daha az database yükü
    initialFilters: { severityMin: 1, severityMax: 5 },
  });

  const handleCategoryChange = (value: string) => {
    setFilters((prev) => ({
      ...prev,
      category: (value === "" ? "" : (value as "EKO" | "COM" | "SYS" | "TRUST")) || undefined,
    }));
  };

  const handleSeverityChange = (min: number, max: number) => {
    setSeverityRange([min, max]);
    setFilters((prev) => ({
      ...prev,
      severityMin: min,
      severityMax: max,
    }));
  };

  const openCase = (userId: string) => {
    router.push(`/admin/aurora/case/${encodeURIComponent(userId)}`);
  };

  return (
    <div className="space-y-6">
      <header className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-gray-100">
            Violation Stream
          </h2>
          <p className="text-xs text-gray-400 max-w-xl">
            Son ihlalleri, CP impact'ini ve hangi vatandaşların hangi kategoride
            patladığını gerçek zamana yakın bir şekilde izle.
          </p>
        </div>
        <button
          onClick={() => refetch()}
          className="self-start rounded-lg border border-white/20 px-3 py-1.5 text-[11px] text-gray-200 hover:bg-white/5 transition"
        >
          Manuel refresh
        </button>
      </header>

      {/* Filters */}
      <section className="rounded-2xl border border-white/10 bg-black/60 p-4 flex flex-col md:flex-row gap-4 md:items-center md:justify-between">
        <div className="flex flex-col gap-2 text-xs text-gray-300">
          <span className="text-[11px] uppercase tracking-[0.2em] text-gray-500">
            Filter
          </span>
          <div className="flex flex-wrap gap-2">
            {CATEGORY_OPTIONS.map((opt) => (
              <button
                key={opt.value}
                onClick={() => handleCategoryChange(opt.value)}
                className={`rounded-full px-3 py-1 text-[11px] border transition ${
                  (filters.category ?? "") === opt.value
                    ? "border-purple-500/70 bg-purple-500/20 text-purple-100"
                    : "border-white/10 text-gray-300 hover:bg-white/5"
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        <div className="flex flex-col gap-1 text-xs text-gray-300">
          <span className="text-[11px] uppercase tracking-[0.2em] text-gray-500">
            Severity
          </span>
          <div className="flex items-center gap-2">
            {[1, 2, 3, 4, 5].map((s) => (
              <button
                key={s}
                onClick={() => {
                  // single selection = min=max=s
                  handleSeverityChange(s, s);
                }}
                className={`rounded-full w-7 h-7 flex items-center justify-center text-[11px] border transition ${
                  severityRange[0] === s && severityRange[1] === s
                    ? "border-red-500/70 bg-red-500/20 text-red-100"
                    : "border-white/10 text-gray-300 hover:bg-white/5"
                }`}
              >
                {s}
              </button>
            ))}
            <button
              onClick={() => handleSeverityChange(1, 5)}
              className="ml-2 rounded-full border border-white/10 px-2 py-1 text-[10px] text-gray-300 hover:bg-white/5 transition"
            >
              All
            </button>
          </div>
        </div>

        <div className="text-[11px] text-gray-500">
          Total: <span className="text-gray-200">{total}</span> violations
        </div>
      </section>

      {/* List */}
      <section className="rounded-2xl border border-white/10 bg-black/70 p-3">
        {loading && (
          <div className="py-10 text-center text-sm text-gray-400">
            Violation stream yükleniyor...
          </div>
        )}
        {!loading && error && (
          <div className="py-10 text-center text-sm text-red-300">
            Violation stream alınamadı.
          </div>
        )}
        {!loading && !error && data.length === 0 && (
          <div className="py-10 text-center text-sm text-gray-400">
            Şu an gösterilecek violation yok.
          </div>
        )}

        {!loading && !error && data.length > 0 && (
          <ul className="space-y-2 max-h-[480px] overflow-y-auto">
            {data.map((v) => (
              <li
                key={v.id}
                className="flex items-start gap-3 rounded-xl border border-white/5 bg-black/60 px-3 py-2 hover:border-purple-500/40 transition"
              >
                <div className="mt-1 text-[10px] text-gray-500 min-w-[72px]">
                  {new Date(v.created_at).toLocaleTimeString("tr-TR", {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </div>

                <div className="flex-1 space-y-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <button
                      onClick={() => openCase(v.user_id)}
                      className="text-xs font-semibold text-gray-100 hover:text-purple-200 transition"
                    >
                      {v.user_id}
                    </button>
                    {v.regime_after && (
                      <RegimeBadge
                        regime={v.regime_after as any}
                        size="sm"
                        showLabel
                      />
                    )}
                    <span className="text-[11px] rounded-full border border-white/10 px-2 py-0.5 text-gray-300">
                      {v.category} · {v.code}
                    </span>
                    <span className="text-[11px] text-red-300">
                      +{v.cp_delta.toFixed(1)} CP
                    </span>
                  </div>

                  {v.message_preview && (
                    <div className="text-[11px] text-gray-400 line-clamp-2">
                      "{v.message_preview}"
                    </div>
                  )}

                  {v.source && (
                    <div className="text-[10px] text-gray-500">
                      source: {v.source}
                    </div>
                  )}
                </div>

                <div className="flex flex-col items-end justify-between h-full text-[10px] text-gray-400">
                  <span className="rounded-full border border-white/10 px-2 py-0.5">
                    sev {v.severity}
                  </span>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

