'use client'

import { useEffect } from 'react'
import Link from 'next/link'
import {  } from 'next/navigation'
import { useRouter } from 'next/navigation'
import { NovaScoreCard, RegimeBadge } from '@aurora/ui'
import { useAuroraEvents } from '@aurora/hooks'
import type { NovaScorePayload } from '@aurora/ui'

export default function NovaScoreModulePage() {
  const router = useRouter()
  const { track } = useAuroraEvents()

  useEffect(() => {
    track('academy_module_viewed', { module: 'novascore' })
  }, [track])

  // Mock data for educational purposes
  const exampleScore: NovaScorePayload = {
    value: 750,
    components: {
      ECO: { value: 80, confidence: 0.95 },
      REL: { value: 85, confidence: 0.98 },
      SOC: { value: 75, confidence: 0.90 },
      ID: { value: 90, confidence: 0.99 },
      CON: { value: 82, confidence: 0.93 },
    },
    confidence_overall: 0.96,
    explanation: 'Example NovaScore for educational purposes',
  }

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-xs uppercase tracking-[0.2em] text-purple-300">
            NovaCore Academy · Core Module
          </div>
          <h1 className="text-2xl md:text-3xl font-semibold mt-1">NovaScore & CP Sistemi</h1>
        </div>
        <button
          onClick={() => router.push('/dashboard')}
          className="hidden md:inline-flex rounded-lg border border-purple-500/60 px-3 py-1.5 text-[11px] text-purple-200 hover:bg-purple-500/10"
        >
          Dashboard'a git
        </button>
      </div>

      <section className="space-y-3 text-sm text-gray-300">
        <p>
          <strong>NovaScore</strong>, Aurora Justice Engine'in seni nasıl gördüğünün sayısal ifadesi. Bu skor,
          davranışların, katkıların, ihlallerin ve sistem içindeki hareketlerinin birleşik bir ölçüsüdür.
        </p>
        <p>
          Skor 5 ana bileşenden oluşur: <strong>ECO</strong> (Ekonomi), <strong>REL</strong>{' '}
          (Güvenilirlik), <strong>SOC</strong> (Sosyal), <strong>ID</strong> (Kimlik),{' '}
          <strong>CON</strong> (Katkı).
        </p>
      </section>

      <section className="rounded-2xl border border-white/10 bg-black/60 p-4 space-y-4">
        <h2 className="text-sm font-semibold text-purple-200">Örnek NovaScore:</h2>
        <NovaScoreCard novaScore={exampleScore} showDetails={true} />
        <div className="text-xs text-gray-400 space-y-2">
          <p>
            <strong>ECO (Economy):</strong> Ekonomik davranışların, işlemlerin ve finansal
            etkileşimlerin skoru.
          </p>
          <p>
            <strong>REL (Reliability):</strong> Güvenilirlik, tutarlılık ve söz tutma oranın.
          </p>
          <p>
            <strong>SOC (Social):</strong> Sosyal etkileşimlerin, topluluk katkılarının ve
            iletişim kaliten.
          </p>
          <p>
            <strong>ID (Identity):</strong> Kimlik doğrulama, hesap güvenliği ve doğruluk seviyen.
          </p>
          <p>
            <strong>CON (Contribution):</strong> Sisteme yaptığın katkılar, içerik üretimi ve
            değer yaratma.
          </p>
        </div>
      </section>

      <section className="space-y-3 text-xs text-gray-400">
        <h3 className="text-sm font-semibold text-gray-200">CP (Ceza Puanı) & Regime</h3>
        <p>
          NovaScore'un yanında <strong>CP (Ceza Puanı)</strong> ve <strong>Regime</strong> sistemi
          var. CP, ihlallerin ve sorunlu davranışların birikmiş ölçüsü. Regime ise CP'ye göre
          belirlenen durumun:
        </p>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-2 mt-3">
          {['NORMAL', 'SOFT_FLAG', 'PROBATION', 'RESTRICTED', 'LOCKDOWN'].map((regime) => (
            <div key={regime} className="text-center">
              <RegimeBadge regime={regime as any} size="sm" showLabel={true} />
            </div>
          ))}
        </div>
        <p className="mt-3">
          CP yükseldikçe regime değişir. Yüksek CP → kısıtlamalar → LOCKDOWN → tüm aksiyonlar
          engellenir.
        </p>
      </section>

      <section className="flex items-center justify-between text-xs text-gray-400 border-t border-white/10 pt-4">
        <Link href="/academy" className="hover:text-gray-200">
          ← Academy ana sayfaya dön
        </Link>
        <button
          onClick={() => router.push('/academy/modules/justice')}
          className="rounded-lg bg-purple-500 px-3 py-1.5 text-[11px] text-white font-semibold hover:bg-purple-400"
        >
          Sonraki ders: Justice Engine →
        </button>
      </section>
    </div>
  )
}

