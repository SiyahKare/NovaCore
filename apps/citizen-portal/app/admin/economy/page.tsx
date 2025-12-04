'use client'

import { useState, useEffect } from 'react'
import { ProtectedView } from '@/components/ProtectedView'
import { useAuroraAPI } from '@aurora/hooks'
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts'

interface EconomySummary {
  current_price_try: number
  price_change_24h: number
  price_change_7d: number
  treasury_reserves_fiat: number
  ncr_outstanding: number
  coverage_ratio: number
  daily_limit_ncr: number
  daily_issued_ncr: number
  daily_load_ratio: number
  net_mint_24h: number
  net_burn_24h: number
  net_redemption_24h: number
  risk_score_distribution: {
    '0-2': number
    '3-5': number
    '6-8': number
    '9-10': number
  }
  total_users: number
  active_users_24h: number
}

interface TreasuryDailyStat {
  day: string
  limit_ncr: number
  issued_ncr: number
  load_ratio: number
  remaining_ncr: number
}

const COLORS = {
  primary: '#8b5cf6',
  success: '#10b981',
  warning: '#f59e0b',
  danger: '#ef4444',
  info: '#3b82f6',
}

const RISK_COLORS = {
  '0-2': '#10b981',
  '3-5': '#f59e0b',
  '6-8': '#f97316',
  '9-10': '#ef4444',
}

export default function EconomyDashboardPage() {
  return (
    <ProtectedView requireAdmin>
      <EconomyDashboardInner />
    </ProtectedView>
  )
}

function EconomyDashboardInner() {
  const { get } = useAuroraAPI()
  const [summary, setSummary] = useState<EconomySummary | null>(null)
  const [treasuryStats, setTreasuryStats] = useState<TreasuryDailyStat[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
    const interval = setInterval(loadData, 30000) // Refresh every 30s
    return () => clearInterval(interval)
  }, [])

  const loadData = async () => {
    try {
      const [summaryRes, treasuryRes] = await Promise.all([
        get('/admin/economy/summary'),
        get('/admin/economy/treasury/daily?days=30'),
      ])

      if (summaryRes.ok) {
        setSummary(await summaryRes.json())
      }
      if (treasuryRes.ok) {
        const data = await treasuryRes.json()
        setTreasuryStats(data)
      }
    } catch (error) {
      console.error('Failed to load economy data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading || !summary) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <div className="text-gray-400">Yükleniyor...</div>
      </div>
    )
  }

  // Format treasury stats for charts
  const treasuryChartData = treasuryStats
    .slice()
    .reverse()
    .map((stat) => ({
      date: new Date(stat.day).toLocaleDateString('tr-TR', { month: 'short', day: 'numeric' }),
      issued: stat.issued_ncr,
      limit: stat.limit_ncr,
      load: (stat.load_ratio * 100).toFixed(1),
    }))

  // Risk distribution for pie chart
  const riskData = [
    { name: 'Düşük Risk (0-2)', value: summary.risk_score_distribution['0-2'], color: RISK_COLORS['0-2'] },
    { name: 'Orta Risk (3-5)', value: summary.risk_score_distribution['3-5'], color: RISK_COLORS['3-5'] },
    { name: 'Yüksek Risk (6-8)', value: summary.risk_score_distribution['6-8'], color: RISK_COLORS['6-8'] },
    { name: 'Kritik Risk (9-10)', value: summary.risk_score_distribution['9-10'], color: RISK_COLORS['9-10'] },
  ].filter((item) => item.value > 0)

  const priceChangeColor = summary.price_change_24h >= 0 ? COLORS.success : COLORS.danger
  const coverageColor = summary.coverage_ratio >= 1.2 ? COLORS.success : summary.coverage_ratio >= 1.0 ? COLORS.warning : COLORS.danger

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-100">NasipQuest Economy Dashboard</h1>
          <p className="text-sm text-gray-400 mt-1">
            NCR fiyatı, Treasury durumu, akış metrikleri ve risk dağılımı
          </p>
        </div>
        <div className="text-right">
          <div className="text-xs text-gray-500">Son Güncelleme</div>
          <div className="text-sm text-gray-300">{new Date().toLocaleTimeString('tr-TR')}</div>
        </div>
      </header>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* NCR Price */}
        <MetricCard
          title="NCR Fiyatı"
          value={`${summary.current_price_try.toFixed(4)} TRY`}
          change={summary.price_change_24h}
          changeLabel="24s"
          color={priceChangeColor}
          icon="💰"
        />

        {/* Coverage Ratio */}
        <MetricCard
          title="Coverage Ratio"
          value={`${(summary.coverage_ratio * 100).toFixed(1)}%`}
          subtitle={`Hedef: ${(1.2 * 100).toFixed(0)}%`}
          color={coverageColor}
          icon="🛡️"
        />

        {/* Daily Load */}
        <MetricCard
          title="Günlük Yük"
          value={`${(summary.daily_load_ratio * 100).toFixed(1)}%`}
          subtitle={`${summary.daily_issued_ncr.toLocaleString('tr-TR', { maximumFractionDigits: 0 })} / ${summary.daily_limit_ncr.toLocaleString('tr-TR', { maximumFractionDigits: 0 })} NCR`}
          color={summary.daily_load_ratio > 0.85 ? COLORS.warning : COLORS.success}
          icon="⚡"
        />

        {/* NCR Outstanding */}
        <MetricCard
          title="Dolaşımdaki NCR"
          value={`${summary.ncr_outstanding.toLocaleString('tr-TR', { maximumFractionDigits: 0 })}`}
          subtitle={`${summary.total_users} kullanıcı`}
          color={COLORS.info}
          icon="📊"
        />
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Treasury Daily Load */}
        <ChartCard title="Günlük Treasury Yükü (Son 30 Gün)">
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={treasuryChartData}>
              <defs>
                <linearGradient id="colorIssued" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={COLORS.primary} stopOpacity={0.8} />
                  <stop offset="95%" stopColor={COLORS.primary} stopOpacity={0.1} />
                </linearGradient>
                <linearGradient id="colorLimit" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={COLORS.info} stopOpacity={0.3} />
                  <stop offset="95%" stopColor={COLORS.info} stopOpacity={0.05} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="date" stroke="#9ca3af" fontSize={12} />
              <YAxis stroke="#9ca3af" fontSize={12} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1f2937',
                  border: '1px solid #374151',
                  borderRadius: '8px',
                }}
                formatter={(value: number) => value.toLocaleString('tr-TR', { maximumFractionDigits: 0 })}
              />
              <Legend />
              <Area
                type="monotone"
                dataKey="limit"
                stroke={COLORS.info}
                fillOpacity={1}
                fill="url(#colorLimit)"
                name="Limit"
              />
              <Area
                type="monotone"
                dataKey="issued"
                stroke={COLORS.primary}
                fillOpacity={1}
                fill="url(#colorIssued)"
                name="Dağıtılan"
              />
            </AreaChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Risk Distribution */}
        <ChartCard title="RiskScore Dağılımı">
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={riskData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {riskData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1f2937',
                  border: '1px solid #374151',
                  borderRadius: '8px',
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Flow Metrics */}
        <ChartCard title="NCR Akış Metrikleri (24 Saat)">
          <div className="space-y-4">
            <FlowBar
              label="Mint (Basılan)"
              value={summary.net_mint_24h}
              color={COLORS.success}
            />
            <FlowBar
              label="Burn (Yakılan)"
              value={summary.net_burn_24h}
              color={COLORS.danger}
            />
            <FlowBar
              label="Redemption (Çekilen)"
              value={summary.net_redemption_24h}
              color={COLORS.warning}
            />
            <div className="pt-4 border-t border-gray-700">
              <div className="flex justify-between items-center">
                <span className="text-sm font-semibold text-gray-300">Net Akış</span>
                <span
                  className={`text-lg font-bold ${
                    summary.net_mint_24h - summary.net_burn_24h - summary.net_redemption_24h >= 0
                      ? 'text-green-400'
                      : 'text-red-400'
                  }`}
                >
                  {(summary.net_mint_24h - summary.net_burn_24h - summary.net_redemption_24h).toLocaleString('tr-TR', {
                    maximumFractionDigits: 0,
                  })}{' '}
                  NCR
                </span>
              </div>
            </div>
          </div>
        </ChartCard>

        {/* Treasury Health */}
        <ChartCard title="Treasury Sağlığı">
          <div className="space-y-6">
            <HealthIndicator
              label="Coverage Ratio"
              value={summary.coverage_ratio}
              target={1.2}
              unit="x"
              color={coverageColor}
            />
            <HealthIndicator
              label="Günlük Yük Oranı"
              value={summary.daily_load_ratio}
              target={0.7}
              unit="%"
              color={summary.daily_load_ratio > 0.85 ? COLORS.warning : COLORS.success}
            />
            <div className="pt-4 border-t border-gray-700">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <div className="text-gray-500">Treasury Rezervi</div>
                  <div className="text-lg font-semibold text-gray-100">
                    {summary.treasury_reserves_fiat.toLocaleString('tr-TR', { maximumFractionDigits: 0 })} TRY
                  </div>
                </div>
                <div>
                  <div className="text-gray-500">Aktif Kullanıcılar</div>
                  <div className="text-lg font-semibold text-gray-100">
                    {summary.active_users_24h.toLocaleString('tr-TR')}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </ChartCard>
      </div>
    </div>
  )
}

function MetricCard({
  title,
  value,
  change,
  changeLabel,
  subtitle,
  color,
  icon,
}: {
  title: string
  value: string
  change?: number
  changeLabel?: string
  subtitle?: string
  color?: string
  icon?: string
}) {
  return (
    <div className="rounded-xl border border-white/10 bg-gradient-to-br from-black/60 to-black/40 p-6 backdrop-blur-sm">
      <div className="flex items-start justify-between mb-2">
        <div className="text-xs font-medium text-gray-400 uppercase tracking-wider">{title}</div>
        {icon && <span className="text-2xl">{icon}</span>}
      </div>
      <div className="text-2xl font-bold text-gray-100 mb-1">{value}</div>
      {subtitle && <div className="text-xs text-gray-500">{subtitle}</div>}
      {change !== undefined && (
        <div className={`text-xs font-semibold mt-2 ${color || 'text-gray-400'}`}>
          {change >= 0 ? '↑' : '↓'} {Math.abs(change).toFixed(2)}% {changeLabel && `(${changeLabel})`}
        </div>
      )}
    </div>
  )
}

function ChartCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-xl border border-white/10 bg-gradient-to-br from-black/60 to-black/40 p-6 backdrop-blur-sm">
      <h3 className="text-sm font-semibold text-gray-200 mb-4">{title}</h3>
      {children}
    </div>
  )
}

function FlowBar({ label, value, color }: { label: string; value: number; color: string }) {
  const maxValue = Math.max(value, 1000) // Minimum scale
  const percentage = (value / maxValue) * 100

  return (
    <div>
      <div className="flex justify-between items-center mb-1">
        <span className="text-xs text-gray-400">{label}</span>
        <span className="text-sm font-semibold text-gray-200">
          {value.toLocaleString('tr-TR', { maximumFractionDigits: 0 })} NCR
        </span>
      </div>
      <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
        <div
          className="h-full transition-all duration-500 rounded-full"
          style={{ width: `${percentage}%`, backgroundColor: color }}
        />
      </div>
    </div>
  )
}

function HealthIndicator({
  label,
  value,
  target,
  unit,
  color,
}: {
  label: string
  value: number
  target: number
  unit: string
  color: string
}) {
  const percentage = (value / target) * 100
  const isHealthy = value >= target

  return (
    <div>
      <div className="flex justify-between items-center mb-2">
        <span className="text-xs text-gray-400">{label}</span>
        <span className="text-sm font-semibold" style={{ color }}>
          {value.toFixed(2)} {unit}
        </span>
      </div>
      <div className="h-3 bg-gray-800 rounded-full overflow-hidden">
        <div
          className="h-full transition-all duration-500 rounded-full"
          style={{
            width: `${Math.min(percentage, 100)}%`,
            backgroundColor: color,
          }}
        />
      </div>
      <div className="text-xs text-gray-500 mt-1">Hedef: {target.toFixed(2)} {unit}</div>
    </div>
  )
}

