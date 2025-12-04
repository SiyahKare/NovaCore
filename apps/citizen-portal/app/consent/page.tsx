'use client'

import { useState, useEffect } from 'react'
import { ProtectedView } from '@/components/ProtectedView'
import { ConsentFlow } from '@aurora/ui'
import { useConsentFlow, useAuroraAPI } from '@aurora/hooks'
import { getToken } from '@/lib/auth'

interface PrivacyProfile {
  user_id: string
  latest_consent_id: string | null
  contract_version: string | null
  consent_level: string | null
  recall_requested_at: string | null
  last_policy_updated_at: string
  policy: {
    behavioral: { allowed: boolean; purposes: string[] }
    performance: { allowed: boolean; purposes: string[] }
    economy: { allowed: boolean; purposes: string[] }
    redline: { allowed: boolean; purposes: string[]; requires_human_ethics_board: boolean }
  }
}

interface ConsentRecord {
  record_id: string
  user_id: string
  contract_version: string
  clauses_accepted: string[]
  redline_accepted: boolean
  signature_text: string
  contract_hash: string
  signed_at: string
  created_at: string
}

interface RecallStatus {
  user_id: string
  recall_requested_at: string | null
  recall_mode: 'FULL_EXCLUDE' | 'ANONYMIZE' | null
  recall_completed_at: string | null
  state?: 'NONE' | 'REQUESTED' | 'IN_PROGRESS' | 'COMPLETED'
}

export default function ConsentPage() {
  return (
    <ProtectedView>
      <ConsentInner />
    </ProtectedView>
  )
}

function ConsentInner() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)
  const [initializing, setInitializing] = useState(true)
  const [session, setSession] = useState<any>(null)
  const [privacyProfile, setPrivacyProfile] = useState<PrivacyProfile | null>(null)
  const [consentRecord, setConsentRecord] = useState<ConsentRecord | null>(null)
  const [recallStatus, setRecallStatus] = useState<RecallStatus | null>(null)
  const [hasConsent, setHasConsent] = useState(false)
  const [showRecallModal, setShowRecallModal] = useState(false)
  const [recallMode, setRecallMode] = useState<'FULL_EXCLUDE' | 'ANONYMIZE'>('FULL_EXCLUDE')
  const [recallLoading, setRecallLoading] = useState(false)
  const { fetchAPI } = useAuroraAPI()
  const { createSession, acceptClause, acceptRedline, signConsent } = useConsentFlow()

  // Initialize: Check existing consent, then create session if needed
  useEffect(() => {
    const init = async () => {
      try {
        const token = getToken()
        if (!token) {
          setError('Önce giriş yapmalısın')
          setInitializing(false)
          return
        }

        // First, check if user already has a privacy profile (consent signed)
        try {
          const { data: profile, error: profileError } = await fetchAPI<PrivacyProfile>('/consent/profile/me')
          if (!profileError && profile && profile.latest_consent_id) {
            setPrivacyProfile(profile)
            setHasConsent(true)
            
            // Load detailed consent record
            try {
              const { data: record } = await fetchAPI<ConsentRecord>(`/consent/records/${profile.latest_consent_id}`)
              if (record) {
                setConsentRecord(record)
              }
            } catch (err) {
              console.error('Failed to load consent record:', err)
            }
            
            // Load recall status
            try {
              const { data: recall } = await fetchAPI<RecallStatus>('/consent/recall/status')
              if (recall) {
                setRecallStatus(recall)
              }
            } catch (err) {
              console.error('Failed to load recall status:', err)
            }
            
            setInitializing(false)
            return
          }
        } catch (err) {
          // Privacy profile not found is OK - means no consent yet
          console.log('No existing consent found, will create new session')
        }

        // If no existing consent, create a new session
        const sessionData = await createSession()
        setSession(sessionData)
      } catch (err: any) {
        console.error('Session initialization error:', err)
        setError(err.message || 'Session oluşturulamadı')
      } finally {
        setInitializing(false)
      }
    }

    init()
  }, [createSession, fetchAPI])

  // Poll recall status if recall is requested but not completed
  useEffect(() => {
    if (!hasConsent || !recallStatus?.recall_requested_at || recallStatus.recall_completed_at) {
      return
    }

    const checkRecallStatus = async () => {
      try {
        const { data: recall } = await fetchAPI<RecallStatus>('/consent/recall/status')
        if (recall) {
          setRecallStatus(recall)
          
          // If completed, reload privacy profile
          if (recall.recall_completed_at) {
            const { data: updatedProfile } = await fetchAPI<PrivacyProfile>('/consent/profile/me')
            if (updatedProfile) {
              setPrivacyProfile(updatedProfile)
            }
          }
        }
      } catch (err) {
        console.error('Failed to check recall status:', err)
      }
    }

    // Poll every 5 seconds if recall is in progress
    const intervalId = setInterval(checkRecallStatus, 5000)
    
    // Cleanup on unmount
    return () => clearInterval(intervalId)
  }, [hasConsent, recallStatus, fetchAPI])

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
    setSuccess(false)

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
        session.user_id
      )

      if (!result) {
        throw new Error('Consent imzalama başarısız oldu')
      }

      setSuccess(true)
      // Reload privacy profile to show signed consent
      try {
        const { data: profile } = await fetchAPI<PrivacyProfile>('/consent/profile/me')
        if (profile && profile.latest_consent_id) {
          setPrivacyProfile(profile)
          setHasConsent(true)
          setSession(null) // Clear session since consent is now signed
        }
      } catch (err) {
        console.error('Failed to reload privacy profile:', err)
      }
    } catch (err: any) {
      console.error('Consent submission error:', err)
      setError(err.message || 'Consent gönderilemedi. Backend çalışıyor mu?')
    } finally {
      setLoading(false)
    }
  }

  const handleRecallRequest = async () => {
    setRecallLoading(true)
    setError(null)

    try {
      const { data, error: recallError } = await fetchAPI<RecallStatus>('/consent/recall', {
        method: 'POST',
        body: JSON.stringify({
          mode: recallMode,
          reason: 'User requested data exclusion from AI training',
        }),
      })

      if (recallError || !data) {
        throw new Error(recallError?.detail || 'Recall talebi oluşturulamadı')
      }

      setRecallStatus(data)
      setShowRecallModal(false)
      
      // Reload privacy profile to reflect recall status
      try {
        const { data: profile } = await fetchAPI<PrivacyProfile>('/consent/profile/me')
        if (profile) {
          setPrivacyProfile(profile)
        }
      } catch (err) {
        console.error('Failed to reload privacy profile:', err)
      }
    } catch (err: any) {
      console.error('Recall request error:', err)
      setError(err.message || 'Recall talebi oluşturulamadı')
    } finally {
      setRecallLoading(false)
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold mb-2">Consent & Privacy</h1>
        <p className="text-gray-400">Manage your data usage preferences and consent agreements</p>
      </div>

      {error && (
        <div className="rounded-lg border border-red-500/30 bg-red-500/10 p-3">
          <p className="text-sm text-red-300">⚠️ {error}</p>
        </div>
      )}

      {success && (
        <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-3">
          <p className="text-sm text-emerald-300">✓ Consent başarıyla imzalandı! Sayfa yenileniyor...</p>
        </div>
      )}

      {initializing ? (
        <div className="aurora-card">
          <div className="flex items-center justify-center min-h-[200px] text-gray-400">
            Consent durumu kontrol ediliyor...
          </div>
        </div>
      ) : hasConsent && privacyProfile ? (
        <div className="space-y-4">
          {/* Consent Status Card */}
          <div className="aurora-card space-y-4">
            <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-4">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="text-lg font-semibold text-emerald-300 mb-1">✓ Consent İmzalanmış</h3>
                  <p className="text-sm text-gray-300">
                    Veri Etiği & Şeffaflık Sözleşmesi başarıyla imzalandı ve immutable ledger'e kaydedildi.
                  </p>
                </div>
                {recallStatus?.recall_requested_at && (
                  <div className="rounded-lg border border-yellow-500/30 bg-yellow-500/10 px-3 py-1.5">
                    <span className="text-xs text-yellow-300">Recall Talebi Aktif</span>
                  </div>
                )}
              </div>
              
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <span className="text-gray-400">Sözleşme Versiyonu:</span>
                  <div className="text-gray-200 font-mono text-xs mt-1">{privacyProfile.contract_version || 'N/A'}</div>
                </div>
                <div>
                  <span className="text-gray-400">Consent Seviyesi:</span>
                  <div className="text-gray-200 mt-1">{privacyProfile.consent_level || 'N/A'}</div>
                </div>
                <div>
                  <span className="text-gray-400">İmza Tarihi:</span>
                  <div className="text-gray-200 mt-1">
                    {consentRecord?.signed_at 
                      ? new Date(consentRecord.signed_at).toLocaleString('tr-TR')
                      : new Date(privacyProfile.last_policy_updated_at).toLocaleString('tr-TR')}
                  </div>
                </div>
                <div>
                  <span className="text-gray-400">Contract Hash:</span>
                  <div className="text-gray-200 font-mono text-xs mt-1 break-all">
                    {consentRecord?.contract_hash?.substring(0, 16) + '...' || 'N/A'}
                  </div>
                </div>
              </div>
            </div>

            {/* Signed Clauses */}
            {consentRecord && (
              <div className="rounded-lg border border-white/10 bg-black/60 p-4">
                <h4 className="text-sm font-semibold text-purple-200 mb-3">Kabul Edilen Maddeler</h4>
                <div className="grid grid-cols-2 gap-2">
                  {consentRecord.clauses_accepted.map((clause) => {
                    const clauseNames: Record<string, string> = {
                      '1.1': 'Veri Egemenliği',
                      '1.2': 'Veri Kullanımı ve Şeffaflık',
                      '2.1': 'NovaScore ve Skorlama',
                      '2.2': 'Kırmızı Hat - Hassas Veriler',
                      '3.1': 'CP (Ceza Puanı) ve Regime Sistemi',
                      '3.2': 'Enforcement ve Kısıtlamalar',
                      '4.1': 'Recall Hakkı (Veri Geri Çekme)',
                      '4.2': 'DAO ve Policy Governance',
                    }
                    return (
                      <div key={clause} className="flex items-center gap-2 text-xs">
                        <span className="text-emerald-400">✓</span>
                        <span className="text-gray-300">
                          <strong>{clause}</strong> - {clauseNames[clause] || clause}
                        </span>
                      </div>
                    )
                  })}
                </div>
                {consentRecord.redline_accepted && (
                  <div className="mt-3 pt-3 border-t border-white/10">
                    <div className="flex items-center gap-2 text-xs">
                      <span className="text-red-400">⚠</span>
                      <span className="text-gray-300">
                        <strong>Kırmızı Hat (2.2)</strong> kabul edildi
                      </span>
                    </div>
                  </div>
                )}
                <div className="mt-3 pt-3 border-t border-white/10">
                  <div className="text-xs">
                    <span className="text-gray-400">E-imza:</span>
                    <span className="text-gray-200 ml-2 font-mono">{consentRecord.signature_text}</span>
                  </div>
                </div>
              </div>
            )}

            {/* Data Usage Policy */}
            <div className="rounded-lg border border-white/10 bg-black/60 p-4">
              <h4 className="text-sm font-semibold text-purple-200 mb-3">Veri Kullanım Politikası</h4>
              <div className="space-y-2 text-xs text-gray-300">
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Behavioral Data:</span>
                  <span className={privacyProfile.policy.behavioral.allowed ? 'text-emerald-400' : 'text-red-400'}>
                    {privacyProfile.policy.behavioral.allowed ? '✓ İzin Verildi' : '✗ Kısıtlandı'}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Performance Data:</span>
                  <span className={privacyProfile.policy.performance.allowed ? 'text-emerald-400' : 'text-red-400'}>
                    {privacyProfile.policy.performance.allowed ? '✓ İzin Verildi' : '✗ Kısıtlandı'}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Economy Data:</span>
                  <span className={privacyProfile.policy.economy.allowed ? 'text-emerald-400' : 'text-red-400'}>
                    {privacyProfile.policy.economy.allowed ? '✓ İzin Verildi' : '✗ Kısıtlandı'}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Redline Data:</span>
                  <span className={privacyProfile.policy.redline.allowed ? 'text-emerald-400' : 'text-red-400'}>
                    {privacyProfile.policy.redline.allowed ? '✓ İzin Verildi' : '✗ Kısıtlandı'}
                  </span>
                </div>
                {privacyProfile.policy.redline.requires_human_ethics_board && (
                  <div className="text-yellow-400 text-xs mt-2">
                    ⚠ Redline verileri için Etik Kurul onayı gerekli
                  </div>
                )}
              </div>
            </div>

            {/* Recall Section */}
            <div className="rounded-lg border border-white/10 bg-black/60 p-4">
              <h4 className="text-sm font-semibold text-purple-200 mb-3">Veri Geri Çekme (Recall)</h4>
              {recallStatus?.recall_requested_at ? (
                <div className="space-y-2">
                  <div className="text-xs text-gray-300">
                    <span className="text-gray-400">Recall Talebi:</span>{' '}
                    <span className="text-yellow-300">
                      {new Date(recallStatus.recall_requested_at).toLocaleString('tr-TR')}
                    </span>
                  </div>
                  <div className="text-xs text-gray-300">
                    <span className="text-gray-400">Mod:</span>{' '}
                    <span className="text-yellow-300">
                      {recallStatus.recall_mode === 'FULL_EXCLUDE' ? 'Tam Geri Çekme' : 'Anonimleştirme'}
                    </span>
                  </div>
                  {recallStatus.recall_completed_at ? (
                    <div className="space-y-2">
                      <div className="text-xs text-emerald-300">
                        ✓ Recall tamamlandı: {new Date(recallStatus.recall_completed_at).toLocaleString('tr-TR')}
                      </div>
                      <div className="text-xs text-gray-400">
                        Verilerin YZ eğitiminden çıkarıldı/anonimleştirildi. NovaScore daha ihtiyatlı hesaplanıyor.
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <div className="text-xs text-yellow-300">
                        ⏳ Recall talebi işleniyor...
                      </div>
                      <div className="text-xs text-gray-400">
                        Talebiniz alındı. SiyahKare NovaCore ekibi recall talebinizi 48 saat içinde işlemekle yükümlüdür.
                        İşlem sırasında:
                      </div>
                      <ul className="text-xs text-gray-400 list-disc list-inside space-y-1 ml-2">
                        <li>Feature store'dan verileriniz silinecek/anonimleştirilecek</li>
                        <li>Gelecekteki YZ eğitimlerinde verileriniz kullanılmayacak</li>
                        <li>NovaScore confidence'ınız düşebilir (veri kapsamı azaldığı için)</li>
                      </ul>
                    </div>
                  )}
                </div>
              ) : (
                <div className="space-y-3">
                  <p className="text-xs text-gray-400">
                    Verilerini YZ eğitiminden geri çekme hakkın var. Bu işlem NovaScore confidence'ını düşürebilir.
                  </p>
                  <button
                    onClick={() => setShowRecallModal(true)}
                    className="rounded-lg border border-red-500/50 bg-red-500/10 px-4 py-2 text-sm text-red-300 hover:bg-red-500/20 transition"
                  >
                    Veri Geri Çekme Talebi Oluştur
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Recall Modal */}
          {showRecallModal && (
            <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
              <div className="aurora-card max-w-md w-full space-y-4">
                <h3 className="text-lg font-semibold text-red-300">Veri Geri Çekme Talebi</h3>
                <p className="text-sm text-gray-300">
                  Bu işlem verilerinin YZ eğitiminden geri çekilmesini talep eder. NovaScore confidence'ın düşebilir.
                </p>
                <div className="space-y-2">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      name="recallMode"
                      value="FULL_EXCLUDE"
                      checked={recallMode === 'FULL_EXCLUDE'}
                      onChange={(e) => setRecallMode(e.target.value as 'FULL_EXCLUDE' | 'ANONYMIZE')}
                      className="text-red-500"
                    />
                    <span className="text-sm text-gray-300">Tam Geri Çekme (Tüm veriler)</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      name="recallMode"
                      value="ANONYMIZE"
                      checked={recallMode === 'ANONYMIZE'}
                      onChange={(e) => setRecallMode(e.target.value as 'ANONYMIZE')}
                      className="text-red-500"
                    />
                    <span className="text-sm text-gray-300">Anonimleştirme (Veriler anonim hale getirilir)</span>
                  </label>
                </div>
                <div className="flex gap-3">
                  <button
                    onClick={() => setShowRecallModal(false)}
                    className="flex-1 rounded-lg border border-white/15 px-4 py-2 text-sm text-gray-300 hover:bg-white/5 transition"
                  >
                    İptal
                  </button>
                  <button
                    onClick={handleRecallRequest}
                    disabled={recallLoading}
                    className="flex-1 rounded-lg bg-red-500 px-4 py-2 text-sm font-semibold text-white hover:bg-red-400 transition disabled:opacity-50"
                  >
                    {recallLoading ? 'Gönderiliyor...' : 'Talep Oluştur'}
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="aurora-card">
          <ConsentFlow onComplete={handleConsentComplete} />
          {loading && (
            <div className="mt-4 text-center text-sm text-gray-400">
              Consent imzalanıyor...
            </div>
          )}
        </div>
      )}
    </div>
  )
}
