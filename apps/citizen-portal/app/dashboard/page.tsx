'use client'

import { useState } from 'react'
import { ProtectedView } from '@/components/ProtectedView'
import { useCitizenState, useRegimeTheme, usePolicy } from '@aurora/hooks'
import {
  NovaScoreCard,
  RegimeBadge,
  PolicyBreakdown,
  CPTrendGraph,
  RegimeBanner,
  AuroraStateHealth,
  CitizenTimeline,
  TrustFactors,
} from '@aurora/ui'
import type { NovaScorePayload, CpState, PolicyParams } from '@aurora/ui'
import Link from 'next/link'

export default function DashboardPage() {
  return (
    <ProtectedView>
      <DashboardInner />
    </ProtectedView>
  )
}

function DashboardInner() {
  const citizenState = useCitizenState()
  const regimeTheme = useRegimeTheme()
  const { policy } = usePolicy()

  const headlineByRegime: Record<string, string> = {
    NORMAL: 'SiyahKare vatandaşlık statün temiz.',
    SOFT_FLAG: 'Davranışlarında küçük sapmalar var. Aurora Justice seni izliyor.',
    PROBATION: 'Probasyon altındasın. Aurora Justice Engine davranışlarını yakından takip ediyor.',
    RESTRICTED: 'Erişimlerin kısıtlandı. Bazı aksiyonlar artık kapalı veya sınırlı.',
    LOCKDOWN: 'Aurora Justice Engine seni kilitledi. Sadece itiraz edebilir, verilerini görebilirsin.',
  }

  if (citizenState.loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="text-gray-400 mb-2">Dashboard yükleniyor...</div>
          <div className="text-xs text-gray-500">Veriler toplanıyor...</div>
        </div>
      </div>
    )
  }

  // Show partial data even if there are errors
  const hasCriticalData = citizenState.identity || citizenState.cpState

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold mb-2 bg-gradient-to-r from-purple-400 via-pink-400 to-cyan-400 bg-clip-text text-transparent">
          NovaCore Profilin
        </h1>
        <p className="text-gray-400">Dijital vatandaşlığının kapsamlı özeti</p>
      </div>

      {/* Error Banner - Only show if no critical data loaded */}
      {citizenState.error && !hasCriticalData && (
        <div className="aurora-card border-yellow-500/30 bg-yellow-500/10">
          <p className="text-yellow-300 text-sm mb-2">⚠️ Veriler yüklenemedi</p>
          <p className="text-xs text-yellow-400 mb-3">{citizenState.error}</p>
          <div className="flex items-center gap-3">
            <button
              onClick={() => citizenState.refetch()}
              className="px-3 py-1.5 text-xs font-medium text-yellow-900 bg-yellow-300 hover:bg-yellow-200 rounded transition-colors"
            >
              Tekrar Dene
            </button>
            <Link
              href="/onboarding"
              className="px-3 py-1.5 text-xs font-medium text-yellow-300 border border-yellow-500/50 hover:border-yellow-500 rounded transition-colors"
            >
              Onboarding'e Git
            </Link>
          </div>
          <p className="text-[10px] text-yellow-500/70 mt-3">
            Not: Eğer yeni bir kullanıcıysan, önce onboarding'i tamamlaman gerekebilir.
          </p>
        </div>
      )}

      {/* Warning Banner - Show if partial data loaded */}
      {citizenState.error && hasCriticalData && (
        <div className="aurora-card border-blue-500/30 bg-blue-500/10">
          <p className="text-blue-300 text-sm mb-2">ℹ️ Bazı veriler yüklenemedi</p>
          <p className="text-xs text-blue-400 mb-2">{citizenState.error}</p>
          <button
            onClick={() => citizenState.refetch()}
            className="text-xs text-blue-300 hover:text-blue-200 underline"
          >
            Tekrar Dene
          </button>
        </div>
      )}

      {/* Regime Banner (if not NORMAL) */}
      {citizenState.cpState && citizenState.cpState.regime !== 'NORMAL' && (
        <RegimeBanner
          regime={citizenState.cpState.regime}
          cpValue={citizenState.cpState.cp_value}
          message={
            citizenState.cpState.regime === 'LOCKDOWN'
              ? 'Hesabın kilitlendi. Tüm aksiyonlar engellendi. İtiraz gerekli.'
              : undefined
          }
        />
      )}

      {/* Top Row: State Health + Citizen Health + Quick Actions */}
      <div className="grid md:grid-cols-3 gap-4">
        {/* Aurora Justice Health */}
        <AuroraStateHealth />

        {/* Citizen Health Summary */}
        <div className={`aurora-card border ${regimeTheme.borderClass} bg-gradient-to-br ${regimeTheme.bgGradient}`}>
          <h3 className="text-lg font-semibold text-slate-200 mb-4 flex items-center gap-2">
            <span className={regimeTheme.accentClass}>⚡</span>
            Citizen Health
          </h3>
          <div className="space-y-3">
            {citizenState.novaScore && (
              <div>
                <p className="text-xs text-gray-400 mb-1">NovaScore</p>
                <p className="text-2xl font-bold text-purple-300">
                  {(() => {
                    const rawScore = (citizenState.novaScore as any).nova_score ?? (citizenState.novaScore as any).value ?? 0
                    const normalizedScore = rawScore > 100 ? rawScore / 10 : rawScore
                    return normalizedScore.toFixed(0)
                  })()}
                </p>
              </div>
            )}
            {citizenState.cpState && (
              <div>
                <p className="text-xs text-gray-400 mb-1">CP Value</p>
                <p className="text-2xl font-bold text-aurora-purple">{citizenState.cpState.cp_value}</p>
              </div>
            )}
            {citizenState.cpState && (
              <div>
                <RegimeBadge regime={citizenState.cpState.regime} size="sm" showLabel={true} />
              </div>
            )}
            <p className={`text-xs ${regimeTheme.accentClass} mt-2`}>
              {headlineByRegime[regimeTheme.regime] ?? ''}
            </p>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="aurora-card border-cyan-500/30 bg-gradient-to-br from-cyan-950/20 to-black">
          <h3 className="text-lg font-semibold text-slate-200 mb-4 flex items-center gap-2">
            <span className="text-cyan-400">⚡</span>
            My Actions
          </h3>
          <div className="space-y-2">
            <Link
              href="/wallet"
              className="block p-3 rounded-lg bg-slate-900/50 border border-slate-800 hover:border-emerald-500/50 transition-colors"
            >
              <div className="text-sm font-semibold text-slate-200">💰 Wallet</div>
              <div className="text-xs text-gray-400">NCR bakiyeni görüntüle</div>
            </Link>
            <Link
              href="/marketplace"
              className="block p-3 rounded-lg bg-slate-900/50 border border-slate-800 hover:border-purple-500/50 transition-colors"
            >
              <div className="text-sm font-semibold text-slate-200">🛒 Marketplace</div>
              <div className="text-xs text-gray-400">Dijital ürünler satın al</div>
            </Link>
            <Link
              href="/justice"
              className="block p-3 rounded-lg bg-slate-900/50 border border-slate-800 hover:border-purple-500/50 transition-colors"
            >
              <div className="text-sm font-semibold text-slate-200">Appeal</div>
              <div className="text-xs text-gray-400">CP itirazı</div>
            </Link>
            <Link
              href="/consent"
              className="block p-3 rounded-lg bg-slate-900/50 border border-slate-800 hover:border-purple-500/50 transition-colors"
            >
              <div className="text-sm font-semibold text-slate-200">Consent Review</div>
              <div className="text-xs text-gray-400">Sözleşme inceleme</div>
            </Link>
          </div>
        </div>
      </div>

      {/* Second Row: NovaScore + Justice Status */}
      <div className="grid md:grid-cols-2 gap-6">
        {citizenState.novaScore ? (
          <NovaScoreCard novaScore={citizenState.novaScore as NovaScorePayload} showDetails={true} />
        ) : (
          <div className="aurora-card">
            <h3 className="text-lg font-semibold text-slate-200 mb-4">NovaScore</h3>
            <p className="text-sm text-slate-400">
              NovaScore mevcut değil. Skorunuzu oluşturmak için consent akışını tamamlayın.
            </p>
            <Link
              href="/onboarding"
              className="mt-2 inline-block text-xs text-purple-300 hover:text-purple-200 underline"
            >
              Onboarding'e git →
            </Link>
          </div>
        )}

        {citizenState.cpState ? (
          <div className="aurora-card">
            <h3 className="text-lg font-semibold text-slate-200 mb-4">Justice Status</h3>
            <div className="space-y-4">
              <RegimeBadge regime={citizenState.cpState.regime} size="lg" showLabel={true} />
              <div>
                <p className="text-sm text-slate-400 mb-1">CP Value</p>
                <p className="text-3xl font-bold text-aurora-purple">{citizenState.cpState.cp_value}</p>
              </div>
              <div>
                <p className="text-sm text-slate-400 mb-1">Last Updated</p>
                <p className="text-xs text-slate-500">
                  {new Date(citizenState.cpState.last_updated_at).toLocaleString('tr-TR')}
                </p>
              </div>
              <button
                onClick={() => citizenState.refetch()}
                className="text-xs text-aurora-sky hover:underline"
              >
                Refresh
              </button>
            </div>
          </div>
        ) : (
          <div className="aurora-card">
            <h3 className="text-lg font-semibold text-slate-200 mb-4">Justice Status</h3>
            <p className="text-sm text-slate-400">CP durumu mevcut değil.</p>
          </div>
        )}
      </div>

      {/* Third Row: Wallet + Loyalty + Trust Factors */}
      <div className="grid md:grid-cols-3 gap-4">
        {/* Wallet */}
        <div className="aurora-card border-emerald-500/30 bg-gradient-to-br from-emerald-950/20 to-black">
          <h3 className="text-lg font-semibold text-slate-200 mb-4 flex items-center gap-2">
            <span className="text-emerald-400">💰</span>
            Wallet
          </h3>
          {citizenState.wallet ? (
            <div className="space-y-2">
              <div>
                <p className="text-xs text-gray-400">NCR Balance</p>
                <p className="text-2xl font-bold text-emerald-300">
                  {parseFloat(citizenState.wallet.balance).toFixed(2)} NCR
                </p>
              </div>
              <Link
                href="/wallet"
                className="text-xs text-emerald-300 hover:text-emerald-200 underline"
              >
                Wallet Detayları →
              </Link>
            </div>
          ) : (
            <p className="text-sm text-gray-400">Wallet bilgisi yüklenemedi</p>
          )}
        </div>

        {/* Loyalty */}
        <div className="aurora-card border-blue-500/30 bg-gradient-to-br from-blue-950/20 to-black">
          <h3 className="text-lg font-semibold text-slate-200 mb-4 flex items-center gap-2">
            <span className="text-blue-400">⭐</span>
            Loyalty
          </h3>
          {citizenState.loyalty ? (
            <div className="space-y-2">
              <div>
                <p className="text-xs text-gray-400">Level</p>
                <p className="text-2xl font-bold text-blue-300">
                  {citizenState.loyalty.level} ({citizenState.loyalty.tier})
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-400">XP Total</p>
                <p className="text-lg font-semibold text-blue-200">{citizenState.loyalty.xp_total} XP</p>
              </div>
              <div>
                <p className="text-xs text-gray-400">Next Level</p>
                <p className="text-sm text-blue-300">{citizenState.loyalty.xp_to_next_level} XP kaldı</p>
              </div>
            </div>
          ) : (
            <p className="text-sm text-gray-400">Loyalty bilgisi yüklenemedi</p>
          )}
        </div>

        {/* Trust Factors */}
        <TrustFactors state={citizenState} />
      </div>

      {/* Fourth Row: Timeline + CP Trend */}
      <div className="grid md:grid-cols-2 gap-6">
        <CitizenTimeline state={citizenState} />
        {citizenState.cpState && (
          <div className="aurora-card">
            <h3 className="text-lg font-semibold text-slate-200 mb-4">CP Trend</h3>
            <CPTrendGraph
              data={[
                {
                  date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
                  cp: 0,
                },
                {
                  date: new Date(Date.now() - 20 * 24 * 60 * 60 * 1000).toISOString(),
                  cp: 5,
                },
                {
                  date: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(),
                  cp: 12,
                },
                {
                  date: citizenState.cpState.last_updated_at,
                  cp: citizenState.cpState.cp_value,
                },
              ]}
            />
          </div>
        )}
      </div>

      {/* Policy Breakdown */}
      {policy && (
        <div className="aurora-card border-purple-500/30 bg-gradient-to-br from-purple-950/20 to-black">
          <h3 className="text-lg font-semibold text-slate-200 mb-4">Active Policy</h3>
          <PolicyBreakdown policy={policy as PolicyParams} />
        </div>
      )}
    </div>
  )
}
