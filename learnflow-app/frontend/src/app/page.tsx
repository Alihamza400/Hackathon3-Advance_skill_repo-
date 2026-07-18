'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { motion, useScroll, useTransform } from 'framer-motion'
import { ArrowRight, Sparkles, GraduationCap, Brain, Code, Zap, Shield, BarChart3, Star, ChevronRight, Bot, Rocket, Users, CheckCircle, Play, Award } from 'lucide-react'

function GradientText({ children }: { children: React.ReactNode }) {
  return <span className="bg-gradient-to-r from-blue-600 via-primary to-purple-600 dark:from-blue-400 dark:via-primary dark:to-purple-400 bg-clip-text text-transparent">{children}</span>
}

const features = [
  { icon: Brain, title: 'AI-Powered Tutoring', description: 'Get personalized explanations from AI that adapts to your learning style in real-time.', gradient: 'from-blue-500/20 to-blue-500/5', iconGradient: 'from-blue-500 to-blue-400' },
  { icon: Bot, title: 'Smart Code Review', description: 'Instant AI code reviews with detailed suggestions for improvement and best practices.', gradient: 'from-purple-500/20 to-purple-500/5', iconGradient: 'from-purple-500 to-purple-400' },
  { icon: Zap, title: 'Real-time Execution', description: 'Write, run, and debug Python code instantly in a secure sandboxed environment.', gradient: 'from-amber-500/20 to-amber-500/5', iconGradient: 'from-amber-500 to-amber-400' },
  { icon: Star, title: 'Smart Exercises', description: 'Auto-generated coding challenges tailored to your current skill level and learning goals.', gradient: 'from-emerald-500/20 to-emerald-500/5', iconGradient: 'from-emerald-500 to-emerald-400' },
  { icon: BarChart3, title: 'Progress Analytics', description: 'Track your mastery with detailed insights, streak tracking, and personalized recommendations.', gradient: 'from-rose-500/20 to-rose-500/5', iconGradient: 'from-rose-500 to-rose-400' },
  { icon: Shield, title: 'Secure Sandbox', description: 'Enterprise-grade code isolation with resource limits for safe, risk-free learning.', gradient: 'from-cyan-500/20 to-cyan-500/5', iconGradient: 'from-cyan-500 to-cyan-400' },
]

const stats = [
  { value: '9', suffix: '+', label: 'AI Microservices', icon: Bot },
  { value: '1000', suffix: '+', label: 'Topics Covered', icon: BookOpenIcon },
  { value: '99.9', suffix: '%', label: 'Uptime', icon: Zap },
  { value: '24/7', suffix: '', label: 'AI Support', icon: Users },
]

function BookOpenIcon(props: any) { return <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg> }

export default function LandingPage() {
  const { scrollYProgress } = useScroll()
  const heroOpacity = useTransform(scrollYProgress, [0, 0.3], [1, 0])
  const heroScale = useTransform(scrollYProgress, [0, 0.3], [1, 0.95])
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 })

  useEffect(() => {
    const handleMouse = (e: MouseEvent) => setMousePos({ x: e.clientX, y: e.clientY })
    window.addEventListener('mousemove', handleMouse)
    return () => window.removeEventListener('mousemove', handleMouse)
  }, [])

  return (
    <div className="min-h-screen overflow-hidden bg-background">
      {/* Animated background */}
      <div className="fixed inset-0 z-0">
        <div className="absolute inset-0 bg-dot opacity-40" />
        <div className="absolute inset-0 bg-radial-gradient" />
        <motion.div
          className="absolute h-[500px] w-[500px] rounded-full bg-gradient-to-r from-blue-500/10 to-purple-500/10 blur-[100px]"
          animate={{ x: mousePos.x * 0.05, y: mousePos.y * 0.05 }}
          transition={{ type: 'spring', stiffness: 50 }}
        />
        <motion.div
          className="absolute right-0 top-1/3 h-[400px] w-[400px] rounded-full bg-gradient-to-r from-amber-500/10 to-rose-500/10 blur-[100px]"
          animate={{ x: mousePos.x * -0.03, y: mousePos.y * -0.03 }}
          transition={{ type: 'spring', stiffness: 50 }}
        />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-background/50 to-background pointer-events-none" />
      </div>

      {/* Nav */}
      <motion.header initial={{ y: -20, opacity: 0 }} animate={{ y: 0, opacity: 1 }}
        className="fixed top-0 z-50 w-full border-b border-white/10 bg-background/70 backdrop-blur-2xl">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6">
          <Link href="/" className="group flex items-center gap-2.5">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-blue-600 to-purple-600 shadow-lg shadow-blue-500/25 transition-all duration-500 group-hover:scale-110 group-hover:shadow-blue-500/40">
              <GraduationCap className="h-5 w-5 text-white" />
            </div>
            <span className="text-xl font-bold">
              Learn<span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">Flow</span>
            </span>
          </Link>
          <div className="flex items-center gap-4">
            <Link href="/login" className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground">Sign In</Link>
            <Link href="/register">
              <button className="group relative inline-flex h-10 items-center justify-center overflow-hidden rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 px-5 text-sm font-medium text-white shadow-lg shadow-blue-500/25 transition-all duration-300 hover:shadow-blue-500/40 hover:scale-105">
                <span className="absolute inset-0 bg-[linear-gradient(45deg,transparent_25%,rgba(255,255,255,0.2)_50%,transparent_75%)] bg-[length:250%_250%] transition-all duration-700 group-hover:bg-[position:100%_0]" />
                <span className="relative flex items-center gap-1.5">Get Started <ArrowRight className="h-3.5 w-3.5" /></span>
              </button>
            </Link>
          </div>
        </div>
      </motion.header>

      {/* Hero */}
      <motion.section style={{ opacity: heroOpacity, scale: heroScale }}
        className="relative z-10 flex min-h-screen items-center justify-center overflow-hidden pt-20">
        <div className="mx-auto max-w-6xl px-4 py-20 text-center sm:px-6">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
            className="mb-6 inline-flex items-center gap-2 rounded-full border border-blue-500/20 bg-gradient-to-r from-blue-500/10 to-purple-500/10 px-4 py-1.5 text-sm">
            <Sparkles className="h-4 w-4 text-blue-500" />
            <span className="bg-gradient-to-r from-blue-500 to-purple-500 bg-clip-text text-transparent font-medium">AI-Powered Python Learning Platform</span>
          </motion.div>

          <motion.h1 initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
            className="text-5xl font-extrabold tracking-tight sm:text-7xl lg:text-8xl leading-[1.1]">
            Master Python with
            <span className="mt-3 block">
              <GradientText>AI-Powered Learning</GradientText>
            </span>
          </motion.h1>

          <motion.p initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}
            className="mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-muted-foreground">
            LearnFlow combines <span className="text-foreground font-semibold">intelligent AI tutoring</span>,{' '}
            <span className="text-foreground font-semibold">real-time code analysis</span>, and{' '}
            <span className="text-foreground font-semibold">personalized practice</span> to help you master Python programming faster.
          </motion.p>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}
            className="mt-10 flex items-center justify-center gap-4 flex-wrap">
            <Link href="/register">
              <button className="group relative inline-flex h-14 items-center justify-center overflow-hidden rounded-2xl bg-gradient-to-r from-blue-600 via-primary to-purple-600 px-8 text-base font-semibold text-white shadow-2xl shadow-blue-500/30 transition-all duration-300 hover:shadow-blue-500/50 hover:scale-105 active:scale-95">
                <span className="absolute inset-0 bg-[linear-gradient(45deg,transparent_25%,rgba(255,255,255,0.2)_50%,transparent_75%)] bg-[length:250%_250%] transition-all duration-700 group-hover:bg-[position:100%_0]" />
                <span className="relative flex items-center gap-2">Start Learning Free <Rocket className="h-5 w-5" /></span>
              </button>
            </Link>
            <Link href="/login">
              <button className="group inline-flex h-14 items-center justify-center rounded-2xl border border-border bg-background/60 px-8 text-base font-medium text-foreground backdrop-blur-sm transition-all duration-300 hover:border-blue-500/30 hover:shadow-[0_0_30px_hsl(var(--primary)/0.15)]">
                Sign In <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
              </button>
            </Link>
          </motion.div>

          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.7 }}
            className="mt-16 flex items-center justify-center gap-8 text-sm">
            {[{ icon: Brain, label: 'AI-Powered' }, { icon: Code, label: 'Interactive Editor' }, { icon: Shield, label: 'Safe Sandbox' }, { icon: Zap, label: 'Real-time Feedback' }].map(({ icon: Icon, label }) => (
              <div key={label} className="flex items-center gap-2 text-muted-foreground">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500/20 to-purple-500/10">
                  <Icon className="h-4 w-4 text-blue-500" />
                </div>
                <span className="hidden sm:inline">{label}</span>
              </div>
            ))}
          </motion.div>

          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.2 }}
            className="absolute bottom-8 left-1/2 -translate-x-1/2">
            <motion.div animate={{ y: [0, 8, 0] }} transition={{ duration: 2, repeat: Infinity }}>
              <ChevronRight className="h-5 w-5 rotate-90 text-muted-foreground/50" />
            </motion.div>
          </motion.div>
        </div>
      </motion.section>

      {/* Stats */}
      <section className="relative z-10 border-y border-white/10 py-16">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 via-transparent to-purple-500/5" />
        <div className="relative mx-auto max-w-7xl px-4">
          <div className="grid grid-cols-2 gap-6 md:grid-cols-4">
            {stats.map((s, i) => (
              <motion.div key={s.label} initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }} transition={{ delay: i * 0.1 }}
                className="group relative overflow-hidden rounded-2xl border border-white/20 bg-gradient-to-br from-white/80 to-white/40 dark:from-white/5 dark:to-white/[0.02] backdrop-blur-xl p-6 text-center transition-all duration-500 hover:shadow-2xl hover:-translate-y-1">
                <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 via-transparent to-purple-500/10 opacity-0 transition-opacity duration-500 group-hover:opacity-100" />
                <div className="relative">
                  <s.icon className="h-6 w-6 mx-auto mb-3 text-blue-500" />
                  <div className="text-3xl font-bold tracking-tight md:text-4xl bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                    {s.value}{s.suffix}
                  </div>
                  <p className="mt-1 text-sm text-muted-foreground">{s.label}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="relative z-10 py-24" id="features">
        <div className="mx-auto max-w-7xl px-4">
          <motion.div initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
            className="text-center">
            <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-blue-500/20 bg-gradient-to-r from-blue-500/10 to-purple-500/10 px-4 py-1.5 text-sm">
              <Sparkles className="h-4 w-4 text-blue-500" />
              <span className="bg-gradient-to-r from-blue-500 to-purple-500 bg-clip-text text-transparent font-medium">Features</span>
            </div>
            <h2 className="text-4xl font-bold sm:text-5xl">Everything you need to <GradientText>master Python</GradientText></h2>
            <p className="mt-4 text-lg text-muted-foreground">Powerful features designed for effective, engaging learning</p>
          </motion.div>

          <div className="mt-16 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {features.map((f, i) => {
              const Icon = f.icon
              return (
                <motion.div key={f.title} initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }} transition={{ duration: 0.5, delay: i * 0.1 }}
                  className="group relative overflow-hidden rounded-2xl border border-white/20 bg-gradient-to-br from-white/80 to-white/40 dark:from-white/5 dark:to-white/[0.02] backdrop-blur-xl p-6 transition-all duration-500 hover:shadow-2xl hover:-translate-y-1"
                  style={{ boxShadow: '0 0 0px hsl(var(--primary)/0)' }}>
                  <div className={`absolute inset-0 bg-gradient-to-br ${f.gradient} opacity-0 transition-opacity duration-500 group-hover:opacity-100`} />
                  <div className="relative z-10">
                    <div className={`mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br ${f.iconGradient} shadow-lg transition-all duration-500 group-hover:scale-110 group-hover:shadow-xl`}>
                      <Icon className="h-6 w-6 text-white" />
                    </div>
                    <h3 className="mb-2 text-lg font-semibold">{f.title}</h3>
                    <p className="text-sm leading-relaxed text-muted-foreground">{f.description}</p>
                  </div>
                  <div className="absolute -bottom-6 -right-6 h-20 w-20 rounded-full bg-gradient-to-r from-blue-500/20 to-purple-500/20 blur-2xl transition-all duration-500 group-hover:scale-150" />
                </motion.div>
              )
            })}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="relative z-10 py-24">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 via-transparent to-purple-500/5" />
        <div className="relative mx-auto max-w-7xl px-4">
          <motion.div initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
            className="text-center mb-16">
            <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-emerald-500/20 bg-gradient-to-r from-emerald-500/10 to-cyan-500/10 px-4 py-1.5 text-sm">
              <Play className="h-4 w-4 text-emerald-500" />
              <span className="bg-gradient-to-r from-emerald-500 to-cyan-500 bg-clip-text text-transparent font-medium">How It Works</span>
            </div>
            <h2 className="text-4xl font-bold sm:text-5xl">Start learning in <GradientText>3 simple steps</GradientText></h2>
          </motion.div>

          <div className="grid gap-8 md:grid-cols-3">
            {[
              { step: '01', title: 'Create Account', desc: 'Sign up free and set your learning goals. No credit card required.', icon: Users, gradient: 'from-blue-500 to-blue-400' },
              { step: '02', title: 'Learn & Practice', desc: 'Chat with AI tutors, solve exercises, and get instant code reviews.', icon: Code, gradient: 'from-purple-500 to-purple-400' },
              { step: '03', title: 'Track Progress', desc: 'Monitor your mastery, earn streaks, and get personalized recommendations.', icon: Award, gradient: 'from-emerald-500 to-emerald-400' },
            ].map((s, i) => (
              <motion.div key={s.step} initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }} transition={{ delay: i * 0.15 }}
                className="relative text-center">
                <div className={`mx-auto flex h-20 w-20 items-center justify-center rounded-2xl bg-gradient-to-br ${s.gradient} shadow-xl mb-6`}>
                  <s.icon className="h-9 w-9 text-white" />
                </div>
                <div className="absolute -top-2 -right-2 text-6xl font-black text-muted-foreground/5 md:-right-8">{s.step}</div>
                <h3 className="text-xl font-semibold mb-2">{s.title}</h3>
                <p className="text-muted-foreground">{s.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="relative z-10 overflow-hidden py-24">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-600/10 via-purple-600/10 to-pink-600/10" />
        <div className="absolute inset-0 bg-grid-subtle opacity-30" />
        <motion.div className="absolute left-1/2 top-1/2 h-[600px] w-[600px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-gradient-to-r from-blue-500/20 to-purple-500/20 blur-[120px]" />
        
        <div className="relative z-10 mx-auto max-w-3xl px-4 text-center">
          <motion.div initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
            className="relative overflow-hidden rounded-3xl border border-white/30 bg-gradient-to-br from-white/90 to-white/70 dark:from-white/10 dark:to-white/[0.05] backdrop-blur-2xl px-8 py-16 sm:px-16 shadow-2xl">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 via-transparent to-purple-500/10" />
            <div className="relative">
              <div className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-600 to-purple-600 shadow-xl shadow-blue-500/30">
                <GraduationCap className="h-10 w-10 text-white" />
              </div>
              <h2 className="text-4xl font-bold sm:text-5xl">Ready to <GradientText>master Python</GradientText>?</h2>
              <p className="mx-auto mt-4 max-w-lg text-lg text-muted-foreground">
                Join thousands of learners mastering Python with AI-powered guidance. Start your journey today.
              </p>
              <div className="mt-10 flex items-center justify-center gap-4 flex-wrap">
                <Link href="/register">
                  <button className="group relative inline-flex h-14 items-center justify-center overflow-hidden rounded-2xl bg-gradient-to-r from-blue-600 via-primary to-purple-600 px-8 text-base font-semibold text-white shadow-2xl shadow-blue-500/30 transition-all duration-300 hover:shadow-blue-500/50 hover:scale-105 active:scale-95">
                    <span className="absolute inset-0 bg-[linear-gradient(45deg,transparent_25%,rgba(255,255,255,0.2)_50%,transparent_75%)] bg-[length:250%_250%] transition-all duration-700 group-hover:bg-[position:100%_0]" />
                    <span className="relative flex items-center gap-2">Get Started Free <Rocket className="h-5 w-5" /></span>
                  </button>
                </Link>
                <Link href="/login">
                  <button className="inline-flex h-14 items-center justify-center rounded-2xl border border-border bg-background/60 px-8 text-base font-medium text-foreground backdrop-blur-sm transition-all duration-300 hover:border-blue-500/30">
                    Sign In <ArrowRight className="ml-2 h-4 w-4" />
                  </button>
                </Link>
              </div>
              <div className="mt-8 flex items-center justify-center gap-6 text-sm text-muted-foreground">
                <span className="flex items-center gap-1.5"><CheckCircle className="h-4 w-4 text-emerald-500" /> Free to start</span>
                <span className="flex items-center gap-1.5"><CheckCircle className="h-4 w-4 text-emerald-500" /> No credit card</span>
                <span className="flex items-center gap-1.5"><CheckCircle className="h-4 w-4 text-emerald-500" /> Cancel anytime</span>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t py-8">
        <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 px-4 sm:flex-row">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-600 to-purple-600">
              <GraduationCap className="h-4 w-4 text-white" />
            </div>
            <span className="text-sm font-semibold">LearnFlow</span>
          </div>
          <p className="text-sm text-muted-foreground">AI-Powered Python Learning Platform</p>
        </div>
      </footer>
    </div>
  )
}
