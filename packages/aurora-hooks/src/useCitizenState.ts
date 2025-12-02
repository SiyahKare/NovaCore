import { useState, useEffect, useCallback } from 'react'
import { useAuroraAPI } from './useAuroraAPI'
import type { NovaScorePayload, CpState } from '@aurora/ui'

export interface WalletBalance {
  user_id: number
  token: string
  balance: string
}

export interface LoyaltyProfile {
  user_id: number
  xp_total: number
  level: number
  tier: string
  total_events: number
  current_streak: number
  max_streak: number
  vip_priority: number
  ai_credits_bonus: number
  xp_to_next_level: number
  xp_to_next_tier: number
  next_tier: string | null
  created_at: string
  updated_at: string
}

export interface PrivacyProfile {
  user_id: string
  latest_consent_id: string | null
  contract_version: string | null
  consent_level: string | null
  recall_requested_at: string | null
  recall_completed_at: string | null
  recall_mode: string | null
  last_policy_updated_at: string
}

export interface ViolationItem {
  id: string
  category: string
  code: string
  severity: number
  cp_delta: number
  created_at: string
}

export interface CitizenIdentity {
  id: number
  telegram_id: number
  username: string | null
  display_name: string | null
  ton_wallet: string | null
  is_performer: boolean
  is_agency_owner: boolean
  is_admin: boolean
  created_at: string
}

export interface CitizenState {
  identity: CitizenIdentity | null
  wallet: WalletBalance | null
  loyalty: LoyaltyProfile | null
  privacy: PrivacyProfile | null
  novaScore: NovaScorePayload | null
  cpState: CpState | null
  violations: ViolationItem[]
  loading: boolean
  error: string | null
}

export function useCitizenState() {
  const { fetchAPI } = useAuroraAPI()
  const [state, setState] = useState<CitizenState>({
    identity: null,
    wallet: null,
    loyalty: null,
    privacy: null,
    novaScore: null,
    cpState: null,
    violations: [],
    loading: true,
    error: null,
  })

  const loadAll = useCallback(async () => {
    setState((prev) => ({ ...prev, loading: true, error: null }))

    try {
      // Parallel fetch all data
      const [
        identityResult,
        walletResult,
        loyaltyResult,
        privacyResult,
        novaScoreResult,
        cpStateResult,
        violationsResult,
      ] = await Promise.allSettled([
        fetchAPI<CitizenIdentity>('/identity/me').catch((err) => ({ data: null, error: { detail: err.message || 'Failed to fetch identity' } })),
        fetchAPI<WalletBalance>('/wallet/me').catch((err) => ({ data: null, error: { detail: err.message || 'Failed to fetch wallet' } })),
        fetchAPI<LoyaltyProfile>('/loyalty/me').catch((err) => ({ data: null, error: { detail: err.message || 'Failed to fetch loyalty' } })),
        fetchAPI<PrivacyProfile>('/consent/profile/me').catch((err) => ({ data: null, error: { detail: err.message || 'Failed to fetch privacy' } })),
        fetchAPI<NovaScorePayload>('/nova-score/me').catch((err) => ({ data: null, error: { detail: err.message || 'Failed to fetch novaScore' } })),
        fetchAPI<CpState>('/justice/cp/me').catch((err) => ({ data: null, error: { detail: err.message || 'Failed to fetch CP state' } })),
        fetchAPI<ViolationItem[]>('/justice/violations/me?limit=10').catch((err) => ({ data: null, error: { detail: err.message || 'Failed to fetch violations' } })),
      ])

      const newState: Partial<CitizenState> = {
        loading: false,
        error: null,
      }

      const errors: string[] = []

      // Process identity
      if (identityResult.status === 'fulfilled') {
        if (!identityResult.value.error && identityResult.value.data) {
          newState.identity = identityResult.value.data
        } else if (identityResult.value.error) {
          console.error('Identity fetch error:', identityResult.value.error)
          errors.push(`Identity: ${identityResult.value.error.detail || identityResult.value.error.error || 'Failed to load'}`)
        }
      } else {
        console.error('Identity request failed:', identityResult.reason)
        errors.push('Identity: Request failed')
      }

      // Process wallet
      if (walletResult.status === 'fulfilled') {
        if (!walletResult.value.error && walletResult.value.data) {
          newState.wallet = walletResult.value.data
        } else if (walletResult.value.error) {
          // Wallet error is not critical, just log
          console.warn('Wallet error:', walletResult.value.error.detail)
        }
      }

      // Process loyalty
      if (loyaltyResult.status === 'fulfilled') {
        if (!loyaltyResult.value.error && loyaltyResult.value.data) {
          newState.loyalty = loyaltyResult.value.data
        } else if (loyaltyResult.value.error) {
          // Loyalty error is not critical, just log
          console.warn('Loyalty error:', loyaltyResult.value.error.detail)
        }
      }

      // Process privacy (may not exist if consent not signed)
      if (privacyResult.status === 'fulfilled') {
        if (!privacyResult.value.error && privacyResult.value.data) {
          newState.privacy = privacyResult.value.data
        } else if (privacyResult.value.error) {
          // Privacy error is expected if consent not signed
          if (!privacyResult.value.error.detail?.includes('not found')) {
            console.warn('Privacy error:', privacyResult.value.error.detail)
          }
        }
      }

      // Process novaScore (may not exist if consent not signed)
      if (novaScoreResult.status === 'fulfilled') {
        if (!novaScoreResult.value.error && novaScoreResult.value.data) {
          newState.novaScore = novaScoreResult.value.data
        } else if (
          novaScoreResult.value.error &&
          !novaScoreResult.value.error.detail?.includes('Privacy profile not found')
        ) {
          // Only log if it's not the expected "privacy profile not found" error
          console.warn('NovaScore error:', novaScoreResult.value.error.detail)
        }
      }

      // Process CP state
      if (cpStateResult.status === 'fulfilled') {
        if (!cpStateResult.value.error && cpStateResult.value.data) {
          newState.cpState = cpStateResult.value.data
        } else if (cpStateResult.value.error) {
          console.error('CP State fetch error:', cpStateResult.value.error)
          errors.push(`CP State: ${cpStateResult.value.error.detail || cpStateResult.value.error.error || 'Failed to load'}`)
        }
      } else {
        console.error('CP State request failed:', cpStateResult.reason)
        errors.push('CP State: Request failed')
      }

      // Process violations
      if (violationsResult.status === 'fulfilled') {
        if (!violationsResult.value.error && violationsResult.value.data) {
          newState.violations = violationsResult.value.data
        } else if (violationsResult.value.error) {
          // Violations error is not critical, just log
          console.warn('Violations error:', violationsResult.value.error.detail)
        }
      }

      // Set error only if critical errors exist
      if (errors.length > 0) {
        newState.error = errors.join('; ')
      }

      setState((prev) => ({ ...prev, ...newState }))
    } catch (err) {
      console.error('useCitizenState error:', err)
      setState((prev) => ({
        ...prev,
        loading: false,
        error: err instanceof Error ? err.message : 'Failed to load citizen state. Please check your connection and try again.',
      }))
    }
  }, [fetchAPI])

  useEffect(() => {
    loadAll()
  }, [loadAll])

  const refetch = useCallback(() => {
    loadAll()
  }, [loadAll])

  return {
    ...state,
    refetch,
  }
}

