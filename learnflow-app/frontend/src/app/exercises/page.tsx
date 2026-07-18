'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useRouter } from 'next/navigation'
import { ExerciseCard } from '@/components/exercises/ExerciseCard'
import { api } from '@/lib/api'
import { FileCode, RefreshCw, Sparkles } from 'lucide-react'
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
    try { const r = await api.generateExercises(selectedTopic, selectedDifficulty, 3); setExercises(r); setGenerated(true) }
    catch { setExercises([]) }
    finally { setLoading(false) }
  }

  useEffect(() => { handleGenerate() }, [])
  function handleStart(id: string) { router.push(`/exercises/${id}`) }

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <div className="mb-2 inline-flex items-center gap-1.5 rounded-full border border-emerald-500/20 bg-gradient-to-r from-emerald-500/10 to-blue-500/10 px-3 py-1 text-xs">
          <Sparkles className="h-3 w-3 text-emerald-500" />
          <span className="bg-gradient-to-r from-emerald-500 to-blue-500 bg-clip-text text-transparent font-medium">Practice</span>
        </div>
        <h1 className="text-3xl font-bold">Practice Exercises</h1>
        <p className="text-muted-foreground">Generate and solve coding challenges</p>
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
        className="relative overflow-hidden rounded-2xl border border-white/20 bg-gradient-to-br from-white/80 to-white/40 dark:from-white/5 dark:to-white/[0.02] backdrop-blur-xl p-6">
        <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 via-transparent to-blue-500/5" />
        <div className="relative">
          <h3 className="font-semibold mb-4 flex items-center gap-2"><Sparkles className="h-4 w-4 text-emerald-500" /> Generate Exercises</h3>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Topic</label>
              <div className="flex flex-wrap gap-2">
                {topics.map((topic) => (
                  <button key={topic} onClick={() => setSelectedTopic(topic)}
                    className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-300 ${
                      selectedTopic === topic
                        ? 'bg-gradient-to-r from-emerald-500 to-blue-500 text-white shadow-lg'
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
                        ? 'bg-gradient-to-r from-emerald-500 to-blue-500 text-white shadow-lg'
                        : 'bg-secondary text-secondary-foreground hover:bg-accent'
                    }`}>
                    {d.charAt(0).toUpperCase() + d.slice(1)}
                  </button>
                ))}
              </div>
            </div>
            <button onClick={handleGenerate} disabled={loading}
              className="group relative inline-flex h-10 items-center justify-center overflow-hidden rounded-xl bg-gradient-to-r from-emerald-500 to-blue-600 px-5 text-sm font-medium text-white shadow-lg shadow-emerald-500/25 transition-all duration-300 hover:shadow-emerald-500/40 hover:scale-105 disabled:opacity-50">
              <span className="absolute inset-0 bg-[linear-gradient(45deg,transparent_25%,rgba(255,255,255,0.2)_50%,transparent_75%)] bg-[length:250%_250%] transition-all duration-700 group-hover:bg-[position:100%_0]" />
              <span className="relative flex items-center gap-1.5">
                {loading ? <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg> : <RefreshCw className="h-4 w-4" />}
                {loading ? 'Generating...' : 'Generate Exercises'}
              </span>
            </button>
          </div>
        </div>
      </motion.div>

      {loading ? (
        <div className="relative overflow-hidden rounded-2xl border border-white/20 bg-gradient-to-br from-white/80 to-white/40 dark:from-white/5 dark:to-white/[0.02] backdrop-blur-xl p-12 text-center">
          <div className="flex flex-col items-center gap-3">
            <div className="relative"><div className="h-10 w-10 animate-spin rounded-full border-2 border-emerald-500 border-t-transparent" /><div className="absolute inset-0 h-10 w-10 animate-ping rounded-full bg-emerald-500/10" /></div>
            <p className="text-sm text-muted-foreground animate-pulse">Generating exercises...</p>
          </div>
        </div>
      ) : exercises.length > 0 ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {exercises.map((exercise, i) => (
            <motion.div key={exercise.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}>
              <ExerciseCard exercise={exercise} onStart={handleStart} />
            </motion.div>
          ))}
        </div>
      ) : generated ? (
        <div className="relative overflow-hidden rounded-2xl border border-white/20 bg-gradient-to-br from-white/80 to-white/40 dark:from-white/5 dark:to-white/[0.02] backdrop-blur-xl p-12 text-center">
          <FileCode className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground">No exercises generated. Try a different topic or difficulty.</p>
        </div>
      ) : null}
    </div>
  )
}
