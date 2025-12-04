// Ombudsman/Validator Hooks
import { useState, useEffect, useCallback } from 'react'
import { useAuroraAPI } from './useAuroraAPI'

export interface PendingAppeal {
  id: number
  submission_id: number
  user_id: string
  reason: string
  status: string
  appeal_fee_paid: boolean
  created_at: string
  task_title?: string
  proof_payload_ref?: string
  risk_score?: number
}

export interface PendingViolation {
  id: number | string  // Can be RiskEvent UUID or legacy ID
  user_id: number | string
  type?: "quest" | "submission" | "risk_event"  // Optional for RiskEvent
  title?: string  // Optional for RiskEvent
  category?: string  // For RiskEvent
  code?: string  // For RiskEvent
  score_ai?: number  // For RiskEvent (0-100)
  source?: string  // For RiskEvent
  status?: string  // For RiskEvent
  assigned_validators?: string[]  // For RiskEvent
  proof_payload_ref?: string
  risk_score?: number  // AbuseGuard RiskScore (0-10)
  ai_score?: number
  submitted_at?: string
  created_at?: string  // For RiskEvent
  quest_uuid?: string
  submission_id?: number
}

export interface DecisionRequest {
  decision: "APPROVE" | "REJECT"
  note?: string
}

export interface DecisionResponse {
  success: boolean
  message: string
  case_id: number
  decision: string
  risk_score_after?: number
  cp_delta?: number
}

export function useOmbudsmanAppeals() {
  const { fetchAPI } = useAuroraAPI()
  const [appeals, setAppeals] = useState<PendingAppeal[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadAppeals = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      const { data, error: apiError } = await fetchAPI<PendingAppeal[]>(
        '/justice/mod/appeals/pending'
      )
      
      if (apiError) {
        setError(apiError.detail || 'Failed to load appeals')
        setAppeals([])
      } else {
        setAppeals(data || [])
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
      setAppeals([])
    } finally {
      setIsLoading(false)
    }
  }, [fetchAPI])

  useEffect(() => {
    loadAppeals()
    // Auto-refresh every 30 seconds
    const interval = setInterval(loadAppeals, 30000)
    return () => clearInterval(interval)
  }, [loadAppeals])

  return { appeals, isLoading, error, refetch: loadAppeals }
}

export function useOmbudsmanViolations() {
  const { fetchAPI } = useAuroraAPI()
  const [violations, setViolations] = useState<PendingViolation[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadViolations = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      const { data, error: apiError } = await fetchAPI<PendingViolation[]>(
        '/justice/mod/violations/pending'
      )
      
      if (apiError) {
        setError(apiError.detail || 'Failed to load violations')
        setViolations([])
      } else {
        setViolations(data || [])
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
      setViolations([])
    } finally {
      setIsLoading(false)
    }
  }, [fetchAPI])

  useEffect(() => {
    loadViolations()
    // Auto-refresh every 30 seconds
    const interval = setInterval(loadViolations, 30000)
    return () => clearInterval(interval)
  }, [loadViolations])

  return { violations, isLoading, error, refetch: loadViolations }
}

export function useOmbudsmanDecision() {
  const { fetchAPI } = useAuroraAPI()
  const [isSubmitting, setIsSubmitting] = useState(false)

  const submitDecision = useCallback(async (
    caseId: number,
    decision: "APPROVE" | "REJECT",
    note?: string
  ): Promise<DecisionResponse | null> => {
    setIsSubmitting(true)
    
    try {
      const { data, error: apiError } = await fetchAPI<DecisionResponse>(
        `/justice/mod/violations/${caseId}/decision`,
        {
          method: 'POST',
          body: JSON.stringify({
            decision,
            note,
          }),
        }
      )
      
      if (apiError) {
        throw new Error(apiError.detail || 'Failed to submit decision')
      }
      
      return data
    } catch (err) {
      throw err
    } finally {
      setIsSubmitting(false)
    }
  }, [fetchAPI])

  return { submitDecision, isSubmitting }
}

