import { useState, useEffect, useCallback } from 'react'
import { useAuroraAPI } from './useAuroraAPI'
import type { CpState, ViolationLog } from '@aurora/ui'

// Token check helper
const hasToken = (): boolean => {
  if (typeof window === 'undefined') return false
  try {
    return !!localStorage.getItem('aurora_token')
  } catch {
    return false
  }
}

// Default demo CP state for non-authenticated users
const DEMO_CP_STATE: CpState = {
  user_id: 'demo',
  cp_value: 0,
  last_updated_at: new Date().toISOString(),
  regime: 'NORMAL',
}

export function useJustice(userId?: string) {
  const { fetchAPI } = useAuroraAPI()
  const [cpState, setCpState] = useState<CpState | null>(null)
  const [violations, setViolations] = useState<ViolationLog[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  const loadJustice = useCallback(async () => {
    setLoading(true)
    setError(null)

    // Check if user is authenticated
    const authenticated = hasToken()
    setIsAuthenticated(authenticated)

    // If not authenticated, use demo values
    if (!authenticated && !userId) {
      setCpState(DEMO_CP_STATE)
      setViolations([])
      setLoading(false)
      return
    }

    const endpoint = userId ? `/justice/cp/${userId}` : '/justice/cp/me'
    const { data, error: apiError } = await fetchAPI<CpState>(endpoint)

    if (apiError) {
      // Handle 401 gracefully - user not authenticated
      if (apiError.detail === 'Not authenticated' || apiError.error === 'Not authenticated') {
        setCpState(DEMO_CP_STATE)
        setError(null) // Don't show error for expected auth failure
      } else {
        setError(apiError.detail || 'Failed to load CP state')
        setCpState(null)
      }
    } else if (data) {
      setCpState(data)
    }

    // Load violations (if endpoint exists)
    // TODO: Add violations endpoint to API
    // const violationsData = await fetchAPI<ViolationLog[]>(`/justice/violations?user_id=${userId || 'me'}`)
    // if (violationsData.data) {
    //   setViolations(violationsData.data)
    // }

    setLoading(false)
  }, [userId, fetchAPI])

  useEffect(() => {
    loadJustice()
  }, [loadJustice])

  const createViolation = useCallback(
    async (violation: {
      user_id: string
      category: 'EKO' | 'COM' | 'SYS' | 'TRUST'
      code: string
      severity: number
      source?: string
    }) => {
      if (!isAuthenticated) {
        throw new Error('Authentication required to create violations')
      }

      const { data, error: apiError } = await fetchAPI<ViolationLog>('/justice/violations', {
        method: 'POST',
        body: JSON.stringify(violation),
      })

      if (apiError) {
        throw new Error(apiError.detail || 'Failed to create violation')
      }

      // Reload justice state after creating violation
      await loadJustice()

      return data
    },
    [fetchAPI, loadJustice, isAuthenticated]
  )

  const refetch = useCallback(() => {
    loadJustice()
  }, [loadJustice])

  return {
    cpState,
    violations,
    loading,
    error,
    isAuthenticated,
    createViolation,
    refetch,
  }
}
