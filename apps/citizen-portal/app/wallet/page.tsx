'use client'

import { ProtectedView } from '@/components/ProtectedView'
import { useCitizenState } from '@aurora/hooks'
import Link from 'next/link'

export default function WalletPage() {
  return (
    <ProtectedView>
      <WalletInner />
    </ProtectedView>
  )
}

function WalletInner() {
  const citizenState = useCitizenState()

  if (citizenState.loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="text-gray-400 mb-2">Wallet yükleniyor...</div>
          <div className="text-xs text-gray-500">Bakiye bilgileri toplanıyor...</div>
        </div>
      </div>
    )
  }

  const wallet = citizenState.wallet
  const balance = wallet ? parseFloat(wallet.balance) : 0
  const available = wallet ? parseFloat(wallet.available) : 0
  const locked = wallet ? parseFloat(wallet.locked) : 0

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold mb-2 bg-gradient-to-r from-emerald-400 via-cyan-400 to-blue-400 bg-clip-text text-transparent">
          NCR Wallet
        </h1>
        <p className="text-gray-400">SiyahKare Cumhuriyeti dijital para birimi cüzdanın</p>
      </div>

      {/* Error Banner */}
      {citizenState.error && !wallet && (
        <div className="aurora-card border-yellow-500/30 bg-yellow-500/10">
          <p className="text-yellow-300 text-sm mb-2">⚠️ Wallet bilgisi yüklenemedi</p>
          <p className="text-xs text-yellow-400 mb-3">{citizenState.error}</p>
          <button
            onClick={() => citizenState.refetch()}
            className="px-3 py-1.5 text-xs font-medium text-yellow-900 bg-yellow-300 hover:bg-yellow-200 rounded transition-colors"
          >
            Tekrar Dene
          </button>
        </div>
      )}

      {/* Balance Cards */}
      <div className="grid md:grid-cols-3 gap-6">
        {/* Total Balance */}
        <div className="aurora-card border-emerald-500/30 bg-gradient-to-br from-emerald-950/20 to-black">
          <h3 className="text-lg font-semibold text-slate-200 mb-4 flex items-center gap-2">
            <span className="text-emerald-400">💰</span>
            Toplam Bakiye
          </h3>
          <div className="space-y-2">
            <p className="text-4xl font-bold text-emerald-300">
              {balance.toFixed(2)} <span className="text-xl text-emerald-400">NCR</span>
            </p>
            <p className="text-xs text-gray-400">SiyahKare Cumhuriyeti Token</p>
          </div>
        </div>

        {/* Available Balance */}
        <div className="aurora-card border-cyan-500/30 bg-gradient-to-br from-cyan-950/20 to-black">
          <h3 className="text-lg font-semibold text-slate-200 mb-4 flex items-center gap-2">
            <span className="text-cyan-400">✅</span>
            Kullanılabilir
          </h3>
          <div className="space-y-2">
            <p className="text-4xl font-bold text-cyan-300">
              {available.toFixed(2)} <span className="text-xl text-cyan-400">NCR</span>
            </p>
            <p className="text-xs text-gray-400">Hemen harcanabilir</p>
          </div>
        </div>

        {/* Locked Balance */}
        <div className="aurora-card border-orange-500/30 bg-gradient-to-br from-orange-950/20 to-black">
          <h3 className="text-lg font-semibold text-slate-200 mb-4 flex items-center gap-2">
            <span className="text-orange-400">🔒</span>
            Kilitli
          </h3>
          <div className="space-y-2">
            <p className="text-4xl font-bold text-orange-300">
              {locked.toFixed(2)} <span className="text-xl text-orange-400">NCR</span>
            </p>
            <p className="text-xs text-gray-400">Stake veya kilitli</p>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="aurora-card border-purple-500/30 bg-gradient-to-br from-purple-950/20 to-black">
        <h3 className="text-lg font-semibold text-slate-200 mb-4 flex items-center gap-2">
          <span className="text-purple-400">⚡</span>
          Hızlı İşlemler
        </h3>
        <div className="grid md:grid-cols-2 gap-4">
          <Link
            href="/marketplace"
            className="p-4 rounded-lg bg-slate-900/50 border border-slate-800 hover:border-purple-500/50 transition-colors"
          >
            <div className="text-sm font-semibold text-slate-200 mb-1">🛒 Marketplace</div>
            <div className="text-xs text-gray-400">Dijital ürünler satın al</div>
          </Link>
          <Link
            href="/dashboard"
            className="p-4 rounded-lg bg-slate-900/50 border border-slate-800 hover:border-purple-500/50 transition-colors"
          >
            <div className="text-sm font-semibold text-slate-200 mb-1">📊 Dashboard</div>
            <div className="text-xs text-gray-400">Genel bakışa dön</div>
          </Link>
        </div>
      </div>

      {/* Info Section */}
      <div className="aurora-card border-blue-500/30 bg-gradient-to-br from-blue-950/20 to-black">
        <h3 className="text-lg font-semibold text-slate-200 mb-4 flex items-center gap-2">
          <span className="text-blue-400">ℹ️</span>
          NCR Hakkında
        </h3>
        <div className="space-y-3 text-sm text-gray-300">
          <p>
            <strong className="text-blue-300">NCR (NovaCore Republic Token)</strong> SiyahKare Cumhuriyeti'nin resmi dijital para birimidir.
          </p>
          <ul className="list-disc list-inside space-y-1 text-xs text-gray-400 ml-2">
            <li>Quest tamamlayarak NCR kazanabilirsin</li>
            <li>Marketplace'te dijital ürünler satın alabilirsin</li>
            <li>Stake ederek pasif gelir elde edebilirsin</li>
            <li>Creator olarak içerik satışından NCR kazanabilirsin</li>
          </ul>
        </div>
      </div>

      {/* Transaction History Placeholder */}
      <div className="aurora-card">
        <h3 className="text-lg font-semibold text-slate-200 mb-4 flex items-center gap-2">
          <span className="text-slate-400">📜</span>
          İşlem Geçmişi
        </h3>
        <div className="text-center py-8 text-gray-400">
          <p className="text-sm mb-2">İşlem geçmişi yakında eklenecek</p>
          <p className="text-xs text-gray-500">Tüm NCR işlemlerin burada görüntülenecek</p>
        </div>
      </div>
    </div>
  )
}

