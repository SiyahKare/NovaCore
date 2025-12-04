'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { ProtectedView } from '@/components/ProtectedView'
import { useAuroraAPI } from '@aurora/hooks'

interface MarketplaceItem {
  id: number
  title: string
  item_type: string
  price_ncr: number
  status: string
  purchase_count: number
  total_revenue_ncr: number
}

interface CreatorSales {
  creator_id: number
  total_sales: number
  total_revenue_ncr: number
}

export default function MyItemsPage() {
  return (
    <ProtectedView>
      <MyItemsInner />
    </ProtectedView>
  )
}

function MyItemsInner() {
  const { fetchAPI } = useAuroraAPI()
  const [items, setItems] = useState<MarketplaceItem[]>([])
  const [sales, setSales] = useState<CreatorSales | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Load items
      const { data: itemsData, error: itemsError } = await fetchAPI<MarketplaceItem[]>('/marketplace/my-items?limit=20')
      if (itemsError) {
        const errorMsg = itemsError.detail || itemsError.error || 'Failed to load items'
        // Handle network errors specifically
        if (itemsError.error === 'NETWORK_ERROR') {
          throw new Error(`Bağlantı hatası: Backend'e erişilemiyor. Backend çalışıyor mu? (${errorMsg})`)
        }
        throw new Error(errorMsg)
      }
      setItems(Array.isArray(itemsData) ? itemsData : [])

      // Load sales
      const { data: salesData, error: salesError } = await fetchAPI<CreatorSales>('/marketplace/my-sales')
      if (!salesError && salesData) {
        setSales(salesData)
      }
    } catch (err: any) {
      console.error('My items load error:', err)
      setError(err.message || 'Failed to load data')
    } finally {
      setLoading(false)
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
        <h1 className="text-3xl font-semibold mb-2">Kendi Ürünlerim</h1>
        <p className="text-gray-400">
          Marketplace'te satışta olan ürünleriniz
        </p>
      </div>

      {sales && (
        <div className="grid md:grid-cols-3 gap-6">
          <div className="rounded-xl border border-white/10 bg-white/5 p-6">
            <div className="text-sm text-gray-400 mb-1">Toplam Satış</div>
            <div className="text-2xl font-bold text-purple-300">
              {sales.total_sales}
            </div>
          </div>
          <div className="rounded-xl border border-white/10 bg-white/5 p-6">
            <div className="text-sm text-gray-400 mb-1">Toplam Gelir</div>
            <div className="text-2xl font-bold text-emerald-300">
              {sales.total_revenue_ncr.toFixed(2)} NCR
            </div>
          </div>
          <div className="rounded-xl border border-white/10 bg-white/5 p-6">
            <div className="text-sm text-gray-400 mb-1">Aktif Ürün</div>
            <div className="text-2xl font-bold text-sky-300">
              {items.filter((i) => i.status === 'active').length}
            </div>
          </div>
        </div>
      )}

      {items.length === 0 ? (
        <div className="rounded-xl border border-white/10 bg-white/5 p-8 text-center">
          <div className="text-gray-400 mb-2">Henüz ürün yok</div>
          <div className="text-sm text-gray-500">
            Quest tamamlayarak ürün oluşturabilirsiniz
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {items.map((item) => (
            <div
              key={item.id}
              className="rounded-xl border border-white/10 bg-white/5 p-6 flex items-center justify-between"
            >
              <div>
                <h3 className="font-semibold text-lg mb-1">{item.title}</h3>
                <div className="flex gap-4 text-sm text-gray-400">
                  <span>Tür: {item.item_type}</span>
                  <span>Durum: {item.status}</span>
                  <span>Fiyat: {item.price_ncr.toFixed(2)} NCR</span>
                </div>
              </div>
              <div className="text-right">
                <div className="text-lg font-bold text-emerald-300">
                  {item.purchase_count} satış
                </div>
                <div className="text-sm text-gray-400">
                  {item.total_revenue_ncr.toFixed(2)} NCR gelir
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <div>
        <Link
          href="/marketplace"
          className="rounded-lg border border-white/15 px-4 py-2 text-sm hover:bg-white/5 transition"
        >
          ← Marketplace'e Dön
        </Link>
      </div>
    </div>
  )
}

