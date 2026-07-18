'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import { GraduationCap, Brain, Code, Zap, Shield, ArrowRight, Star, Users, BarChart3, Sparkles, ChevronRight } from 'lucide-react'
import { GlowButton } from '@/components/ui/GlowButton'
import { Typewriter } from '@/components/ui/Typewriter'
import { AnimatedGrid } from '@/components/ui/AnimatedGrid'
import { Spotlight } from '@/components/ui/Spotlight'
import { FeatureCard } from '@/components/ui/FeatureCard'
import { GlassCard, GlassCardContent } from '@/components/ui/GlassCard'
import { AnimatedCounter } from '@/components/ui/AnimatedCounter'

const features = [
  { icon: Brain, title: 'AI-Powered Tutoring', description: 'Get personalized explanations and learn at your own pace with our intelligent tutoring system.' },
  { icon: Code, title: 'Interactive Code Editor', description: 'Write, run, and debug Python code directly in your browser with real-time feedback.' },
  { icon: Zap, title: 'Smart Code Review', description: 'Receive instant AI-powered code reviews with suggestions for improvement.' },
  { icon: Star, title: 'Practice Exercises', description: 'Test your skills with automatically generated exercises tailored to your level.' },
  { icon: BarChart3, title: 'Progress Tracking', description: 'Track your mastery across concepts with detailed analytics and streak tracking.' },
  { icon: Shield, title: 'Safe Sandbox', description: 'Execute code in a secure, sandboxed environment perfect for learning.' },
]

const stats = [
  { value: 9, suffix: '+', label: 'AI Microservices', prefix: '' },
  { value: 1000, suffix: '+', label: 'Concepts Covered', prefix: '' },
  { value: 99.9, suffix: '%', label: 'Uptime', prefix: '', decimals: 1 },
  { value: 24, suffix: '/7', label: 'AI Support', prefix: '' },
]

function AnimatedSection({ children, className, delay = 0 }: { children: React.ReactNode; className?: string; delay?: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 40 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-100px' }}
      transition={{ duration: 0.7, delay, ease: 'easeOut' }}
      className={className}
    >
      {children}
    </motion.div>
  )
}

function FloatingShape({ className, delay = 0 }: { className: string; delay?: number }) {
  return (
    <motion.div
      className={cn('absolute rounded-full opacity-20 blur-xl', className)}
      animate={{
        y: [0, -20, 0],
        x: [0, 10, 0],
        scale: [1, 1.05, 1],
      }}
      transition={{ duration: 6, delay, repeat: Infinity, ease: 'easeInOut' }}
    />
  )
}

function cn(...classes: (string | boolean | undefined | null)[]) {
  return classes.filter(Boolean).join(' ')
}

export default function LandingPage() {
  return (
    <div className="min-h-screen overflow-hidden">
      <motion.header
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="fixed top-0 z-50 w-full border-b border-white/10 bg-background/60 backdrop-blur-xl supports-[backdrop-filter]:bg-background/30"
      >
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <Link href="/" className="group flex items-center gap-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-primary/60 shadow-lg transition-transform duration-300 group-hover:scale-110">
              <GraduationCap className="h-5 w-5 text-white" />
            </div>
            <span className="text-xl font-bold tracking-tight">LearnFlow</span>
          </Link>
          <nav className="hidden items-center gap-6 md:flex">
            <Link href="/login" className="text-sm text-muted-foreground transition-colors hover:text-foreground">Sign In</Link>
            <Link href="/register">
              <GlowButton size="sm">
                Get Started
                <ArrowRight className="ml-1.5 h-3.5 w-3.5" />
              </GlowButton>
            </Link>
          </nav>
        </div>
      </motion.header>

      {/* Hero */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-16">
        <div className="absolute inset-0 bg-gradient-to-b from-primary-50/50 via-background to-secondary-50/50 dark:from-primary-950/20 dark:via-background dark:to-secondary-950/20" />
        <AnimatedGrid className="opacity-50" />
        <Spotlight className="-top-40 -left-40" size={600} />
        <Spotlight className="-bottom-40 -right-40" size={500} fill="hsl(var(--secondary-foreground))" />

        <FloatingShape className="top-1/4 left-1/4 h-64 w-64 bg-primary" delay={0} />
        <FloatingShape className="bottom-1/3 right-1/4 h-48 w-48 bg-secondary-foreground" delay={2} />
        <FloatingShape className="top-1/3 right-1/3 h-32 w-32 bg-primary/50" delay={4} />

        <div className="relative z-10 mx-auto max-w-5xl px-4 py-20 text-center sm:px-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="mb-6 inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-4 py-1.5 text-sm"
          >
            <Sparkles className="h-4 w-4 text-primary" />
            <span>AI-Powered Python Tutoring Platform</span>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="text-4xl font-bold tracking-tight sm:text-6xl lg:text-7xl"
          >
            Master Python with
            <span className="mt-2 block bg-gradient-to-r from-primary via-primary/80 to-blue-400 bg-clip-text text-transparent">
              AI-Powered Learning
            </span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-muted-foreground"
          >
            <Typewriter
              texts={[
                "LearnFlow combines intelligent AI tutoring, real-time code analysis, and personalized practice to help you master Python.",
                "Chat with AI tutors, get instant code reviews, debug errors, and track your progress — all in one platform.",
                "From variables to advanced algorithms — LearnFlow adapts to your skill level and learning pace.",
              ]}
              speed={30}
              deleteSpeed={20}
              pauseDuration={3000}
            />
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.5 }}
            className="mt-10 flex items-center justify-center gap-4"
          >
            <Link href="/register">
              <GlowButton size="lg" className="group text-base">
                Start Learning Free
                <ArrowRight className="ml-2 h-5 w-5 transition-transform duration-300 group-hover:translate-x-1" />
              </GlowButton>
            </Link>
            <Link href="/login">
              <GlowButton variant="outline" size="lg" className="text-base">
                Sign In
              </GlowButton>
            </Link>
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.7 }}
            className="mt-12 flex items-center justify-center gap-8 text-sm text-muted-foreground"
          >
            {[
              { icon: Brain, label: 'AI-Powered' },
              { icon: Code, label: 'Interactive' },
              { icon: Shield, label: 'Safe Sandbox' },
              { icon: Zap, label: 'Real-time Feedback' },
            ].map(({ icon: Icon, label }) => (
              <div key={label} className="flex items-center gap-1.5">
                <Icon className="h-4 w-4 text-primary" />
                <span>{label}</span>
              </div>
            ))}
          </motion.div>
        </div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.2 }}
          className="absolute bottom-8 left-1/2 -translate-x-1/2"
        >
          <motion.div
            animate={{ y: [0, 8, 0] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            <ChevronRight className="h-5 w-5 rotate-90 text-muted-foreground" />
          </motion.div>
        </motion.div>
      </section>

      {/* Stats */}
      <section className="relative border-y border-white/10 bg-gradient-to-b from-background to-secondary/30 py-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 gap-8 md:grid-cols-4">
            {stats.map((stat) => (
              <AnimatedSection key={stat.label} className="text-center" delay={0.1}>
                <GlassCard className="inline-flex flex-col items-center px-8 py-6">
                  <GlassCardContent className="p-0 text-center">
                    <div className="text-3xl font-bold tracking-tight md:text-4xl">
                      <AnimatedCounter to={stat.value} suffix={stat.suffix} prefix={stat.prefix} decimals={stat.decimals || 0} />
                    </div>
                    <p className="mt-1 text-sm text-muted-foreground">{stat.label}</p>
                  </GlassCardContent>
                </GlassCard>
              </AnimatedSection>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="relative py-24" id="features">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,hsl(var(--primary)/0.03),transparent_50%)]" />
        <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <AnimatedSection className="text-center" delay={0.1}>
            <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-4 py-1.5 text-sm">
              <Sparkles className="h-4 w-4 text-primary" />
              <span>Features</span>
            </div>
            <h2 className="text-3xl font-bold sm:text-4xl">Everything you need to learn Python</h2>
            <p className="mt-4 text-muted-foreground">Powerful features designed for effective learning</p>
          </AnimatedSection>

          <div className="mt-16 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {features.map((feature, index) => (
              <FeatureCard key={feature.title} {...feature} index={index} />
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="relative overflow-hidden py-24">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-background to-secondary/10" />
        <AnimatedGrid className="opacity-30" spacing={40} dotSize={1.5} />
        <Spotlight className="top-0 left-1/2 -translate-x-1/2" size={700} />

        <AnimatedSection className="relative z-10 mx-auto max-w-3xl px-4 text-center sm:px-6" delay={0.2}>
          <GlassCard glow className="px-8 py-12 sm:px-16">
            <GlassCardContent className="p-0">
              <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-primary to-primary/60 shadow-lg">
                <GraduationCap className="h-8 w-8 text-white" />
              </div>
              <h2 className="text-3xl font-bold sm:text-4xl">Ready to start learning?</h2>
              <p className="mx-auto mt-4 max-w-md text-muted-foreground">
                Join LearnFlow and accelerate your Python journey with AI-powered guidance.
              </p>
              <div className="mt-8 flex items-center justify-center gap-4">
                <Link href="/register">
                  <GlowButton size="lg" className="group text-base">
                    Get Started Free
                    <ArrowRight className="ml-2 h-5 w-5 transition-transform duration-300 group-hover:translate-x-1" />
                  </GlowButton>
                </Link>
              </div>
            </GlassCardContent>
          </GlassCard>
        </AnimatedSection>
      </section>

      {/* Footer */}
      <motion.footer
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        className="border-t py-8"
      >
        <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 px-4 sm:flex-row sm:px-6 lg:px-8">
          <div className="flex items-center gap-2">
            <GraduationCap className="h-5 w-5 text-primary" />
            <span className="text-sm font-semibold">LearnFlow</span>
          </div>
          <p className="text-sm text-muted-foreground">AI-Powered Python Learning Platform</p>
        </div>
      </motion.footer>
    </div>
  )
}
