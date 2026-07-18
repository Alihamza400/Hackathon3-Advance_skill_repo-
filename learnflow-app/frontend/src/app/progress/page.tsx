'use client'

import { useEffect, useState } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { StatsCard } from '@/components/dashboard/StatsCard'
import { ProgressChart } from '@/components/dashboard/ProgressChart'
import { Spinner } from '@/components/ui/Spinner'
import { api } from '@/lib/api'
import { Flame, Trophy, Zap, BookOpen, Target, TrendingUp } from 'lucide-react'
import Link from 'next/link'
import { Button } from '@/components/ui/Button'
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
    ]).then(([d, s, m]) => {
      setDash(d)
      setStreak(s)
      setMastery(m)
    }).finally(() => setLoading(false))
  }, [])

  if (loading) {
    return <div className="flex items-center justify-center h-64"><Spinner size="lg" /></div>
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Progress</h1>
        <p className="text-muted-foreground">Track your learning journey</p>
      </div>

      {!dash ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Target className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h2 className="text-xl font-semibold mb-2">No Progress Yet</h2>
            <p className="text-muted-foreground mb-4">Start learning to track your progress</p>
            <Link href="/learn"><Button>Start Learning</Button></Link>
          </CardContent>
        </Card>
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatsCard
              title="Overall Mastery"
              value={`${Math.round(dash.overall_mastery)}%`}
              icon={TrendingUp}
              trend={dash.overall_mastery > 50 ? { value: 12, positive: true } : undefined}
            />
            <StatsCard
              title="Current Streak"
              value={`${streak?.current_streak || dash.streak.current_streak} days`}
              icon={Flame}
              description={`Best: ${streak?.longest_streak || dash.streak.longest_streak} days`}
            />
            <StatsCard
              title="Concepts Mastered"
              value={dash.concepts_mastered}
              icon={Trophy}
              description="Topics completed"
            />
            <StatsCard
              title="Exercises Passed"
              value={`${dash.passed_exercises}/${dash.total_exercises}`}
              icon={Zap}
            />
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            <ProgressChart
              data={(mastery.length ? mastery : dash.concept_mastery || []).map(c => ({
                concept: c.concept,
                score: c.score,
                level: c.mastery_level,
              }))}
            />
            <Card>
              <CardHeader><CardTitle>Learning Stats</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between py-2 border-b">
                  <span className="text-sm">Total Exercises Attempted</span>
                  <span className="font-semibold">{dash.total_exercises}</span>
                </div>
                <div className="flex items-center justify-between py-2 border-b">
                  <span className="text-sm">Pass Rate</span>
                  <span className="font-semibold">
                    {dash.total_exercises > 0
                      ? `${Math.round((dash.passed_exercises / dash.total_exercises) * 100)}%`
                      : 'N/A'}
                  </span>
                </div>
                <div className="flex items-center justify-between py-2 border-b">
                  <span className="text-sm">Concepts Learning</span>
                  <span className="font-semibold">{dash.concept_mastery?.length || 0}</span>
                </div>
                <div className="flex items-center justify-between py-2">
                  <span className="text-sm">Mastery Score</span>
                  <span className="font-semibold">{Math.round(dash.overall_mastery)}%</span>
                </div>
              </CardContent>
            </Card>
          </div>

          {dash.suggested_topics?.length > 0 && (
            <Card>
              <CardHeader><CardTitle>Recommended Next Topics</CardTitle></CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {dash.suggested_topics.map((topic) => (
                    <Link
                      key={topic}
                      href={`/learn?concept=${topic}`}
                      className="inline-flex items-center gap-1 px-3 py-1.5 rounded-full bg-secondary text-sm font-medium hover:bg-accent transition-colors"
                    >
                      <BookOpen className="h-3 w-3" />
                      {topic.replace(/_/g, ' ')}
                    </Link>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  )
}
