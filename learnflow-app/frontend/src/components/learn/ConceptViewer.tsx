'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { GlassCard } from '@/components/ui/GlassCard'
import { GlowButton } from '@/components/ui/GlowButton'
import { api } from '@/lib/api'
import { BookOpen, ChevronRight, Lightbulb, AlertTriangle, ArrowRight, Sparkles, Play, RotateCcw, Code } from 'lucide-react'
import type { ExplainResponse, DifficultyLevel, CodeExecutionResult } from '@/types'

const allTopics = ['variable', 'function', 'loop', 'conditional', 'list', 'string', 'dictionary', 'class', 'module', 'exception', 'file_io', 'lambda', 'comprehensions', 'decorator', 'recursion']
const levels: DifficultyLevel[] = ['beginner', 'intermediate', 'advanced']

export function ConceptViewer({ initialConcept }: { initialConcept?: string }) {
  const [concept, setConcept] = useState(initialConcept || '')
  const [level, setLevel] = useState<DifficultyLevel>('beginner')
  const [result, setResult] = useState<ExplainResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [runCode, setRunCode] = useState('')
  const [runResult, setRunResult] = useState<CodeExecutionResult | null>(null)
  const [running, setRunning] = useState(false)
  const [showRunner, setShowRunner] = useState(false)

  async function handleExplain() {
    if (!concept.trim()) return
    setLoading(true)
    setError(null)
    setRunResult(null)
    try {
      const res = await api.explainConcept(concept, level)
      setResult(res)
      const firstExample = res.explanation.code_examples?.[0]
      if (firstExample) setRunCode(firstExample.code)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to get explanation')
    } finally {
      setLoading(false)
    }
  }

  async function handleRun() {
    setRunning(true)
    setRunResult(null)
    try {
      const res = await api.executeCode(runCode)
      setRunResult(res)
    } catch {
      setRunResult({ stdout: '', stderr: 'Execution failed', exit_code: -1, execution_time_ms: 0, output: '' })
    } finally {
      setRunning(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Search */}
      <GlassCard>
        <div className="p-6">
          <h3 className="font-semibold mb-4 flex items-center gap-2">
            <BookOpen className="h-5 w-5 text-blue-500" />
            Learn a Python Concept
          </h3>
          <div className="flex gap-3 flex-wrap sm:flex-nowrap">
            <div className="relative flex-1 w-full">
              <input type="text" value={concept} onChange={e => setConcept(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleExplain()}
                placeholder="Type any Python concept — variable, class, lambda, decorator..."
                className="w-full h-12 rounded-xl border border-white/20 bg-gradient-to-r from-white/50 to-white/30 dark:from-white/5 dark:to-white/[0.02] backdrop-blur px-4 pr-10 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/50"
              />
              <kbd className="absolute right-3 top-1/2 -translate-y-1/2 hidden sm:inline-flex items-center gap-1 rounded-md border px-1.5 py-0.5 text-xs text-muted-foreground">
                ↵
              </kbd>
            </div>
            <GlowButton onClick={handleExplain} loading={loading}>
              <Sparkles className="h-4 w-4 mr-1.5" />
              Explain
            </GlowButton>
          </div>

          {/* Quick topic pills */}
          <div className="flex flex-wrap gap-1.5 mt-3">
            {allTopics.map(t => (
              <button key={t} onClick={() => { setConcept(t); setTimeout(handleExplain, 50) }}
                className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-all ${
                  concept === t ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-md' : 'bg-secondary text-muted-foreground hover:bg-accent'
                }`}>
                {t.replace(/_/g, ' ')}
              </button>
            ))}
          </div>

          {/* Level selector */}
          <div className="flex gap-2 mt-3">
            {levels.map(l => (
              <button key={l} onClick={() => setLevel(l)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  level === l ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-sm' : 'bg-secondary text-muted-foreground hover:bg-accent'
                }`}>
                {l.charAt(0).toUpperCase() + l.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </GlassCard>

      {/* Loading */}
      <AnimatePresence>
        {loading && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <GlassCard>
              <div className="flex items-center justify-center py-12">
                <div className="flex flex-col items-center gap-3">
                  <div className="relative">
                    <div className="h-10 w-10 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />
                    <div className="absolute inset-0 h-10 w-10 animate-ping rounded-full bg-blue-500/10" />
                  </div>
                  <p className="text-sm text-muted-foreground animate-pulse">Loading explanation...</p>
                </div>
              </div>
            </GlassCard>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Error */}
      {error && (
        <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }}>
          <GlassCard>
            <div className="p-4 text-sm text-red-500 flex items-center gap-2">
              <AlertTriangle className="h-4 w-4" /> {error}
            </div>
          </GlassCard>
        </motion.div>
      )}

      {/* Result */}
      <AnimatePresence mode="wait">
        {result && (
          <motion.div key={result.explanation.concept} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="space-y-4">
            {/* Definition header */}
            <GlassCard>
              <div className="p-6">
                <div className="flex items-center gap-3 mb-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-purple-500 shadow-lg">
                    <BookOpen className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h2 className="text-2xl font-bold capitalize">{result.explanation.concept.replace(/_/g, ' ')}</h2>
                      <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-gradient-to-r from-blue-500/20 to-purple-500/20 text-blue-600 dark:text-blue-400">
                        {result.explanation.level}
                      </span>
                    </div>
                    <p className="text-muted-foreground">{result.explanation.definition}</p>
                  </div>
                </div>
                <p className="text-sm leading-relaxed">{result.explanation.explanation}</p>
              </div>
            </GlassCard>

            {/* Key Points + Analogies row */}
            <div className="grid gap-4 sm:grid-cols-2">
              {result.explanation.key_points.length > 0 && (
                <GlassCard>
                  <div className="p-5">
                    <h4 className="text-sm font-semibold mb-3 flex items-center gap-1.5">
                      <Sparkles className="h-4 w-4 text-blue-500" /> Key Points
                    </h4>
                    <ul className="space-y-2">
                      {result.explanation.key_points.map((p, i) => (
                        <motion.li key={i} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.05 }}
                          className="text-sm text-muted-foreground flex items-start gap-2">
                          <span className="mt-0.5 flex h-5 w-5 items-center justify-center rounded-full bg-gradient-to-r from-blue-500/20 to-purple-500/20 text-xs text-blue-500">
                            {i + 1}
                          </span>
                          {p}
                        </motion.li>
                      ))}
                    </ul>
                  </div>
                </GlassCard>
              )}
              {result.explanation.analogies.length > 0 && (
                <GlassCard>
                  <div className="p-5">
                    <h4 className="text-sm font-semibold mb-3 flex items-center gap-1.5">
                      <Lightbulb className="h-4 w-4 text-amber-500" /> Analogies
                    </h4>
                    <ul className="space-y-2">
                      {result.explanation.analogies.map((a, i) => (
                        <motion.li key={i} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.08 }}
                          className="text-sm text-muted-foreground flex items-start gap-2">
                          <ChevronRight className="h-4 w-4 mt-0.5 text-amber-500 flex-shrink-0" />
                          {a}
                        </motion.li>
                      ))}
                    </ul>
                  </div>
                </GlassCard>
              )}
            </div>

            {/* Code Examples with Live Runner */}
            {result.explanation.code_examples.length > 0 && (
              <GlassCard>
                <div className="p-5">
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="text-sm font-semibold flex items-center gap-1.5">
                      <Code className="h-4 w-4 text-emerald-500" /> Code Examples
                    </h4>
                    <button onClick={() => setShowRunner(!showRunner)}
                      className="text-xs text-blue-500 hover:underline flex items-center gap-1">
                      <Play className="h-3 w-3" /> {showRunner ? 'Hide Runner' : 'Run Live'}
                    </button>
                  </div>
                  <div className="space-y-3">
                    {result.explanation.code_examples.map((ex, i) => (
                      <div key={i}>
                        <div className="flex items-center justify-between mb-1">
                          <p className="text-sm font-medium">{ex.title}</p>
                          <button onClick={() => { setRunCode(ex.code); setShowRunner(true) }}
                            className="text-xs text-muted-foreground hover:text-foreground flex items-center gap-1">
                            <Play className="h-3 w-3" /> Try it
                          </button>
                        </div>
                        <pre className="bg-secondary/80 rounded-xl p-4 text-sm font-mono overflow-x-auto border border-white/10 cursor-pointer hover:border-blue-500/30 transition-colors"
                          onClick={() => { setRunCode(ex.code); setShowRunner(true) }}>
                          <code>{ex.code}</code>
                        </pre>
                        <p className="text-xs text-muted-foreground mt-1">{ex.explanation}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </GlassCard>
            )}

            {/* Live Code Runner */}
            <AnimatePresence>
              {showRunner && (
                <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }}>
                  <GlassCard>
                    <div className="p-5">
                      <h4 className="text-sm font-semibold mb-3 flex items-center gap-1.5">
                        <Play className="h-4 w-4 text-emerald-500" /> Live Python Runner
                      </h4>
                      <textarea value={runCode} onChange={e => setRunCode(e.target.value)}
                        className="w-full h-32 rounded-xl border border-white/10 bg-secondary/50 p-4 text-sm font-mono focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500/50 resize-y"
                        spellCheck={false} />
                      <div className="flex items-center gap-2 mt-3">
                        <GlowButton onClick={handleRun} loading={running} size="sm">
                          <Play className="h-4 w-4 mr-1" />
                          Run
                        </GlowButton>
                        <button onClick={() => { setRunCode(result.explanation.code_examples[0]?.code || ''); setRunResult(null) }}
                          className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium bg-secondary text-muted-foreground hover:bg-accent transition-colors">
                          <RotateCcw className="h-3 w-3" /> Reset
                        </button>
                      </div>
                      {runResult && (
                        <div className="mt-3 space-y-1">
                          {runResult.stdout && (
                            <div className="rounded-xl bg-secondary/50 border border-white/10 p-3">
                              <p className="text-xs font-medium text-muted-foreground mb-1">Output</p>
                              <pre className="text-sm font-mono whitespace-pre-wrap">{runResult.stdout}</pre>
                            </div>
                          )}
                          {runResult.stderr && (
                            <div className="rounded-xl bg-red-50 dark:bg-red-500/10 border border-red-500/20 p-3">
                              <p className="text-xs font-medium text-red-500 mb-1">Error</p>
                              <pre className="text-sm text-red-600 font-mono whitespace-pre-wrap">{runResult.stderr}</pre>
                            </div>
                          )}
                          {runResult.execution_time_ms > 0 && (
                            <p className="text-xs text-muted-foreground">Completed in {runResult.execution_time_ms}ms</p>
                          )}
                        </div>
                      )}
                    </div>
                  </GlassCard>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Common Mistakes + Related Concepts row */}
            <div className="grid gap-4 sm:grid-cols-2">
              {result.explanation.common_mistakes.length > 0 && (
                <GlassCard>
                  <div className="p-5">
                    <h4 className="text-sm font-semibold mb-3 flex items-center gap-1.5">
                      <AlertTriangle className="h-4 w-4 text-red-500" /> Common Mistakes
                    </h4>
                    <ul className="space-y-1.5">
                      {result.explanation.common_mistakes.map((m, i) => (
                        <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                          <span className="mt-0.5 text-red-400">!</span>
                          {m}
                        </li>
                      ))}
                    </ul>
                  </div>
                </GlassCard>
              )}
              {result.explanation.related_concepts.length > 0 && (
                <GlassCard>
                  <div className="p-5">
                    <h4 className="text-sm font-semibold mb-3">Related Concepts</h4>
                    <div className="flex flex-wrap gap-2">
                      {result.explanation.related_concepts.map((c, i) => (
                        <motion.div key={c} initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: i * 0.05 }}>
                          <button onClick={() => { setConcept(c); setResult(null); setTimeout(handleExplain, 50) }}
                            className="inline-flex items-center gap-1 px-3 py-1.5 rounded-full bg-gradient-to-r from-blue-500/10 to-purple-500/10 text-xs font-medium text-blue-600 dark:text-blue-400 transition-all hover:shadow-[0_0_10px_hsl(var(--primary)/0.2)] hover:scale-105">
                            {c.replace(/_/g, ' ')}
                            <ArrowRight className="h-3 w-3" />
                          </button>
                        </motion.div>
                      ))}
                    </div>
                  </div>
                </GlassCard>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
