'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { StatsCard } from '@/components/dashboard/StatsCard'
import { ProgressChart } from '@/components/dashboard/ProgressChart'
import { api } from '@/lib/api'
import { Flame, Trophy, Zap, BookOpen, Target, TrendingUp, Sparkles, ArrowRight } from 'lucide-react'
import Link from 'next/link'
import type { DashboardData, StreakInfo, ConceptMastery } from '@/types'

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
    ]).then(([d, s, m]) => { setDash(d); setStreak(s); setMastery(m) }).finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex flex-col items-center gap-3">
          <div className="relative"><div className="h-10 w-10 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" /><div className="absolute inset-0 h-10 w-10 animate-ping rounded-full bg-blue-500/10" /></div>
          <p className="text-sm text-muted-foreground animate-pulse">Loading your progress...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <div className="mb-2 inline-flex items-center gap-1.5 rounded-full border border-rose-500/20 bg-gradient-to-r from-rose-500/10 to-purple-500/10 px-3 py-1 text-xs">
          <Sparkles className="h-3 w-3 text-rose-500" />
          <span className="bg-gradient-to-r from-rose-500 to-purple-500 bg-clip-text text-transparent font-medium">Progress</span>
        </div>
        <h1 className="text-3xl font-bold">Progress</h1>
        <p className="text-muted-foreground">Track your learning journey</p>
      </motion.div>

      {!dash ? (
        <div className="relative overflow-hidden rounded-3xl border border-white/20 bg-gradient-to-br from-white/80 to-white/40 dark:from-white/5 dark:to-white/[0.02] backdrop-blur-xl p-12 text-center shadow-xl">
          <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ type: 'spring', stiffness: 200 }}>
            <Target className="h-16 w-16 mx-auto mb-4 text-blue-500" />
          </motion.div>
          <h2 className="text-2xl font-semibold mb-2">No Progress Yet</h2>
          <p className="text-muted-foreground mb-6">Start learning to track your progress</p>
          <Link href="/learn">
            <button className="group relative inline-flex h-12 items-center justify-center overflow-hidden rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 px-6 text-sm font-semibold text-white shadow-lg shadow-blue-500/25 transition-all duration-300 hover:shadow-blue-500/40 hover:scale-105">
              <span className="absolute inset-0 bg-[linear-gradient(45deg,transparent_25%,rgba(255,255,255,0.2)_50%,transparent_75%)] bg-[length:250%_250%] transition-all duration-700 group-hover:bg-[position:100%_0]" />
              <span className="relative flex items-center gap-2">Start Learning</span>
            </button>
          </Link>
        </div>
      ) : (
        <>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatsCard title="Overall Mastery" value={`${Math.round(dash.overall_mastery)}%`} icon={TrendingUp} trend={dash.overall_mastery > 50 ? { value: 12, positive: true } : undefined} />
            <StatsCard title="Current Streak" value={`${streak?.current_streak || dash.streak.current_streak} days`} icon={Flame} description={`Best: ${streak?.longest_streak || dash.streak.longest_streak} days`} />
            <StatsCard title="Concepts Mastered" value={dash.concepts_mastered} icon={Trophy} description="Topics completed" />
            <StatsCard title="Exercises Passed" value={`${dash.passed_exercises}/${dash.total_exercises}`} icon={Zap} />
          </motion.div>

          <div className="grid gap-6 lg:grid-cols-2">
            <ProgressChart data={(mastery.length ? mastery : dash.concept_mastery || []).map(c => ({ concept: c.concept, score: c.score, level: c.mastery_level }))} />
            <div className="relative overflow-hidden rounded-2xl border border-white/20 bg-gradient-to-br from-white/80 to-white/40 dark:from-white/5 dark:to-white/[0.02] backdrop-blur-xl p-6">
              <div className="absolute inset-0 bg-gradient-to-br from-rose-500/5 via-transparent to-purple-500/5" />
              <div className="relative">
                <h3 className="font-semibold mb-4">Learning Stats</h3>
                <div className="space-y-4">
                  {[
                    { label: 'Total Exercises Attempted', value: dash.total_exercises },
                    { label: 'Pass Rate', value: dash.total_exercises > 0 ? `${Math.round((dash.passed_exercises / dash.total_exercises) * 100)}%` : 'N/A' },
                    { label: 'Concepts Learning', value: dash.concept_mastery?.length || 0 },
                    { label: 'Mastery Score', value: `${Math.round(dash.overall_mastery)}%` },
                  ].map((s) => (
                    <div key={s.label} className="flex items-center justify-between py-2 border-b border-white/10 last:border-0">
                      <span className="text-sm text-muted-foreground">{s.label}</span>
                      <span className="font-semibold tabular-nums">{s.value}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {dash.suggested_topics?.length > 0 && (
            <div className="relative overflow-hidden rounded-2xl border border-white/20 bg-gradient-to-br from-white/80 to-white/40 dark:from-white/5 dark:to-white/[0.02] backdrop-blur-xl p-6">
              <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 via-transparent to-purple-500/5" />
              <div className="relative">
                <h3 className="font-semibold mb-3 flex items-center gap-2"><Sparkles className="h-4 w-4 text-blue-500" /> Recommended Next Topics</h3>
                <div className="flex flex-wrap gap-2">
                  {dash.suggested_topics.map((topic, i) => (
                    <motion.div key={topic} initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: i * 0.05 }}>
                      <Link href={`/learn?concept=${topic}`}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-gradient-to-r from-blue-500/10 to-purple-500/10 text-sm font-medium text-blue-600 dark:text-blue-400 transition-all hover:shadow-[0_0_15px_hsl(var(--primary)/0.2)] hover:scale-105">
                        <BookOpen className="h-3 w-3" /> {topic.replace(/_/g, ' ')} <ArrowRight className="h-3 w-3" />
                      </Link>
                    </motion.div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
