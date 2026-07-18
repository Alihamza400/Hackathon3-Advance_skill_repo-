'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { useAuthStore } from '@/hooks/useAuth'
import { GraduationCap, ArrowRight, Sparkles, CheckCircle, Rocket } from 'lucide-react'
import Link from 'next/link'

export default function RegisterPage() {
  const router = useRouter()
  const { register, loading, error, clearError } = useAuthStore()
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [errors, setErrors] = useState<Record<string, string>>({})

  function validate() {
    const e: Record<string, string> = {}
    if (!fullName.trim()) e.fullName = 'Full name is required'
    if (!email) e.email = 'Email is required'
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) e.email = 'Invalid email format'
    if (!password) e.password = 'Password is required'
    else if (password.length < 8) e.password = 'At least 8 characters'
    if (password !== confirmPassword) e.confirmPassword = 'Passwords do not match'
    setErrors(e)
    return Object.keys(e).length === 0
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    clearError()
    if (!validate()) return
    try { await register(fullName, email, password); router.push('/login?registered=true') } catch {}
  }

  return (
    <div className="relative flex min-h-screen overflow-hidden bg-background">
      <div className="absolute inset-0 bg-dot opacity-30" />
      <div className="absolute inset-0 bg-gradient-to-br from-emerald-600/20 via-blue-600/10 to-background" />
      <motion.div className="absolute -top-40 -right-40 h-[500px] w-[500px] rounded-full bg-gradient-to-l from-emerald-500/20 to-transparent blur-[120px]"
        animate={{ x: [0, -30, 0], y: [0, 20, 0] }} transition={{ duration: 8, repeat: Infinity }} />
      <motion.div className="absolute -bottom-40 -left-40 h-[500px] w-[500px] rounded-full bg-gradient-to-r from-blue-500/20 to-transparent blur-[120px]"
        animate={{ x: [0, 30, 0], y: [0, -20, 0] }} transition={{ duration: 8, repeat: Infinity }} />

      <div className="relative z-10 m-auto flex w-full max-w-[1100px] items-center">
        <motion.div initial={{ opacity: 0, x: -30 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.6 }}
          className="hidden lg:flex flex-1 flex-col items-center justify-center p-12 text-center">
          <div className="mx-auto mb-8 flex h-24 w-24 items-center justify-center rounded-3xl bg-gradient-to-br from-emerald-500 to-blue-600 shadow-2xl shadow-emerald-500/30">
            <Rocket className="h-12 w-12 text-white" />
          </div>
          <h2 className="text-4xl font-bold mb-4">
            Start your <span className="bg-gradient-to-r from-emerald-500 to-blue-600 bg-clip-text text-transparent">journey</span>
          </h2>
          <p className="text-muted-foreground max-w-sm mb-8">Join thousands of learners mastering Python with AI.</p>
          <div className="space-y-4 text-left">
            {[
              { text: 'Free AI-powered tutoring' }, { text: 'Personalized learning path' }, { text: 'No credit card required' },
            ].map(({ text }) => (
              <div key={text} className="flex items-center gap-3">
                <CheckCircle className="h-5 w-5 text-emerald-500" />
                <span className="text-sm">{text}</span>
              </div>
            ))}
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.6, delay: 0.1 }}
          className="w-full max-w-md mx-auto px-4 lg:px-8">
          <div className="relative overflow-hidden rounded-3xl border border-white/30 bg-gradient-to-br from-white/90 to-white/70 dark:from-white/10 dark:to-white/[0.05] backdrop-blur-2xl p-8 shadow-2xl">
            <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 via-transparent to-blue-500/5" />
            <div className="relative">
              <div className="text-center mb-6 lg:hidden">
                <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-emerald-500 to-blue-600 shadow-lg">
                  <GraduationCap className="h-8 w-8 text-white" />
                </div>
              </div>

              <div className="mb-6 text-center">
                <div className="mb-2 inline-flex items-center gap-1.5 rounded-full border border-emerald-500/20 bg-gradient-to-r from-emerald-500/10 to-blue-500/10 px-3 py-1 text-xs">
                  <Sparkles className="h-3 w-3 text-emerald-500" />
                  <span className="bg-gradient-to-r from-emerald-500 to-blue-500 bg-clip-text text-transparent font-medium">New account</span>
                </div>
                <h1 className="text-3xl font-bold">Create account</h1>
                <p className="text-muted-foreground mt-2">Start your learning journey</p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-3.5">
                {error && (
                  <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }}
                    className="p-3 rounded-xl bg-red-50 dark:bg-red-500/10 border border-red-500/20 text-red-600 text-sm">{error}</motion.div>
                )}

                {[
                  { id: 'fullName', label: 'Full Name', type: 'text', placeholder: 'John Doe', autoComplete: 'name', value: fullName, set: setFullName },
                  { id: 'email', label: 'Email', type: 'email', placeholder: 'you@example.com', autoComplete: 'email', value: email, set: setEmail },
                  { id: 'password', label: 'Password', type: 'password', placeholder: 'At least 8 characters', autoComplete: 'new-password', value: password, set: setPassword },
                  { id: 'confirmPassword', label: 'Confirm Password', type: 'password', placeholder: 'Repeat your password', autoComplete: 'new-password', value: confirmPassword, set: setConfirmPassword },
                ].map((f) => (
                  <div key={f.id} className="space-y-1">
                    <label htmlFor={f.id} className="text-sm font-medium">{f.label}</label>
                    <input id={f.id} type={f.type} placeholder={f.placeholder} value={f.value}
                      onChange={e => { f.set(e.target.value); clearError() }} autoComplete={f.autoComplete}
                      className="flex h-11 w-full rounded-xl border border-input bg-background/50 px-4 text-sm transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500/50 focus-visible:border-emerald-500/50 placeholder:text-muted-foreground" />
                    {errors[f.id] && <p className="text-xs text-red-500">{errors[f.id]}</p>}
                  </div>
                ))}

                <button type="submit" disabled={loading}
                  className="group relative flex h-12 w-full items-center justify-center overflow-hidden rounded-xl bg-gradient-to-r from-emerald-500 to-blue-600 text-sm font-semibold text-white shadow-lg shadow-emerald-500/25 transition-all duration-300 hover:shadow-emerald-500/40 hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50">
                  <span className="absolute inset-0 bg-[linear-gradient(45deg,transparent_25%,rgba(255,255,255,0.2)_50%,transparent_75%)] bg-[length:250%_250%] transition-all duration-700 group-hover:bg-[position:100%_0]" />
                  <span className="relative flex items-center gap-2">
                    {loading ? (
                      <svg className="h-5 w-5 animate-spin" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg>
                    ) : (<>Create Account <ArrowRight className="h-4 w-4" /></>)}
                  </span>
                </button>
              </form>

              <p className="text-center text-sm text-muted-foreground mt-6">
                Already have an account?{' '}
                <Link href="/login" className="text-blue-500 hover:underline font-medium">Sign in</Link>
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
