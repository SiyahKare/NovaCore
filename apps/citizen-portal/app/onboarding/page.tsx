'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { ConsentFlow, NovaScoreCard, RegimeBadge } from '@aurora/ui'
import { useNovaScore, useJustice, useAuroraEvents, useConsentFlow, useCurrentCitizen } from '@aurora/hooks'
import { setToken, getToken } from '@/lib/auth'
import type { NovaScorePayload, CpState } from '@aurora/ui'

// Telegram OAuth Types
interface TelegramAuthResult {
  id: number
  first_name: string
  last_name?: string
  username?: string
  photo_url?: string
  auth_date: number
  hash: string
}

let telegramLoginScriptPromise: Promise<void> | null = null

async function ensureTelegramLoginScript() {
  if (typeof window === 'undefined') {
    throw new Error('Telegram doğrulaması sadece tarayıcıda başlatılabilir.')
  }

  if ((window as any).Telegram?.Login) {
    return
  }

  if (!telegramLoginScriptPromise) {
    telegramLoginScriptPromise = new Promise((resolve, reject) => {
      const script = document.createElement('script')
      script.id = 'telegram-login-script'
      script.src = 'https://telegram.org/js/telegram-widget.js?22'
      script.async = true
      script.onload = () => resolve()
      script.onerror = () => {
        telegramLoginScriptPromise = null
        reject(new Error('Telegram doğrulama betiği yüklenemedi.'))
      }
      document.body.appendChild(script)
    })
  }

  await telegramLoginScriptPromise

  if (!(window as any).Telegram?.Login) {
    throw new Error('Telegram doğrulama betiği hazır değil. Yeniden deneyin.')
  }
}

async function requestTelegramOAuth(): Promise<TelegramAuthResult> {
  await ensureTelegramLoginScript()

  const botIdStr = process.env.NEXT_PUBLIC_TELEGRAM_BOT_ID
  if (!botIdStr) {
    throw new Error('Telegram bot ID tanımlı değil (NEXT_PUBLIC_TELEGRAM_BOT_ID).')
  }

  const botId = Number(botIdStr)
  if (!botId) {
    throw new Error('Geçersiz Telegram bot ID.')
  }

  // Origin URL'i al (production'da Cloudflare domain, dev'de localhost)
  const origin = typeof window !== 'undefined' 
    ? window.location.origin 
    : (process.env.NEXT_PUBLIC_AURORA_API_URL?.replace('/api/v1', '') || 'http://localhost:3000')

  return await new Promise((resolve, reject) => {
    const login = (window as any).Telegram?.Login
    if (!login?.auth) {
      reject(new Error('Telegram doğrulama arayüzü bulunamadı.'))
      return
    }

    login.auth(
      {
        bot_id: botId,
        request_access: 'write',
        origin: origin,
      },
      (response: TelegramAuthResult | { error?: string } | undefined) => {
        if (!response || (response as any).error) {
          reject(new Error('Telegram doğrulaması iptal edildi.'))
        } else {
          resolve(response as TelegramAuthResult)
        }
      },
    )
  })
}

type Step = 1 | 2 | 3 | 4

export default function OnboardingPage() {
  const [step, setStep] = useState<Step>(1)
  const router = useRouter()
  const { isAuthenticated, loading } = useCurrentCitizen()

  // Token varsa ve geçerliyse direkt dashboard'a yönlendir
  useEffect(() => {
    if (!loading && isAuthenticated) {
      router.push('/dashboard')
    }
  }, [isAuthenticated, loading, router])

  const next = () => setStep((s) => (s === 4 ? 4 : ((s + 1) as Step)))
  const back = () => setStep((s) => (s === 1 ? 1 : ((s - 1) as Step)))

  // Loading durumunda göster
  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-sm text-gray-400">Kimlik doğrulanıyor...</div>
      </div>
    )
  }

  // Zaten authenticated ise hiçbir şey gösterme (redirect olacak)
  if (isAuthenticated) {
    return null
  }

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <header className="space-y-2">
        <div className="text-xs uppercase tracking-[0.2em] text-purple-300">SiyahKare Onboarding</div>
        <h1 className="text-3xl font-semibold">Become a Citizen</h1>
        <p className="text-sm text-gray-400">
          3 adımda SiyahKare Cumhuriyeti'ne giriş yapıyorsun. Bu bir ürün kayıt formu değil; dijital
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
  const [isTelegramWebApp, setIsTelegramWebApp] = useState(false)
  const { isAuthenticated, loading: authLoading } = useCurrentCitizen()
  
  // Check token on client-side only to avoid hydration mismatch
  useEffect(() => {
    const token = getToken()
    setHasToken(!!token)
    
    // Token varsa ve geçerliyse otomatik olarak bir sonraki adıma geç
    if (token && !authLoading && isAuthenticated) {
      onNext()
    }
  }, [isAuthenticated, authLoading, onNext])
  
  // Telegram WebApp kontrolü
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const checkTelegram = async () => {
        try {
          const { loadTelegramWebAppScript, isTelegramWebApp, getTelegramUser } = await import('@/lib/telegram-webapp')
          await loadTelegramWebAppScript()
          const isTg = isTelegramWebApp()
          setIsTelegramWebApp(isTg)
          
          // Eğer Telegram WebApp içindeyse ve kullanıcı varsa otomatik auth dene
          if (isTg && !getToken()) {
            const user = getTelegramUser()
            if (user) {
              // Otomatik auth dene
              handleTelegramWebAppAuth()
            }
          }
        } catch (err) {
          // Telegram WebApp değil, normal web
          setIsTelegramWebApp(false)
        }
      }
      checkTelegram()
    }
  }, [])

  // URL'den telegram_user_id parametresini kontrol et (bot'tan deep link)
  useEffect(() => {
    if (typeof window !== 'undefined' && !getToken()) {
      const params = new URLSearchParams(window.location.search)
      const telegramUserId = params.get('telegram_user_id')
      
      if (telegramUserId) {
        // Bot'tan gelen deep link ile token al
        handleTelegramLinkFromUrl(telegramUserId)
      }
    }
  }, [])

  const handleEmailAuth = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const apiUrl = process.env.NEXT_PUBLIC_AURORA_API_URL || 'http://localhost:8000/api/v1'
      
      // Try login first
      let res = await fetch(`${apiUrl}/identity/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })

      // If login fails with 401, try register
      if (!res.ok && res.status === 401) {
        res = await fetch(`${apiUrl}/identity/register`, {
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

  const handleTelegramWebAppAuth = async () => {
    setLoading(true)
    setError(null)

    try {
      const { getTelegramInitData, parseTelegramInitData } = await import('@/lib/telegram-webapp')
      const initData = getTelegramInitData()
      
      if (!initData) {
        throw new Error('Telegram initData bulunamadı')
      }

      const parsed = parseTelegramInitData(initData)
      if (!parsed || !parsed.telegram_id) {
        throw new Error('Telegram kullanıcı bilgileri parse edilemedi')
      }

      const apiUrl = process.env.NEXT_PUBLIC_AURORA_API_URL || 'http://localhost:8000/api/v1'
      const res = await fetch(`${apiUrl}/identity/telegram/auth`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          telegram_id: parsed.telegram_id,
          username: parsed.username,
          first_name: parsed.first_name,
          last_name: parsed.last_name,
          photo_url: parsed.photo_url,
          auth_date: parsed.auth_date,
          hash: parsed.hash,
        }),
      })

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({ detail: 'Telegram auth hatası' }))
        throw new Error(errorData.detail || 'Telegram ile giriş yapılamadı')
      }

      const { access_token } = await res.json()
      setToken(access_token)
      setHasToken(true)
      onNext()
    } catch (err: any) {
      setError(err.message || 'Telegram ile otomatik giriş yapılamadı')
      setLoading(false)
    }
  }

  const handleTelegramLinkFromUrl = async (telegramUserId: string) => {
    setLoading(true)
    setError(null)

    try {
      const apiUrl = process.env.NEXT_PUBLIC_AURORA_API_URL || 'http://localhost:8000/api/v1'
      const res = await fetch(`${apiUrl}/dev/token/telegram?telegram_user_id=${encodeURIComponent(telegramUserId)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      })

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({ detail: 'Token alınamadı' }))
        throw new Error(errorData.detail || 'Telegram kullanıcısı bulunamadı. Önce Telegram\'da /start gönderin.')
      }

      const { token } = await res.json()
      setToken(token)
      setHasToken(true)
      
      // URL'den parametreyi temizle
      window.history.replaceState({}, '', window.location.pathname)
      
      onNext()
    } catch (err: any) {
      setError(err.message || 'Telegram kullanıcısı bulunamadı. Önce Telegram\'da /start gönderin.')
      setLoading(false)
    }
  }

  const handleTelegramOAuth = async () => {
    setLoading(true)
    setError(null)

    try {
      // Telegram Login script'ini yükle ve OAuth widget'ını başlat
      const authResult = await requestTelegramOAuth()

      // API URL'i belirle (production'da Cloudflare domain)
      const apiUrl = process.env.NEXT_PUBLIC_AURORA_API_URL || 
        (typeof window !== 'undefined' && window.location.hostname.includes('siyahkare.com')
          ? 'https://api.siyahkare.com/api/v1'
          : 'http://localhost:8000/api/v1')

      console.log('Telegram OAuth - API URL:', apiUrl)
      console.log('Telegram OAuth - Auth Result:', authResult)

      const res = await fetch(`${apiUrl}/identity/telegram/auth`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          telegram_id: authResult.id,
          username: authResult.username,
          first_name: authResult.first_name,
          last_name: authResult.last_name,
          photo_url: authResult.photo_url,
          auth_date: authResult.auth_date,
          hash: authResult.hash,
        }),
      })

      console.log('Telegram OAuth - Response status:', res.status)

      if (!res.ok) {
        let errorMessage = 'Telegram ile giriş yapılamadı'
        try {
          const errorData = await res.json()
          errorMessage = errorData.detail || errorData.error || errorMessage
          console.error('Telegram OAuth - Error:', errorData)
        } catch (parseError) {
          const text = await res.text()
          errorMessage = `Backend hatası (${res.status}): ${text || 'Bilinmeyen hata'}`
          console.error('Telegram OAuth - Parse error:', parseError, 'Response text:', text)
        }
        throw new Error(errorMessage)
      }

      const responseData = await res.json()
      console.log('Telegram OAuth - Success:', responseData)

      if (!responseData.access_token) {
        throw new Error('Token alınamadı. Backend response formatı beklenmedik.')
      }

      setToken(responseData.access_token)
      setHasToken(true)
      onNext()
    } catch (err: any) {
      console.error('Telegram OAuth - Exception:', err)
      const errorMessage = err.message || 'Telegram ile giriş yapılamadı'
      setError(errorMessage)
      setLoading(false)
    }
  }

  const handleTelegramLink = async () => {
    const telegramUserId = prompt('Telegram User ID\'nizi girin (Telegram\'da /start gönderdiğinizde bot log\'larında görünür):')
    if (!telegramUserId) return

    await handleTelegramLinkFromUrl(telegramUserId)
  }

  return (
    <>
      <h2 className="text-xl font-semibold mb-2">SiyahKare Vatandaşlığına Başla</h2>
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

        {/* Telegram OAuth */}
        <div className="rounded-xl border border-cyan-500/30 bg-cyan-500/10 p-4">
          <button
            onClick={handleTelegramOAuth}
            disabled={loading}
            className="w-full flex items-center justify-between text-left disabled:opacity-50"
          >
            <div>
              <h3 className="text-sm font-semibold text-cyan-200">🤖 Telegram Connect ile Auth</h3>
              <p className="text-xs text-cyan-300/70 mt-1">
                Telegram hesabın ile hızlıca giriş yap
              </p>
            </div>
            <span className="text-cyan-400">→</span>
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
      <h2 className="text-xl font-semibold mb-2">NovaCore + Aurora bir "uygulama" değil, bir devlet motoru.</h2>
      <p className="text-sm text-gray-300 mb-4">
        Burada hesap açmıyorsun; davranışın, verin ve hakların{' '}
        <strong>NovaScore + Aurora Justice + Consent</strong> üçgenine yazılıyor. Devlet motoru NovaCore’da,
        politika Aurora Justice DAO’da, hakların SiyahKare Anayasası’nda.
      </p>

      <ul className="list-disc list-inside text-sm text-gray-300 space-y-1 mb-6">
        <li>Verinin sahibi sensin, onayı veren de sensin.</li>
        <li>Politika parametreleri Aurora Justice DAO tarafından oylanır.</li>
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
        SiyahKare sistemine kabul edilmeden önce, Veri Etiği Sözleşmesi'ni interaktif olarak onaylaman
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

