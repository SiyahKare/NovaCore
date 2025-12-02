'use client'

import { useState, useEffect } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { format } from 'date-fns'
import { useAuroraAPI } from '@aurora/hooks'

interface EventDetail {
  id: number
  code: string
  name: string
  description: string | null
  event_type: string
  status: string
  starts_at: string
  ends_at: string
  reward_multiplier_xp: number
  reward_multiplier_ncr: number
  max_participants: number | null
  min_level_required: number
  user_score: {
    xp?: number
    tasks_completed?: number
    participation_count?: number
  } | null
}

export default function EventDetailPage() {
  const router = useRouter()
  const params = useParams()
  const { fetchAPI } = useAuroraAPI()
  const eventId = params?.eventId as string

  const [event, setEvent] = useState<EventDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!eventId) return

    const fetchEvent = async () => {
      setLoading(true)
      setError(null)
      try {
        const { data, error: apiError } = await fetchAPI<EventDetail>(`/admin/events/${eventId}`)

        if (apiError) {
          throw new Error(apiError.detail || 'Failed to fetch event')
        }

        if (data) {
          setEvent(data)
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch event')
      } finally {
        setLoading(false)
      }
    }

    fetchEvent()
  }, [eventId, fetchAPI])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-sm text-gray-400">Yükleniyor...</div>
      </div>
    )
  }

  if (error || !event) {
    return (
      <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-4">
        <div className="text-sm font-medium text-red-300">Hata</div>
        <div className="text-xs text-red-200 mt-1">{error || 'Event bulunamadı'}</div>
        <button
          onClick={() => router.push('/admin/aurora/events')}
          className="mt-3 rounded-lg border border-red-500/30 px-3 py-1.5 text-xs text-red-300 hover:bg-red-500/20 transition"
        >
          ← Geri Dön
        </button>
      </div>
    )
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ACTIVE':
        return 'bg-green-500/20 text-green-300 border-green-500/30'
      case 'DRAFT':
        return 'bg-gray-500/20 text-gray-300 border-gray-500/30'
      case 'FINISHED':
        return 'bg-blue-500/20 text-blue-300 border-blue-500/30'
      case 'CANCELLED':
        return 'bg-red-500/20 text-red-300 border-red-500/30'
      default:
        return 'bg-gray-500/20 text-gray-300 border-gray-500/30'
    }
  }

  const getEventTypeColor = (type: string) => {
    switch (type) {
      case 'NASIP_FRIDAY':
        return 'bg-purple-500/20 text-purple-300'
      case 'QUEST_WAR':
        return 'bg-orange-500/20 text-orange-300'
      case 'SEASONAL':
        return 'bg-yellow-500/20 text-yellow-300'
      case 'RITUAL':
        return 'bg-pink-500/20 text-pink-300'
      default:
        return 'bg-gray-500/20 text-gray-300'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <button
            onClick={() => router.push('/admin/aurora/events')}
            className="text-xs text-gray-400 hover:text-gray-200 mb-2"
          >
            ← Event Listesi
          </button>
          <h2 className="text-lg font-semibold text-gray-100">{event.name}</h2>
          <p className="text-xs text-gray-400 mt-1">{event.code}</p>
        </div>
        <div className="flex gap-2">
          <span
            className={`rounded px-2 py-1 text-[10px] font-medium border ${getStatusColor(
              event.status
            )}`}
          >
            {event.status}
          </span>
          <span
            className={`rounded px-2 py-1 text-[10px] font-medium ${getEventTypeColor(
              event.event_type
            )}`}
          >
            {event.event_type}
          </span>
        </div>
      </div>

      {/* Event Info */}
      <div className="rounded-xl border border-white/10 bg-black/60 p-4 space-y-4">
        {event.description && (
          <div>
            <div className="text-xs text-gray-500 mb-1">Açıklama</div>
            <div className="text-sm text-gray-300">{event.description}</div>
          </div>
        )}

        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="text-xs text-gray-500 mb-1">Başlangıç</div>
            <div className="text-sm text-gray-100">
              {format(new Date(event.starts_at), 'dd MMM yyyy, HH:mm')}
            </div>
          </div>
          <div>
            <div className="text-xs text-gray-500 mb-1">Bitiş</div>
            <div className="text-sm text-gray-100">
              {format(new Date(event.ends_at), 'dd MMM yyyy, HH:mm')}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="text-xs text-gray-500 mb-1">XP Multiplier</div>
            <div className="text-sm text-green-300 font-medium">{event.reward_multiplier_xp}x</div>
          </div>
          <div>
            <div className="text-xs text-gray-500 mb-1">NCR Multiplier</div>
            <div className="text-sm text-green-300 font-medium">{event.reward_multiplier_ncr}x</div>
          </div>
        </div>

        {event.max_participants && (
          <div>
            <div className="text-xs text-gray-500 mb-1">Max Katılımcı</div>
            <div className="text-sm text-gray-100">{event.max_participants}</div>
          </div>
        )}

        <div>
          <div className="text-xs text-gray-500 mb-1">Min Level Gereksinimi</div>
          <div className="text-sm text-gray-100">{event.min_level_required}</div>
        </div>
      </div>

      {/* Stats */}
      {event.user_score && (
        <div className="rounded-xl border border-white/10 bg-black/60 p-4">
          <div className="text-xs text-gray-500 mb-3">İstatistikler</div>
          <div className="grid grid-cols-3 gap-4">
            {event.user_score.participation_count !== undefined && (
              <div>
                <div className="text-xs text-gray-400">Katılımcı</div>
                <div className="text-lg font-semibold text-purple-300">
                  {event.user_score.participation_count}
                </div>
              </div>
            )}
            {event.user_score.xp !== undefined && (
              <div>
                <div className="text-xs text-gray-400">Toplam XP</div>
                <div className="text-lg font-semibold text-green-300">
                  {event.user_score.xp.toLocaleString()}
                </div>
              </div>
            )}
            {event.user_score.tasks_completed !== undefined && (
              <div>
                <div className="text-xs text-gray-400">Tamamlanan Görev</div>
                <div className="text-lg font-semibold text-blue-300">
                  {event.user_score.tasks_completed}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-3">
        <button
          onClick={() => router.push(`/admin/aurora/events/${eventId}/participants`)}
          className="rounded-lg border border-white/15 bg-black/60 px-4 py-2 text-sm text-gray-100 hover:bg-white/5 transition"
        >
          Katılımcıları Gör
        </button>
      </div>
    </div>
  )
}

