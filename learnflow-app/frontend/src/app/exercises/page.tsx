'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useRouter } from 'next/navigation'
import { GlassCard, GlassCardContent } from '@/components/ui/GlassCard'
import { GlowButton } from '@/components/ui/GlowButton'
import { Spinner } from '@/components/ui/Spinner'
import { ExerciseCard } from '@/components/exercises/ExerciseCard'
import { api } from '@/lib/api'
import { FileCode, RefreshCw, Sparkles } from 'lucide-react'
import type { Exercise, DifficultyLevel } from '@/types'

const topics = ['variables', 'functions', 'loops', 'conditionals', 'lists', 'strings']

const container = { hidden: {}, show: { transition: { staggerChildren: 0.08 } } }
const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } }

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
    } catch { setExercises([]) }
    finally { setLoading(false) }
  }

  useEffect(() => { handleGenerate() }, [])

  function handleStart(id: string) { router.push(`/exercises/${id}`) }

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-6">
      <motion.div variants={item}>
        <div className="mb-2 inline-flex items-center gap-1.5 rounded-full border border-primary/20 bg-primary/5 px-3 py-1 text-xs">
          <Sparkles className="h-3 w-3 text-primary" />
          <span>Practice</span>
        </div>
        <h1 className="text-3xl font-bold">Practice Exercises</h1>
        <p className="text-muted-foreground">Generate and solve coding challenges</p>
      </motion.div>

      <motion.div variants={item}>
        <GlassCard>
          <GlassCardContent>
            <h3 className="font-semibold mb-4">Generate Exercises</h3>
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium mb-2 block">Topic</label>
                <div className="flex flex-wrap gap-2">
                  {topics.map((topic) => (
                    <button key={topic} onClick={() => setSelectedTopic(topic)}
                      className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-300 ${
                        selectedTopic === topic
                          ? 'bg-primary text-primary-foreground shadow-[0_0_10px_hsl(var(--primary)/0.3)]'
                          : 'bg-secondary text-secondary-foreground hover:bg-accent'
                      }`}>
                      {topic.charAt(0).toUpperCase() + topic.slice(1)}
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">Difficulty</label>
                <div className="flex gap-2">
                  {(['beginner', 'intermediate', 'advanced'] as DifficultyLevel[]).map((d) => (
                    <button key={d} onClick={() => setSelectedDifficulty(d)}
                      className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-300 ${
                        selectedDifficulty === d
                          ? 'bg-primary text-primary-foreground shadow-[0_0_10px_hsl(var(--primary)/0.3)]'
                          : 'bg-secondary text-secondary-foreground hover:bg-accent'
                      }`}>
                      {d.charAt(0).toUpperCase() + d.slice(1)}
                    </button>
                  ))}
                </div>
              </div>
              <GlowButton onClick={handleGenerate} loading={loading}>
                <RefreshCw className="h-4 w-4 mr-1.5" />
                Generate Exercises
              </GlowButton>
            </div>
          </GlassCardContent>
        </GlassCard>
      </motion.div>

      {loading ? (
        <motion.div variants={item}>
          <GlassCard><GlassCardContent className="flex items-center justify-center py-12">
            <div className="flex flex-col items-center gap-3">
              <div className="relative">
                <div className="h-10 w-10 animate-spin rounded-full border-2 border-primary border-t-transparent" />
                <div className="absolute inset-0 h-10 w-10 animate-ping rounded-full bg-primary/10" />
              </div>
              <p className="text-sm text-muted-foreground animate-pulse">Generating exercises...</p>
            </div>
          </GlassCardContent></GlassCard>
        </motion.div>
      ) : exercises.length > 0 ? (
        <motion.div variants={item} className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {exercises.map((exercise, i) => (
            <motion.div key={exercise.id} initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}>
              <ExerciseCard exercise={exercise} onStart={handleStart} />
            </motion.div>
          ))}
        </motion.div>
      ) : generated ? (
        <motion.div variants={item}>
          <GlassCard><GlassCardContent className="py-12 text-center">
            <FileCode className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-muted-foreground">No exercises generated. Try a different topic or difficulty.</p>
          </GlassCardContent></GlassCard>
        </motion.div>
      ) : null}
    </motion.div>
  )
}
