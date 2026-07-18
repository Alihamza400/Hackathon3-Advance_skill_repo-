'use client'

import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { cn } from '@/lib/utils'

interface ConceptData {
  concept: string
  score: number
  level: string
}

interface ProgressChartProps {
  data: ConceptData[]
  className?: string
}

export function ProgressChart({ data, className }: ProgressChartProps) {
  if (!data.length) {
    return (
      <Card className={className}>
        <CardHeader><CardTitle>Concept Mastery</CardTitle></CardHeader>
        <CardContent>
          <p className="text-muted-foreground text-sm">Start learning to see your progress</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={className}>
      <CardHeader><CardTitle>Concept Mastery</CardTitle></CardHeader>
      <CardContent className="space-y-4">
        {data.map((item) => (
          <div key={item.concept} className="space-y-1">
            <div className="flex justify-between text-sm">
              <span className="font-medium capitalize">{item.concept.replace(/_/g, ' ')}</span>
              <span className="text-muted-foreground">{Math.round(item.score)}%</span>
            </div>
            <div className="h-2 rounded-full bg-secondary overflow-hidden">
              <div
                className={cn(
                  'h-full rounded-full transition-all duration-500',
                  item.score >= 80 ? 'bg-success-500' :
                  item.score >= 60 ? 'bg-primary' :
                  item.score >= 40 ? 'bg-warning-500' :
                  'bg-error-500'
                )}
                style={{ width: `${item.score}%` }}
              />
            </div>
            <p className="text-xs text-muted-foreground capitalize">{item.level}</p>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}
