'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { ExerciseView } from '@/components/exercises/ExerciseView'
import { Spinner } from '@/components/ui/Spinner'
import { api } from '@/lib/api'
import type { Exercise } from '@/types'

export default function ExerciseDetailPage() {
  const params = useParams()
  const router = useRouter()
  const [exercise, setExercise] = useState<Exercise | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (params.id) {
      api.getExercise(params.id as string)
        .then(setExercise)
        .catch(() => {})
        .finally(() => setLoading(false))
    }
  }, [params.id])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    )
  }

  if (!exercise) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Exercise not found</p>
      </div>
    )
  }

  return <ExerciseView exercise={exercise} onBack={() => router.push('/exercises')} />
}
