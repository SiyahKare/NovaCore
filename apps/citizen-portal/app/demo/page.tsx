"use client";

import { useState } from "react";
import {
  NovaScoreCard,
  RegimeBadge,
  RegimeBanner,
} from "@aurora/ui";
import type { NovaScorePayload } from "@aurora/ui";

type DemoProfileKey = "CLEAN" | "AT_RISK" | "LOCKDOWN";

interface DemoProfile {
  id: DemoProfileKey;
  label: string;
  description: string;
  regime: "NORMAL" | "SOFT_FLAG" | "PROBATION" | "RESTRICTED" | "LOCKDOWN";
  cp: number;
  novaScore: number;
  components: {
    ECO: { value: number; confidence: number };
    REL: { value: number; confidence: number };
    SOC: { value: number; confidence: number };
    ID: { value: number; confidence: number };
    CON: { value: number; confidence: number };
  };
  confidence: number;
  blockedActions: string[];
  allowedActions: string[];
}

const DEMO_PROFILES: Record<DemoProfileKey, DemoProfile> = {
  CLEAN: {
    id: "CLEAN",
    label: "Clean Citizen",
    description: "Hiç ihlali olmayan, Aurora tarafından full güvenilen vatandaş.",
    regime: "NORMAL",
    cp: 0,
    novaScore: 820,
    components: {
      ECO: { value: 0.88, confidence: 0.95 },
      REL: { value: 0.8, confidence: 0.98 },
      SOC: { value: 0.75, confidence: 0.9 },
      ID: { value: 0.82, confidence: 0.99 },
      CON: { value: 0.9, confidence: 0.97 },
    },
    confidence: 0.98,
    blockedActions: [],
    allowedActions: [
      "Mesaj gönderme",
      "Call başlatma",
      "Withdraw / Topup",
      "Yeni Flirt oturumu açma",
    ],
  },
  AT_RISK: {
    id: "AT_RISK",
    label: "Probation Citizen",
    description: "Orta seviye ihlalleri olan, dikkatle izlenen kullanıcı.",
    regime: "PROBATION",
    cp: 42,
    novaScore: 690,
    components: {
      ECO: { value: 0.74, confidence: 0.85 },
      REL: { value: 0.6, confidence: 0.8 },
      SOC: { value: 0.52, confidence: 0.75 },
      ID: { value: 0.7, confidence: 0.88 },
      CON: { value: 0.65, confidence: 0.82 },
    },
    confidence: 0.9,
    blockedActions: ["Bazı yüksek riskli call türleri", "Yüksek hacimli withdraw"],
    allowedActions: [
      "Normal mesajlaşma (enforcement limitleriyle)",
      "Düşük hacimli işlemler",
      "İtiraz ve açıklama gönderme",
    ],
  },
  LOCKDOWN: {
    id: "LOCKDOWN",
    label: "Lockdown Citizen",
    description:
      "Sistemi kötüye kullanmaya çalışan, geçici olarak tamamen kilitlenmiş kullanıcı.",
    regime: "LOCKDOWN",
    cp: 95,
    novaScore: 420,
    components: {
      ECO: { value: 0.3, confidence: 0.7 },
      REL: { value: 0.25, confidence: 0.65 },
      SOC: { value: 0.2, confidence: 0.6 },
      ID: { value: 0.4, confidence: 0.75 },
      CON: { value: 0.35, confidence: 0.68 },
    },
    confidence: 0.85,
    blockedActions: [
      "Mesaj gönderme",
      "Call başlatma",
      "Withdraw / Topup",
      "Yeni Flirt oturumu",
    ],
    allowedActions: [
      "Kendi verisini görüntüleme",
      "Case file inceleme",
      "İtiraz ve açıklama gönderme",
      "Recall (veri geri çekme) talebi",
    ],
  },
};

export default function DemoPage() {
  const [selected, setSelected] = useState<DemoProfileKey>("CLEAN");
  const profile = DEMO_PROFILES[selected];

  const novaScorePayload: NovaScorePayload = {
    value: profile.novaScore,
    components: profile.components,
    confidence_overall: profile.confidence,
    explanation: `Demo profile: ${profile.label}`,
  };

  return (
    <div className="space-y-8">
      {/* Hero */}
      <section className="space-y-3">
        <p className="text-[11px] uppercase tracking-[0.18em] text-gray-400">
          Aurora Live Demo
        </p>
        <h1 className="text-3xl md:text-4xl font-semibold tracking-tight text-white">
          See Aurora as <span className="text-purple-300">three different citizens</span>.
        </h1>
        <p className="text-sm md:text-base text-gray-300 max-w-2xl">
          Bu demo, backend'e bağlı olmadan; Aurora'nın regime, NovaScore ve enforcement
          davranışını canlı olarak göstermeyi amaçlar. Soldan farklı vatandaş profillerini
          seçtiğinde, sağdaki ekran bir anda başka bir hayata dönüşür.
        </p>
      </section>

      {/* Main grid */}
      <section className="grid gap-6 lg:grid-cols-[minmax(0,1.2fr)_minmax(0,1.6fr)]">
        {/* SOL: Citizen selector */}
        <div className="space-y-4 rounded-2xl border border-white/10 bg-black/60 p-4">
          <p className="text-[11px] uppercase tracking-[0.18em] text-gray-400 mb-1">
            Choose Demo Citizen
          </p>

          <div className="inline-flex rounded-2xl border border-white/10 bg-black/60 p-1 text-xs">
            {(
              [
                ["CLEAN", "Clean"],
                ["AT_RISK", "Probation"],
                ["LOCKDOWN", "Lockdown"],
              ] as [DemoProfileKey, string][]
            ).map(([key, label]) => {
              const active = selected === key;
              return (
                <button
                  key={key}
                  onClick={() => setSelected(key)}
                  className={[
                    "px-3 py-1.5 rounded-xl font-medium transition",
                    active
                      ? "bg-purple-500 text-white shadow-[0_0_18px_rgba(168,85,247,0.5)]"
                      : "text-gray-300 hover:bg-white/5",
                  ].join(" ")}
                >
                  {label}
                </button>
              );
            })}
          </div>

          <div className="flex items-center justify-between gap-3 pt-2">
            <div>
              <p className="text-xs font-medium text-gray-100">{profile.label}</p>
              <p className="text-[11px] text-gray-400">{profile.description}</p>
            </div>
            <RegimeBadge regime={profile.regime as any} size="sm" showLabel />
          </div>

          <div className="grid gap-3 sm:grid-cols-2 text-xs">
            <div className="rounded-2xl border border-white/10 bg-black/70 p-3 space-y-1.5">
              <p className="text-[11px] uppercase tracking-[0.18em] text-gray-400">
                Aurora neye izin veriyor?
              </p>
              <ul className="space-y-1 text-gray-300">
                {profile.allowedActions.map((a) => (
                  <li key={a}>• {a}</li>
                ))}
              </ul>
            </div>
            <div className="rounded-2xl border border-white/10 bg-black/70 p-3 space-y-1.5">
              <p className="text-[11px] uppercase tracking-[0.18em] text-gray-400">
                Neyi blokluyor?
              </p>
              {profile.blockedActions.length === 0 ? (
                <p className="text-gray-300">Şu an bloklanan aksiyon yok.</p>
              ) : (
                <ul className="space-y-1 text-gray-300">
                  {profile.blockedActions.map((a) => (
                    <li key={a}>• {a}</li>
                  ))}
                </ul>
              )}
            </div>
          </div>

          <p className="text-[11px] text-gray-500">
            Demo boyunca; backend enforcement gerçek dünyada aynı şekilde çalışır:
            Lockdown vatandaş, bu ekranda "ghost" gördüğün butonlara tıklasa bile,
            Aurora hem UI hem API tarafında bloklar.
          </p>
        </div>

        {/* SAĞ: Live preview panel */}
        <div className="space-y-4 rounded-2xl border border-white/10 bg-black/60 p-4 md:p-5">
          <RegimeBanner regime={profile.regime as any} cpValue={profile.cp} />

          <NovaScoreCard novaScore={novaScorePayload} showDetails={true} />

          <div className="grid gap-4 md:grid-cols-2">
            {/* Mesaj örneği */}
            <div className="rounded-2xl border border-white/10 bg-black/70 p-3 space-y-2 text-xs">
              <p className="text-[11px] uppercase tracking-[0.18em] text-gray-400">
                Messaging Action (Example)
              </p>
              <p className="text-gray-300">
                Bu, FlirtMarket/Aurora içindeki "mesaj gönder" aksiyonunun sadeleştirilmiş
                bir örneği.
              </p>
              <DemoActionButton profile={profile} action="SEND_MESSAGE" />
              <p className="text-[11px] text-gray-500">
                Lockdown modunda buton gölgelenir, backend de 403 döner. 
                Probation kullanıcısında buton aktif kalır ama CP artışı risklidir.
              </p>
            </div>

            {/* Withdraw örneği */}
            <div className="rounded-2xl border border-white/10 bg-black/70 p-3 space-y-2 text-xs">
              <p className="text-[11px] uppercase tracking-[0.18em] text-gray-400">
                Withdraw / Topup Action (Example)
              </p>
              <p className="text-gray-300">
                Finansal aksiyonlar, Aurora'nın en sıkı enforcement uyguladığı katmandır.
              </p>
              <DemoActionButton profile={profile} action="WITHDRAW" />
              <p className="text-[11px] text-gray-500">
                Aurora'nın DAO kontrollü policy parametreleri, hangi regime seviyesinde
                hangi aksiyonun kapanacağını belirler.
              </p>
            </div>
          </div>

          <div className="rounded-2xl border border-purple-500/40 bg-purple-950/40 p-3 text-[11px] text-purple-100">
            <p className="font-medium mb-1">Pitch Note</p>
            <p>
              Bu sayfa, Aurora'yı ilk defa gören birine şunu göstermek için tasarlandı:
              "Bu sadece puanlama sistemi değil; ceza, veri, politika ve UI hepsi aynı
              protokolün parçası."
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}

function DemoActionButton({
  profile,
  action,
}: {
  profile: DemoProfile;
  action: "SEND_MESSAGE" | "WITHDRAW";
}) {
  const isLockdown = profile.regime === "LOCKDOWN";
  const isRestricted =
    profile.regime === "RESTRICTED" || profile.regime === "PROBATION";

  const blockedByRegime =
    action === "SEND_MESSAGE"
      ? profile.regime === "LOCKDOWN"
      : profile.regime === "LOCKDOWN" || profile.regime === "RESTRICTED";

  const label = (() => {
    if (blockedByRegime) {
      return action === "SEND_MESSAGE"
        ? "LOCKDOWN · Messaging blocked"
        : "LOCKDOWN · Withdraw blocked";
    }
    if (isRestricted) {
      return action === "SEND_MESSAGE"
        ? "Send Message (under supervision)"
        : "Withdraw (limited)";
    }
    return action === "SEND_MESSAGE" ? "Send Message" : "Withdraw Funds";
  })();

  const base =
    "inline-flex items-center justify-center rounded-xl px-4 py-2 text-[13px] font-semibold border transition";

  const style = blockedByRegime
    ? "bg-gray-900 text-gray-500 border-red-500/40 cursor-not-allowed"
    : isRestricted
    ? "bg-amber-500/90 hover:bg-amber-400 text-black border-amber-300/70"
    : "bg-purple-500 hover:bg-purple-400 text-white border-purple-400/70";

  return (
    <button
      type="button"
      disabled={blockedByRegime}
      className={`${base} ${style}`}
    >
      {label}
    </button>
  );
}

