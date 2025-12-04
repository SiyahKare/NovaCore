'use client'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { NovaScoreCard, RegimeBadge } from '@aurora/ui'
import type { NovaScorePayload } from '@aurora/ui'

export default function HomePage() {
  const router = useRouter()

  // Mock data for landing page preview
  const mockScore: NovaScorePayload = {
    value: 732,
    components: {
      ECO: { value: 75, confidence: 0.9 },
      REL: { value: 80, confidence: 0.95 },
      SOC: { value: 70, confidence: 0.85 },
      ID: { value: 85, confidence: 0.98 },
      CON: { value: 78, confidence: 0.92 },
    },
    confidence_overall: 0.97,
    explanation: 'Citizen in good standing',
  }

  return (
    <div className="space-y-16">
      {/* Hero */}
      <section className="grid md:grid-cols-[3fr,2fr] gap-10 items-center">
        <div className="space-y-6">
          <div className="inline-flex items-center gap-2 rounded-full border border-purple-500/40 bg-purple-500/10 px-3 py-1 text-xs text-purple-200">
            <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
            SiyahKare Republic · NovaCore Kernel
          </div>

          <h1 className="text-4xl md:text-5xl font-semibold leading-tight">
            Dijital Vatandaşlığa{' '}
            <span className="text-purple-300">Hoş Geldiniz</span>
          </h1>

          <p className="text-gray-300 text-lg max-w-xl">
            SiyahKare Cumhuriyeti'ne katılın, NovaScore'unuzu yükseltin ve Aurora Justice DAO yönetimine dahil olun.
          </p>

          <div className="flex flex-wrap gap-4">
            <button
              onClick={() => router.push('/onboarding')}
              className="rounded-xl bg-purple-500 px-5 py-3 text-sm font-semibold text-white shadow-[0_0_30px_rgba(168,85,247,0.5)] hover:bg-purple-400 transition"
            >
              Vatandaş Ol
            </button>

            <Link
              href="/dashboard"
              className="rounded-xl border border-white/15 px-5 py-3 text-sm font-semibold text-gray-200 hover:bg-white/5 transition"
            >
              Dashboard'u Aç
            </Link>
          </div>

          <div className="flex flex-wrap gap-6 text-xs text-gray-400">
            <div>
              ⛓ DAO Kontrollü <br />
              <span className="text-gray-300">Merkezi olmayan yönetim</span>
            </div>
            <div>
              ⚖ Adalet Motoru <br />
              <span className="text-gray-300">Otomatik ceza sistemi</span>
            </div>
            <div>
              🧱 Anayasa <br />
              <span className="text-gray-300">On-chain kurallar</span>
            </div>
          </div>
        </div>

        {/* Hero Right: Fake preview */}
        <div className="rounded-2xl border border-white/10 bg-white/5 bg-gradient-to-br from-purple-500/10 via-sky-500/5 to-transparent p-4 shadow-[0_0_60px_rgba(59,130,246,0.25)]">
          <div className="rounded-xl border border-white/10 bg-black/60 p-4 space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs uppercase tracking-widest text-gray-400">
                Anlık Görüntü
              </span>
              <span className="text-[10px] rounded-full border border-emerald-400/40 bg-emerald-500/10 px-2 py-0.5 text-emerald-300">
                Simüle
              </span>
            </div>

            <NovaScoreCard novaScore={mockScore} showDetails={false} />

            <div className="flex items-center justify-between gap-4">
              <RegimeBadge regime="NORMAL" size="md" showLabel={true} />
              <div className="text-right text-xs text-gray-300">
                <div className="text-[11px] text-gray-400">Rejim</div>
                <div className="font-semibold text-emerald-300">NORMAL · CP 4</div>
                <div className="text-[11px] text-gray-500">&quot;İyi durumda vatandaş&quot;</div>
              </div>
            </div>

            <div className="mt-3 rounded-lg border border-white/10 bg-black/60 p-2 text-[11px] text-gray-300">
              <div className="flex items-center justify-between mb-1">
                <span className="text-gray-400">Son Politika Değişikliği</span>
                <span className="text-[10px] text-purple-300">On-Chain</span>
              </div>
              <div className="text-[10px] text-slate-400 mt-1">
                v1.0 · Initial Policy · {new Date().toLocaleDateString('tr-TR')}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="space-y-6">
        <h2 className="text-2xl font-semibold">Nasıl Çalışır?</h2>

        <div className="grid md:grid-cols-3 gap-6 text-sm text-gray-300">
          <div className="rounded-xl border border-white/10 bg-white/5 p-4 space-y-2">
            <div className="text-xs font-semibold text-purple-300">
              Adım 1: Kayıt Ol
            </div>
            <p>
              Dijital kimliğinizi oluşturun ve NovaScore'unuzu başlatın.
            </p>
          </div>
          <div className="rounded-xl border border-white/10 bg-white/5 p-4 space-y-2">
            <div className="text-xs font-semibold text-sky-300">Adım 2: Aktif Ol</div>
            <p>
              Görevleri tamamlayın, toplulukla etkileşime geçin ve puan kazanın.
            </p>
          </div>
          <div className="rounded-xl border border-white/10 bg-white/5 p-4 space-y-2">
            <div className="text-xs font-semibold text-emerald-300">Adım 3: Yönet</div>
            <p>
              DAO kararlarına oy verin ve topluluk yönetimine katılın.
            </p>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="mt-4 rounded-2xl border border-purple-500/40 bg-gradient-to-r from-purple-600/20 via-sky-500/10 to-transparent p-6 flex flex-col md:flex-row items-center justify-between gap-4">
        <div>
          <div className="text-sm font-semibold text-purple-200 mb-1">
            Hemen Başlayın
          </div>
          <div className="text-gray-200 text-sm">
            Dijital vatandaşlığınızı oluşturun ve SiyahKare Cumhuriyeti'ne katılın.
          </div>
        </div>
        <button
          onClick={() => router.push('/onboarding')}
          className="rounded-xl bg-purple-500 px-5 py-3 text-sm font-semibold text-white shadow-[0_0_30px_rgba(168,85,247,0.5)] hover:bg-purple-400 transition"
        >
          Onboarding'e Başla
        </button>
      </section>
    </div>
  )
}
