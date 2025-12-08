'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuroraAPI } from '@aurora/hooks'
import Link from 'next/link'
import {  } from 'next/navigation'

interface UserListItem {
  user_id: string
  display_name: string | null
  email: string | null
  username: string | null
  has_consent: boolean
  consent_level: string | null
  recall_state: 'NONE' | 'REQUESTED' | 'COMPLETED'
  recall_mode: string | null
  recall_requested_at: string | null
  recall_completed_at: string | null
  cp_value: number
  created_at: string
  is_admin: boolean
}

interface UserListResponse {
  users: UserListItem[]
  total: number
  page: number
  limit: number
}

export default function AuroraUsersPage() {
  const router = useRouter()
  const { fetchAPI } = useAuroraAPI()
  const [users, setUsers] = useState<UserListItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [limit] = useState(50)
  const [search, setSearch] = useState('')
  const [recallFilter, setRecallFilter] = useState<string>('')
  const [searchInput, setSearchInput] = useState('')
  const [updatingAdmin, setUpdatingAdmin] = useState<string | null>(null)
  const [processingRecall, setProcessingRecall] = useState<string | null>(null)

  const loadUsers = async () => {
    setLoading(true)
    setError(null)
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        limit: limit.toString(),
      })
      if (search) {
        params.append('search', search)
      }
      if (recallFilter) {
        params.append('recall_filter', recallFilter)
      }

      const { data, error: apiError } = await fetchAPI<UserListResponse>(
        `/admin/aurora/users?${params.toString()}`
      )

      if (apiError || !data) {
        setError(apiError ? (apiError.detail || apiError.error || 'Failed to load users') : 'Failed to load users')
        return
      }

      setUsers(data.users)
      setTotal(data.total)
    } catch (err: any) {
      setError(err.message || 'Failed to load users')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadUsers()
  }, [page, search, recallFilter])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setSearch(searchInput)
    setPage(1)
  }

  const getRecallBadgeColor = (state: string) => {
    switch (state) {
      case 'REQUESTED':
        return 'bg-yellow-500/20 text-yellow-300 border-yellow-500/50'
      case 'COMPLETED':
        return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/50'
      default:
        return 'bg-gray-500/20 text-gray-300 border-gray-500/50'
    }
  }

  const getConsentBadgeColor = (hasConsent: boolean) => {
    return hasConsent
      ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/50'
      : 'bg-gray-500/20 text-gray-300 border-gray-500/50'
  }

  const handleToggleAdmin = async (user: UserListItem) => {
    if (updatingAdmin === user.user_id) return
    
    setUpdatingAdmin(user.user_id)
    try {
      const { error: apiError } = await fetchAPI(
        `/admin/aurora/users/${user.user_id}/admin`,
        {
          method: 'PATCH',
          body: JSON.stringify({ is_admin: !user.is_admin }),
        }
      )

      if (apiError) {
        setError(apiError.detail || apiError.error || 'Failed to update admin status')
        return
      }

      // Reload users
      await loadUsers()
    } catch (err: any) {
      setError(err.message || 'Failed to update admin status')
    } finally {
      setUpdatingAdmin(null)
    }
  }

  const handleCancelRecall = async (userId: string) => {
    if (processingRecall === userId) return
    
    if (!confirm('Recall talebini iptal etmek istediğinizden emin misiniz? Kullanıcının verileri silinmeyecek.')) {
      return
    }
    
    setProcessingRecall(userId)
    try {
      const { error: apiError } = await fetchAPI(
        `/consent/recall/${userId}/cancel`,
        {
          method: 'POST',
        }
      )

      if (apiError) {
        setError(apiError.detail || apiError.error || 'Failed to update admin status')
        return
      }

      // Reload users
      await loadUsers()
    } catch (err: any) {
      setError(err.message || 'Failed to cancel recall')
    } finally {
      setProcessingRecall(null)
    }
  }

  const handleCompleteRecall = async (userId: string) => {
    if (processingRecall === userId) return
    
    if (!confirm('Recall talebini manuel olarak tamamlamak istediğinizden emin misiniz? Bu işlemden önce:\n\n1. Feature store\'dan kullanıcı verilerini silmelisiniz\n2. Training log\'larını işaretlemelisiniz\n\nBu işlemleri yaptınız mı?')) {
      return
    }
    
    setProcessingRecall(userId)
    try {
      const { error: apiError } = await fetchAPI(
        `/consent/recall/${userId}/complete`,
        {
          method: 'POST',
        }
      )

      if (apiError) {
        setError(apiError.detail || apiError.error || 'Failed to update admin status')
        return
      }

      // Reload users
      await loadUsers()
    } catch (err: any) {
      setError(err.message || 'Failed to complete recall')
    } finally {
      setProcessingRecall(null)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-gray-100">User Management</h2>
        <p className="text-xs text-gray-400 mt-1">
          Tüm kullanıcıları görüntüle, consent durumlarını kontrol et ve recall taleplerini yönet.
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-col md:flex-row gap-3">
        <form onSubmit={handleSearch} className="flex-1 flex gap-2">
          <input
            type="text"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="User ID, email, veya isim ara..."
            className="flex-1 rounded-xl border border-white/15 bg-black/60 px-3 py-2 text-sm text-gray-100 placeholder:text-gray-500 focus:outline-none focus:border-purple-500/70 transition"
          />
          <button
            type="submit"
            className="rounded-xl bg-purple-500 px-4 py-2 text-sm font-semibold text-white hover:bg-purple-400 transition"
          >
            Ara
          </button>
        </form>

        <select
          value={recallFilter}
          onChange={(e) => {
            setRecallFilter(e.target.value)
            setPage(1)
          }}
          className="rounded-xl border border-white/15 bg-black/60 px-3 py-2 text-sm text-gray-100 focus:outline-none focus:border-purple-500/70 transition"
        >
          <option value="">Tüm Recall Durumları</option>
          <option value="NONE">Recall Yok</option>
          <option value="REQUESTED">Recall Talebi Var</option>
          <option value="COMPLETED">Recall Tamamlandı</option>
        </select>
      </div>

      {/* Error */}
      {error && (
        <div className="rounded-xl border border-red-500/50 bg-red-500/10 p-3 text-sm text-red-300">
          {error}
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="text-center py-8 text-gray-400">Yükleniyor...</div>
      )}

      {/* Users Table */}
      {!loading && !error && (
        <>
          <div className="rounded-2xl border border-white/10 bg-black/60 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead className="bg-white/5 border-b border-white/10">
                  <tr>
                    <th className="px-4 py-3 text-left text-gray-300 font-semibold">User ID</th>
                    <th className="px-4 py-3 text-left text-gray-300 font-semibold">Display Name</th>
                    <th className="px-4 py-3 text-left text-gray-300 font-semibold">Email</th>
                    <th className="px-4 py-3 text-left text-gray-300 font-semibold">Consent</th>
                    <th className="px-4 py-3 text-left text-gray-300 font-semibold">Recall</th>
                    <th className="px-4 py-3 text-left text-gray-300 font-semibold">CP</th>
                    <th className="px-4 py-3 text-left text-gray-300 font-semibold">Admin</th>
                    <th className="px-4 py-3 text-left text-gray-300 font-semibold">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {users.length === 0 ? (
                    <tr>
                      <td colSpan={8} className="px-4 py-8 text-center text-gray-400">
                        Kullanıcı bulunamadı
                      </td>
                    </tr>
                  ) : (
                    users.map((user) => (
                      <tr key={user.user_id} className="hover:bg-white/5 transition">
                        <td className="px-4 py-3 text-gray-200 font-mono text-[10px]">
                          {user.user_id}
                        </td>
                        <td className="px-4 py-3 text-gray-200">
                          {user.display_name || '-'}
                        </td>
                        <td className="px-4 py-3 text-gray-400">
                          {user.email || '-'}
                        </td>
                        <td className="px-4 py-3">
                          <span
                            className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] border ${getConsentBadgeColor(
                              user.has_consent
                            )}`}
                          >
                            {user.has_consent ? '✓ Consent' : 'No Consent'}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          {user.recall_state !== 'NONE' && (
                            <div className="space-y-1">
                              <span
                                className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] border ${getRecallBadgeColor(
                                  user.recall_state
                                )}`}
                              >
                                {user.recall_state}
                              </span>
                              {user.recall_mode && (
                                <div className="text-[10px] text-gray-400">
                                  {user.recall_mode}
                                </div>
                              )}
                              {user.recall_requested_at && (
                                <div className="text-[10px] text-gray-500">
                                  {new Date(user.recall_requested_at).toLocaleDateString('tr-TR')}
                                </div>
                              )}
                              {user.recall_state === 'REQUESTED' && (
                                <div className="flex gap-1 mt-1">
                                  <button
                                    onClick={() => handleCancelRecall(user.user_id)}
                                    disabled={processingRecall === user.user_id}
                                    className="text-[9px] px-1.5 py-0.5 rounded bg-red-500/20 text-red-300 border border-red-500/50 hover:bg-red-500/30 transition disabled:opacity-50 disabled:cursor-not-allowed"
                                  >
                                    {processingRecall === user.user_id ? '...' : 'İptal'}
                                  </button>
                                  <button
                                    onClick={() => handleCompleteRecall(user.user_id)}
                                    disabled={processingRecall === user.user_id}
                                    className="text-[9px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/50 hover:bg-emerald-500/30 transition disabled:opacity-50 disabled:cursor-not-allowed"
                                  >
                                    {processingRecall === user.user_id ? '...' : 'Tamamla'}
                                  </button>
                                </div>
                              )}
                            </div>
                          )}
                          {user.recall_state === 'NONE' && (
                            <span className="text-gray-500 text-[10px]">-</span>
                          )}
                        </td>
                        <td className="px-4 py-3">
                          <span className="text-gray-200">{user.cp_value}</span>
                        </td>
                        <td className="px-4 py-3">
                          <button
                            onClick={() => handleToggleAdmin(user)}
                            disabled={updatingAdmin === user.user_id}
                            className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] border transition ${
                              user.is_admin
                                ? 'bg-purple-500/20 text-purple-300 border-purple-500/50 hover:bg-purple-500/30'
                                : 'bg-gray-500/20 text-gray-300 border-gray-500/50 hover:bg-gray-500/30'
                            } disabled:opacity-50 disabled:cursor-not-allowed`}
                          >
                            {updatingAdmin === user.user_id ? '...' : user.is_admin ? 'Admin' : 'User'}
                          </button>
                        </td>
                        <td className="px-4 py-3">
                          <Link
                            href={`/admin/aurora/case/${user.user_id}`}
                            className="text-purple-300 hover:text-purple-200 text-[10px] transition"
                          >
                            Case →
                          </Link>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Pagination */}
          {total > limit && (
            <div className="flex items-center justify-between text-xs text-gray-400">
              <div>
                Toplam {total} kullanıcı, Sayfa {page} / {Math.ceil(total / limit)}
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="px-3 py-1.5 rounded-lg border border-white/15 bg-black/60 hover:bg-white/5 disabled:opacity-50 disabled:cursor-not-allowed transition"
                >
                  ← Önceki
                </button>
                <button
                  onClick={() => setPage((p) => Math.min(Math.ceil(total / limit), p + 1))}
                  disabled={page >= Math.ceil(total / limit)}
                  className="px-3 py-1.5 rounded-lg border border-white/15 bg-black/60 hover:bg-white/5 disabled:opacity-50 disabled:cursor-not-allowed transition"
                >
                  Sonraki →
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}

