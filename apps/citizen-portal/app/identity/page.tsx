'use client'

import { useState, useEffect } from 'react'
import { ProtectedView } from '@/components/ProtectedView'
import { useCurrentCitizen, useAuroraAPI } from '@aurora/hooks'

interface TelegramStatus {
  is_linked: boolean
  telegram_user_id: number | null
  telegram_username: string | null
  telegram_display_name: string | null
}

export default function IdentityPage() {
  // Identity page should work even without auth (show basic info)
  return <IdentityInner />
}

function IdentityInner() {
  const { citizen, loading, refetch } = useCurrentCitizen()
  const { fetchAPI } = useAuroraAPI()
  const [telegramStatus, setTelegramStatus] = useState<TelegramStatus | null>(null)
  const [linking, setLinking] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // Only load telegram status if user is authenticated
    if (!citizen) return
    
    const loadTelegramStatus = async () => {
      try {
        const { data, error: apiError } = await fetchAPI<TelegramStatus>('/identity/telegram/status')
        if (!apiError && data) {
          setTelegramStatus(data)
        }
      } catch (err) {
        // Silently fail - telegram status is optional
        console.log('Telegram status not available')
      }
    }
    loadTelegramStatus()
  }, [citizen, fetchAPI])

  const handleConnectTelegram = async () => {
    setLinking(true)
    setError(null)

    try {
      // Check if Telegram WebApp is available
      if (typeof window !== 'undefined' && (window as any).Telegram?.WebApp) {
        const tg = (window as any).Telegram.WebApp
        
        // Get Telegram user data
        const tgUser = tg.initDataUnsafe?.user
        if (!tgUser) {
          throw new Error('Telegram user data not available. Please open this page from Telegram.')
        }

        // Link Telegram account
        const { data, error: apiError } = await fetchAPI<{ id: number; telegram_id: number }>(
          `/identity/telegram/link?telegram_user_id=${tgUser.id}&telegram_username=${tgUser.username || ''}&telegram_first_name=${tgUser.first_name || ''}&telegram_last_name=${tgUser.last_name || ''}`
        )

        if (apiError) {
          throw new Error(apiError.detail || 'Failed to link Telegram account')
        }

        if (data) {
          // Refresh citizen data
          await refetch()
          // Reload telegram status
          const { data: statusData } = await fetchAPI<TelegramStatus>('/identity/telegram/status')
          if (statusData) {
            setTelegramStatus(statusData)
          }
        }
      } else {
        // Fallback: Open Telegram bot
        const botUsername = process.env.NEXT_PUBLIC_TELEGRAM_BOT_USERNAME || 'nasipquest_bot'
        const botUrl = `https://t.me/${botUsername}?start=link_${citizen?.id || 'web'}`
        window.open(botUrl, '_blank')
        
        setError('Telegram WebApp bulunamadı. Telegram bot\'u açtık, oradan bağlantı kurabilirsin.')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to connect Telegram')
    } finally {
      setLinking(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-gray-400">Loading identity...</div>
      </div>
    )
  }

  if (!citizen) {
    return (
      <div className="space-y-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">Your Identity</h1>
          <p className="text-gray-400">Your digital citizenship profile</p>
        </div>
        <div className="aurora-card">
          <p className="text-gray-400">Please log in to view your identity information.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold mb-2">Your Identity</h1>
        <p className="text-gray-400">Your digital citizenship profile</p>
      </div>

      <div className="aurora-card">
        <h3 className="text-lg font-semibold text-slate-200 mb-4">Citizen Information</h3>
        <div className="space-y-3">
          <div>
            <p className="text-sm text-slate-400 mb-1">Citizen ID</p>
            <p className="text-lg font-mono text-aurora-purple">{citizen.id}</p>
          </div>
          <div>
            <p className="text-sm text-slate-400 mb-1">Display Name</p>
            <p className="text-lg text-slate-200">{citizen.display_name || 'Not set'}</p>
          </div>
          <div>
            <p className="text-sm text-slate-400 mb-1">Username</p>
            <p className="text-lg text-slate-200">@{citizen.username || 'not-set'}</p>
          </div>
          <div>
            <p className="text-sm text-slate-400 mb-1">Telegram ID</p>
            <div className="flex items-center gap-3">
              <p className={`text-sm ${citizen.telegram_id && citizen.telegram_id > 0 ? 'text-slate-300' : 'text-yellow-500'}`}>
                {citizen.telegram_id && citizen.telegram_id > 0 
                  ? `${citizen.telegram_id}${telegramStatus?.is_linked ? ' ✅' : ''}`
                  : 'Not connected (dummy)'}
              </p>
              {(!citizen.telegram_id || citizen.telegram_id <= 0 || !telegramStatus?.is_linked) && (
                <button
                  onClick={handleConnectTelegram}
                  disabled={linking}
                  className="rounded-lg border border-purple-500/50 bg-purple-500/20 px-3 py-1.5 text-xs text-purple-200 hover:bg-purple-500/30 transition disabled:opacity-50"
                >
                  {linking ? 'Connecting...' : 'Connect Telegram'}
                </button>
              )}
            </div>
            {telegramStatus?.is_linked && telegramStatus.telegram_username && (
              <p className="text-xs text-slate-400 mt-1">
                @{telegramStatus.telegram_username}
              </p>
            )}
          </div>
          <div>
            <p className="text-sm text-slate-400 mb-1">Member Since</p>
            <p className="text-sm text-slate-300">
              {new Date(citizen.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>
      </div>

      {error && (
        <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-4">
          <div className="text-sm font-medium text-red-300">Hata</div>
          <div className="text-xs text-red-200 mt-1">{error}</div>
        </div>
      )}

      {!telegramStatus?.is_linked && (
        <div className="rounded-xl border border-yellow-500/30 bg-yellow-500/10 p-4">
          <div className="text-sm font-medium text-yellow-300 mb-2">Telegram Hesabını Bağla</div>
          <div className="text-xs text-yellow-200 mb-3">
            Telegram hesabını bağlayarak bot üzerinden görevleri tamamlayabilir, event'lere katılabilir ve daha fazla özellik kullanabilirsin.
          </div>
          <div className="text-xs text-gray-400 space-y-1">
            <p>• Telegram MiniApp'ten açıldıysan "Connect Telegram" butonuna tıkla</p>
            <p>• Web'den açıldıysan Telegram bot'u açılacak, oradan bağlantı kurabilirsin</p>
          </div>
        </div>
      )}
    </div>
  )
}
