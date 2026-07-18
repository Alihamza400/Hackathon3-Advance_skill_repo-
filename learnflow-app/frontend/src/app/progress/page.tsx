'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { StatsCard } from '@/components/dashboard/StatsCard'
import { ProgressChart } from '@/components/dashboard/ProgressChart'
import { GlassCard, GlassCardContent } from '@/components/ui/GlassCard'
import { GlowButton } from '@/components/ui/GlowButton'
import { api } from '@/lib/api'
import { Flame, Trophy, Zap, BookOpen, Target, TrendingUp, Sparkles } from 'lucide-react'
import Link from 'next/link'
import type { DashboardData, StreakInfo, ConceptMastery } from '@/types'

const container = { hidden: {}, show: { transition: { staggerChildren: 0.08 } } }
const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } }

export default function ProgressPage() {
  const [dash, setDash] = useState<DashboardData | null>(null)
  const [streak, setStreak] = useState<StreakInfo | null>(null)
  const [mastery, setMastery] = useState<ConceptMastery[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      api.getDashboard().catch(() => null),
      api.getStreak().catch(() => null),
      api.getConceptMastery().catch(() => []),
    ]).then(([d, s, m]) => { setDash(d); setStreak(s); setMastery(m) })
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex flex-col items-center gap-3">
          <div className="relative">
            <div className="h-10 w-10 animate-spin rounded-full border-2 border-primary border-t-transparent" />
            <div className="absolute inset-0 h-10 w-10 animate-ping rounded-full bg-primary/10" />
          </div>
          <p className="text-sm text-muted-foreground animate-pulse">Loading your progress...</p>
        </div>
      </div>
    )
  }

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-6">
      <motion.div variants={item}>
        <div className="mb-2 inline-flex items-center gap-1.5 rounded-full border border-primary/20 bg-primary/5 px-3 py-1 text-xs">
          <Sparkles className="h-3 w-3 text-primary" />
          <span>Progress</span>
        </div>
        <h1 className="text-3xl font-bold">Progress</h1>
        <p className="text-muted-foreground">Track your learning journey</p>
      </motion.div>

      {!dash ? (
        <motion.div variants={item}>
          <GlassCard className="p-12 text-center">
            <GlassCardContent className="p-0">
              <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }}
                transition={{ type: 'spring', stiffness: 200, delay: 0.2 }}>
                <Target className="h-16 w-16 text-primary mx-auto mb-4" />
              </motion.div>
              <h2 className="text-2xl font-semibold mb-2">No Progress Yet</h2>
              <p className="text-muted-foreground mb-6">Start learning to track your progress</p>
              <Link href="/learn"><GlowButton>Start Learning</GlowButton></Link>
            </GlassCardContent>
          </GlassCard>
        </motion.div>
      ) : (
        <>
          <motion.div variants={item} className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatsCard title="Overall Mastery" value={`${Math.round(dash.overall_mastery)}%`} icon={TrendingUp}
              trend={dash.overall_mastery > 50 ? { value: 12, positive: true } : undefined} />
            <StatsCard title="Current Streak" value={`${streak?.current_streak || dash.streak.current_streak} days`}
              icon={Flame} description={`Best: ${streak?.longest_streak || dash.streak.longest_streak} days`} />
            <StatsCard title="Concepts Mastered" value={dash.concepts_mastered} icon={Trophy} description="Topics completed" />
            <StatsCard title="Exercises Passed" value={`${dash.passed_exercises}/${dash.total_exercises}`} icon={Zap} />
          </motion.div>

          <motion.div variants={item} className="grid gap-6 lg:grid-cols-2">
            <ProgressChart data={(mastery.length ? mastery : dash.concept_mastery || []).map(c => ({
              concept: c.concept, score: c.score, level: c.mastery_level,
            }))} />
            <GlassCard>
              <GlassCardContent>
                <h3 className="font-semibold mb-4">Learning Stats</h3>
                <div className="space-y-4">
                  {[
                    { label: 'Total Exercises Attempted', value: dash.total_exercises },
                    { label: 'Pass Rate', value: dash.total_exercises > 0 ? `${Math.round((dash.passed_exercises / dash.total_exercises) * 100)}%` : 'N/A' },
                    { label: 'Concepts Learning', value: dash.concept_mastery?.length || 0 },
                    { label: 'Mastery Score', value: `${Math.round(dash.overall_mastery)}%` },
                  ].map((s) => (
                    <div key={s.label} className="flex items-center justify-between py-2 border-b last:border-0">
                      <span className="text-sm">{s.label}</span>
                      <span className="font-semibold tabular-nums">{s.value}</span>
                    </div>
                  ))}
                </div>
              </GlassCardContent>
            </GlassCard>
          </motion.div>

          {dash.suggested_topics?.length > 0 && (
            <motion.div variants={item}>
              <GlassCard>
                <GlassCardContent>
                  <h3 className="font-semibold mb-3">Recommended Next Topics</h3>
                  <div className="flex flex-wrap gap-2">
                    {dash.suggested_topics.map((topic, i) => (
                      <motion.div key={topic} initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }} transition={{ delay: i * 0.05 }}>
                        <Link href={`/learn?concept=${topic}`}
                          className="inline-flex items-center gap-1 px-3 py-1.5 rounded-full bg-secondary text-sm font-medium
                            hover:bg-accent transition-all hover:shadow-[0_0_10px_hsl(var(--primary)/0.2)]">
                          <BookOpen className="h-3 w-3" />
                          {topic.replace(/_/g, ' ')}
                        </Link>
                      </motion.div>
                    ))}
                  </div>
                </GlassCardContent>
              </GlassCard>
            </motion.div>
          )}
        </>
      )}
    </motion.div>
  )
}
