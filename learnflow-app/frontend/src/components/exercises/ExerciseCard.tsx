'use client'

import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Clock, Code, Star } from 'lucide-react'
import type { Exercise } from '@/types'

interface ExerciseCardProps {
  exercise: Exercise
  onStart: (id: string) => void
}

export function ExerciseCard({ exercise, onStart }: ExerciseCardProps) {
  const difficultyColor = {
    beginner: 'success' as const,
    intermediate: 'warning' as const,
    advanced: 'error' as const,
  }

  return (
    <Card hover className="flex flex-col">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <CardTitle className="text-lg">{exercise.title}</CardTitle>
            <CardDescription>{exercise.description}</CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent className="flex-1">
        <div className="flex flex-wrap gap-2 mb-3">
          <Badge variant={difficultyColor[exercise.difficulty]}>
            {exercise.difficulty}
          </Badge>
          <Badge variant="secondary">
            <Code className="h-3 w-3 mr-1" />
            {exercise.type.replace(/_/g, ' ')}
          </Badge>
          <Badge variant="secondary">
            <Clock className="h-3 w-3 mr-1" />
            {exercise.estimated_minutes} min
          </Badge>
        </div>
        <p className="text-xs text-muted-foreground capitalize">
          Topic: {exercise.topic.replace(/_/g, ' ')}
        </p>
      </CardContent>
      <CardFooter>
        <Button onClick={() => onStart(exercise.id)} className="w-full" size="sm">
          <Star className="h-4 w-4 mr-1" />
          Start Exercise
        </Button>
      </CardFooter>
    </Card>
  )
}
