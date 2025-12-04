'use client'

import { useEffect } from 'react'
import Link from 'next/link'
import {  } from 'next/navigation'
import { useRouter } from 'next/navigation'
import { RegimeBadge } from '@aurora/ui'
import { useAuroraEvents } from '@aurora/hooks'

const violationCategories = [
  { code: 'EKO', name: 'Ekonomik', base: 10, examples: ['No-show', 'Chargeback', 'Fraud'] },
  { code: 'COM', name: 'İletişim', base: 15, examples: ['Toxic', 'Spam', 'Harassment'] },
  { code: 'SYS', name: 'Sistem', base: 20, examples: ['Exploit', 'Abuse', 'Bot'] },
  { code: 'TRUST', name: 'Güven', base: 25, examples: ['Multi-account', 'Identity fraud'] },
]

const regimes = [
  { name: 'NORMAL', threshold: 0, description: 'Tüm aksiyonlar serbest' },
  { name: 'SOFT_FLAG', threshold: 20, description: 'Uyarı seviyesi' },
  { name: 'PROBATION', threshold: 40, description: 'Bazı aksiyonlar kısıtlı' },
  { name: 'RESTRICTED', threshold: 60, description: 'Çoğu aksiyon engellenmiş' },
  { name: 'LOCKDOWN', threshold: 80, description: 'Tüm aksiyonlar engellenmiş' },
]

export default function JusticeModulePage() {
  const router = useRouter()
  const { track } = useAuroraEvents()

  useEffect(() => {
    track('academy_module_viewed', { module: 'justice' })
  }, [track])

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-xs uppercase tracking-[0.2em] text-purple-300">
            NovaCore Academy · Advanced Module
          </div>
          <h1 className="text-2xl md:text-3xl font-semibold mt-1">Justice Engine & Regime</h1>
        </div>
        <button
          onClick={() => router.push('/justice')}
          className="hidden md:inline-flex rounded-lg border border-purple-500/60 px-3 py-1.5 text-[11px] text-purple-200 hover:bg-purple-500/10"
        >
          Justice sayfasına git
        </button>
      </div>

      <section className="space-y-3 text-sm text-gray-300">
        <p>
          <strong>Justice Engine</strong>, Aurora Justice modülünün ceza ve enforcement sistemidir. Her
          ihlal bir <strong>ViolationLog</strong> kaydı oluşturur ve <strong>CP (Ceza Puanı)</strong>{' '}
          artırır.
        </p>
        <p>
          CP zamanla <strong>decay</strong> eder (günde 1 puan azalır). Ama yeni ihlaller geldikçe
          artar. CP seviyesine göre <strong>Regime</strong> belirlenir ve enforcement devreye
          girer.
        </p>
      </section>

      <section className="rounded-2xl border border-white/10 bg-black/60 p-4 space-y-4">
        <h2 className="text-sm font-semibold text-purple-200">Violation Kategorileri:</h2>
        <div className="grid md:grid-cols-2 gap-3">
          {violationCategories.map((cat) => (
            <div key={cat.code} className="bg-slate-900/50 rounded-lg p-3 border border-slate-800">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-semibold text-slate-200">{cat.name}</span>
                <span className="text-xs text-purple-300">Base: {cat.base} CP</span>
              </div>
              <div className="text-xs text-gray-400">
                Örnekler: {cat.examples.join(', ')}
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="rounded-2xl border border-white/10 bg-black/60 p-4 space-y-4">
        <h2 className="text-sm font-semibold text-purple-200">Regime Seviyeleri:</h2>
        <div className="space-y-3">
          {regimes.map((regime) => (
            <div
              key={regime.name}
              className="flex items-center gap-4 bg-slate-900/50 rounded-lg p-3 border border-slate-800"
            >
              <RegimeBadge regime={regime.name as any} size="md" showLabel={true} />
              <div className="flex-1">
                <div className="text-xs text-gray-300">
                  CP ≥ {regime.threshold} · {regime.description}
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="space-y-3 text-xs text-gray-400">
        <h3 className="text-sm font-semibold text-gray-200">Enforcement Matrix</h3>
        <p>
          Her regime seviyesinde hangi aksiyonların izinli olduğu <strong>Enforcement Matrix</strong>{' '}
          tarafından belirlenir. Bu matrix DAO tarafından kontrol edilir ve değiştirilebilir.
        </p>
        <p>
          Örnek: <strong>LOCKDOWN</strong> regime'inde mesaj gönderme, arama başlatma, transfer
          yapma gibi tüm kritik aksiyonlar engellenir.
        </p>
      </section>

      <section className="flex items-center justify-between text-xs text-gray-400 border-t border-white/10 pt-4">
        <Link href="/academy" className="hover:text-gray-200">
          ← Academy ana sayfaya dön
        </Link>
        <button
          onClick={() => router.push('/academy/modules/dao')}
          className="rounded-lg bg-purple-500 px-3 py-1.5 text-[11px] text-white font-semibold hover:bg-purple-400"
        >
          Sonraki ders: DAO & Policy →
        </button>
      </section>
    </div>
  )
}

