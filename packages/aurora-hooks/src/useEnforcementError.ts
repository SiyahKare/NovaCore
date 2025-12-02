import { useState, useCallback } from 'react'
import type { EnforcementError } from '@aurora/ui'

export function useEnforcementError() {
  const [error, setError] = useState<EnforcementError | null>(null)
  const [isOpen, setIsOpen] = useState(false)

  const handleError = useCallback((err: unknown) => {
    // Check if it's an Aurora enforcement error
    if (
      err &&
      typeof err === 'object' &&
      'error' in err &&
      err.error === 'AURORA_ENFORCEMENT'
    ) {
      setError(err as EnforcementError)
      setIsOpen(true)
      return true
    }
    return false
  }, [])

  const close = useCallback(() => {
    setIsOpen(false)
    setError(null)
  }, [])

  return {
    error,
    isOpen,
    handleError,
    close,
  }
}

