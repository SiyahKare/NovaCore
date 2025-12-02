import { useState, useCallback } from 'react'
import { useAuroraAPI } from './useAuroraAPI'

interface ConsentSession {
  session_id: string
  user_id: string
  created_at: string
}

export function useConsentFlow() {
  const { fetchAPI } = useAuroraAPI()
  const [session, setSession] = useState<ConsentSession | null>(null)
  const [loading, setLoading] = useState(false)

  const createSession = useCallback(async (userId?: string) => {
    setLoading(true)
    
    // If userId not provided, try to get from current citizen
    let finalUserId = userId
    
    if (!finalUserId) {
      try {
        const { data: citizen, error } = await fetchAPI<{ id: number }>('/identity/me')
        if (!error && citizen) {
          finalUserId = String(citizen.id)  // Convert id to string
        }
      } catch {
        // If not authenticated, userId must be provided
        // This is normal during onboarding before token is set
      }
    }
    
    if (!finalUserId) {
      setLoading(false)
      throw new Error('user_id gerekli. Önce giriş yapın veya user_id sağlayın.')
    }

    const { data, error } = await fetchAPI<ConsentSession>('/consent/session', {
      method: 'POST',
      body: JSON.stringify({
        user_id: finalUserId,
        client_fingerprint: navigator.userAgent,
      }),
    })

    if (error || !data) {
      setLoading(false)
      throw new Error(error?.detail || 'Failed to create consent session')
    }

    setSession(data)
    setLoading(false)
    return data
  }, [fetchAPI])

  const acceptClause = useCallback(
    async (sessionId: string, clauseId: string, status: 'ACCEPTED' | 'REJECTED') => {
      const { error } = await fetchAPI('/consent/clauses', {
        method: 'POST',
        body: JSON.stringify({
          session_id: sessionId,
          clause_id: clauseId,
          status,
          comprehension_passed: true,
        }),
      })

      if (error) {
        throw new Error(error.detail || 'Failed to accept clause')
      }
    },
    [fetchAPI]
  )

  const acceptRedline = useCallback(
    async (sessionId: string, redlineStatus: 'ACCEPTED' | 'REJECTED' = 'ACCEPTED') => {
      const { error } = await fetchAPI('/consent/redline', {
        method: 'POST',
        body: JSON.stringify({
          session_id: sessionId,
          redline_status: redlineStatus,
          user_note_hash: null,
        }),
      })

      if (error) {
        throw new Error(error.detail || 'Failed to accept redline clause')
      }
    },
    [fetchAPI]
  )

  const signConsent = useCallback(
    async (
      sessionId: string,
      clauses: string[],
      signature: string,
      userId?: string
    ) => {
      // Get userId from session if not provided
      let finalUserId = userId
      if (!finalUserId && session) {
        finalUserId = session.user_id
      }
      
      if (!finalUserId) {
        // Try to get from current citizen
        try {
          const { data: citizen, error } = await fetchAPI<{ id: number }>('/identity/me')
          if (!error && citizen) {
            finalUserId = String(citizen.id)  // Convert id to string
          }
        } catch {
          // If not authenticated, userId must be provided
        }
      }
      
      if (!finalUserId) {
        throw new Error('user_id gerekli. Önce giriş yapın veya user_id sağlayın.')
      }

      const { data, error } = await fetchAPI('/consent/sign', {
        method: 'POST',
        body: JSON.stringify({
          session_id: sessionId,
          user_id: finalUserId,
          clauses_accepted: clauses,
          redline_status: 'ACCEPTED',
          signature_text: signature,
          contract_version: 'Aurora-DataEthics-v1.0',
          client_fingerprint: typeof navigator !== 'undefined' ? navigator.userAgent : null,
        }),
      })

      if (error || !data) {
        throw new Error(error?.detail || 'Failed to sign consent')
      }

      return data
    },
    [fetchAPI, session]
  )

  return {
    session,
    loading,
    createSession,
    acceptClause,
    acceptRedline,
    signConsent,
  }
}

