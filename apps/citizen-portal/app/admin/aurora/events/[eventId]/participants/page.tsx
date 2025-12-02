'use client'

import { useState, useEffect } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { useAuroraAPI } from '@aurora/hooks'

interface Participant {
  rank: number
  user_id: number
  telegram_user_id: number
  username: string | null
  display_name: string | null
  total_xp_earned: number
  total_ncr_earned: string
  tasks_completed: number
}

interface LeaderboardData {
  event_id: number
  event_name: string
  entries: Participant[]
  total_participants: number
  updated_at: string
}

export default function EventParticipantsPage() {
  const router = useRouter()
  const params = useParams()
  const { fetchAPI } = useAuroraAPI()
  const eventId = params?.eventId as string

  const [data, setData] = useState<LeaderboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!eventId) return

    const fetchParticipants = async () => {
      setLoading(true)
      setError(null)
      try {
        const { data: apiData, error: apiError } = await fetchAPI<LeaderboardData>(
          `/admin/events/${eventId}/participants?limit=100`
        )

        if (apiError) {
          throw new Error(apiError.detail || 'Failed to fetch participants')
        }

        if (apiData) {
          setData(apiData)
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch participants')
      } finally {
        setLoading(false)
      }
    }

    fetchParticipants()
  }, [eventId, fetchAPI])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-sm text-gray-400">Yükleniyor...</div>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-4">
        <div className="text-sm font-medium text-red-300">Hata</div>
        <div className="text-xs text-red-200 mt-1">{error || 'Katılımcılar bulunamadı'}</div>
        <button
          onClick={() => router.push(`/admin/aurora/events/${eventId}`)}
          className="mt-3 rounded-lg border border-red-500/30 px-3 py-1.5 text-xs text-red-300 hover:bg-red-500/20 transition"
        >
          ← Geri Dön
        </button>
      </div>
    )
  }

  const getRankColor = (rank: number) => {
    if (rank === 1) return 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30'
    if (rank === 2) return 'bg-gray-400/20 text-gray-300 border-gray-400/30'
    if (rank === 3) return 'bg-orange-500/20 text-orange-300 border-orange-500/30'
    return 'bg-gray-500/20 text-gray-300 border-gray-500/30'
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <button
            onClick={() => router.push(`/admin/aurora/events/${eventId}`)}
            className="text-xs text-gray-400 hover:text-gray-200 mb-2"
          >
            ← Event Detayı
          </button>
          <h2 className="text-lg font-semibold text-gray-100">{data.event_name}</h2>
          <p className="text-xs text-gray-400 mt-1">
            {data.total_participants} katılımcı
          </p>
        </div>
      </div>

      {/* Leaderboard */}
      {data.entries.length === 0 ? (
        <div className="rounded-xl border border-white/10 bg-black/60 p-8 text-center">
          <div className="text-sm text-gray-400">Henüz katılımcı yok</div>
        </div>
      ) : (
        <div className="rounded-xl border border-white/10 bg-black/60 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="border-b border-white/10">
                <tr className="text-xs text-gray-400">
                  <th className="text-left p-3">Rank</th>
                  <th className="text-left p-3">Kullanıcı</th>
                  <th className="text-right p-3">XP</th>
                  <th className="text-right p-3">NCR</th>
                  <th className="text-right p-3">Görevler</th>
                </tr>
              </thead>
              <tbody>
                {data.entries.map((entry) => (
                  <tr
                    key={entry.user_id}
                    className="border-b border-white/5 hover:bg-white/5 transition"
                  >
                    <td className="p-3">
                      <span
                        className={`inline-flex items-center justify-center w-8 h-8 rounded border text-xs font-medium ${getRankColor(
                          entry.rank
                        )}`}
                      >
                        {entry.rank}
                      </span>
                    </td>
                    <td className="p-3">
                      <div className="text-sm text-gray-100">
                        {entry.display_name || entry.username || `User ${entry.user_id}`}
                      </div>
                      {entry.telegram_user_id > 0 && (
                        <div className="text-xs text-gray-500">
                          @{entry.username || `tg_${entry.telegram_user_id}`}
                        </div>
                      )}
                    </td>
                    <td className="p-3 text-right">
                      <div className="text-sm font-medium text-green-300">
                        {entry.total_xp_earned.toLocaleString()}
                      </div>
                    </td>
                    <td className="p-3 text-right">
                      <div className="text-sm font-medium text-purple-300">
                        {parseFloat(entry.total_ncr_earned).toFixed(2)}
                      </div>
                    </td>
                    <td className="p-3 text-right">
                      <div className="text-sm text-gray-300">{entry.tasks_completed}</div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}

