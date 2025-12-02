'use client'

import { ProtectedView } from '@/components/ProtectedView'
import Link from 'next/link'
import { ModuleCard } from './components/ModuleCard'

const modules = [
  {
    slug: 'constitution',
    title: 'Aurora Constitution',
    level: 'Core · Zorunlu',
    minutes: 6,
    description: 'Veri Etiği & Şeffaflık Sözleşmesi, Kırmızı Hat verileri ve recall hakkın.',
  },
  {
    slug: 'novascore',
    title: 'NovaScore & CP',
    level: 'Core · Zorunlu',
    minutes: 8,
    description: 'NovaScore bileşenleri, CP/Regime sistemi ve davranış → skor haritası.',
  },
  {
    slug: 'justice',
    title: 'Justice Engine & Regime',
    level: 'Advanced',
    minutes: 10,
    description: 'Violation log, CP hesaplama, decay, enforcement ve regime seviyeleri.',
  },
  {
    slug: 'dao',
    title: 'DAO & Policy Governance',
    level: 'Advanced',
    minutes: 9,
    description: 'Policy parametreleri, DAO oylaması, on-chain → backend sync akışı.',
  },
]

export default function AcademyPage() {
  return (
    <ProtectedView>
      <AcademyInner />
    </ProtectedView>
  )
}

// Start Here CTA Section
function StartHereSection() {
  return (
    <div className="rounded-2xl border-2 border-purple-500/40 bg-gradient-to-br from-purple-950/40 to-black/60 p-6 md:p-8 space-y-4">
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-2">
          <div className="text-xs uppercase tracking-[0.2em] text-purple-300">
            Yeni Başlayanlar İçin
          </div>
          <h2 className="text-2xl font-semibold text-white">
            Start Here: 7 Dakikada Aurora
          </h2>
          <p className="text-sm text-gray-300 max-w-xl">
            Aurora'yı ilk defa görüyorsan, bu track ile başla. 3 adımda tüm sistemi kavrayacaksın:
            "Bu ne?", "Beni nasıl puanlıyorsun?", "Politikayı nasıl değiştiririm?"
          </p>
        </div>
        <Link
          href="/academy/start-here"
          className="rounded-xl bg-purple-500 px-6 py-3 text-sm font-semibold text-white hover:bg-purple-400 transition whitespace-nowrap"
        >
          Başla →
        </Link>
      </div>
    </div>
  )
}

function AcademyInner() {
  return (
    <div className="space-y-8">
      <header className="space-y-2">
        <div className="text-xs uppercase tracking-[0.2em] text-purple-300">Aurora Academy</div>
        <h1 className="text-3xl font-semibold">Dijital Devlet için Hızlandırılmış Eğitim</h1>
        <p className="text-sm text-gray-400 max-w-2xl">
          Burada Aurora'nın nasıl çalıştığını; NovaScore, Justice Engine, DAO governance ve
          Anayasa katmanını parça parça öğrenirsin. Amaç: "Bu ne lan?" seviyesinden → "Ben bu
          sistemi hackleyip optimize ederim" seviyesine çıkartmak.
        </p>
      </header>

      {/* Start Here CTA */}
      <StartHereSection />

      <div className="grid md:grid-cols-2 gap-5">
        {modules.map((m) => (
          <ModuleCard key={m.slug} {...m} />
        ))}
      </div>

      <div className="text-xs text-gray-500">
        İpucu: Dashboard + Academy birlikte çalışacak. NovaScore'un değiştikçe eğitim tavsiyeleri
        önerebiliriz (sonraki sprint).
      </div>
    </div>
  )
}

