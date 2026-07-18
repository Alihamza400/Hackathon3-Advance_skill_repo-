'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/hooks/useAuth'
import { GlowButton } from '@/components/ui/GlowButton'
import { Input } from '@/components/ui/Input'
import { GraduationCap, Sparkles } from 'lucide-react'

export function RegisterForm() {
  const router = useRouter()
  const { register, loading, error, clearError } = useAuthStore()
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({})

  function validate() {
    const errors: Record<string, string> = {}
    if (!fullName.trim()) errors.fullName = 'Full name is required'
    if (!email) errors.email = 'Email is required'
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) errors.email = 'Invalid email format'
    if (!password) errors.password = 'Password is required'
    else if (password.length < 8) errors.password = 'Password must be at least 8 characters'
    if (password !== confirmPassword) errors.confirmPassword = 'Passwords do not match'
    setValidationErrors(errors)
    return Object.keys(errors).length === 0
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    clearError()
    if (!validate()) return
    try {
      await register(fullName, email, password)
      router.push('/login?registered=true')
    } catch {}
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="w-full max-w-md mx-auto p-8"
    >
      <motion.div
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ type: 'spring', stiffness: 200, delay: 0.1 }}
        className="text-center mb-8"
      >
        <div className="flex justify-center mb-4">
          <div className="h-16 w-16 rounded-2xl bg-gradient-to-br from-primary to-primary/60 shadow-lg flex items-center justify-center">
            <GraduationCap className="h-8 w-8 text-white" />
          </div>
        </div>
        <div className="mb-2 inline-flex items-center gap-1.5 rounded-full border border-primary/20 bg-primary/5 px-3 py-1 text-xs">
          <Sparkles className="h-3 w-3 text-primary" />
          <span>New account</span>
        </div>
        <h1 className="text-3xl font-bold">Create account</h1>
        <p className="text-muted-foreground mt-2">Start your learning journey</p>
      </motion.div>

      <motion.form
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        onSubmit={handleSubmit}
        className="space-y-4"
      >
        {error && (
          <motion.div
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            className="p-3 rounded-lg bg-error-50 dark:bg-error-500/10 border border-error-500/20 text-error-600 text-sm"
          >
            {error}
          </motion.div>
        )}

        <Input id="fullName" label="Full Name" placeholder="John Doe"
          value={fullName} onChange={e => { setFullName(e.target.value); clearError() }}
          error={validationErrors.fullName} autoComplete="name" />
        <Input id="email" label="Email" type="email" placeholder="you@example.com"
          value={email} onChange={e => { setEmail(e.target.value); clearError() }}
          error={validationErrors.email} autoComplete="email" />
        <Input id="password" label="Password" type="password" placeholder="At least 8 characters"
          value={password} onChange={e => { setPassword(e.target.value); clearError() }}
          error={validationErrors.password} autoComplete="new-password" />
        <Input id="confirmPassword" label="Confirm Password" type="password" placeholder="Repeat your password"
          value={confirmPassword} onChange={e => { setConfirmPassword(e.target.value); clearError() }}
          error={validationErrors.confirmPassword} autoComplete="new-password" />

        <GlowButton type="submit" className="w-full" size="lg" loading={loading}>
          Create Account
        </GlowButton>
      </motion.form>

      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
        className="text-center text-sm text-muted-foreground mt-6"
      >
        Already have an account?{' '}
        <a href="/login" className="text-primary hover:underline font-medium">Sign in</a>
      </motion.p>
    </motion.div>
  )
}
