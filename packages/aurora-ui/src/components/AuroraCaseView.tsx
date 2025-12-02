'use client'

import { useEffect, useState } from 'react'
import { RegimeBadge } from './RegimeBadge'
import type { CpState, NovaScorePayload } from '../types'

// Support both Vite (import.meta.env) and Next.js (process.env)
const getAPIBaseURL = () => {
  if (typeof window !== 'undefined') {
    return (
      (window as any).__NEXT_DATA__?.env?.NEXT_PUBLIC_AURORA_API_URL ||
      process.env.NEXT_PUBLIC_AURORA_API_URL ||
      'http://localhost:8000/api/v1'
    )
  }
  return (
    (typeof import.meta !== 'undefined' && (import.meta as any).env?.VITE_AURORA_API_URL) ||
    'http://localhost:8000/api/v1'
  )
}

const getToken = (): string | null => {
  if (typeof window === 'undefined') return null
  try {
    return localStorage.getItem('aurora_token')
  } catch {
    return null
  }
}

interface PrivacyProfile {
  user_id: string
  latest_consent_id?: string | null
  contract_version?: string | null
  consent_level?: 'FULL' | 'LIMITED' | 'MINIMUM' | null
  recall_mode?: 'ANONYMIZE' | 'FULL_EXCLUDE' | null
  recall_requested_at?: string | null
  last_policy_updated_at?: string | null
}

interface Violation {
  id: string
  user_id: string
  category: 'EKO' | 'COM' | 'SYS' | 'TRUST'
  code: string
  severity: number
  cp_delta: number
  source?: string | null
  created_at: string
}

interface CaseFileResponse {
  user_id: string
  privacy_profile: PrivacyProfile | null
  cp_state: CpState
  nova_score: NovaScorePayload | null
  recent_violations: Violation[]
}

interface AuroraCaseViewProps {
  userId: string
  className?: string
}

const categoryLabel: Record<Violation['category'], string> = {
  EKO: 'Ekonomi',
  COM: 'İletişim',
  SYS: 'Sistem',
  TRUST: 'Güven',
}

export const AuroraCaseView: React.FC<AuroraCaseViewProps> = ({ userId, className = '' }) => {
  const [data, setData] = useState<CaseFileResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    const loadCase = async () => {
      setLoading(true)
      setError(null)

      try {
        const token = getToken()
        const apiUrl = getAPIBaseURL()
        const res = await fetch(`${apiUrl}/justice/case/${encodeURIComponent(userId)}`, {
          headers: {
            'Content-Type': 'application/json',
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
        })

        if (!res.ok) {
          throw new Error(`HTTP ${res.status}`)
        }

        const caseData = (await res.json()) as CaseFileResponse

        if (!cancelled) {
          setData(caseData)
        }
      } catch (err: any) {
        if (!cancelled) {
          setError(err?.message || 'Case dosyası alınamadı')
          setData(null)
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    loadCase()

    return () => {
      cancelled = true
    }
  }, [userId])

  if (loading && !data) {
    return (
      <div className={`p-6 text-sm text-slate-400 ${className}`}>
        Aurora case dosyası yükleniyor...
      </div>
    )
  }

  if (error) {
    return (
      <div className={`p-6 text-sm text-red-500 ${className}`}>
        Aurora case dosyası alınamadı: {error}
      </div>
    )
  }

  if (!data) {
    return (
      <div className={`p-6 text-sm text-slate-400 ${className}`}>Henüz case verisi yok.</div>
    )
  }

  const { cp_state, nova_score, privacy_profile, recent_violations } = data

  return (
    <div className={`p-6 space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between gap-4">
        <div>
          <div className="text-xs uppercase tracking-wide text-slate-400">Aurora Case File</div>
          <div className="text-lg font-semibold text-slate-100">
            Kullanıcı: <span className="font-mono">{data.user_id}</span>
          </div>
        </div>
        <div className="flex flex-col items-end gap-2">
          <RegimeBadge regime={cp_state.regime} size="md" showLabel />
          {nova_score && (
            <div className="text-sm text-slate-300">
              NovaScore:{' '}
              <span className="font-mono text-base text-sky-300">{nova_score.value}</span> / 1000{' '}
              <span className="text-xs text-slate-500">
                (conf: {Math.round(nova_score.confidence_overall * 100)}%)
              </span>
            </div>
          )}
        </div>
      </div>

      {/* 3-column grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Column 1: Consent & Privacy */}
        <div className="bg-slate-900/60 border border-slate-700/70 rounded-2xl p-4 space-y-3">
          <div className="text-xs font-semibold uppercase text-slate-400">Consent & Privacy</div>
          {privacy_profile ? (
            <div className="space-y-2 text-xs text-slate-200">
              <div className="flex justify-between">
                <span className="text-slate-400">Contract:</span>
                <span>{privacy_profile.contract_version ?? '—'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Consent Level:</span>
                <span className="font-mono">{privacy_profile.consent_level ?? 'unknown'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Recall Mode:</span>
                <span className="font-mono">{privacy_profile.recall_mode ?? 'none'}</span>
              </div>
              {privacy_profile.recall_requested_at && (
                <div className="flex justify-between">
                  <span className="text-slate-400">Recall Requested:</span>
                  <span className="font-mono">
                    {new Date(privacy_profile.recall_requested_at).toLocaleString()}
                  </span>
                </div>
              )}
              {privacy_profile.last_policy_updated_at && (
                <div className="flex justify-between">
                  <span className="text-slate-400">Policy Updated:</span>
                  <span className="font-mono">
                    {new Date(privacy_profile.last_policy_updated_at).toLocaleString()}
                  </span>
                </div>
              )}
            </div>
          ) : (
            <div className="text-xs text-slate-500">Bu kullanıcı için henüz consent kaydı yok.</div>
          )}
        </div>

        {/* Column 2: NovaScore Components */}
        {nova_score && (
          <div className="bg-slate-900/60 border border-slate-700/70 rounded-2xl p-4 space-y-3">
            <div className="text-xs font-semibold uppercase text-slate-400">
              NovaScore Components
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs text-slate-200">
              {Object.entries(nova_score.components).map(([key, comp]) => (
                <div key={key} className="flex flex-col rounded-xl bg-slate-800/80 px-3 py-2">
                  <div className="text-[10px] uppercase text-slate-400">{key}</div>
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-sm">{Math.round(comp.value)}</span>
                    <span className="text-[10px] text-slate-500">
                      conf: {Math.round(comp.confidence * 100)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
            {nova_score.explanation && (
              <div className="mt-3 text-[11px] text-slate-400 border-t border-slate-800 pt-2">
                {nova_score.explanation}
              </div>
            )}
          </div>
        )}

        {/* Column 3: CP & Timeline */}
        <div className="bg-slate-900/60 border border-slate-700/70 rounded-2xl p-4 space-y-3">
          <div className="text-xs font-semibold uppercase text-slate-400">CP & Timeline</div>
          <div className="text-xs text-slate-200 space-y-1">
            <div className="flex justify-between">
              <span className="text-slate-400">CP:</span>
              <span className="font-mono">{cp_state.cp_value}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Regime:</span>
              <span className="font-mono">{cp_state.regime}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Last Updated:</span>
              <span className="font-mono">
                {new Date(cp_state.last_updated_at).toLocaleString()}
              </span>
            </div>
          </div>
          <div className="mt-3 text-[11px] text-slate-500">
            CP değeri zamanla otomatik olarak decay oluyor. Yüksek CP + LOCKDOWN, Ombudsman
            incelemesi gerektirir.
          </div>
        </div>
      </div>

      {/* Violations Table */}
      <div className="bg-slate-900/60 border border-slate-700/70 rounded-2xl p-4 space-y-3">
        <div className="flex items-center justify-between">
          <div className="text-xs font-semibold uppercase text-slate-400">Recent Violations</div>
          <div className="text-[11px] text-slate-500">Toplam: {recent_violations.length}</div>
        </div>
        {recent_violations.length === 0 ? (
          <div className="text-xs text-slate-500">
            Bu kullanıcı için violation kaydı bulunamadı.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full text-xs text-slate-200">
              <thead className="border-b border-slate-800 text-[11px] text-slate-400">
                <tr>
                  <th className="py-2 pr-4 text-left">Tarih</th>
                  <th className="py-2 pr-4 text-left">Kategori</th>
                  <th className="py-2 pr-4 text-left">Kod</th>
                  <th className="py-2 pr-4 text-right">Severity</th>
                  <th className="py-2 pr-4 text-right">CP Δ</th>
                  <th className="py-2 pr-4 text-left">Kaynak</th>
                </tr>
              </thead>
              <tbody>
                {recent_violations.map((v) => (
                  <tr key={v.id} className="border-b border-slate-900/70 last:border-0">
                    <td className="py-1 pr-4 align-top">
                      {new Date(v.created_at).toLocaleString()}
                    </td>
                    <td className="py-1 pr-4 align-top">{categoryLabel[v.category]}</td>
                    <td className="py-1 pr-4 align-top font-mono">{v.code}</td>
                    <td className="py-1 pr-4 align-top text-right">{v.severity}</td>
                    <td className="py-1 pr-4 align-top text-right text-red-300">+{v.cp_delta}</td>
                    <td className="py-1 pr-4 align-top text-slate-400">{v.source ?? '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

