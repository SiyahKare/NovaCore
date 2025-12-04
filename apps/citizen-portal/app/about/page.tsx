"use client";

import type { ReactNode } from "react";
import { useNovaScore, useJustice, useRegimeTheme, usePolicy } from "@aurora/hooks";
import { NovaScoreCard, RegimeBadge, PolicyBreakdown } from "@aurora/ui";
import type { NovaScorePayload } from "@aurora/ui";

function Pill({ children }: { children: ReactNode }) {
  return (
    <span className="inline-flex items-center rounded-full border border-white/10 bg-white/5 px-3 py-1 text-[11px] font-medium uppercase tracking-[0.18em] text-gray-300">
      {children}
    </span>
  );
}

export default function AboutPage() {
  const { score, loading: scoreLoading } = useNovaScore();
  const { cpState } = useJustice();
  const regimeTheme = useRegimeTheme();
  const { policy } = usePolicy();

  const regime = cpState?.regime ?? regimeTheme.regime ?? "NORMAL";

  return (
    <div className="space-y-10">
      {/* HERO */}
      <section className="grid gap-8 md:grid-cols-[minmax(0,2fr)_minmax(0,1.2fr)] items-start">
        <div className="space-y-5">
          <Pill>SiyahKare · NovaCore Kernel</Pill>
          <h1 className="text-3xl md:text-4xl font-semibold tracking-tight text-white">
            Protocol-State for <span className="text-purple-300">Digital Citizens</span>
          </h1>
          <p className="text-sm md:text-base text-gray-300 leading-relaxed">
            NovaCore, klasik "app" değildir.{" "}
            <span className="text-gray-100 font-medium"> Üç katmanlı bir dijital devlet motoru</span>
            dur: veri egemenliği, adalet motoru ve DAO tabanlı politika yönetimi.
          </p>
          <p className="text-xs md:text-sm text-gray-400">
            Her işlem; consent log'larına, adalet kayıtlarına ve DAO kontrollü policy
            parametrelerine bağlanır. Hiçbir ceza, hiç bir puanlama "gizli" değildir.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
            <div className="rounded-2xl border border-white/10 bg-black/50 p-3">
              <p className="text-[11px] text-gray-400 mb-1 uppercase tracking-[0.16em]">
                Katman 1
              </p>
              <p className="text-sm text-gray-100 font-medium">
                Anayasa & Veri Egemenliği
              </p>
              <p className="text-xs text-gray-400 mt-1.5">
                Immutable consent ledger, recall hakkı, Kırmızı Hat veri koruması.
              </p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-black/50 p-3">
              <p className="text-[11px] text-gray-400 mb-1 uppercase tracking-[0.16em]">
                Katman 2
              </p>
              <p className="text-sm text-gray-100 font-medium">
                NovaScore & Adalet Motoru
              </p>
              <p className="text-xs text-gray-400 mt-1.5">
                CP, regime, enforcement. Ceza puanı direkt davranıştan akar.
              </p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-black/50 p-3">
              <p className="text-[11px] text-gray-400 mb-1 uppercase tracking-[0.16em]">
                Katman 3
              </p>
              <p className="text-sm text-gray-100 font-medium">
                DAO & Policy Governance
              </p>
              <p className="text-xs text-gray-400 mt-1.5">
                CP ağırlıkları, decay, regime threshold'ları DAO tarafından yönetilir.
              </p>
            </div>
          </div>
        </div>

        {/* CANLI DURUM PANELİ */}
        <aside className="space-y-4 rounded-3xl border border-white/10 bg-black/60 p-4 md:p-5">
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="text-[11px] uppercase tracking-[0.18em] text-gray-400">
                Senin Aurora Justice Durumun
              </p>
              <p className="text-xs text-gray-500">
                Bu sayfa gerçek verinle çalışır (login isen).
              </p>
            </div>
            <RegimeBadge
              regime={regime as any}
              size="sm"
              showLabel
            />
          </div>

          {score ? (
            <NovaScoreCard novaScore={score as NovaScorePayload} showDetails={true} />
          ) : (
            <div className="rounded-2xl border border-white/10 bg-black/70 p-3 text-xs text-gray-400">
              {scoreLoading ? "Loading NovaScore..." : "NovaScore not available"}
            </div>
          )}

          {policy && (
            <div className="rounded-2xl border border-white/10 bg-black/70 p-3 space-y-2">
              <p className="text-[11px] uppercase tracking-[0.18em] text-gray-400">
                Aurora Policy Snapshot
              </p>
              <PolicyBreakdown policy={policy as any} />
              <p className="text-[11px] text-gray-500">
                Policy parametreleri DAO tarafından değiştirildiğinde; NovaScore ve
                regime davranışı otomatik güncellenir.
              </p>
            </div>
          )}
        </aside>
      </section>

      {/* HOW IT WORKS */}
      <section className="space-y-4">
        <h2 className="text-lg md:text-xl font-semibold text-white">
          Nasıl Çalışır — NovaCore & Aurora Flow'u
        </h2>
        <div className="grid gap-4 md:grid-cols-4">
          <StepCard
            index={1}
            title="Onboarding & Kimlik"
            body="Vatandaş portalına girersin, kimliğin bağlanır ve ilk citizen profili oluşturulur."
          />
          <StepCard
            index={2}
            title="PLA & Consent Flow"
            body="Veri Etiği Sözleşmesi madde madde okunur, Kırmızı Hat veriler ayrı onaylanır, imza immutable ledger'e yazılır."
          />
          <StepCard
            index={3}
            title="NovaScore & CP"
            body="Davranışların NovaScore bileşenlerini doldurur. İhlaller CP oluşturur, CP → regime'e maplenir."
          />
          <StepCard
            index={4}
            title="Enforcement & DAO"
            body="Regime seviyene göre aksiyonların kısıtlanır. Policy'ler DAO oylaması ile değiştirilebilir."
          />
        </div>
      </section>

      {/* ARCHITECTURE SECTION */}
      <section className="space-y-4">
        <h2 className="text-lg md:text-xl font-semibold text-white">
          Architecture — State Motorunun İç Yapısı
        </h2>
        <div className="grid gap-6 md:grid-cols-[minmax(0,1.6fr)_minmax(0,1.4fr)]">
          <div className="space-y-3 rounded-2xl border border-white/10 bg-black/60 p-4">
            <h3 className="text-sm font-semibold text-gray-100">
              1. Constitution & Consent Engine
            </h3>
            <ul className="space-y-1.5 text-xs text-gray-300">
              <li>• /consent/session, /consent/clauses, /consent/sign</li>
              <li>• Immutable consent_records + Redline verileri</li>
              <li>• Recall hakkı: ANONYMIZE / FULL_EXCLUDE modları</li>
            </ul>

            <h3 className="text-sm font-semibold text-gray-100 pt-3">
              2. NovaScore Engine
            </h3>
            <ul className="space-y-1.5 text-xs text-gray-300">
              <li>• Policy-aware feature query (PP = Polis Kontrol Katmanı)</li>
              <li>• ECO / REL / SOC / ID / CON bileşenleri + confidence</li>
              <li>• CP entegrasyonu: score = base - f(CP)</li>
            </ul>

            <h3 className="text-sm font-semibold text-gray-100 pt-3">
              3. Justice & Enforcement
            </h3>
            <ul className="space-y-1.5 text-xs text-gray-300">
              <li>• ViolationLog + UserCpState modelleri</li>
              <li>• CP decay (günde 1 puan, DAO parametreli)</li>
              <li>• Regime → Action matrix (SEND_MESSAGE, START_CALL, WITHDRAW...)</li>
            </ul>
          </div>

          <div className="space-y-3 rounded-2xl border border-white/10 bg-black/60 p-4">
            <h3 className="text-sm font-semibold text-gray-100">
              4. DAO-Controlled Policy Layer
            </h3>
            <p className="text-xs text-gray-300">
              CP ağırlıkları, decay rate, regime threshold'ları, AuroraPolicyConfig
              sözleşmesi tarafından yönetilir. NovaCore bu parametreleri DB'de cacheleyip
              tüm adalet kararlarında kullanır.
            </p>
            <ul className="space-y-1.5 text-xs text-gray-300 mt-2">
              <li>• contracts/AuroraPolicyConfig.sol</li>
              <li>• JusticePolicyParams + PolicyChangeLog tablosu</li>
              <li>• scripts/simulate_aurora_policies.py → policy tuning aracı</li>
            </ul>

            <h3 className="text-sm font-semibold text-gray-100 pt-3">
              5. Observatory & Control Room
            </h3>
            <p className="text-xs text-gray-300">
              Admin paneli; stats, case file, violation stream ve growth metriklerini tek
              ekranda göstererek devlet operatörüne "gerçek zamanlı röntgen" verir.
            </p>
            <ul className="space-y-1.5 text-xs text-gray-300 mt-2">
              <li>• /admin/aurora/stats</li>
              <li>• /admin/aurora/case/:userId</li>
              <li>• /admin/aurora/violations</li>
              <li>• /admin/aurora/growth</li>
            </ul>
          </div>
        </div>
      </section>
    </div>
  );
}

function StepCard({
  index,
  title,
  body,
}: {
  index: number;
  title: string;
  body: string;
}) {
  return (
    <div className="rounded-2xl border border-white/10 bg-black/60 p-4 flex flex-col gap-2">
      <div className="flex items-center gap-2 text-xs text-gray-400">
        <span className="inline-flex h-6 w-6 items-center justify-center rounded-full border border-white/15 bg-white/5 text-[11px] font-medium text-gray-200">
          {index}
        </span>
        <span className="uppercase tracking-[0.16em]">Step {index}</span>
      </div>
      <p className="text-sm font-medium text-gray-100">{title}</p>
      <p className="text-xs text-gray-300 leading-relaxed">{body}</p>
    </div>
  );
}

