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
            <p className={`text-sm ${citizen.telegram_id && citizen.telegram_id > 0 ? 'text-slate-300' : 'text-yellow-500'}`}>
              {citizen.telegram_id && citizen.telegram_id > 0 
                ? `${citizen.telegram_id}${telegramStatus?.is_linked ? ' ✅' : ''}`
                : 'Not connected (dummy)'}
            </p>
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

    </div>
  )
}
