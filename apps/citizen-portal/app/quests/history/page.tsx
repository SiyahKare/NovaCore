'use client'

import { useState, useEffect } from 'react'
import { ProtectedView } from '@/components/ProtectedView'
import { useAuroraAPI } from '@aurora/hooks'
import Link from 'next/link'

interface QuestHistoryItem {
  id: number
  quest_uuid: string
  quest_type: string
  key: string
  title: string
  description: string
  base_reward_ncr: number
  base_reward_xp: number
  final_reward_ncr: number | null
  final_reward_xp: number | null
  final_score: number | null
  status: string
  assigned_at: string
  submitted_at: string | null
  resolved_at: string | null
  marketplace_item_id: number | null
}

interface QuestHistoryResponse {
  items: QuestHistoryItem[]
  total: number
  page: number
  per_page: number
}

export default function QuestHistoryPage() {
  return (
    <ProtectedView>
      <QuestHistoryInner />
    </ProtectedView>
  )
}

function QuestHistoryInner() {
  const { fetchAPI } = useAuroraAPI()
  const [history, setHistory] = useState<QuestHistoryResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [statusFilter, setStatusFilter] = useState<string>('')

  const perPage = 20

  const loadHistory = async () => {
    try {
      setLoading(true)
      setError(null)

      const params = new URLSearchParams({
        page: page.toString(),
        per_page: perPage.toString(),
      })
      if (statusFilter) {
        params.append('status_filter', statusFilter)
      }

      const { data, error: apiError } = await fetchAPI<QuestHistoryResponse>(
        `/quests/me/history?${params}`
      )

      if (apiError) {
        throw new Error(apiError.detail || 'Failed to load quest history')
      }

      setHistory(data || { items: [], total: 0, page: 1, per_page: perPage })
    } catch (err: any) {
      setError(err.message || 'Failed to load quest history')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadHistory()
  }, [page, statusFilter])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'APPROVED':
        return 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30'
      case 'REJECTED':
        return 'text-red-400 bg-red-500/20 border-red-500/30'
      case 'UNDER_REVIEW':
        return 'text-yellow-400 bg-yellow-500/20 border-yellow-500/30'
      case 'EXPIRED':
        return 'text-gray-400 bg-gray-500/20 border-gray-500/30'
      default:
        return 'text-gray-400 bg-gray-500/20 border-gray-500/30'
    }
  }

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'APPROVED':
        return 'Onaylandı'
      case 'REJECTED':
        return 'Reddedildi'
      case 'UNDER_REVIEW':
        return 'İncelemede'
      case 'EXPIRED':
        return 'Süresi Doldu'
      default:
        return status
    }
  }

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return '—'
    return new Date(dateStr).toLocaleDateString('tr-TR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  if (loading && !history) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="text-gray-400 mb-2">Quest geçmişi yükleniyor...</div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">Quest Geçmişi</h1>
          <p className="text-gray-400">Tamamladığın görevlerin detaylı kaydı</p>
        </div>
        <div className="aurora-card border-red-500/30 bg-red-500/10">
          <p className="text-red-300 text-sm mb-2">⚠️ Hata</p>
          <p className="text-xs text-red-400 mb-3">{error}</p>
          <button
            onClick={loadHistory}
            className="px-3 py-1.5 text-xs font-medium text-red-900 bg-red-300 hover:bg-red-200 rounded transition-colors"
          >
            Tekrar Dene
          </button>
        </div>
      </div>
    )
  }

  const totalPages = history ? Math.ceil(history.total / perPage) : 1

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold mb-2 bg-gradient-to-r from-purple-400 via-pink-400 to-cyan-400 bg-clip-text text-transparent">
          Quest Geçmişi
        </h1>
        <p className="text-gray-400">Tamamladığın görevlerin detaylı kaydı</p>
      </div>

      {/* Filters */}
      <div className="aurora-card border-purple-500/30 bg-gradient-to-br from-purple-950/20 to-black">
        <div className="flex flex-col md:flex-row gap-4 items-start md:items-center justify-between">
          <div className="flex items-center gap-3">
            <label className="text-sm text-gray-400">Durum Filtresi:</label>
            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value)
                setPage(1)
              }}
              className="rounded-lg border border-white/15 bg-black/60 px-3 py-2 text-sm text-gray-200"
            >
              <option value="">Tümü</option>
              <option value="APPROVED">Onaylandı</option>
              <option value="REJECTED">Reddedildi</option>
              <option value="UNDER_REVIEW">İncelemede</option>
              <option value="EXPIRED">Süresi Doldu</option>
            </select>
          </div>
          {history && (
            <div className="text-sm text-gray-400">
              Toplam: <span className="text-gray-200 font-semibold">{history.total}</span> quest
            </div>
          )}
        </div>
      </div>

      {/* Quest List */}
      {history && history.items.length === 0 ? (
        <div className="aurora-card">
          <div className="text-center py-12">
            <p className="text-gray-400 mb-2">Henüz tamamlanmış quest yok</p>
            <p className="text-xs text-gray-500 mb-4">
              Quest'leri tamamladıkça burada görünecek
            </p>
            <Link
              href="/dashboard"
              className="inline-block px-4 py-2 text-sm font-medium text-purple-300 hover:text-purple-200 transition"
            >
              Dashboard'a Dön
            </Link>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {history?.items.map((quest) => (
            <div
              key={quest.id}
              className="aurora-card border-white/10 bg-gradient-to-br from-slate-900/50 to-black"
            >
              <div className="flex flex-col md:flex-row md:items-start gap-4">
                {/* Left: Quest Info */}
                <div className="flex-1 space-y-3">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-100 mb-1">
                        {quest.title}
                      </h3>
                      {quest.description && (
                        <p className="text-sm text-gray-400 line-clamp-2">
                          {quest.description}
                        </p>
                      )}
                      <div className="flex items-center gap-2 mt-2">
                        <span
                          className={`text-xs px-2 py-1 rounded border ${getStatusColor(
                            quest.status
                          )}`}
                        >
                          {getStatusLabel(quest.status)}
                        </span>
                        <span className="text-xs text-gray-500">
                          {quest.quest_type}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Rewards */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-2 border-t border-white/5">
                    <div>
                      <p className="text-xs text-gray-400 mb-1">Base Ödül</p>
                      <p className="text-sm font-semibold text-gray-200">
                        {quest.base_reward_xp} XP
                      </p>
                      <p className="text-xs text-gray-400">
                        {quest.base_reward_ncr.toFixed(2)} NCR
                      </p>
                    </div>
                    {quest.final_reward_xp !== null && quest.final_reward_ncr !== null ? (
                      <>
                        <div>
                          <p className="text-xs text-gray-400 mb-1">Final Ödül</p>
                          <p className="text-sm font-semibold text-emerald-300">
                            {quest.final_reward_xp} XP
                          </p>
                          <p className="text-xs text-emerald-400">
                            {quest.final_reward_ncr.toFixed(2)} NCR
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-400 mb-1">AI Skoru</p>
                          <p className="text-sm font-semibold text-purple-300">
                            {quest.final_score !== null
                              ? quest.final_score.toFixed(1)
                              : '—'}
                          </p>
                        </div>
                      </>
                    ) : (
                      <div className="col-span-2">
                        <p className="text-xs text-gray-500">Henüz ödül verilmedi</p>
                      </div>
                    )}
                    {quest.marketplace_item_id && (
                      <div>
                        <p className="text-xs text-gray-400 mb-1">Marketplace</p>
                        <Link
                          href={`/marketplace/my-items`}
                          className="text-xs text-cyan-400 hover:text-cyan-300 transition"
                        >
                          Ürün #{quest.marketplace_item_id}
                        </Link>
                      </div>
                    )}
                  </div>

                  {/* Dates */}
                  <div className="flex flex-wrap gap-4 text-xs text-gray-500 pt-2 border-t border-white/5">
                    <div>
                      <span className="text-gray-400">Atandı:</span>{' '}
                      {formatDate(quest.assigned_at)}
                    </div>
                    {quest.submitted_at && (
                      <div>
                        <span className="text-gray-400">Gönderildi:</span>{' '}
                        {formatDate(quest.submitted_at)}
                      </div>
                    )}
                    {quest.resolved_at && (
                      <div>
                        <span className="text-gray-400">Tamamlandı:</span>{' '}
                        {formatDate(quest.resolved_at)}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {history && totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-3 py-1.5 text-sm rounded-lg border border-white/15 bg-black/60 text-gray-300 hover:bg-white/5 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Önceki
          </button>
          <span className="text-sm text-gray-400">
            Sayfa {page} / {totalPages}
          </span>
          <button
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page >= totalPages}
            className="px-3 py-1.5 text-sm rounded-lg border border-white/15 bg-black/60 text-gray-300 hover:bg-white/5 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Sonraki
          </button>
        </div>
      )}
    </div>
  )
}

