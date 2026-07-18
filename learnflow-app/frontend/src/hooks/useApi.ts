'use client'

import { useState, useCallback } from 'react'
import { api } from '@/lib/api'

interface UseApiState<T> {
  data: T | null
  loading: boolean
  error: string | null
}

export function useApi<T>(fetcher: () => Promise<T>) {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: true,
    error: null,
  })

  const execute = useCallback(async () => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }))
      const data = await fetcher()
      setState({ data, loading: false, error: null })
      return data
    } catch (e: unknown) {
      const message = e instanceof Error ? e.message : 'Request failed'
      setState(prev => ({ ...prev, loading: false, error: message }))
      return null
    }
  }, [fetcher])

  return { ...state, execute, refetch: execute }
}

export { api }
