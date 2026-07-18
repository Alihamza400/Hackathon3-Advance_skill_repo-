'use client'

import { create } from 'zustand'
import { api } from '@/lib/api'
import type { User } from '@/types'

interface AuthState {
  user: User | null
  loading: boolean
  error: string | null
  initialized: boolean

  initialize: () => Promise<void>
  login: (email: string, password: string) => Promise<void>
  register: (fullName: string, email: string, password: string, role?: string) => Promise<void>
  logout: () => Promise<void>
  updateProfile: (updates: Partial<User>) => Promise<void>
  clearError: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  loading: false,
  error: null,
  initialized: false,

  initialize: async () => {
    if (!api.isAuthenticated()) {
      set({ initialized: true })
      return
    }

    try {
      set({ loading: true })
      const user = await api.getProfile()
      set({ user, initialized: true, loading: false })
    } catch {
      api.clearTokens()
      set({ user: null, initialized: true, loading: false })
    }
  },

  login: async (email: string, password: string) => {
    try {
      set({ loading: true, error: null })
      const tokens = await api.login(email, password)
      set({ user: tokens.user, loading: false })
    } catch (e: unknown) {
      const message = e instanceof Error ? e.message : 'Login failed'
      set({ error: message, loading: false })
      throw e
    }
  },

  register: async (fullName: string, email: string, password: string, role = 'student') => {
    try {
      set({ loading: true, error: null })
      await api.register(fullName, email, password, role)
      set({ loading: false })
    } catch (e: unknown) {
      const message = e instanceof Error ? e.message : 'Registration failed'
      set({ error: message, loading: false })
      throw e
    }
  },

  logout: async () => {
    try {
      await api.logout()
    } finally {
      set({ user: null })
    }
  },

  updateProfile: async (updates: Partial<User>) => {
    try {
      set({ loading: true })
      const user = await api.updateProfile(updates)
      set({ user, loading: false })
    } catch (e: unknown) {
      const message = e instanceof Error ? e.message : 'Update failed'
      set({ error: message, loading: false })
    }
  },

  clearError: () => set({ error: null }),
}))
