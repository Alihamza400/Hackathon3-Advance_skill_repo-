#!/bin/bash
# Aceternity UI Design — Generate a complete animated landing page
# Usage: bash generate-landing.sh /path/to/nextjs-app [page-name]

set -e

TARGET="${1:-.}"
PAGE_DIR="$TARGET/src/app"
PAGE_NAME="${2:-page}"

if [ "$PAGE_NAME" = "page" ]; then
  OUTPUT="$PAGE_DIR/page.tsx"
else
  OUTPUT="$PAGE_DIR/$PAGE_NAME/page.tsx"
fi

cat > "$OUTPUT" << 'PAGE'
'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import { ArrowRight, Sparkles, GraduationCap, Brain, Code, Zap, Shield, BarChart3, Star, ChevronRight } from 'lucide-react'
import { AnimatedGrid } from '@/components/ui/AnimatedGrid'
import { Spotlight } from '@/components/ui/Spotlight'
import { GlowButton } from '@/components/ui/GlowButton'
import { Typewriter } from '@/components/ui/Typewriter'
import { GlassCard, GlassCardContent } from '@/components/ui/GlassCard'
import { FeatureCard } from '@/components/ui/FeatureCard'
import { AnimatedCounter } from '@/components/ui/AnimatedCounter'

const features = [
  { icon: Brain, title: 'AI-Powered', description: 'Intelligent tutoring that adapts to your learning style and pace.' },
  { icon: Code, title: 'Interactive', description: 'Write and run code directly in your browser with real-time feedback.' },
  { icon: Zap, title: 'Real-time', description: 'Instant code reviews, debugging, and performance analysis.' },
  { icon: Star, title: 'Practice', description: 'Auto-generated exercises tailored to your skill level.' },
  { icon: BarChart3, title: 'Analytics', description: 'Track mastery across concepts with detailed insights.' },
  { icon: Shield, title: 'Secure', description: 'Safe sandboxed environment for risk-free learning.' },
]

const stats = [
  { value: 9, suffix: '+', label: 'Microservices', decimals: 0 },
  { value: 1000, suffix: '+', label: 'Topics Covered', decimals: 0 },
  { value: 99.9, suffix: '%', label: 'Uptime', decimals: 1 },
  { value: 24, suffix: '/7', label: 'AI Support', decimals: 0 },
]

export default function LandingPage() {
  return (
    <div className="min-h-screen overflow-hidden">
      {/* Navigation */}
      <motion.header initial={{ y: -20, opacity: 0 }} animate={{ y: 0, opacity: 1 }}
        className="fixed top-0 z-50 w-full border-b border-white/10 bg-background/60 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4">
          <Link href="/" className="group flex items-center gap-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-primary/60 shadow-lg transition-transform group-hover:scale-110">
              <GraduationCap className="h-5 w-5 text-white" />
            </div>
            <span className="text-xl font-bold">LearnFlow</span>
          </Link>
          <div className="flex items-center gap-4">
            <Link href="/login" className="text-sm text-muted-foreground hover:text-foreground">Sign In</Link>
            <Link href="/register"><GlowButton size="sm">Get Started <ArrowRight className="ml-1.5 h-3.5 w-3.5" /></GlowButton></Link>
          </div>
        </div>
      </motion.header>

      {/* Hero */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-16">
        <div className="absolute inset-0 bg-gradient-to-b from-primary-50/50 via-background to-secondary-50/50" />
        <AnimatedGrid />
        <Spotlight className="-top-40 -left-40" size={600} />
        <Spotlight className="-bottom-40 -right-40" size={500} fill="hsl(var(--secondary-foreground))" />

        <div className="relative z-10 mx-auto max-w-5xl px-4 py-20 text-center">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
            className="mb-6 inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-4 py-1.5 text-sm">
            <Sparkles className="h-4 w-4 text-primary" />
            <span>AI-Powered Learning Platform</span>
          </motion.div>

          <motion.h1 initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
            className="text-4xl font-bold sm:text-6xl lg:text-7xl">
            Master Skills with
            <span className="mt-2 block bg-gradient-to-r from-primary via-primary/80 to-blue-400 bg-clip-text text-transparent">
              AI-Powered Learning
            </span>
          </motion.h1>

          <motion.p initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}
            className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground">
            <Typewriter texts={[
              "Combine AI tutoring, real-time code analysis, and personalized practice to master any skill.",
              "Chat with AI tutors, get instant feedback, debug errors, and track progress — all in one place.",
              "From basics to advanced — adapts to your level and pace.",
            ]} speed={30} deleteSpeed={20} pauseDuration={3000} />
          </motion.p>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}
            className="mt-10 flex items-center justify-center gap-4">
            <Link href="/register"><GlowButton size="lg" className="group text-base">
              Start Free <ArrowRight className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
            </GlowButton></Link>
            <Link href="/login"><GlowButton variant="outline" size="lg" className="text-base">Sign In</GlowButton></Link>
          </motion.div>

          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.7 }}
            className="mt-12 flex items-center justify-center gap-8 text-sm text-muted-foreground">
            {[{ icon: Brain, label: 'AI-Powered' }, { icon: Code, label: 'Interactive' },
              { icon: Shield, label: 'Secure' }, { icon: Zap, label: 'Real-time' }].map(({ icon: Icon, label }) => (
              <div key={label} className="flex items-center gap-1.5">
                <Icon className="h-4 w-4 text-primary" /><span>{label}</span>
              </div>
            ))}
          </motion.div>
        </div>

        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.2 }}
          className="absolute bottom-8 left-1/2 -translate-x-1/2">
          <motion.div animate={{ y: [0, 8, 0] }} transition={{ duration: 2, repeat: Infinity }}>
            <ChevronRight className="h-5 w-5 rotate-90 text-muted-foreground" />
          </motion.div>
        </motion.div>
      </section>

      {/* Stats */}
      <section className="border-y border-white/10 bg-gradient-to-b from-background to-secondary/30 py-16">
        <div className="mx-auto max-w-7xl px-4">
          <div className="grid grid-cols-2 gap-8 md:grid-cols-4">
            {stats.map((s) => (
              <motion.div key={s.label} initial={{ opacity: 0, y: 40 }} whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }} transition={{ delay: 0.1 }} className="text-center">
                <GlassCard className="inline-flex flex-col items-center px-8 py-6">
                  <GlassCardContent className="p-0 text-center">
                    <div className="text-3xl font-bold md:text-4xl">
                      <AnimatedCounter to={s.value} suffix={s.suffix} decimals={s.decimals} />
                    </div>
                    <p className="mt-1 text-sm text-muted-foreground">{s.label}</p>
                  </GlassCardContent>
                </GlassCard>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-24">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,hsl(var(--primary)/0.03),transparent_50%)]" />
        <div className="relative mx-auto max-w-7xl px-4">
          <motion.div initial={{ opacity: 0, y: 40 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
            className="text-center">
            <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-4 py-1.5 text-sm">
              <Sparkles className="h-4 w-4 text-primary" /><span>Features</span>
            </div>
            <h2 className="text-3xl font-bold sm:text-4xl">Everything you need</h2>
            <p className="mt-4 text-muted-foreground">Powerful features for effective learning</p>
          </motion.div>
          <div className="mt-16 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {features.map((f, i) => <FeatureCard key={f.title} {...f} index={i} />)}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="relative overflow-hidden py-24">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-background to-secondary/10" />
        <AnimatedGrid className="opacity-30" spacing={40} dotSize={1.5} />
        <Spotlight className="top-0 left-1/2 -translate-x-1/2" size={700} />
        <div className="relative z-10 mx-auto max-w-3xl px-4 text-center">
          <GlassCard glow className="px-8 py-12">
            <GlassCardContent className="p-0">
              <h2 className="text-3xl font-bold sm:text-4xl">Ready to start?</h2>
              <p className="mx-auto mt-4 max-w-md text-muted-foreground">Join and accelerate your journey with AI-powered guidance.</p>
              <div className="mt-8">
                <Link href="/register"><GlowButton size="lg" className="group text-base">
                  Get Started Free <ArrowRight className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
                </GlowButton></Link>
              </div>
            </GlassCardContent>
          </GlassCard>
        </div>
      </section>

      <footer className="border-t py-8">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4">
          <div className="flex items-center gap-2">
            <GraduationCap className="h-5 w-5 text-primary" />
            <span className="text-sm font-semibold">LearnFlow</span>
          </div>
          <p className="text-sm text-muted-foreground">AI-Powered Learning Platform</p>
        </div>
      </footer>
    </div>
  )
}
PAGE

echo "✅ Landing page generated at $OUTPUT"
