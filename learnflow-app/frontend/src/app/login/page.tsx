'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { useAuthStore } from '@/hooks/useAuth'
import { GraduationCap, Eye, EyeOff, ArrowRight, Sparkles, Zap } from 'lucide-react'
import Link from 'next/link'

export default function LoginPage() {
  const router = useRouter()
  const { login, loading, error, clearError } = useAuthStore()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})

  function validate() {
    const e: Record<string, string> = {}
    if (!email) e.email = 'Email is required'
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) e.email = 'Invalid email format'
    if (!password) e.password = 'Password is required'
    else if (password.length < 8) e.password = 'Password must be at least 8 characters'
    setErrors(e)
    return Object.keys(e).length === 0
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    clearError()
    if (!validate()) return
    try { await login(email, password); router.push('/dashboard') } catch {}
  }

  return (
    <div className="relative flex min-h-screen overflow-hidden bg-background">
      {/* Animated background */}
      <div className="absolute inset-0 bg-dot opacity-30" />
      <div className="absolute inset-0 bg-gradient-to-br from-blue-600/20 via-purple-600/10 to-background" />
      <motion.div className="absolute -top-40 -left-40 h-[500px] w-[500px] rounded-full bg-gradient-to-r from-blue-500/20 to-transparent blur-[120px]"
        animate={{ x: [0, 30, 0], y: [0, -20, 0] }} transition={{ duration: 8, repeat: Infinity }} />
      <motion.div className="absolute -bottom-40 -right-40 h-[500px] w-[500px] rounded-full bg-gradient-to-l from-purple-500/20 to-transparent blur-[120px]"
        animate={{ x: [0, -30, 0], y: [0, 20, 0] }} transition={{ duration: 8, repeat: Infinity }} />

      <div className="relative z-10 m-auto flex w-full max-w-[1100px] items-center">
        {/* Left panel - brand */}
        <motion.div initial={{ opacity: 0, x: -30 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.6 }}
          className="hidden lg:flex flex-1 flex-col items-center justify-center p-12 text-center">
          <div className="mx-auto mb-8 flex h-24 w-24 items-center justify-center rounded-3xl bg-gradient-to-br from-blue-600 to-purple-600 shadow-2xl shadow-blue-500/30">
            <GraduationCap className="h-12 w-12 text-white" />
          </div>
          <h2 className="text-4xl font-bold mb-4">
            Welcome to <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">LearnFlow</span>
          </h2>
          <p className="text-muted-foreground max-w-sm mb-8">Continue your Python learning journey with AI-powered guidance.</p>
          <div className="space-y-4 text-left">
            {[
              { icon: Zap, text: 'AI-powered code reviews' },
              { icon: Sparkles, text: 'Personalized learning paths' },
              { icon: GraduationCap, text: 'Interactive exercises' },
            ].map(({ icon: Icon, text }) => (
              <div key={text} className="flex items-center gap-3">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500/20 to-purple-500/20">
                  <Icon className="h-4 w-4 text-blue-500" />
                </div>
                <span className="text-sm">{text}</span>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Right panel - form */}
        <motion.div initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.6, delay: 0.1 }}
          className="w-full max-w-md mx-auto px-4 lg:px-8">
          <div className="relative overflow-hidden rounded-3xl border border-white/30 bg-gradient-to-br from-white/90 to-white/70 dark:from-white/10 dark:to-white/[0.05] backdrop-blur-2xl p-8 shadow-2xl">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 via-transparent to-purple-500/5" />
            <div className="relative">
              <div className="text-center mb-8 lg:hidden">
                <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-600 to-purple-600 shadow-lg">
                  <GraduationCap className="h-8 w-8 text-white" />
                </div>
              </div>

              <div className="mb-8 text-center">
                <div className="mb-2 inline-flex items-center gap-1.5 rounded-full border border-blue-500/20 bg-gradient-to-r from-blue-500/10 to-purple-500/10 px-3 py-1 text-xs">
                  <Sparkles className="h-3 w-3 text-blue-500" />
                  <span className="bg-gradient-to-r from-blue-500 to-purple-500 bg-clip-text text-transparent font-medium">Welcome back</span>
                </div>
                <h1 className="text-3xl font-bold">Sign in</h1>
                <p className="text-muted-foreground mt-2">Continue your learning journey</p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                {error && (
                  <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }}
                    className="p-3 rounded-xl bg-red-50 dark:bg-red-500/10 border border-red-500/20 text-red-600 text-sm">
                    {error}
                  </motion.div>
                )}

                <div className="space-y-1.5">
                  <label htmlFor="email" className="text-sm font-medium">Email</label>
                  <input id="email" type="email" placeholder="you@example.com" value={email}
                    onChange={e => { setEmail(e.target.value); clearError() }}
                    className="flex h-11 w-full rounded-xl border border-input bg-background/50 px-4 text-sm transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/50 focus-visible:border-blue-500/50 placeholder:text-muted-foreground" />
                  {errors.email && <p className="text-xs text-red-500">{errors.email}</p>}
                </div>

                <div className="space-y-1.5">
                  <label htmlFor="password" className="text-sm font-medium">Password</label>
                  <div className="relative">
                    <input id="password" type={showPassword ? 'text' : 'password'} placeholder="Enter your password" value={password}
                      onChange={e => { setPassword(e.target.value); clearError() }}
                      className="flex h-11 w-full rounded-xl border border-input bg-background/50 px-4 pr-11 text-sm transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/50 focus-visible:border-blue-500/50 placeholder:text-muted-foreground" />
                    <button type="button" onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors">
                      {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                  {errors.password && <p className="text-xs text-red-500">{errors.password}</p>}
                </div>

                <div className="flex items-center justify-between">
                  <label className="flex items-center gap-2 text-sm text-muted-foreground">
                    <input type="checkbox" className="rounded" /> Remember me
                  </label>
                </div>

                <button type="submit" disabled={loading}
                  className="group relative flex h-12 w-full items-center justify-center overflow-hidden rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 text-sm font-semibold text-white shadow-lg shadow-blue-500/25 transition-all duration-300 hover:shadow-blue-500/40 hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50">
                  <span className="absolute inset-0 bg-[linear-gradient(45deg,transparent_25%,rgba(255,255,255,0.2)_50%,transparent_75%)] bg-[length:250%_250%] transition-all duration-700 group-hover:bg-[position:100%_0]" />
                  <span className="relative flex items-center gap-2">
                    {loading ? (
                      <svg className="h-5 w-5 animate-spin" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg>
                    ) : (
                      <>Sign In <ArrowRight className="h-4 w-4" /></>
                    )}
                  </span>
                </button>
              </form>

              <p className="text-center text-sm text-muted-foreground mt-6">
                Don&apos;t have an account?{' '}
                <Link href="/register" className="text-blue-500 hover:underline font-medium">Create one</Link>
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
