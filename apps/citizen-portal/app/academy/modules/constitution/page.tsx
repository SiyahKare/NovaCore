'use client'

import { useEffect } from 'react'
import Link from 'next/link'
import {  } from 'next/navigation'
import { useRouter } from 'next/navigation'
import { RecallRequest } from '@aurora/ui'
import { useAuroraEvents, useAcademyProgress } from '@aurora/hooks'

const bullets = [
  'Verinin yegâne sahibi sensin (Mutlak Sahiplik).',
  'Kırmızı Hat veriler (sağlık, inanç, politika, cinsellik) ekstra koruma altında.',
  'Recall hakkın var: eğitim datasetinden çıkma hakkı.',
  'Aurora Justice kararlarından temyiz talep edebilirsin (Ombudsman).',
]

export default function ConstitutionModulePage() {
  const router = useRouter()
  const { track } = useAuroraEvents()
  const { completeModule } = useAcademyProgress()

  useEffect(() => {
    // Track module view
    track('academy_module_viewed', { module: 'constitution' })
  }, [track])

  const handleRecallRequest = (mode: 'ANONYMIZE' | 'FULL_EXCLUDE') => {
    track('recall_requested', { mode })
    console.log('Recall requested:', mode)
  }

  const handleComplete = async () => {
    try {
      await completeModule('constitution')
      alert('Modül tamamlandı! 🎉')
    } catch (err: any) {
      console.error('Failed to mark module as completed:', err)
      alert('Modül tamamlanırken bir hata oluştu. Lütfen tekrar deneyin.')
    }
  }

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-xs uppercase tracking-[0.2em] text-purple-300">
            NovaCore Academy · Core Module
          </div>
          <h1 className="text-2xl md:text-3xl font-semibold mt-1">
            SiyahKare Constitution & Veri Egemenliği
          </h1>
        </div>
        <button
          onClick={() => router.push('/consent')}
          className="hidden md:inline-flex rounded-lg border border-purple-500/60 px-3 py-1.5 text-[11px] text-purple-200 hover:bg-purple-500/10"
        >
          Consent Center'a git
        </button>
      </div>

      <section className="space-y-3 text-sm text-gray-300">
        <p>
          SiyahKare Cumhuriyeti'nin kalbinde bir söz var:{' '}
          <strong>"Veri devlete değil, vatandaşa aittir."</strong> Bu, sadece bir slogan değil;
          NovaCore kayıtlarına ve chain'deki anayasa hash'ine yazılmış bir gerçek.
        </p>
        <p>
          Burada kabul ettiğin Veri Etiği & Şeffaflık Sözleşmesi, YZ modellerinin hangi verini
          nasıl kullanabileceğini, nerede durmaları gerektiğini ve ne zaman silinmek zorunda
          olduklarını belirliyor.
        </p>
      </section>

      <section className="rounded-2xl border border-white/10 bg-black/60 p-4 space-y-3">
        <h2 className="text-sm font-semibold text-purple-200">Vatandaş olarak çekirdek hakların:</h2>
        <ul className="list-disc list-inside text-xs text-gray-300 space-y-1">
          {bullets.map((b) => (
            <li key={b}>{b}</li>
          ))}
        </ul>
      </section>

      <section className="space-y-3 text-xs text-gray-400">
        <h3 className="text-sm font-semibold text-gray-200">Recall hakkı pratikte ne demek?</h3>
        <p>
          Diyelim ki son 1 yılda yaptığın etkileşimler NovaCore/Aurora modellerini eğitmek için kullanıldı.
          Bir gün fikrini değiştirdin ve "Artık bu modelin eğitim setinde olmak istemiyorum."
          dedin.
        </p>
        <p>İşte o noktada devreye <strong>Recall Request</strong> giriyor:</p>
        <div className="rounded-xl border border-white/10 bg-black/70 p-3">
          <RecallRequest
            onSubmit={handleRecallRequest}
            onCancel={() => {}}
          />
        </div>
        <p className="mt-2">
          Bu UI sadece bir form değil; backend'de feature store'dan, training log'lardan ve
          NovaScore açıklama mesajından seni çekmek için tetikleyici.
        </p>
      </section>

      <section className="flex items-center justify-between text-xs text-gray-400 border-t border-white/10 pt-4">
        <Link href="/academy" className="hover:text-gray-200">
          ← Academy ana sayfaya dön
        </Link>
        <div className="flex items-center gap-2">
          <button
            onClick={handleComplete}
            className="rounded-lg bg-emerald-500 px-3 py-1.5 text-[11px] text-white font-semibold hover:bg-emerald-400"
          >
            ✓ Tamamlandı
          </button>
          <button
            onClick={() => router.push('/academy/modules/novascore')}
            className="rounded-lg bg-purple-500 px-3 py-1.5 text-[11px] text-white font-semibold hover:bg-purple-400"
          >
            Sonraki ders: NovaScore & CP →
          </button>
        </div>
      </section>
    </div>
  )
}

