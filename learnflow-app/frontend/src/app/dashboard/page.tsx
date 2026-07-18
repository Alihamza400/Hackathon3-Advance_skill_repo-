'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { StatsCard } from '@/components/dashboard/StatsCard'
import { ProgressChart } from '@/components/dashboard/ProgressChart'
import { RecentActivity } from '@/components/dashboard/RecentActivity'
import { Spinner } from '@/components/ui/Spinner'
import { GlassCard, GlassCardContent } from '@/components/ui/GlassCard'
import { GlowButton } from '@/components/ui/GlowButton'
import { api } from '@/lib/api'
import { BookOpen, Trophy, Zap, CheckCircle, TrendingUp, Clock, Flame, Sparkles } from 'lucide-react'
import Link from 'next/link'
import type { DashboardData } from '@/types'

const container = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.08 } },
}

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4 } },
}

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getDashboard()
      .then(setData)
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex flex-col items-center gap-3">
          <div className="relative">
            <div className="h-12 w-12 animate-spin rounded-full border-2 border-primary border-t-transparent" />
            <div className="absolute inset-0 h-12 w-12 animate-ping rounded-full bg-primary/10" />
          </div>
          <p className="text-sm text-muted-foreground animate-pulse">Loading your dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-6">
      <motion.div variants={item} className="flex items-center justify-between">
        <div>
          <div className="mb-2 inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-3 py-1 text-xs">
            <Sparkles className="h-3 w-3 text-primary" />
            <span>Dashboard</span>
          </div>
          <h1 className="text-3xl font-bold">Welcome back!</h1>
          <p className="text-muted-foreground">Track your learning journey</p>
        </div>
        <Link href="/learn">
          <GlowButton size="sm">
            <BookOpen className="h-4 w-4 mr-1.5" />
            Continue Learning
          </GlowButton>
        </Link>
      </motion.div>

      {!data ? (
        <motion.div variants={item}>
          <GlassCard className="p-12 text-center">
            <GlassCardContent className="p-0">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: 'spring', stiffness: 200, delay: 0.2 }}
              >
                <Trophy className="h-16 w-16 text-primary mx-auto mb-4" />
              </motion.div>
              <h2 className="text-2xl font-semibold mb-2">Welcome to LearnFlow!</h2>
              <p className="text-muted-foreground mb-6 max-w-sm mx-auto">
                Start your learning journey by exploring concepts or trying exercises.
              </p>
              <Link href="/learn">
                <GlowButton>Start Learning</GlowButton>
              </Link>
            </GlassCardContent>
          </GlassCard>
        </motion.div>
      ) : (
        <>
          <motion.div variants={item} className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatsCard title="Overall Mastery" value={`${Math.round(data.overall_mastery)}%`} icon={TrendingUp} description="Across all concepts" />
            <StatsCard title="Current Streak" value={`${data.streak.current_streak} days`} icon={Flame} description={`Best: ${data.streak.longest_streak} days`} />
            <StatsCard title="Concepts Mastered" value={data.concepts_mastered} icon={CheckCircle} description="Topics completed" />
            <StatsCard title="Exercises" value={`${data.passed_exercises}/${data.total_exercises}`} icon={Zap} description="Passed / Total" />
          </motion.div>

          <motion.div variants={item} className="grid gap-6 lg:grid-cols-2">
            <ProgressChart data={data.concept_mastery?.map(c => ({ concept: c.concept, score: c.score, level: c.mastery_level })) || []} />
            <RecentActivity events={data.recent_activity || []} />
          </motion.div>

          <motion.div variants={item} className="grid gap-4 sm:grid-cols-2">
            <Card>
              <CardHeader><CardTitle>Suggested Topics</CardTitle></CardHeader>
              <CardContent>
                {data.suggested_topics?.length > 0 ? (
                  <motion.div className="flex flex-wrap gap-2" variants={container} initial="hidden" animate="show">
                    {data.suggested_topics.map((topic) => (
                      <motion.div key={topic} variants={item}>
                        <Link
                          href={`/learn?concept=${topic}`}
                          className="inline-flex items-center gap-1 px-3 py-1.5 rounded-full bg-secondary text-sm font-medium hover:bg-accent transition-all hover:shadow-[0_0_10px_hsl(var(--primary)/0.2)]"
                        >
                          {topic.replace(/_/g, ' ')}
                        </Link>
                      </motion.div>
                    ))}
                  </motion.div>
                ) : (
                  <p className="text-sm text-muted-foreground">Complete more exercises for personalized suggestions</p>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader><CardTitle>Quick Actions</CardTitle></CardHeader>
              <CardContent className="space-y-2">
                <Link href="/learn">
                  <GlowButton variant="outline" className="w-full justify-start">
                    <BookOpen className="h-4 w-4 mr-2" />
                    Learn a New Concept
                  </GlowButton>
                </Link>
                <Link href="/exercises">
                  <GlowButton variant="outline" className="w-full justify-start">
                    <Zap className="h-4 w-4 mr-2" />
                    Practice Exercises
                  </GlowButton>
                </Link>
                <Link href="/code-editor">
                  <GlowButton variant="outline" className="w-full justify-start">
                    <Clock className="h-4 w-4 mr-2" />
                    Open Code Editor
                  </GlowButton>
                </Link>
              </CardContent>
            </Card>
          </motion.div>
        </>
      )}
    </motion.div>
  )
}
