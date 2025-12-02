'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { ConsentFlow, NovaScoreCard, RegimeBadge } from '@aurora/ui'
import { useNovaScore, useJustice, useAuroraEvents, useConsentFlow } from '@aurora/hooks'
import { setToken, getToken } from '@/lib/auth'
import type { NovaScorePayload, CpState } from '@aurora/ui'

type Step = 1 | 2 | 3 | 4

export default function OnboardingPage() {
  const [step, setStep] = useState<Step>(1)
  const router = useRouter()

  const next = () => setStep((s) => (s === 4 ? 4 : ((s + 1) as Step)))
  const back = () => setStep((s) => (s === 1 ? 1 : ((s - 1) as Step)))

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <header className="space-y-2">
        <div className="text-xs uppercase tracking-[0.2em] text-purple-300">Aurora Onboarding</div>
        <h1 className="text-3xl font-semibold">Become a Citizen</h1>
        <p className="text-sm text-gray-400">
          3 adımda Aurora devletine giriş yapıyorsun. Bu bir ürün kayıt formu değil; bir dijital
          vatandaşlık sözleşmesi.
        </p>
      </header>

      {/* Stepper */}
      <div className="flex items-center gap-3 text-xs text-gray-400">
        <StepDot active={step === 1} label="Auth" />
        <StepLine />
        <StepDot active={step === 2} label="Intro" />
        <StepLine />
        <StepDot active={step === 3} label="Consent" />
        <StepLine />
        <StepDot active={step === 4} label="NovaScore" />
      </div>

      {/* Content */}
      <div className="rounded-2xl border border-white/10 bg-black/50 p-6 space-y-6">
        {step === 1 && <StepAuth onNext={next} />}
        {step === 2 && <StepIntro onBack={back} onNext={next} />}
        {step === 3 && <StepConsent onBack={back} onNext={next} />}
        {step === 4 && (
          <StepNovaScore onBack={back} onFinish={() => router.push('/dashboard')} />
        )}
      </div>
    </div>
  )
}

function StepDot({ active, label }: { active: boolean; label: string }) {
  return (
    <div className="flex items-center gap-2">
      <div
        className={`h-2.5 w-2.5 rounded-full ${
          active ? 'bg-purple-400 shadow-[0_0_12px_rgba(168,85,247,0.8)]' : 'bg-gray-600'
        }`}
      />
      <span className={active ? 'text-purple-200' : ''}>{label}</span>
    </div>
  )
}

function StepLine() {
  return <div className="h-px flex-1 bg-gradient-to-r from-gray-700 via-gray-600 to-gray-700" />
}

/* --- Step 1: Auth --- */

function StepAuth({ onNext }: { onNext: () => void }) {
  const [authMethod, setAuthMethod] = useState<'email' | 'google' | 'dev' | null>(null)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [hasToken, setHasToken] = useState(false)
  
  // Check token on client-side only to avoid hydration mismatch
  useEffect(() => {
    setHasToken(!!getToken())
  }, [])

  const handleEmailAuth = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const apiUrl = process.env.NEXT_PUBLIC_AURORA_API_URL || 'http://localhost:8000/api/v1'
      
      // Try login first
      let res = await fetch(`${apiUrl}/auth/email/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })

      // If login fails with 401, try register
      if (!res.ok && res.status === 401) {
        res = await fetch(`${apiUrl}/auth/email/register`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password, display_name: email.split('@')[0] }),
        })
      }

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({ detail: 'Email auth hatası' }))
        throw new Error(errorData.detail || 'Email ile giriş/kayıt yapılamadı')
      }

      const { access_token } = await res.json()
      setToken(access_token)
      setHasToken(true)
      onNext()
    } catch (err: any) {
      setError(err.message || 'Email auth hatası. Dev mode kullanabilirsin.')
    } finally {
      setLoading(false)
    }
  }

  const handleGoogleAuth = async () => {
    setLoading(true)
    setError(null)

    try {
      // TODO: Implement Google OAuth
      const apiUrl = process.env.NEXT_PUBLIC_AURORA_API_URL || 'http://localhost:8000/api/v1'
      window.location.href = `${apiUrl}/auth/google/login`
    } catch (err: any) {
      setError('Google OAuth henüz aktif değil. Dev mode kullanabilirsin.')
      setLoading(false)
    }
  }

  const handleDevMode = async () => {
    setLoading(true)
    setError(null)

    try {
      const apiUrl = process.env.NEXT_PUBLIC_AURORA_API_URL || 'http://localhost:8000/api/v1'
      const newUserId = `NEW-CITIZEN-${Date.now()}`
      const res = await fetch(`${apiUrl}/dev/token?user_id=${encodeURIComponent(newUserId)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      })

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({ detail: 'Dev token alınamadı' }))
        throw new Error(errorData.detail || 'Dev token alınamadı. Backend dev modunda mı?')
      }

      const { token } = await res.json()
      setToken(token)
      setHasToken(true)
      onNext()
    } catch (err: any) {
      setError(err.message || 'Dev token alınamadı. Backend çalışıyor mu?')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <h2 className="text-xl font-semibold mb-2">Aurora Vatandaşlığına Başla</h2>
      <p className="text-sm text-gray-300 mb-6">
        Devam etmek için bir kimlik doğrulama yöntemi seç. Email, Google veya dev mode kullanabilirsin.
      </p>

      {error && (
        <div className="rounded-lg border border-red-500/30 bg-red-500/10 p-3 mb-4">
          <p className="text-sm text-red-300">⚠️ {error}</p>
        </div>
      )}

      <div className="space-y-3">
        {/* Email Auth */}
        <div className="rounded-xl border border-white/10 bg-black/60 p-4">
          <button
            onClick={() => setAuthMethod(authMethod === 'email' ? null : 'email')}
            className="w-full flex items-center justify-between text-left"
          >
            <div>
              <h3 className="text-sm font-semibold text-gray-100">📧 Email ile Giriş</h3>
              <p className="text-xs text-gray-400 mt-1">Email ve şifre ile kayıt ol / giriş yap</p>
            </div>
            <span className="text-purple-400">{authMethod === 'email' ? '▼' : '▶'}</span>
          </button>

          {authMethod === 'email' && (
            <form onSubmit={handleEmailAuth} className="mt-4 space-y-3">
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Email adresin"
                required
                className="w-full rounded-lg border border-white/15 bg-black/60 px-3 py-2 text-sm text-gray-100 placeholder:text-gray-500 focus:outline-none focus:border-purple-500/70"
              />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Şifre (min 8 karakter)"
                required
                minLength={8}
                className="w-full rounded-lg border border-white/15 bg-black/60 px-3 py-2 text-sm text-gray-100 placeholder:text-gray-500 focus:outline-none focus:border-purple-500/70"
              />
              <button
                type="submit"
                disabled={loading || !email || !password}
                className="w-full rounded-lg bg-purple-500 px-4 py-2 text-sm font-semibold text-white hover:bg-purple-400 transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Giriş yapılıyor...' : 'Giriş Yap / Kayıt Ol'}
              </button>
            </form>
          )}
        </div>

        {/* Google OAuth */}
        <div className="rounded-xl border border-white/10 bg-black/60 p-4">
          <button
            onClick={handleGoogleAuth}
            disabled={loading}
            className="w-full flex items-center justify-between text-left disabled:opacity-50"
          >
            <div>
              <h3 className="text-sm font-semibold text-gray-100">🔐 Google ile Giriş</h3>
              <p className="text-xs text-gray-400 mt-1">Google hesabın ile hızlıca giriş yap</p>
            </div>
            <span className="text-purple-400">→</span>
          </button>
          <p className="text-xs text-gray-500 mt-2 text-center">
            Google OAuth henüz aktif değil. Dev mode kullanabilirsin.
          </p>
        </div>

        {/* Dev Mode */}
        <div className="rounded-xl border border-purple-500/30 bg-purple-500/10 p-4">
          <button
            onClick={handleDevMode}
            disabled={loading}
            className="w-full flex items-center justify-between text-left disabled:opacity-50"
          >
            <div>
              <h3 className="text-sm font-semibold text-purple-200">⚡ Dev Mode (Hızlı Test)</h3>
              <p className="text-xs text-purple-300/70 mt-1">
                Anında vatandaş ol, test için ideal
              </p>
            </div>
            <span className="text-purple-400">→</span>
          </button>
        </div>
      </div>

      <div className="flex justify-end pt-4">
        <button
          onClick={onNext}
          disabled={!hasToken}
          className="rounded-xl bg-purple-500 px-4 py-2 text-sm font-semibold text-white hover:bg-purple-400 transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {hasToken ? 'Devam Et →' : 'Önce giriş yap'}
        </button>
      </div>
    </>
  )
}

/* --- Step 2: Intro --- */

function StepIntro({ onBack, onNext }: { onBack: () => void; onNext: () => void }) {
  return (
    <>
      <h2 className="text-xl font-semibold mb-2">Aurora bir "uygulama" değil, bir protokol-devlet.</h2>
      <p className="text-sm text-gray-300 mb-4">
        Burada hesap açmıyorsun; davranışın, verin ve hakların bir{' '}
        <strong>NovaScore + Justice + Consent</strong> üçgenine yazılıyor. Devlet motoru backend'de,
        politika DAO'da, hakların anayasada.
      </p>

      <ul className="list-disc list-inside text-sm text-gray-300 space-y-1 mb-6">
        <li>Verinin sahibi sensin, onayı veren de sensin.</li>
        <li>Politika parametreleri AuroraDAO tarafından oylanır.</li>
        <li>Ceza sistemi şeffaf; CP ve rejimin her an görünür.</li>
      </ul>

      <div className="flex justify-end">
        <button
          onClick={onNext}
          className="rounded-xl bg-purple-500 px-4 py-2 text-sm font-semibold text-white hover:bg-purple-400 transition"
        >
          Devam et
        </button>
      </div>
    </>
  )
}

/* --- Step 2: Consent --- */

function StepConsent({ onBack, onNext }: { onBack: () => void; onNext: () => void }) {
  const [consentCompleted, setConsentCompleted] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [initializing, setInitializing] = useState(true)
  const [userId, setUserId] = useState<string | undefined>()
  const { createSession, acceptClause, acceptRedline, signConsent, session } = useConsentFlow()

  // Initialize: Get dev token if not exists, then create consent session
  useEffect(() => {
    const init = async () => {
      try {
        // 1. Check if we have a token
        let token = getToken()
        let userId: string | undefined
        
        // 2. If no token, get a dev token (for onboarding)
        if (!token) {
          const apiUrl = process.env.NEXT_PUBLIC_AURORA_API_URL || 'http://localhost:8000/api/v1'
          const newUserId = `NEW-CITIZEN-${Date.now()}`
          
          try {
            const res = await fetch(`${apiUrl}/dev/token?user_id=${encodeURIComponent(newUserId)}`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
            })
            
            if (!res.ok) {
              const errorData = await res.json().catch(() => ({ detail: 'Unknown error' }))
              throw new Error(
                errorData.detail || 
                `Backend hatası (${res.status}). Backend çalışıyor mu? Dev modunda mı?`
              )
            }
            
            const { token: newToken, user_id } = await res.json()
            setToken(newToken)
            token = newToken
            const finalUserId = user_id || newUserId
            setUserId(finalUserId)
            userId = finalUserId
          } catch (fetchError: any) {
            // Network error or other fetch error
            if (fetchError.message) {
              throw fetchError
            }
            throw new Error(
              `Backend'e bağlanılamadı. Backend çalışıyor mu? (${apiUrl})`
            )
          }
        }

        // 3. Create consent session (with userId if we have it)
        await createSession(userId)
      } catch (err: any) {
        console.error('Initialization error:', err)
        setError(err.message || 'Başlatılamadı. Backend çalışıyor mu?')
      } finally {
        setInitializing(false)
      }
    }

    init()
  }, [createSession])

  const handleConsentComplete = async (consentData: {
    clauses: string[]
    redlineAccepted: boolean
    signature: string
  }) => {
    if (!session) {
      setError('Consent session bulunamadı. Lütfen sayfayı yenileyin.')
      return
    }

    setLoading(true)
    setError(null)

    try {
      // 1. Accept all clauses
      for (const clauseId of consentData.clauses) {
        await acceptClause(session.session_id, clauseId, 'ACCEPTED')
      }

      // 2. Accept redline if needed
      if (consentData.redlineAccepted) {
        await acceptRedline(session.session_id, 'ACCEPTED')
      }

      // 3. Sign consent
      const result = await signConsent(
        session.session_id,
        consentData.clauses,
        consentData.signature,
        userId || session.user_id
      )

      if (!result) {
        throw new Error('Consent imzalama başarısız oldu')
      }

      setConsentCompleted(true)
      onNext()
    } catch (err: any) {
      console.error('Consent submission error:', err)
      setError(err.message || 'Consent gönderilemedi. Backend çalışıyor mu?')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <h2 className="text-xl font-semibold mb-2">Veri Etiği & Şeffaflık Sözleşmesi</h2>
      <p className="text-sm text-gray-300 mb-4">
        Aurora'ya kabul edilmeden önce, Veri Etiği Sözleşmesi'ni interaktif olarak onaylaman
        gerekiyor. Bu, seni de devleti de koruyan katman.
      </p>

      {initializing ? (
        <div className="flex items-center justify-center min-h-[200px] text-gray-400">
          Consent session başlatılıyor...
        </div>
      ) : (
        <div className="rounded-xl border border-white/10 bg-black/60 p-3 mb-4">
          <ConsentFlow onComplete={handleConsentComplete} />
        </div>
      )}

      {error && (
        <div className="rounded-lg border border-red-500/30 bg-red-500/10 p-3 mb-4">
          <p className="text-sm text-red-300">⚠️ {error}</p>
        </div>
      )}

      {consentCompleted && (
        <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-3 mb-4">
          <p className="text-sm text-emerald-300">✓ Consent signed successfully</p>
        </div>
      )}

      <div className="flex items-center justify-between text-xs text-gray-400">
        <button
          onClick={onBack}
          className="rounded-lg border border-white/15 px-3 py-1.5 hover:bg-white/5 transition"
        >
          Geri
        </button>
        <button
          onClick={onNext}
          disabled={!consentCompleted || loading}
          className="rounded-lg bg-purple-500 px-3 py-1.5 text-white font-semibold hover:bg-purple-400 transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Gönderiliyor...' : 'Onayı tamamladım'}
        </button>
      </div>
    </>
  )
}

/* --- Step 3: NovaScore --- */

function StepNovaScore({
  onBack,
  onFinish,
}: {
  onBack: () => void
  onFinish: () => void
}) {
  const { score, loading: scoreLoading } = useNovaScore()
  const { cpState, loading: justiceLoading } = useJustice()
  const { track } = useAuroraEvents()

  const handleFinish = async () => {
    // Track onboarding completion
    await track('onboarding_completed', {
      nova_score: score?.value || 0,
      regime: cpState?.regime || 'NORMAL',
      cp_value: cpState?.cp_value || 0,
    })
    onFinish()
  }

  // Show loading state
  if (scoreLoading || justiceLoading) {
    return (
      <div className="flex items-center justify-center min-h-[300px]">
        <div className="text-gray-400">Generating your NovaScore...</div>
      </div>
    )
  }

  // Use real data if available, otherwise show mock
  const displayScore = score || {
    value: 710,
    components: {
      ECO: { value: 70, confidence: 0.9 },
      REL: { value: 75, confidence: 0.95 },
      SOC: { value: 68, confidence: 0.85 },
      ID: { value: 80, confidence: 0.98 },
      CON: { value: 72, confidence: 0.92 },
    },
    confidence_overall: 0.95,
    explanation: 'Initial NovaScore generated after consent completion',
  }

  const displayCp = cpState || {
    user_id: 'new-citizen',
    cp_value: 0,
    regime: 'NORMAL' as const,
    last_updated_at: new Date().toISOString(),
  }

  return (
    <>
      <h2 className="text-xl font-semibold mb-2">İlk NovaScore'un hazır. Hoş geldin.</h2>
      <p className="text-sm text-gray-300 mb-4">
        Onay akışını tamamladın. Buradan sonra davranışların, etkileşimlerin ve sistem içindeki
        hareketlerin NovaScore ve CP/Regime üzerinden değerlendirilecek.
      </p>

      <div className="grid md:grid-cols-2 gap-4 mb-4">
        <NovaScoreCard novaScore={displayScore as NovaScorePayload} showDetails={true} />
        <div className="aurora-card">
          <h3 className="text-lg font-semibold text-slate-200 mb-4">Justice Status</h3>
          <div className="space-y-4">
            <RegimeBadge regime={displayCp.regime} size="lg" showLabel={true} />
            <div>
              <p className="text-sm text-slate-400 mb-1">CP Value</p>
              <p className="text-2xl font-bold text-aurora-purple">{displayCp.cp_value}</p>
            </div>
            <div>
              <p className="text-sm text-slate-400 mb-1">Status</p>
              <p className="text-sm text-emerald-300">Citizen in good standing</p>
            </div>
          </div>
        </div>
      </div>

      {!score && (
        <p className="text-xs text-gray-400 mb-4">
          ⚠️ Backend API'ye bağlanamadı. Demo değerler gösteriliyor. API çalıştığında gerçek
          NovaScore hesaplanacak.
        </p>
      )}

      <div className="flex items-center justify-between text-xs text-gray-400">
        <button
          onClick={onBack}
          className="rounded-lg border border-white/15 px-3 py-1.5 hover:bg-white/5 transition"
        >
          Geri
        </button>
        <button
          onClick={handleFinish}
          className="rounded-lg bg-emerald-500 px-3 py-1.5 text-white font-semibold hover:bg-emerald-400 transition"
        >
          Dashboard'a geç
        </button>
      </div>
    </>
  )
}

