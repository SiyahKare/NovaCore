import { useState, useEffect, useCallback } from 'react'
import { useAuroraAPI } from './useAuroraAPI'
import type { CpState, ViolationLog } from '@aurora/ui'

export function useJustice(userId?: string) {
  const { fetchAPI } = useAuroraAPI()
  const [cpState, setCpState] = useState<CpState | null>(null)
  const [violations, setViolations] = useState<ViolationLog[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadJustice = useCallback(async () => {
    setLoading(true)
    setError(null)

    const endpoint = userId ? `/justice/cp/${userId}` : '/justice/cp/me'
    const { data, error: apiError } = await fetchAPI<CpState>(endpoint)

    if (apiError) {
      setError(apiError.detail || 'Failed to load CP state')
      setCpState(null)
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
    [fetchAPI, loadJustice]
  )

  const refetch = useCallback(() => {
    loadJustice()
  }, [loadJustice])

  return {
    cpState,
    violations,
    loading,
    error,
    createViolation,
    refetch,
  }
}

