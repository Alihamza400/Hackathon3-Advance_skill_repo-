'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Spinner } from '@/components/ui/Spinner'
import { Badge } from '@/components/ui/Badge'
import { ExerciseCard } from '@/components/exercises/ExerciseCard'
import { api } from '@/lib/api'
import { FileCode, RefreshCw } from 'lucide-react'
import type { Exercise, DifficultyLevel } from '@/types'

const topics = ['variables', 'functions', 'loops', 'conditionals', 'lists', 'strings']

export default function ExercisesPage() {
  const router = useRouter()
  const [exercises, setExercises] = useState<Exercise[]>([])
  const [loading, setLoading] = useState(false)
  const [selectedTopic, setSelectedTopic] = useState('functions')
  const [selectedDifficulty, setSelectedDifficulty] = useState<DifficultyLevel>('beginner')
  const [generated, setGenerated] = useState(false)

  async function handleGenerate() {
    setLoading(true)
    try {
      const result = await api.generateExercises(selectedTopic, selectedDifficulty, 3)
      setExercises(result)
      setGenerated(true)
    } catch {
      setExercises([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    handleGenerate()
  }, [])

  function handleStart(id: string) {
    router.push(`/exercises/${id}`)
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Practice Exercises</h1>
        <p className="text-muted-foreground">Generate and solve coding challenges</p>
      </div>

      <Card>
        <CardHeader><CardTitle>Generate Exercises</CardTitle></CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Topic</label>
              <div className="flex flex-wrap gap-2">
                {topics.map((topic) => (
                  <button
                    key={topic}
                    onClick={() => setSelectedTopic(topic)}
                    className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                      selectedTopic === topic
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-secondary text-secondary-foreground hover:bg-accent'
                    }`}
                  >
                    {topic.charAt(0).toUpperCase() + topic.slice(1)}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Difficulty</label>
              <div className="flex gap-2">
                {(['beginner', 'intermediate', 'advanced'] as DifficultyLevel[]).map((d) => (
                  <button
                    key={d}
                    onClick={() => setSelectedDifficulty(d)}
                    className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                      selectedDifficulty === d
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-secondary text-secondary-foreground hover:bg-accent'
                    }`}
                  >
                    {d.charAt(0).toUpperCase() + d.slice(1)}
                  </button>
                ))}
              </div>
            </div>
            <Button onClick={handleGenerate} loading={loading}>
              <RefreshCw className="h-4 w-4 mr-1" />
              Generate Exercises
            </Button>
          </div>
        </CardContent>
      </Card>

      {loading ? (
        <Card><CardContent className="flex items-center justify-center py-12"><Spinner size="lg" /></CardContent></Card>
      ) : exercises.length > 0 ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {exercises.map((exercise) => (
            <ExerciseCard key={exercise.id} exercise={exercise} onStart={handleStart} />
          ))}
        </div>
      ) : generated ? (
        <Card>
          <CardContent className="py-12 text-center">
            <FileCode className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-muted-foreground">No exercises generated. Try a different topic or difficulty.</p>
          </CardContent>
        </Card>
      ) : null}
    </div>
  )
}
