'use client'

import { useState, useEffect } from 'react'
import { useAuroraAPI } from '@aurora/hooks'

interface CreatorAsset {
  id: number
  creator_id: number
  media_type: string
  content_url: string
  ai_score: number
  is_available: boolean
  tags?: string
}

export default function AgencyPage() {
  const { fetchAPI } = useAuroraAPI()
  const [assets, setAssets] = useState<CreatorAsset[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filters, setFilters] = useState({
    media_type: '',
    min_score: 90,
    only_available: true,
  })

  useEffect(() => {
    loadAssets()
  }, [filters])

  const loadAssets = async () => {
    try {
      setLoading(true)
      setError(null)
      const params = new URLSearchParams({
        limit: '50',
        min_score: filters.min_score.toString(),
        only_available: filters.only_available.toString(),
      })
      if (filters.media_type) params.append('media_type', filters.media_type)

      const { data, error: apiError } = await fetchAPI<CreatorAsset[]>(`/agency/assets/viral?${params}`)
      if (apiError) {
        const errorMsg = apiError.detail || apiError.error || 'Failed to load assets'
        if (apiError.error === 'NETWORK_ERROR') {
          throw new Error(`Bağlantı hatası: Backend'e erişilemiyor. Backend çalışıyor mu? (${errorMsg})`)
        }
        throw new Error(errorMsg)
      }
      setAssets(Array.isArray(data) ? data : [])
    } catch (err: any) {
      console.error('Agency load error:', err)
      setError(err.message || 'Failed to load viral assets')
    } finally {
      setLoading(false)
    }
  }

  const handleUseAsset = async (assetId: number) => {
    if (!confirm("Bu asset'i kampanyada kullanmak istediğinizden emin misiniz?")) {
      return
    }

    try {
      const { data, error: apiError } = await fetchAPI(`/agency/assets/${assetId}/use`, {
        method: 'PATCH',
      })
      if (apiError) {
        throw new Error(apiError.detail || 'Failed to use asset')
      }
      alert('Asset kampanyada kullanıldı!')
      loadAssets()
    } catch (err: any) {
      alert(`Hata: ${err.message}`)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-gray-400">Yükleniyor...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-xl border border-red-500/40 bg-red-500/10 p-6">
        <div className="text-red-300 font-semibold mb-2">Hata</div>
        <div className="text-red-200 text-sm">{error}</div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-semibold mb-2">Agency - Viral Assets</h1>
        <p className="text-gray-400">
          Aurora Contact için viral içerik yönetimi
        </p>
      </div>

      {/* Filters */}
      <div className="rounded-xl border border-white/10 bg-white/5 p-6 space-y-4">
        <div className="grid md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm text-gray-400 mb-2">Medya Tipi</label>
            <select
              value={filters.media_type}
              onChange={(e) => setFilters({ ...filters, media_type: e.target.value })}
              className="w-full rounded-lg border border-white/15 bg-black/60 px-3 py-2 text-sm"
            >
              <option value="">Tümü</option>
              <option value="image">Görsel</option>
              <option value="video">Video</option>
              <option value="text">Metin</option>
            </select>
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-2">Min AI Score</label>
            <input
              type="number"
              value={filters.min_score}
              onChange={(e) =>
                setFilters({ ...filters, min_score: parseInt(e.target.value) || 90 })
              }
              className="w-full rounded-lg border border-white/15 bg-black/60 px-3 py-2 text-sm"
            />
          </div>
          <div className="flex items-end">
            <label className="flex items-center gap-2 text-sm text-gray-400">
              <input
                type="checkbox"
                checked={filters.only_available}
                onChange={(e) =>
                  setFilters({ ...filters, only_available: e.target.checked })
                }
                className="rounded"
              />
              Sadece müsait olanlar
            </label>
          </div>
        </div>
      </div>

      {assets.length === 0 ? (
        <div className="rounded-xl border border-white/10 bg-white/5 p-8 text-center">
          <div className="text-gray-400 mb-2">Henüz asset yok</div>
          <div className="text-sm text-gray-500">
            Yüksek kaliteli içerikler otomatik olarak buraya eklenir
          </div>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {assets.map((asset) => (
            <div
              key={asset.id}
              className="rounded-xl border border-white/10 bg-white/5 p-6 space-y-4"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-gray-400">{asset.media_type}</span>
                  <span className="text-xs font-semibold text-purple-300">
                    ⭐ {asset.ai_score}
                  </span>
                </div>
                {asset.content_url && (
                  <div className="text-xs text-gray-400 truncate">
                    {asset.content_url}
                  </div>
                )}
              </div>

              <button
                onClick={() => handleUseAsset(asset.id)}
                disabled={!asset.is_available}
                className="w-full rounded-lg bg-purple-500 px-4 py-2 text-sm font-semibold hover:bg-purple-400 transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {asset.is_available ? 'Kampanyada Kullan' : 'Kullanılamaz'}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

