'use client'

import { useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { PolicyBreakdown } from '@aurora/ui'
import type { PolicyParams } from '@aurora/ui'
import { usePolicy, useAuroraEvents } from '@aurora/hooks'

// Mock policy for educational purposes
const examplePolicy: PolicyParams = {
  version: 'v1.0',
  decay_per_day: 1,
  base_eko: 10,
  base_com: 15,
  base_sys: 20,
  base_trust: 25,
  threshold_soft_flag: 20,
  threshold_probation: 40,
  threshold_restricted: 60,
  threshold_lockdown: 80,
  onchain_block: 12345,
  onchain_tx: '0xabc...',
  synced_at: new Date().toISOString(),
}

export default function DAOModulePage() {
  const router = useRouter()
  const { policy } = usePolicy()
  const { track } = useAuroraEvents()
  const displayPolicy = (policy as PolicyParams) || examplePolicy

  useEffect(() => {
    track('academy_module_viewed', { module: 'dao' })
  }, [track])

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-xs uppercase tracking-[0.2em] text-purple-300">
            Aurora Academy · Advanced Module
          </div>
          <h1 className="text-2xl md:text-3xl font-semibold mt-1">DAO & Policy Governance</h1>
        </div>
      </div>

      <section className="space-y-3 text-sm text-gray-300">
        <p>
          Aurora'nın ceza politikası <strong>DAO (Decentralized Autonomous Organization)</strong>{' '}
          tarafından kontrol edilir. Policy parametreleri (decay, CP ağırlıkları, regime
          threshold'ları) zincirde saklanır ve oylama ile değiştirilebilir.
        </p>
        <p>
          Backend, zincirden policy'yi senkronize eder ve runtime'da bu parametreleri kullanır.
          Bu sayede "merkezi otorite" yok; topluluk karar verir.
        </p>
      </section>

      <section className="rounded-2xl border border-white/10 bg-black/60 p-4 space-y-4">
        <h2 className="text-sm font-semibold text-purple-200">Aktif Policy:</h2>
        <PolicyBreakdown policy={displayPolicy} />
      </section>

      <section className="space-y-3 text-xs text-gray-400">
        <h3 className="text-sm font-semibold text-gray-200">DAO Governance Süreci:</h3>
        <ol className="list-decimal list-inside space-y-2 text-gray-300">
          <li>
            <strong>Proposal:</strong> Bir vatandaş veya delegasyon policy değişikliği önerir
          </li>
          <li>
            <strong>Simulation:</strong> Değişikliğin etkisi simüle edilir (simulate_aurora_policies.py)
          </li>
          <li>
            <strong>Vote:</strong> AuroraDAO token sahipleri oy verir
          </li>
          <li>
            <strong>Execution:</strong> Proposal geçerse, zincire yazılır (AuroraPolicyConfig.sol)
          </li>
          <li>
            <strong>Sync:</strong> Backend sync_dao_policy.py ile yeni policy'yi çeker
          </li>
          <li>
            <strong>Active:</strong> Yeni policy aktif olur, tüm yeni violation'lar bu policy ile
            hesaplanır
          </li>
        </ol>
      </section>

      <section className="space-y-3 text-xs text-gray-400">
        <h3 className="text-sm font-semibold text-gray-200">3-Layer Architecture:</h3>
        <div className="space-y-2 text-gray-300">
          <div className="bg-slate-900/50 rounded-lg p-3 border border-slate-800">
            <strong className="text-purple-300">Layer 1 - Chain Law (Değişken):</strong>
            <p className="mt-1">DAO policy parametreleri, CP weights, regime thresholds</p>
          </div>
          <div className="bg-slate-900/50 rounded-lg p-3 border border-slate-800">
            <strong className="text-emerald-300">Layer 2 - Constitution (Değişmez):</strong>
            <p className="mt-1">Veri Etiği Sözleşmesi, temel haklar, recall hakkı</p>
          </div>
          <div className="bg-slate-900/50 rounded-lg p-3 border border-slate-800">
            <strong className="text-sky-300">Layer 3 - Execution (Runtime):</strong>
            <p className="mt-1">JusticeService, Enforcement Engine, NovaScore calculation</p>
          </div>
        </div>
      </section>

      <section className="flex items-center justify-between text-xs text-gray-400 border-t border-white/10 pt-4">
        <Link href="/academy" className="hover:text-gray-200">
          ← Academy ana sayfaya dön
        </Link>
        <div className="text-gray-500">Tüm modüller tamamlandı! 🎉</div>
      </section>
    </div>
  )
}

