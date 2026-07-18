'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { StatsCard } from '@/components/dashboard/StatsCard'
import { ProgressChart } from '@/components/dashboard/ProgressChart'
import { RecentActivity } from '@/components/dashboard/RecentActivity'
import { api } from '@/lib/api'
import { BookOpen, Trophy, Zap, CheckCircle, TrendingUp, Clock, Flame, Sparkles, GraduationCap, ArrowRight, Rocket } from 'lucide-react'
import Link from 'next/link'
import type { DashboardData } from '@/types'

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getDashboard().then(setData).catch(() => {}).finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex flex-col items-center gap-3">
          <div className="relative">
            <div className="h-12 w-12 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />
            <div className="absolute inset-0 h-12 w-12 animate-ping rounded-full bg-blue-500/10" />
          </div>
          <p className="text-sm text-muted-foreground animate-pulse">Loading your dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <div className="mb-2 inline-flex items-center gap-1.5 rounded-full border border-blue-500/20 bg-gradient-to-r from-blue-500/10 to-purple-500/10 px-3 py-1 text-xs">
            <Sparkles className="h-3 w-3 text-blue-500" />
            <span className="bg-gradient-to-r from-blue-500 to-purple-500 bg-clip-text text-transparent font-medium">Dashboard</span>
          </div>
          <h1 className="text-3xl font-bold">Welcome back!</h1>
          <p className="text-muted-foreground">Track your learning journey</p>
        </div>
        <Link href="/learn">
          <button className="group relative inline-flex h-10 items-center justify-center overflow-hidden rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 px-5 text-sm font-medium text-white shadow-lg shadow-blue-500/25 transition-all duration-300 hover:shadow-blue-500/40 hover:scale-105">
            <span className="absolute inset-0 bg-[linear-gradient(45deg,transparent_25%,rgba(255,255,255,0.2)_50%,transparent_75%)] bg-[length:250%_250%] transition-all duration-700 group-hover:bg-[position:100%_0]" />
            <span className="relative flex items-center gap-1.5"><BookOpen className="h-4 w-4" /> Continue Learning</span>
          </button>
        </Link>
      </div>

      {!data ? (
        <div className="relative overflow-hidden rounded-3xl border border-white/20 bg-gradient-to-br from-white/80 to-white/40 dark:from-white/5 dark:to-white/[0.02] backdrop-blur-xl p-12 text-center shadow-xl">
          <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ type: 'spring', stiffness: 200, delay: 0.2 }}>
            <div className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-600 to-purple-600 shadow-xl">
              <GraduationCap className="h-10 w-10 text-white" />
            </div>
          </motion.div>
          <h2 className="text-2xl font-semibold mb-2">Welcome to LearnFlow!</h2>
          <p className="text-muted-foreground mb-8 max-w-sm mx-auto">Start your learning journey by exploring concepts or trying exercises.</p>
          <Link href="/learn">
            <button className="group relative inline-flex h-12 items-center justify-center overflow-hidden rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 px-6 text-sm font-semibold text-white shadow-lg shadow-blue-500/25 transition-all duration-300 hover:shadow-blue-500/40 hover:scale-105">
              <span className="absolute inset-0 bg-[linear-gradient(45deg,transparent_25%,rgba(255,255,255,0.2)_50%,transparent_75%)] bg-[length:250%_250%] transition-all duration-700 group-hover:bg-[position:100%_0]" />
              <span className="relative flex items-center gap-2">Start Learning <Rocket className="h-4 w-4" /></span>
            </button>
          </Link>
        </div>
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatsCard title="Overall Mastery" value={`${Math.round(data.overall_mastery)}%`} icon={TrendingUp} description="Across all concepts" />
            <StatsCard title="Current Streak" value={`${data.streak.current_streak} days`} icon={Flame} description={`Best: ${data.streak.longest_streak} days`} />
            <StatsCard title="Concepts Mastered" value={data.concepts_mastered} icon={CheckCircle} description="Topics completed" />
            <StatsCard title="Exercises" value={`${data.passed_exercises}/${data.total_exercises}`} icon={Zap} description="Passed / Total" />
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            <ProgressChart data={data.concept_mastery?.map(c => ({ concept: c.concept, score: c.score, level: c.mastery_level })) || []} />
            <RecentActivity events={data.recent_activity || []} />
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div className="relative overflow-hidden rounded-2xl border border-white/20 bg-gradient-to-br from-white/80 to-white/40 dark:from-white/5 dark:to-white/[0.02] backdrop-blur-xl p-6">
              <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 via-transparent to-purple-500/5" />
              <div className="relative">
                <h3 className="font-semibold mb-4 flex items-center gap-2"><Sparkles className="h-4 w-4 text-blue-500" /> Suggested Topics</h3>
                {data.suggested_topics?.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {data.suggested_topics.map((topic, i) => (
                      <motion.div key={topic} initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: i * 0.05 }}>
                        <Link href={`/learn?concept=${topic}`}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-gradient-to-r from-blue-500/10 to-purple-500/10 text-sm font-medium text-blue-600 dark:text-blue-400 transition-all hover:shadow-[0_0_15px_hsl(var(--primary)/0.2)] hover:scale-105">
                          {topic.replace(/_/g, ' ')} <ArrowRight className="h-3 w-3" />
                        </Link>
                      </motion.div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground">Complete more exercises for personalized suggestions</p>
                )}
              </div>
            </div>

            <div className="relative overflow-hidden rounded-2xl border border-white/20 bg-gradient-to-br from-white/80 to-white/40 dark:from-white/5 dark:to-white/[0.02] backdrop-blur-xl p-6">
              <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 via-transparent to-blue-500/5" />
              <div className="relative">
                <h3 className="font-semibold mb-4">Quick Actions</h3>
                <div className="space-y-2">
                  {[
                    { href: '/learn', icon: BookOpen, text: 'Learn a New Concept', gradient: 'from-blue-600 to-purple-600' },
                    { href: '/exercises', icon: Zap, text: 'Practice Exercises', gradient: 'from-emerald-500 to-blue-600' },
                    { href: '/code-editor', icon: Clock, text: 'Open Code Editor', gradient: 'from-amber-500 to-rose-500' },
                  ].map((item) => (
                    <Link key={item.href} href={item.href}>
                      <button className="group relative flex w-full items-center gap-3 overflow-hidden rounded-xl border border-white/20 bg-gradient-to-r from-white/50 to-white/30 dark:from-white/5 dark:to-white/[0.02] px-4 py-3 text-sm font-medium transition-all duration-300 hover:shadow-lg hover:scale-[1.01]">
                        <div className={`flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br ${item.gradient}`}>
                          <item.icon className="h-4 w-4 text-white" />
                        </div>
                        <span className="flex-1 text-left">{item.text}</span>
                        <ArrowRight className="h-4 w-4 text-muted-foreground transition-transform group-hover:translate-x-1" />
                      </button>
                    </Link>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
