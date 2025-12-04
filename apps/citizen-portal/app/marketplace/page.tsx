'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useAuroraAPI } from '@aurora/hooks'

interface MarketplaceItem {
  id: number
  title: string
  description: string
  item_type: string
  price_ncr: number
  ai_score: number
  status: string
  purchase_count: number
  preview_text?: string
}

export default function MarketplacePage() {
  const { fetchAPI } = useAuroraAPI()
  const [items, setItems] = useState<MarketplaceItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadItems()
  }, [])

  const loadItems = async () => {
    try {
      setLoading(true)
      setError(null)
      const { data, error: apiError } = await fetchAPI<MarketplaceItem[]>('/marketplace/items?status=active&limit=20')
      if (apiError) {
        throw new Error(apiError.detail || 'Failed to load items')
      }
      setItems(Array.isArray(data) ? data : [])
    } catch (err: any) {
      console.error('Marketplace load error:', err)
      setError(err.message || 'Failed to load marketplace items')
    } finally {
      setLoading(false)
    }
  }

  const handlePurchase = async (itemId: number) => {
    if (!confirm('Satın almak istediğinizden emin misiniz?')) return

    try {
      const { data, error: apiError } = await fetchAPI(`/marketplace/items/${itemId}/purchase`, {
        method: 'POST',
      })
      if (apiError) {
        throw new Error(apiError.detail || 'Purchase failed')
      }
      alert('Satın alma başarılı!')
      loadItems()
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
        <h1 className="text-3xl font-semibold mb-2">Marketplace</h1>
        <p className="text-gray-400">
          Vatandaşların ürettiği içerikleri satın alın
        </p>
      </div>

      {items.length === 0 ? (
        <div className="rounded-xl border border-white/10 bg-white/5 p-8 text-center">
          <div className="text-gray-400 mb-2">Henüz ürün yok</div>
          <div className="text-sm text-gray-500">
            Quest tamamlayarak ürün oluşturabilirsiniz
          </div>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {items.map((item) => (
            <div
              key={item.id}
              className="rounded-xl border border-white/10 bg-white/5 p-6 space-y-4 hover:bg-white/10 transition"
            >
              <div>
                <h3 className="font-semibold text-lg mb-2">{item.title}</h3>
                <p className="text-sm text-gray-400 line-clamp-2">
                  {item.preview_text || item.description}
                </p>
              </div>

              <div className="flex items-center justify-between text-xs text-gray-400">
                <span>Tür: {item.item_type}</span>
                <span>⭐ {item.ai_score}</span>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <div className="text-2xl font-bold text-purple-300">
                    {item.price_ncr.toFixed(2)} NCR
                  </div>
                  <div className="text-xs text-gray-400">
                    {item.purchase_count} satış
                  </div>
                </div>
                <button
                  onClick={() => handlePurchase(item.id)}
                  className="rounded-lg bg-purple-500 px-4 py-2 text-sm font-semibold hover:bg-purple-400 transition"
                >
                  Satın Al
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="flex gap-4">
        <Link
          href="/marketplace/my-items"
          className="rounded-lg border border-white/15 px-4 py-2 text-sm hover:bg-white/5 transition"
        >
          Kendi Ürünlerim
        </Link>
      </div>
    </div>
  )
}

