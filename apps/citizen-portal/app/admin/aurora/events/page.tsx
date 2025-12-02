'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { format } from 'date-fns'
import { useAuroraAPI } from '@aurora/hooks'

interface Event {
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
  is_joined: boolean
  user_rank: number | null
  user_score: {
    participation_count?: number
    total_xp_distributed?: number
    total_ncr_distributed?: string
    tasks_count?: number
  } | null
}

export default function AdminEventsPage() {
  const router = useRouter()
  const { fetchAPI } = useAuroraAPI()
  const [events, setEvents] = useState<Event[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [eventTypeFilter, setEventTypeFilter] = useState<string>('')

  const fetchEvents = async () => {
    setLoading(true)
    setError(null)
    try {
      const params = new URLSearchParams()
      if (statusFilter) params.append('status', statusFilter)
      if (eventTypeFilter) params.append('event_type', eventTypeFilter)

      const url = `/admin/events${params.toString() ? '?' + params.toString() : ''}`
      const { data, error: apiError } = await fetchAPI<Event[]>(url)

      if (apiError) {
        throw new Error(apiError.detail || 'Failed to fetch events')
      }

      if (data) {
        setEvents(data)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch events')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchEvents()
  }, [statusFilter, eventTypeFilter])

  const handleViewDetails = (eventId: number) => {
    router.push(`/admin/aurora/events/${eventId}`)
  }

  const handleViewParticipants = (eventId: number) => {
    router.push(`/admin/aurora/events/${eventId}/participants`)
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

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-sm text-gray-400">Yükleniyor...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-4">
        <div className="text-sm font-medium text-red-300">Hata</div>
        <div className="text-xs text-red-200 mt-1">{error}</div>
        <button
          onClick={fetchEvents}
          className="mt-3 rounded-lg border border-red-500/30 px-3 py-1.5 text-xs text-red-300 hover:bg-red-500/20 transition"
        >
          Tekrar Dene
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-lg font-semibold text-gray-100">Event Yönetimi</h2>
        <p className="text-xs text-gray-400 mt-1">
          Telegram event'lerini görüntüle, detaylarına bak, katılımcıları kontrol et.
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="rounded-lg border border-white/15 bg-black/60 px-3 py-1.5 text-xs text-gray-100 focus:outline-none focus:border-purple-500/70"
        >
          <option value="">Tüm Durumlar</option>
          <option value="DRAFT">Draft</option>
          <option value="ACTIVE">Aktif</option>
          <option value="FINISHED">Bitti</option>
          <option value="CANCELLED">İptal</option>
        </select>

        <select
          value={eventTypeFilter}
          onChange={(e) => setEventTypeFilter(e.target.value)}
          className="rounded-lg border border-white/15 bg-black/60 px-3 py-1.5 text-xs text-gray-100 focus:outline-none focus:border-purple-500/70"
        >
          <option value="">Tüm Tipler</option>
          <option value="NASIP_FRIDAY">Nasip Friday</option>
          <option value="QUEST_WAR">Quest War</option>
          <option value="SEASONAL">Seasonal</option>
          <option value="RITUAL">Ritual</option>
          <option value="ONBOARDING">Onboarding</option>
        </select>

        <button
          onClick={fetchEvents}
          className="rounded-lg border border-white/15 bg-black/60 px-3 py-1.5 text-xs text-gray-100 hover:bg-white/5 transition"
        >
          🔄 Yenile
        </button>
      </div>

      {/* Events List */}
      {events.length === 0 ? (
        <div className="rounded-xl border border-white/10 bg-black/60 p-8 text-center">
          <div className="text-sm text-gray-400">Henüz event yok</div>
        </div>
      ) : (
        <div className="grid gap-4">
          {events.map((event) => (
            <div
              key={event.id}
              className="rounded-xl border border-white/10 bg-black/60 p-4 hover:border-white/20 transition"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 space-y-2">
                  <div className="flex items-center gap-2 flex-wrap">
                    <h3 className="text-sm font-semibold text-gray-100">{event.name}</h3>
                    <span
                      className={`rounded px-2 py-0.5 text-[10px] font-medium border ${getStatusColor(
                        event.status
                      )}`}
                    >
                      {event.status}
                    </span>
                    <span
                      className={`rounded px-2 py-0.5 text-[10px] font-medium ${getEventTypeColor(
                        event.event_type
                      )}`}
                    >
                      {event.event_type}
                    </span>
                  </div>

                  <div className="text-xs text-gray-400">{event.code}</div>

                  {event.description && (
                    <div className="text-xs text-gray-300">{event.description}</div>
                  )}

                  <div className="flex flex-wrap gap-4 text-xs text-gray-400">
                    <div>
                      <span className="text-gray-500">Başlangıç:</span>{' '}
                      {format(new Date(event.starts_at), 'dd MMM yyyy, HH:mm')}
                    </div>
                    <div>
                      <span className="text-gray-500">Bitiş:</span>{' '}
                      {format(new Date(event.ends_at), 'dd MMM yyyy, HH:mm')}
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-4 text-xs">
                    <div className="text-gray-400">
                      <span className="text-gray-500">XP Multiplier:</span>{' '}
                      <span className="text-green-300">{event.reward_multiplier_xp}x</span>
                    </div>
                    <div className="text-gray-400">
                      <span className="text-gray-500">NCR Multiplier:</span>{' '}
                      <span className="text-green-300">{event.reward_multiplier_ncr}x</span>
                    </div>
                    {event.user_score?.participation_count !== undefined && (
                      <div className="text-gray-400">
                        <span className="text-gray-500">Katılımcı:</span>{' '}
                        <span className="text-purple-300">
                          {event.user_score.participation_count}
                        </span>
                      </div>
                    )}
                  </div>
                </div>

                <div className="flex flex-col gap-2">
                  <button
                    onClick={() => handleViewDetails(event.id)}
                    className="rounded-lg border border-white/15 bg-black/60 px-3 py-1.5 text-xs text-gray-100 hover:bg-white/5 transition whitespace-nowrap"
                  >
                    Detay
                  </button>
                  <button
                    onClick={() => handleViewParticipants(event.id)}
                    className="rounded-lg border border-white/15 bg-black/60 px-3 py-1.5 text-xs text-gray-100 hover:bg-white/5 transition whitespace-nowrap"
                  >
                    Katılımcılar
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

