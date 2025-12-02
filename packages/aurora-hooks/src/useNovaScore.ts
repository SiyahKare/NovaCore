import { useState, useEffect, useCallback } from 'react'
import { useAuroraAPI } from './useAuroraAPI'
import type { NovaScorePayload } from '@aurora/ui'

export function useNovaScore(userId?: string) {
  const { fetchAPI } = useAuroraAPI()
  const [score, setScore] = useState<NovaScorePayload | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadScore = useCallback(async () => {
    setLoading(true)
    setError(null)

    const endpoint = userId ? `/nova-score/${userId}` : '/nova-score/me'
    const { data, error: apiError } = await fetchAPI<NovaScorePayload>(endpoint)

    if (apiError) {
      // If privacy profile not found, it means consent hasn't been completed yet
      // This is expected during onboarding, so we don't treat it as a critical error
      if (apiError.detail?.includes('Privacy profile not found') || 
          apiError.detail?.includes('privacy profile')) {
        setError(null) // Don't show error for missing privacy profile
        setScore(null)
      } else {
        setError(apiError.detail || 'Failed to load NovaScore')
        setScore(null)
      }
    } else if (data) {
      setScore(data)
      setError(null)
    }

    setLoading(false)
  }, [userId, fetchAPI])

  useEffect(() => {
    loadScore()
  }, [loadScore])

  const refetch = useCallback(() => {
    loadScore()
  }, [loadScore])

  return { score, loading, error, refetch }
}

