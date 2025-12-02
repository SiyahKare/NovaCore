import { useState, useEffect, useCallback } from 'react'
import { useAuroraAPI } from './useAuroraAPI'

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

export function useCurrentCitizen() {
  const { fetchAPI } = useAuroraAPI()
  const [data, setData] = useState<CitizenIdentity | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadCitizen = useCallback(async () => {
    setLoading(true)
    setError(null)

    const { data: apiData, error: apiError } = await fetchAPI<CitizenIdentity>('/identity/me')

    if (apiError) {
      setError(apiError.detail || 'AUTH_ERROR')
      setData(null)
    } else if (apiData) {
      setData(apiData)
    }

    setLoading(false)
  }, [fetchAPI])

  useEffect(() => {
    loadCitizen()
  }, [loadCitizen])

  const refetch = useCallback(() => {
    loadCitizen()
  }, [loadCitizen])

  return {
    citizen: data,
    loading,
    error,
    refetch,
    isAuthenticated: data !== null && !error,
  }
}

