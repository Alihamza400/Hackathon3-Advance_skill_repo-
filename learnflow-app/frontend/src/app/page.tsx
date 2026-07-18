'use client'

import Link from 'next/link'
import { Button } from '@/components/ui/Button'
import { GraduationCap, Brain, Code, Zap, Shield, ArrowRight, Star, Users, BarChart3 } from 'lucide-react'

const features = [
  {
    icon: Brain,
    title: 'AI-Powered Tutoring',
    description: 'Get personalized explanations and learn at your own pace with our intelligent tutoring system.',
  },
  {
    icon: Code,
    title: 'Interactive Code Editor',
    description: 'Write, run, and debug Python code directly in your browser with real-time feedback.',
  },
  {
    icon: Zap,
    title: 'Smart Code Review',
    description: 'Receive instant AI-powered code reviews with suggestions for improvement.',
  },
  {
    icon: Star,
    title: 'Practice Exercises',
    description: 'Test your skills with automatically generated exercises tailored to your level.',
  },
  {
    icon: BarChart3,
    title: 'Progress Tracking',
    description: 'Track your mastery across concepts with detailed analytics and streak tracking.',
  },
  {
    icon: Shield,
    title: 'Safe Sandbox',
    description: 'Execute code in a secure, sandboxed environment perfect for learning.',
  },
]

export default function LandingPage() {
  return (
    <div className="min-h-screen">
      <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link href="/" className="flex items-center gap-2">
              <GraduationCap className="h-8 w-8 text-primary" />
              <span className="font-bold text-xl">LearnFlow</span>
            </Link>
            <div className="flex items-center gap-3">
              <Link href="/login"><Button variant="ghost">Sign In</Button></Link>
              <Link href="/register"><Button>Get Started</Button></Link>
            </div>
          </div>
        </div>
      </header>

      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary-50 via-background to-secondary-50 dark:from-primary-950 dark:via-background dark:to-secondary-950" />
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 sm:py-32">
          <div className="text-center max-w-3xl mx-auto">
            <h1 className="text-4xl sm:text-6xl font-bold tracking-tight">
              Master Python with
              <span className="text-primary block mt-2">AI-Powered Learning</span>
            </h1>
            <p className="mt-6 text-lg text-muted-foreground leading-relaxed">
              LearnFlow combines intelligent AI tutoring, real-time code analysis, and personalized practice
              to help you master Python programming faster than ever before.
            </p>
            <div className="mt-10 flex items-center justify-center gap-4">
              <Link href="/register">
                <Button size="lg" className="text-base">
                  Start Learning Free
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </Link>
              <Link href="/login">
                <Button variant="outline" size="lg" className="text-base">
                  Sign In
                </Button>
              </Link>
            </div>
            <div className="mt-8 flex items-center justify-center gap-6 text-sm text-muted-foreground">
              <span className="flex items-center gap-1"><Users className="h-4 w-4" /> AI-Powered</span>
              <span className="flex items-center gap-1"><Code className="h-4 w-4" /> Interactive</span>
              <span className="flex items-center gap-1"><Shield className="h-4 w-4" /> Safe Sandbox</span>
            </div>
          </div>
        </div>
      </section>

      <section className="py-20 border-t">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold">Everything you need to learn Python</h2>
            <p className="mt-4 text-muted-foreground">Powerful features designed for effective learning</p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature) => {
              const Icon = feature.icon
              return (
                <div key={feature.title} className="p-6 rounded-xl border bg-card hover:shadow-md transition-shadow">
                  <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                    <Icon className="h-6 w-6 text-primary" />
                  </div>
                  <h3 className="font-semibold text-lg mb-2">{feature.title}</h3>
                  <p className="text-sm text-muted-foreground">{feature.description}</p>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      <section className="py-20 border-t bg-secondary/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold mb-4">Ready to start learning?</h2>
          <p className="text-muted-foreground mb-8 max-w-md mx-auto">
            Join LearnFlow and accelerate your Python journey with AI-powered guidance.
          </p>
          <Link href="/register">
            <Button size="lg">Get Started Free</Button>
          </Link>
        </div>
      </section>

      <footer className="border-t py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-sm text-muted-foreground">
          <p>LearnFlow — AI-Powered Python Learning Platform</p>
        </div>
      </footer>
    </div>
  )
}
