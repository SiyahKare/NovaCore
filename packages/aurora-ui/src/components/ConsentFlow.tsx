import React, { useState } from 'react'

interface ConsentFlowProps {
  onComplete: (consentData: ConsentData) => void
  onCancel?: () => void
  className?: string
}

interface ConsentData {
  clauses: string[]
  redlineAccepted: boolean
  signature: string
}

// Clause definitions with Turkish content
const CLAUSE_DEFINITIONS: Record<string, { title: string; description: string }> = {
  '1.1': {
    title: 'Veri Egemenliği',
    description:
      'Verinin sahibi sensin. Aurora, verini senin iznin olmadan kullanamaz. Verilerin immutable ledger\'e kaydedilir ve değiştirilemez.',
  },
  '1.2': {
    title: 'Veri Kullanımı ve Şeffaflık',
    description:
      'Verilerin sadece NovaScore hesaplama, davranış analizi ve sistem optimizasyonu için kullanılır. Her kullanım loglanır ve şeffaftır.',
  },
  '2.1': {
    title: 'NovaScore ve Skorlama',
    description:
      'Davranışların NovaScore ile değerlendirilir. Skorunun nasıl hesaplandığı, hangi faktörlerin etkili olduğu ve skorunun nasıl iyileştirilebileceği şeffaftır.',
  },
  '2.2': {
    title: 'Kırmızı Hat - Hassas Veriler',
    description:
      'Cinsel içerik, finansal bilgiler ve kişisel kimlik verileri "Kırmızı Hat" kapsamındadır. Bu veriler sadece açık onayınla ve etik kurul denetiminde kullanılabilir.',
  },
  '3.1': {
    title: 'CP (Ceza Puanı) ve Regime Sistemi',
    description:
      'İhlaller CP oluşturur. CP seviyene göre regime belirlenir (NORMAL, SOFT_FLAG, PROBATION, RESTRICTED, LOCKDOWN). CP zamanla decay eder.',
  },
  '3.2': {
    title: 'Enforcement ve Kısıtlamalar',
    description:
      'Yüksek CP ve LOCKDOWN regime\'inde bazı aksiyonlar bloklanabilir (mesaj, call, withdraw). Bu kısıtlamalar şeffaftır ve itiraz edilebilir.',
  },
  '4.1': {
    title: 'Recall Hakkı (Veri Geri Çekme)',
    description:
      'İstediğin zaman verini sistemden geri çekebilirsin. Recall talebi NovaScore confidence\'ını düşürür ama bu hukuki hakkındır.',
  },
  '4.2': {
    title: 'DAO ve Policy Governance',
    description:
      'Ceza politikası parametreleri (CP ağırlıkları, decay, threshold\'lar) AuroraDAO tarafından oylanır ve zincirde saklanır. Hard-code yok.',
  },
}

export const ConsentFlow: React.FC<ConsentFlowProps> = ({
  onComplete,
  onCancel,
  className = '',
}) => {
  const [step, setStep] = useState(1)
  const [acceptedClauses, setAcceptedClauses] = useState<Set<string>>(new Set())
  const [redlineAccepted, setRedlineAccepted] = useState(false)
  const [signature, setSignature] = useState('')

  const requiredClauses = ['1.1', '1.2', '2.1', '2.2', '3.1', '3.2', '4.1', '4.2']

  const toggleClause = (clauseId: string) => {
    const newSet = new Set(acceptedClauses)
    if (newSet.has(clauseId)) {
      newSet.delete(clauseId)
    } else {
      newSet.add(clauseId)
    }
    setAcceptedClauses(newSet)
  }

  const allClausesAccepted = requiredClauses.every((c) => acceptedClauses.has(c))

  const handleComplete = () => {
    if (allClausesAccepted && redlineAccepted && signature.trim()) {
      onComplete({
        clauses: Array.from(acceptedClauses),
        redlineAccepted,
        signature,
      })
    }
  }

  return (
    <div className={`aurora-card max-w-2xl mx-auto ${className}`}>
      <h2 className="text-2xl font-bold text-slate-200 mb-6">
        Aurora Veri Etiği & Şeffaflık Sözleşmesi
      </h2>

      {step === 1 && (
        <div className="space-y-4">
          <p className="text-slate-300 text-sm">
            Devam etmek için aşağıdaki maddeleri inceleyip kabul etmen gerekiyor:
          </p>
          <div className="space-y-3">
            {requiredClauses.map((clauseId) => {
              const clause = CLAUSE_DEFINITIONS[clauseId]
              const isAccepted = acceptedClauses.has(clauseId)
              return (
                <label
                  key={clauseId}
                  className={`flex items-start gap-3 p-4 rounded-lg cursor-pointer transition-colors ${
                    isAccepted
                      ? 'bg-purple-500/20 border border-purple-500/50'
                      : 'bg-slate-900/50 border border-white/10 hover:bg-slate-900/70'
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={isAccepted}
                    onChange={() => toggleClause(clauseId)}
                    className="mt-1 w-4 h-4 rounded border-white/30 bg-black/50 text-purple-500 focus:ring-purple-500"
                  />
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-sm font-semibold text-slate-200">
                        Madde {clauseId}: {clause.title}
                      </span>
                      {isAccepted && (
                        <span className="text-xs text-emerald-400">✓ Kabul edildi</span>
                      )}
                    </div>
                    <p className="text-xs text-slate-400 leading-relaxed">{clause.description}</p>
                    <p className="text-xs text-slate-500 mt-2 italic">
                      Bu maddeyi anladım ve Aurora Veri Etiği Sözleşmesi'nin bu bölümünü kabul
                      ediyorum.
                    </p>
                  </div>
                </label>
              )
            })}
          </div>
          <div className="flex items-center justify-between text-xs text-slate-400 pt-2">
            <span>
              {acceptedClauses.size} / {requiredClauses.length} madde kabul edildi
            </span>
            {!allClausesAccepted && (
              <span className="text-orange-400">
                Tüm maddeleri kabul etmen gerekiyor
              </span>
            )}
          </div>
          <button
            onClick={() => setStep(2)}
            disabled={!allClausesAccepted}
            className="aurora-button w-full disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Devam Et →
          </button>
        </div>
      )}

      {step === 2 && (
        <div className="space-y-4">
          <div className="bg-red-500/10 border-2 border-red-500/40 rounded-lg p-5">
            <div className="flex items-center gap-2 mb-3">
              <span className="text-2xl">⚠️</span>
              <h3 className="text-lg font-semibold text-red-400">Kırmızı Hat - Madde 2.2</h3>
            </div>
            <p className="text-sm text-slate-300 mb-3 leading-relaxed">
              Bu madde özel dikkat gerektirir. Lütfen dikkatlice oku.
            </p>
            <div className="bg-black/40 rounded-lg p-3 mb-4 border border-red-500/20">
              <p className="text-xs text-slate-200 font-medium mb-2">
                {CLAUSE_DEFINITIONS['2.2'].title}
              </p>
              <p className="text-xs text-slate-300 leading-relaxed">
                {CLAUSE_DEFINITIONS['2.2'].description}
              </p>
            </div>
            <label className="flex items-start gap-3 cursor-pointer p-3 bg-black/30 rounded-lg hover:bg-black/40 transition">
              <input
                type="checkbox"
                checked={redlineAccepted}
                onChange={(e) => setRedlineAccepted(e.target.checked)}
                className="mt-1 w-4 h-4 rounded border-white/30 bg-black/50 text-red-500 focus:ring-red-500"
              />
              <div>
                <span className="text-sm text-slate-200 font-medium block">
                  Kırmızı Hat maddesini okudum ve kabul ediyorum
                </span>
                <span className="text-xs text-slate-400 mt-1 block">
                  Hassas verilerimin sadece açık onayımla ve etik kurul denetiminde
                  kullanılabileceğini anlıyorum.
                </span>
              </div>
            </label>
          </div>
          <button
            onClick={() => setStep(3)}
            disabled={!redlineAccepted}
            className="aurora-button w-full disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Devam Et →
          </button>
        </div>
      )}

      {step === 3 && (
        <div className="space-y-4">
          <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-lg p-4 mb-4">
            <h3 className="text-sm font-semibold text-emerald-300 mb-2">
              ✓ Kabul Edilen Maddeler
            </h3>
            <div className="grid grid-cols-2 gap-2 text-xs">
              {Array.from(acceptedClauses)
                .sort()
                .map((clauseId) => (
                  <div
                    key={clauseId}
                    className="flex items-center gap-2 text-slate-300"
                  >
                    <span className="text-emerald-400">✓</span>
                    <span>
                      {clauseId} - {CLAUSE_DEFINITIONS[clauseId].title}
                    </span>
                  </div>
                ))}
            </div>
            {redlineAccepted && (
              <div className="mt-2 pt-2 border-t border-emerald-500/20">
                <div className="flex items-center gap-2 text-xs text-emerald-300">
                  <span>✓</span>
                  <span>Kırmızı Hat (2.2) kabul edildi</span>
                </div>
              </div>
            )}
          </div>
          <div>
            <label className="block text-sm font-semibold text-slate-200 mb-2">
              E-imza (Ad veya Rumuz)
            </label>
            <input
              type="text"
              value={signature}
              onChange={(e) => setSignature(e.target.value)}
              placeholder="Adınızı veya rumuzunuzu girin"
              className="aurora-input w-full"
            />
            <p className="text-xs text-slate-400 mt-2">
              Bu imza immutable ledger'e kaydedilecek ve değiştirilemez.
            </p>
          </div>
          <div className="flex gap-3">
            {onCancel && (
              <button
                onClick={onCancel}
                className="aurora-button-secondary flex-1"
              >
                İptal
              </button>
            )}
            <button
              onClick={handleComplete}
              disabled={!signature.trim()}
              className="aurora-button flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              İmzala ve Tamamla
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

