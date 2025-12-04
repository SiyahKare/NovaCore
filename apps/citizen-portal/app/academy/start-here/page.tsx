"use client";

import { useState } from "react";
import Link from 'next/link'
import {  } from 'next/navigation';
import { useRouter } from 'next/navigation';
import {
  NovaScoreCard,
  RegimeBadge,
  RecallRequest,
  PolicyBreakdown,
} from "@aurora/ui";
import type { NovaScorePayload, PolicyParams } from "@aurora/ui";
import { usePolicy } from "@aurora/hooks";
import { ProtectedView } from "@/components/ProtectedView";

// Mock data for educational purposes
const exampleNovaScore: NovaScorePayload = {
  value: 750,
  components: {
    ECO: { value: 80, confidence: 0.95 },
    REL: { value: 85, confidence: 0.98 },
    SOC: { value: 75, confidence: 0.9 },
    ID: { value: 90, confidence: 0.99 },
    CON: { value: 82, confidence: 0.93 },
  },
  confidence_overall: 0.96,
  explanation: "Example NovaScore for educational purposes",
};

type Step = 1 | 2 | 3;

export default function StartHerePage() {
  return (
    <ProtectedView>
      <StartHereInner />
    </ProtectedView>
  );
}

function StartHereInner() {
  const [step, setStep] = useState<Step>(1);
  const router = useRouter();
  const { policy } = usePolicy();

  const next = () => setStep((s) => (s === 3 ? 3 : ((s + 1) as Step)));
  const back = () => setStep((s) => (s === 1 ? 1 : ((s - 1) as Step)));

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <header className="space-y-3 text-center">
        <div className="text-xs uppercase tracking-[0.2em] text-purple-300">
          NovaCore Academy · Start Here
        </div>
        <h1 className="text-3xl md:text-4xl font-semibold">
          7 Dakikada SiyahKare / NovaCore
        </h1>
        <p className="text-sm text-gray-400 max-w-2xl mx-auto">
          Bu track, SiyahKare + NovaCore + Aurora Justice kavramlarını hızlıca kavraman için tasarlandı.
          Her adımda bir parça öğrenecek, sonunda tüm sistemi anlayacaksın.
        </p>
      </header>

      {/* Progress Bar */}
      <div className="flex items-center gap-2">
        {[1, 2, 3].map((s) => (
          <div key={s} className="flex-1 flex items-center gap-2">
            <div
              className={`h-2 flex-1 rounded-full transition-colors ${
                step >= s ? "bg-purple-500" : "bg-gray-800"
              }`}
            />
            {s < 3 && (
              <div
                className={`h-0.5 flex-1 ${
                  step > s ? "bg-purple-500" : "bg-gray-800"
                }`}
              />
            )}
          </div>
        ))}
      </div>

      {/* Step Content */}
      <div className="rounded-2xl border border-white/10 bg-black/50 p-6 md:p-8 space-y-6">
        {step === 1 && <Step1WhatIsNovaCore onNext={next} />}
        {step === 2 && <Step2ScoringAndJustice onBack={back} onNext={next} />}
        {step === 3 && (
          <Step3PolicyAndDAO onBack={back} onFinish={() => router.push("/academy")} />
        )}
      </div>

      {/* Navigation */}
      <div className="flex items-center justify-between text-xs text-gray-400">
        <button
          onClick={back}
          disabled={step === 1}
          className="rounded-lg border border-white/15 px-3 py-1.5 hover:bg-white/5 transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          ← Geri
        </button>
        <div className="text-center">
          Adım {step} / 3
        </div>
        {step < 3 ? (
          <button
            onClick={next}
            className="rounded-lg bg-purple-500 px-3 py-1.5 text-white font-semibold hover:bg-purple-400 transition"
          >
            İleri →
          </button>
        ) : (
          <Link
            href="/academy"
            className="rounded-lg bg-emerald-500 px-3 py-1.5 text-white font-semibold hover:bg-emerald-400 transition"
          >
            Academy'ye Git →
          </Link>
        )}
      </div>
    </div>
  );
}

/* --- Step 1: Bu Ne? --- */

function Step1WhatIsNovaCore({ onNext }: { onNext: () => void }) {
  return (
    <>
      <div className="space-y-4">
        <h2 className="text-2xl font-semibold text-white">
          NovaCore & Aurora Justice Nedir?
        </h2>
        <p className="text-sm text-gray-300 leading-relaxed">
          NovaCore, klasik bir "uygulama" değildir. <strong>SiyahKare Cumhuriyeti için üç katmanlı bir dijital devlet motorudur</strong> ve Aurora Justice Engine bu motorun adalet katmanıdır:
        </p>

        <div className="grid md:grid-cols-3 gap-4 mt-6">
          <div className="rounded-xl border border-white/10 bg-black/60 p-4 space-y-2">
            <div className="text-xs uppercase tracking-[0.16em] text-purple-300">
              Katman 1
            </div>
            <h3 className="text-sm font-semibold text-gray-100">
              Anayasa & Veri Egemenliği
            </h3>
            <p className="text-xs text-gray-400">
              Verinin sahibi sensin. Consent immutable ledger'e yazılır, recall hakkın var.
            </p>
          </div>
          <div className="rounded-xl border border-white/10 bg-black/60 p-4 space-y-2">
            <div className="text-xs uppercase tracking-[0.16em] text-purple-300">
              Katman 2
            </div>
            <h3 className="text-sm font-semibold text-gray-100">
              NovaScore & Adalet
            </h3>
            <p className="text-xs text-gray-400">
              Davranışların skorlanır, ihlaller CP oluşturur, regime belirlenir.
            </p>
          </div>
          <div className="rounded-xl border border-white/10 bg-black/60 p-4 space-y-2">
            <div className="text-xs uppercase tracking-[0.16em] text-purple-300">
              Katman 3
            </div>
            <h3 className="text-sm font-semibold text-gray-100">
              DAO & Policy
            </h3>
            <p className="text-xs text-gray-400">
              Ceza politikası DAO tarafından yönetilir, zincirde saklanır.
            </p>
          </div>
        </div>

        <div className="mt-6 p-4 rounded-xl border border-purple-500/30 bg-purple-950/20">
          <p className="text-xs text-purple-200">
            <strong>Önemli:</strong> Aurora Justice Engine’de hiçbir şey "gizli" değildir. Her ceza, her skor,
            her policy değişikliği loglanır ve şeffaftır.
          </p>
        </div>
      </div>

      <div className="flex justify-end pt-4">
        <button
          onClick={onNext}
          className="rounded-xl bg-purple-500 px-4 py-2 text-sm font-semibold text-white hover:bg-purple-400 transition"
        >
          Devam et →
        </button>
      </div>
    </>
  );
}

/* --- Step 2: Beni Nasıl Puanlıyorsun & Cezalandırıyorsun? --- */

function Step2ScoringAndJustice({
  onBack,
  onNext,
}: {
  onBack: () => void;
  onNext: () => void;
}) {
  return (
    <>
      <div className="space-y-4">
        <h2 className="text-2xl font-semibold text-white">
          NovaScore & Ceza Sistemi
        </h2>
        <p className="text-sm text-gray-300 leading-relaxed">
          Aurora Justice Engine seni <strong>NovaScore</strong> ile puanlar ve <strong>CP (Ceza Puanı)</strong> ile cezalandırır.
        </p>

        {/* NovaScore Example */}
        <div className="mt-6">
          <h3 className="text-sm font-semibold text-gray-200 mb-3">
            NovaScore — Davranış Skorun
          </h3>
          <NovaScoreCard novaScore={exampleNovaScore} showDetails={true} />
          <p className="text-xs text-gray-400 mt-3">
            NovaScore 5 bileşenden oluşur: <strong>ECO</strong> (Ekonomi), <strong>REL</strong> (Güvenilirlik),
            <strong>SOC</strong> (Sosyal), <strong>ID</strong> (Kimlik), <strong>CON</strong> (Katkı).
          </p>
        </div>

        {/* CP & Regime */}
        <div className="mt-6 grid md:grid-cols-2 gap-4">
          <div className="rounded-xl border border-white/10 bg-black/60 p-4 space-y-3">
            <h3 className="text-sm font-semibold text-gray-200">CP (Ceza Puanı)</h3>
            <p className="text-xs text-gray-300">
              Her ihlal CP artırır. CP zamanla <strong>decay</strong> eder (günde 1 puan azalır).
            </p>
            <div className="flex items-center gap-2">
              <span className="text-2xl font-bold text-red-400">42</span>
              <span className="text-xs text-gray-400">CP</span>
            </div>
          </div>
          <div className="rounded-xl border border-white/10 bg-black/60 p-4 space-y-3">
            <h3 className="text-sm font-semibold text-gray-200">Regime</h3>
            <p className="text-xs text-gray-300">
              CP seviyene göre regime belirlenir. Yüksek CP → kısıtlamalar.
            </p>
            <div className="flex items-center gap-2">
              <RegimeBadge regime="PROBATION" size="md" showLabel />
            </div>
          </div>
        </div>

        {/* Regime Levels */}
        <div className="mt-6 space-y-2">
          <h3 className="text-sm font-semibold text-gray-200">Regime Seviyeleri</h3>
          <div className="grid grid-cols-5 gap-2">
            {["NORMAL", "SOFT_FLAG", "PROBATION", "RESTRICTED", "LOCKDOWN"].map((regime) => (
              <div key={regime} className="text-center">
                <RegimeBadge regime={regime as any} size="sm" showLabel />
              </div>
            ))}
          </div>
          <p className="text-xs text-gray-400 mt-2">
            LOCKDOWN regime'inde tüm kritik aksiyonlar (mesaj, call, withdraw) bloklanır.
          </p>
        </div>
      </div>

      <div className="flex items-center justify-between pt-4">
        <button
          onClick={onBack}
          className="rounded-lg border border-white/15 px-3 py-1.5 text-sm hover:bg-white/5 transition"
        >
          ← Geri
        </button>
        <button
          onClick={onNext}
          className="rounded-xl bg-purple-500 px-4 py-2 text-sm font-semibold text-white hover:bg-purple-400 transition"
        >
          Devam et →
        </button>
      </div>
    </>
  );
}

/* --- Step 3: Ben Bu Politikayı Nasıl Değiştiririm? --- */

function Step3PolicyAndDAO({
  onBack,
  onFinish,
}: {
  onBack: () => void;
  onFinish: () => void;
}) {
  const { policy } = usePolicy();

  return (
    <>
      <div className="space-y-4">
        <h2 className="text-2xl font-semibold text-white">
          DAO & Policy Governance
        </h2>
        <p className="text-sm text-gray-300 leading-relaxed">
          Aurora Justice Engine'in ceza politikası <strong>DAO (Decentralized Autonomous Organization)</strong> tarafından yönetilir.
          Policy parametreleri zincirde saklanır ve oylama ile değiştirilebilir.
        </p>

        {/* Policy Breakdown */}
        {policy && (
          <div className="mt-6">
            <h3 className="text-sm font-semibold text-gray-200 mb-3">
              Aktif Policy Parametreleri
            </h3>
            <PolicyBreakdown policy={policy as PolicyParams} />
            <p className="text-xs text-gray-400 mt-3">
              Bu parametreler <strong>AuroraPolicyConfig</strong> sözleşmesinde saklanır ve NovaCore backend tarafından
              senkronize edilir.
            </p>
          </div>
        )}

        {/* DAO Process */}
        <div className="mt-6 space-y-3">
          <h3 className="text-sm font-semibold text-gray-200">
            Policy Değiştirme Süreci
          </h3>
          <ol className="list-decimal list-inside space-y-2 text-xs text-gray-300">
            <li>
              <strong>Proposal:</strong> Bir vatandaş veya delegasyon policy değişikliği önerir
            </li>
            <li>
              <strong>Simulation:</strong> Değişikliğin etkisi simüle edilir (1000+ vatandaş üzerinde)
            </li>
            <li>
              <strong>Vote:</strong> Aurora Justice DAO token sahipleri oy verir
            </li>
            <li>
              <strong>Execution:</strong> Proposal geçerse, zincire yazılır
            </li>
            <li>
              <strong>Sync:</strong> Backend yeni policy'yi çeker ve aktif eder
            </li>
          </ol>
        </div>

        {/* Recall Example */}
        <div className="mt-6 p-4 rounded-xl border border-white/10 bg-black/60 space-y-3">
          <h3 className="text-sm font-semibold text-gray-200">
            Veri Egemenliği: Recall Hakkı
          </h3>
          <p className="text-xs text-gray-300">
            SiyahKare / NovaCore'da verinin sahibi sensin. İstediğin zaman verini sistemden geri çekebilirsin:
          </p>
          <div className="rounded-lg border border-white/10 bg-black/70 p-3">
            <RecallRequest
              onSubmit={(mode) => {
                console.log("Recall requested:", mode);
              }}
              onCancel={() => {}}
            />
          </div>
          <p className="text-xs text-gray-400">
            Recall talebi, NovaScore'daki confidence'ı düşürür çünkü daha az veri ile skor hesaplanır.
            Bu, hukuki hakkın teknik bir prosedüre bağlanmasıdır.
          </p>
        </div>
      </div>

      <div className="flex items-center justify-between pt-4">
        <button
          onClick={onBack}
          className="rounded-lg border border-white/15 px-3 py-1.5 text-sm hover:bg-white/5 transition"
        >
          ← Geri
        </button>
        <button
          onClick={onFinish}
          className="rounded-xl bg-emerald-500 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-400 transition"
        >
          Academy'ye Git →
        </button>
      </div>
    </>
  );
}

