// HITL Quest Hook - Ombudsman Paneli için
import { useState, useEffect } from 'react'
import { useAuroraAPI } from './useAuroraAPI'

export interface HitlQuest {
  id: number
  user_id: number
  quest_uuid: string
  quest_type: string
  key: string
  title: string
  description: string
  base_reward_ncr: number
  base_reward_xp: number
  final_reward_ncr: number | null
  final_reward_xp: number | null
  final_score: number | null
  status: string
  assigned_at: string
  expires_at: string
  submitted_at: string | null
  resolved_at: string | null
  proof_type: string | null
  proof_payload_ref: string | null
  abuse_risk_snapshot: number | null
  house_edge_snapshot: number | null
}

export function useHitlQuests(minRiskScore: number = 6.0) {
  const { fetchAPI } = useAuroraAPI()
  const [quests, setQuests] = useState<HitlQuest[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadQuests = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      const { data, error: apiError } = await fetchAPI<HitlQuest[]>(
        `/admin/quests/hitl?min_risk_score=${minRiskScore}&limit=100`
      )
      
      if (apiError) {
        setError(apiError.detail || 'Failed to load HITL quests')
        setQuests([])
      } else {
        setQuests(data || [])
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
      setQuests([])
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadQuests()
    // Auto-refresh every 30 seconds
    const interval = setInterval(loadQuests, 30000)
    return () => clearInterval(interval)
  }, [minRiskScore])

  return { quests, isLoading, error, refetch: loadQuests }
}

