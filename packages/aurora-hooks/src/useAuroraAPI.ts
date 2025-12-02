// Base API client hook
import { useCallback } from 'react'

// Token management (client-side only)
const getToken = (): string | null => {
  if (typeof window === 'undefined') return null
  try {
    return localStorage.getItem('aurora_token')
  } catch {
    return null
  }
}

// Support both Vite (import.meta.env) and Next.js (process.env)
const getAPIBaseURL = () => {
  if (typeof window !== 'undefined') {
    // Client-side: Next.js
    return (
      (window as any).__NEXT_DATA__?.env?.NEXT_PUBLIC_AURORA_API_URL ||
      process.env.NEXT_PUBLIC_AURORA_API_URL ||
      'http://localhost:8000/api/v1'
    )
  }
  // Server-side or Vite
  return (
    (typeof import.meta !== 'undefined' && (import.meta as any).env?.VITE_AURORA_API_URL) ||
    'http://localhost:8000/api/v1'
  )
}

const API_BASE_URL = getAPIBaseURL()

interface APIError {
  error: string
  detail: string
  regime?: string
  action?: string
}

export function useAuroraAPI() {
  const fetchAPI = useCallback(
    async <T>(
      endpoint: string,
      options: RequestInit = {}
    ): Promise<{ data: T | null; error: APIError | null }> => {
      try {
        // Get token from localStorage (client-side only)
        const token = getToken()

        const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint}`
        const response = await fetch(url, {
          ...options,
          headers: {
            'Content-Type': 'application/json',
            ...(token && { Authorization: `Bearer ${token}` }),
            ...options.headers,
          },
        })

        if (!response.ok) {
          // Try to parse error response, but handle empty responses
          let errorData: any = { error: 'Unknown error' }
          const contentType = response.headers.get('content-type')
          if (contentType && contentType.includes('application/json')) {
            try {
              const text = await response.text()
              if (text) {
                errorData = JSON.parse(text)
              }
            } catch {
              // If JSON parse fails, use default error
            }
          }
          return { data: null, error: errorData }
        }

        // Check if response has content
        const contentType = response.headers.get('content-type')
        const contentLength = response.headers.get('content-length')
        
        // Handle 204 No Content or empty responses
        if (response.status === 204 || (contentLength === '0' && !contentType?.includes('json'))) {
          return { data: null, error: null }
        }

        // Try to parse JSON response
        try {
          const text = await response.text()
          if (!text) {
            return { data: null, error: null }
          }
          const data = JSON.parse(text)
          return { data, error: null }
        } catch (parseError) {
          return {
            data: null,
            error: {
              error: 'PARSE_ERROR',
              detail: parseError instanceof Error ? parseError.message : 'Failed to parse response',
            },
          }
        }
      } catch (error) {
        return {
          data: null,
          error: {
            error: 'NETWORK_ERROR',
            detail: error instanceof Error ? error.message : 'Network request failed',
          },
        }
      }
    },
    []
  )

  return { fetchAPI }
}

