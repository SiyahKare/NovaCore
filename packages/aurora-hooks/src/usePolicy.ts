import { useState, useEffect } from 'react'
import { useAuroraAPI } from './useAuroraAPI'
import type { PolicyParams } from '@aurora/ui'

export function usePolicy() {
  const { fetchAPI } = useAuroraAPI()
  const [policy, setPolicy] = useState<PolicyParams | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadPolicy = async () => {
      setLoading(true)
      setError(null)

      const { data, error: apiError } = await fetchAPI<PolicyParams>('/justice/policy/current')

      if (apiError) {
        setError(apiError.detail || 'Failed to load policy')
        setPolicy(null)
      } else if (data) {
        setPolicy(data)
      }

      setLoading(false)
    }

    loadPolicy()
  }, [fetchAPI])

  return {
    policy,
    loading,
    error,
    refetch: () => {},
  }
}

