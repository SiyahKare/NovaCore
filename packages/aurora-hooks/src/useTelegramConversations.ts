// Telegram Conversations Hook
import { useState, useEffect, useCallback } from 'react'
import { useAuroraAPI } from './useAuroraAPI'

// Types (inline to avoid path issues)
export type LeadSegment = "hot" | "warm" | "cold" | "spam"
export type ContactChannel = "telegram" | "whatsapp" | "voice"

export interface Lead {
  id: string
  businessName: string
  contactName?: string
  telegramUsername?: string
  phone?: string
  sector: string
  city?: string
  source: string
  score: number
  segment: LeadSegment
  status: "new" | "contacting" | "reached" | "warm" | "hot" | "closed_won" | "closed_lost"
  lastMessagePreview?: string
  lastContactAt?: string
  lastContactChannel?: ContactChannel
  priority: "low" | "medium" | "high"
  risk: "low" | "medium" | "high"
  monthlyMsgVolumeEst?: string
}

export interface Message {
  id: string
  from: "user" | "ai" | "system" | "human_agent"
  text: string
  createdAt: string
  meta?: {
    action?: "reply_only" | "tool_call" | "handoff"
    toolName?: string
    toolPayloadSummary?: string
  }
}

export interface Conversation {
  id: string
  leadId: string
  title: string
  channel: ContactChannel
  unreadCount: number
  lastMessageAt: string
  segment: LeadSegment
  score: number
  status: Lead["status"]
  messages: Message[]
}

export interface HandoffEvent {
  id: string
  at: string
  from: "ai" | "human_agent"
  to: "ai" | "human_agent"
  reason: string
  note?: string
}

export function useTelegramConversations(segment?: string) {
  const { fetchAPI } = useAuroraAPI()
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let mounted = true
    
    const loadConversations = async () => {
      if (!mounted) return
      setIsLoading(true)
      setError(null)
      
      try {
        const params = segment ? `?segment=${segment}` : ''
        const { data, error: apiError } = await fetchAPI<Conversation[]>(
          `/admin/telegram/conversations${params}`
        )
        
        if (!mounted) return
        
        if (apiError) {
          setError(apiError.detail || 'Failed to load conversations')
          setConversations([])
        } else {
          setConversations(data || [])
        }
      } catch (err) {
        if (!mounted) return
        setError(err instanceof Error ? err.message : 'Unknown error')
        setConversations([])
      } finally {
        if (mounted) {
          setIsLoading(false)
        }
      }
    }

    loadConversations()
    // Auto-refresh every 30 seconds
    const interval = setInterval(loadConversations, 30000)
    
    return () => {
      mounted = false
      clearInterval(interval)
    }
  }, [segment, fetchAPI])

  const refetch = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      const params = segment ? `?segment=${segment}` : ''
      const { data, error: apiError } = await fetchAPI<Conversation[]>(
        `/admin/telegram/conversations${params}`
      )
      
      if (apiError) {
        setError(apiError.detail || 'Failed to load conversations')
        setConversations([])
      } else {
        setConversations(data || [])
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
      setConversations([])
    } finally {
      setIsLoading(false)
    }
  }, [segment, fetchAPI])

  return { conversations, isLoading, error, refetch }
}

export function useTelegramConversation(conversationId: string | null) {
  const { fetchAPI } = useAuroraAPI()
  const [conversation, setConversation] = useState<Conversation | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let mounted = true
    
    if (!conversationId) {
      setConversation(null)
      setIsLoading(false)
      return
    }

    const loadConversation = async () => {
      if (!mounted) return
      setIsLoading(true)
      setError(null)
      
      try {
        const { data, error: apiError } = await fetchAPI<Conversation>(
          `/admin/telegram/conversations/${conversationId}`
        )
        
        if (!mounted) return
        
        if (apiError) {
          setError(apiError.detail || 'Failed to load conversation')
          setConversation(null)
        } else {
          setConversation(data)
        }
      } catch (err) {
        if (!mounted) return
        setError(err instanceof Error ? err.message : 'Unknown error')
        setConversation(null)
      } finally {
        if (mounted) {
          setIsLoading(false)
        }
      }
    }

    loadConversation()
    
    return () => {
      mounted = false
    }
  }, [conversationId, fetchAPI])

  return { conversation, isLoading, error }
}

export function useTelegramLead(leadId: string | null) {
  const { fetchAPI } = useAuroraAPI()
  const [lead, setLead] = useState<Lead | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let mounted = true
    
    if (!leadId) {
      setLead(null)
      setIsLoading(false)
      return
    }

    const loadLead = async () => {
      if (!mounted) return
      setIsLoading(true)
      setError(null)
      
      try {
        const { data, error: apiError } = await fetchAPI<Lead>(
          `/admin/telegram/leads/${leadId}`
        )
        
        if (!mounted) return
        
        if (apiError) {
          setError(apiError.detail || 'Failed to load lead')
          setLead(null)
        } else {
          setLead(data)
        }
      } catch (err) {
        if (!mounted) return
        setError(err instanceof Error ? err.message : 'Unknown error')
        setLead(null)
      } finally {
        if (mounted) {
          setIsLoading(false)
        }
      }
    }

    loadLead()
    
    return () => {
      mounted = false
    }
  }, [leadId, fetchAPI])

  return { lead, isLoading, error }
}

export function useTelegramStats() {
  const { fetchAPI } = useAuroraAPI()
  const [stats, setStats] = useState<{
    totalCallsToday: number
    hotCount: number
    warmCount: number
    coldCount: number
  } | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let mounted = true
    
    const loadStats = async () => {
      if (!mounted) return
      setIsLoading(true)
      setError(null)
      
      try {
        const { data, error: apiError } = await fetchAPI<typeof stats>(
          `/admin/telegram/stats`
        )
        
        if (!mounted) return
        
        if (apiError) {
          setError(apiError.detail || 'Failed to load stats')
          setStats(null)
        } else {
          setStats(data)
        }
      } catch (err) {
        if (!mounted) return
        setError(err instanceof Error ? err.message : 'Unknown error')
        setStats(null)
      } finally {
        if (mounted) {
          setIsLoading(false)
        }
      }
    }

    loadStats()
    // Auto-refresh every 60 seconds
    const interval = setInterval(loadStats, 60000)
    
    return () => {
      mounted = false
      clearInterval(interval)
    }
  }, [fetchAPI])

  const refetch = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      const { data, error: apiError } = await fetchAPI<typeof stats>(
        `/admin/telegram/stats`
      )
      
      if (apiError) {
        setError(apiError.detail || 'Failed to load stats')
        setStats(null)
      } else {
        setStats(data)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
      setStats(null)
    } finally {
      setIsLoading(false)
    }
  }, [fetchAPI])

  return { stats, isLoading, error, refetch }
}

