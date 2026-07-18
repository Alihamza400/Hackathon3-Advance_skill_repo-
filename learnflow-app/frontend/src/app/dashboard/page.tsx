'use client'

import { useEffect, useState } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { StatsCard } from '@/components/dashboard/StatsCard'
import { ProgressChart } from '@/components/dashboard/ProgressChart'
import { RecentActivity } from '@/components/dashboard/RecentActivity'
import { Spinner } from '@/components/ui/Spinner'
import { api } from '@/lib/api'
import { BookOpen, Trophy, Zap, CheckCircle, TrendingUp, Clock, Flame } from 'lucide-react'
import Link from 'next/link'
import { Button } from '@/components/ui/Button'
import type { DashboardData } from '@/types'

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
        <Spinner size="lg" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground">Track your learning progress</p>
        </div>
        <Link href="/learn">
          <Button>
            <BookOpen className="h-4 w-4 mr-1" />
            Continue Learning
          </Button>
        </Link>
      </div>

      {!data ? (
        <Card>
          <CardContent className="p-12 text-center">
            <Trophy className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h2 className="text-xl font-semibold mb-2">Welcome to LearnFlow!</h2>
            <p className="text-muted-foreground mb-4">Start your learning journey by exploring concepts or trying exercises.</p>
            <Link href="/learn">
              <Button>Start Learning</Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatsCard
              title="Overall Mastery"
              value={`${Math.round(data.overall_mastery)}%`}
              icon={TrendingUp}
              description="Across all concepts"
            />
            <StatsCard
              title="Current Streak"
              value={`${data.streak.current_streak} days`}
              icon={Flame}
              description={`Best: ${data.streak.longest_streak} days`}
            />
            <StatsCard
              title="Concepts Mastered"
              value={data.concepts_mastered}
              icon={CheckCircle}
              description="Topics completed"
            />
            <StatsCard
              title="Exercises"
              value={`${data.passed_exercises}/${data.total_exercises}`}
              icon={Zap}
              description="Passed / Total"
            />
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            <ProgressChart
              data={data.concept_mastery?.map(c => ({
                concept: c.concept,
                score: c.score,
                level: c.mastery_level,
              })) || []}
            />
            <RecentActivity events={data.recent_activity || []} />
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <Card>
              <CardHeader><CardTitle>Suggested Topics</CardTitle></CardHeader>
              <CardContent>
                {data.suggested_topics?.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {data.suggested_topics.map((topic) => (
                      <Link
                        key={topic}
                        href={`/learn?concept=${topic}`}
                        className="px-3 py-1.5 rounded-full bg-secondary text-sm font-medium hover:bg-accent transition-colors"
                      >
                        {topic.replace(/_/g, ' ')}
                      </Link>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground">Complete more exercises for personalized suggestions</p>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader><CardTitle>Quick Actions</CardTitle></CardHeader>
              <CardContent className="space-y-2">
                <Link href="/learn" className="block">
                  <Button variant="outline" className="w-full justify-start">
                    <BookOpen className="h-4 w-4 mr-2" />
                    Learn a New Concept
                  </Button>
                </Link>
                <Link href="/exercises" className="block">
                  <Button variant="outline" className="w-full justify-start">
                    <Zap className="h-4 w-4 mr-2" />
                    Practice Exercises
                  </Button>
                </Link>
                <Link href="/code-editor" className="block">
                  <Button variant="outline" className="w-full justify-start">
                    <Clock className="h-4 w-4 mr-2" />
                    Open Code Editor
                  </Button>
                </Link>
              </CardContent>
            </Card>
          </div>
        </>
      )}
    </div>
  )
}
