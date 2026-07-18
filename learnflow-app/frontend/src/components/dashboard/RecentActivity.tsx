'use client'

import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { formatRelativeTime } from '@/lib/utils'
import { BookOpen, CheckCircle, XCircle, Zap, Timer, Award } from 'lucide-react'
import type { ProgressEvent } from '@/types'
import { cn } from '@/lib/utils'

const eventConfig: Record<string, { icon: typeof BookOpen; color: string; label: string }> = {
  lesson_started: { icon: BookOpen, color: 'text-blue-500', label: 'Lesson Started' },
  lesson_completed: { icon: CheckCircle, color: 'text-green-500', label: 'Lesson Completed' },
  exercise_attempted: { icon: Timer, color: 'text-yellow-500', label: 'Exercise Attempted' },
  exercise_passed: { icon: CheckCircle, color: 'text-green-500', label: 'Exercise Passed' },
  exercise_failed: { icon: XCircle, color: 'text-red-500', label: 'Exercise Failed' },
  quiz_taken: { icon: Zap, color: 'text-purple-500', label: 'Quiz Taken' },
  topic_mastered: { icon: Award, color: 'text-primary', label: 'Topic Mastered' },
  streak_extended: { icon: Zap, color: 'text-orange-500', label: 'Streak Extended' },
  level_up: { icon: Award, color: 'text-green-500', label: 'Level Up' },
  struggle_detected: { icon: XCircle, color: 'text-red-500', label: 'Struggle Detected' },
}

interface RecentActivityProps {
  events: ProgressEvent[]
  className?: string
}

export function RecentActivity({ events, className }: RecentActivityProps) {
  return (
    <Card className={className}>
      <CardHeader><CardTitle>Recent Activity</CardTitle></CardHeader>
      <CardContent>
        {events.length === 0 ? (
          <p className="text-sm text-muted-foreground">No recent activity</p>
        ) : (
          <div className="space-y-4">
            {events.map((event) => {
              const config = eventConfig[event.event_type] || { icon: BookOpen, color: 'text-gray-500', label: event.event_type }
              const Icon = config.icon
              return (
                <div key={event.id} className="flex items-start gap-3">
                  <div className={cn('mt-0.5', config.color)}>
                    <Icon className="h-4 w-4" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium">{config.label}</p>
                    {event.concept && (
                      <p className="text-xs text-muted-foreground capitalize">{event.concept.replace(/_/g, ' ')}</p>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="secondary">{formatRelativeTime(event.created_at)}</Badge>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
