// packages/aurora-hooks/src/useAcademyProgress.ts
import { useState, useEffect, useCallback } from 'react'
import { useAuroraAPI } from './useAuroraAPI'

export interface ModuleProgress {
  module: string
  viewed: boolean
  completed: boolean
  viewed_at: string | null
  completed_at: string | null
}

export interface AcademyProgress {
  modules: ModuleProgress[]
  total_modules: number
  completed_modules: number
  completion_percentage: number
}

export function useAcademyProgress() {
  const { fetchAPI } = useAuroraAPI()
  const [progress, setProgress] = useState<AcademyProgress | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadProgress = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      
      const { data, error: apiError } = await fetchAPI<AcademyProgress>('/academy/progress')
      
      if (apiError) {
        throw new Error(apiError.detail || 'Failed to load academy progress')
      }
      
      setProgress(data)
    } catch (err: any) {
      setError(err.message || 'Failed to load academy progress')
    } finally {
      setLoading(false)
    }
  }, [fetchAPI])

  const completeModule = useCallback(async (module: string) => {
    try {
      const { error: apiError } = await fetchAPI(`/academy/modules/${module}/complete`, {
        method: 'POST',
      })
      
      if (apiError) {
        throw new Error(apiError.detail || 'Failed to complete module')
      }
      
      // Reload progress after completion
      await loadProgress()
    } catch (err: any) {
      throw err
    }
  }, [fetchAPI, loadProgress])

  useEffect(() => {
    loadProgress()
  }, [loadProgress])

  return {
    progress,
    loading,
    error,
    refetch: loadProgress,
    completeModule,
  }
}

