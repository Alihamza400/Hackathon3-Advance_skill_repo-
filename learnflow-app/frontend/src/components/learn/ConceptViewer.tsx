'use client'

import { useState } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Spinner } from '@/components/ui/Spinner'
import { api } from '@/lib/api'
import { BookOpen, ChevronRight, Lightbulb, AlertTriangle, ArrowRight } from 'lucide-react'
import type { ExplainResponse, DifficultyLevel } from '@/types'

interface ConceptViewerProps {
  initialConcept?: string
}

export function ConceptViewer({ initialConcept }: ConceptViewerProps) {
  const [concept, setConcept] = useState(initialConcept || '')
  const [level, setLevel] = useState<DifficultyLevel>('beginner')
  const [result, setResult] = useState<ExplainResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleExplain() {
    if (!concept.trim()) return
    setLoading(true)
    setError(null)
    try {
      const res = await api.explainConcept(concept, level)
      setResult(res)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to get explanation')
    } finally {
      setLoading(false)
    }
  }

  const levels: DifficultyLevel[] = ['beginner', 'intermediate', 'advanced']

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader><CardTitle>Learn a Concept</CardTitle></CardHeader>
        <CardContent>
          <div className="flex gap-3">
            <div className="flex-1">
              <input
                type="text"
                value={concept}
                onChange={e => setConcept(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleExplain()}
                placeholder="e.g., variables, functions, loops, conditionals"
                className="w-full h-10 rounded-lg border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              />
            </div>
            <Button onClick={handleExplain} loading={loading}>
              <BookOpen className="h-4 w-4 mr-1" />
              Explain
            </Button>
          </div>

          <div className="flex gap-2 mt-3">
            {levels.map(l => (
              <button
                key={l}
                onClick={() => setLevel(l)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                  level === l
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-secondary text-secondary-foreground hover:bg-accent'
                }`}
              >
                {l.charAt(0).toUpperCase() + l.slice(1)}
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      {loading && (
        <Card><CardContent className="flex items-center justify-center py-8"><Spinner /></CardContent></Card>
      )}

      {error && (
        <Card className="border-error-500/50">
          <CardContent className="p-4 text-sm text-error-600">{error}</CardContent>
        </Card>
      )}

      {result && (
        <div className="space-y-4 animate-in">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <CardTitle className="capitalize">{result.explanation.concept}</CardTitle>
                <Badge variant="primary">{result.explanation.level}</Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <p className="text-lg font-medium mb-2">{result.explanation.definition}</p>
                <p className="text-muted-foreground">{result.explanation.explanation}</p>
              </div>

              {result.explanation.analogies.length > 0 && (
                <div>
                  <h4 className="flex items-center gap-2 text-sm font-medium mb-2">
                    <Lightbulb className="h-4 w-4 text-yellow-500" /> Analogies
                  </h4>
                  <ul className="space-y-1">
                    {result.explanation.analogies.map((a, i) => (
                      <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                        <ChevronRight className="h-4 w-4 mt-0.5 flex-shrink-0" />
                        {a}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {result.explanation.key_points.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium mb-2">Key Points</h4>
                  <ul className="space-y-1">
                    {result.explanation.key_points.map((p, i) => (
                      <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                        <span className="text-primary mt-1">•</span>
                        {p}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {result.explanation.code_examples.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium mb-2">Code Examples</h4>
                  {result.explanation.code_examples.map((ex, i) => (
                    <div key={i} className="mb-3">
                      <p className="text-sm font-medium mb-1">{ex.title}</p>
                      <pre className="bg-secondary rounded-lg p-3 text-sm font-mono overflow-x-auto">
                        <code>{ex.code}</code>
                      </pre>
                      <p className="text-xs text-muted-foreground mt-1">{ex.explanation}</p>
                    </div>
                  ))}
                </div>
              )}

              {result.explanation.common_mistakes.length > 0 && (
                <div>
                  <h4 className="flex items-center gap-2 text-sm font-medium mb-2">
                    <AlertTriangle className="h-4 w-4 text-yellow-500" /> Common Mistakes
                  </h4>
                  <ul className="space-y-1">
                    {result.explanation.common_mistakes.map((m, i) => (
                      <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                        <span className="text-yellow-500 mt-1">!</span>
                        {m}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="flex flex-wrap gap-2">
                {result.explanation.related_concepts.map((c) => (
                  <button
                    key={c}
                    onClick={() => { setConcept(c); setResult(null) }}
                    className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-secondary text-xs font-medium hover:bg-accent transition-colors"
                  >
                    {c.replace(/_/g, ' ')}
                    <ArrowRight className="h-3 w-3" />
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
