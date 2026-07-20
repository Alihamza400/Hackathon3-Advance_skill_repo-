'use client'

import { useState } from 'react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { CodeEditor } from '@/components/learn/CodeEditor'
import { api } from '@/lib/api'
import { Lightbulb, CheckCircle, XCircle, Target, Code } from 'lucide-react'
import type { Exercise, ExerciseResult, TestResult } from '@/types'

interface ExerciseViewProps {
  exercise: Exercise
  onBack: () => void
}

export function ExerciseView({ exercise, onBack }: ExerciseViewProps) {
  const [code, setCode] = useState(exercise.starter_code || '# Write your solution here\n')
  const [result, setResult] = useState<ExerciseResult | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [hintIndex, setHintIndex] = useState(-1)
  const [showHints, setShowHints] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit() {
    setSubmitting(true)
    setError(null)
    setResult(null)
    try {
      const res = await api.submitExercise({
        exercise_id: exercise.id,
        code,
      })
      setResult(res)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Submission failed')
    } finally {
      setSubmitting(false)
    }
  }

  function showHint() {
    if (hintIndex < exercise.hints.length - 1) {
      setHintIndex(prev => prev + 1)
    }
    setShowHints(true)
  }

  const visibleTests = exercise.test_cases.filter(t => !t.hidden)

  return (
    <div className="space-y-4">
      <Button variant="ghost" size="sm" onClick={onBack}>← Back to exercises</Button>

      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <CardTitle>{exercise.title}</CardTitle>
              <CardDescription>{exercise.description}</CardDescription>
            </div>
            <Badge variant={exercise.difficulty === 'beginner' ? 'success' : exercise.difficulty === 'intermediate' ? 'warning' : 'error'}>
              {exercise.difficulty}
            </Badge>
          </div>
        </CardHeader>
      </Card>

      {visibleTests.length > 0 && (
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Target className="h-4 w-4 text-emerald-500" />
              <CardTitle className="text-base">Problem: Expected Behavior</CardTitle>
            </div>
            <CardDescription>
              Your code will be tested against these cases. Make sure it produces the correct output for each.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {visibleTests.map((test, i) => (
                <div key={i} className="rounded-lg border bg-card p-3 text-sm">
                  <p className="font-medium mb-1">{test.description || `Test ${i + 1}`}</p>
                  <div className="grid grid-cols-2 gap-2 text-xs text-muted-foreground">
                    <div>
                      <span className="font-medium text-foreground">Input:</span>{' '}
                      <code className="bg-secondary px-1 rounded">
                        {Object.keys(test.input).length > 0
                          ? Object.entries(test.input).map(([k, v]) => `${k} = ${JSON.stringify(v)}`).join(', ')
                          : '(none)'}
                      </code>
                    </div>
                    <div>
                      <span className="font-medium text-foreground">Expected:</span>{' '}
                      <code className="bg-secondary px-1 rounded">{String(test.expected_output ?? '')}</code>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Code className="h-4 w-4 text-blue-500" />
            <CardTitle className="text-base">Your Solution</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          <CodeEditor
            initialCode={code}
            onChange={setCode}
            height="350px"
          />
        </CardContent>
      </Card>

      <div className="flex items-center gap-2">
        <Button onClick={handleSubmit} loading={submitting}>
          Submit Solution
        </Button>
        <Button variant="outline" size="sm" onClick={showHint} disabled={hintIndex >= exercise.hints.length - 1}>
          <Lightbulb className="h-4 w-4 mr-1" />
          Hint
        </Button>
      </div>

      {showHints && hintIndex >= 0 && (
        <Card className="border-yellow-500/50 bg-yellow-50 dark:bg-yellow-500/10">
          <CardContent className="p-4">
            <p className="text-sm font-medium flex items-center gap-1 text-yellow-700 dark:text-yellow-400">
              <Lightbulb className="h-4 w-4" />
              Hint {hintIndex + 1}/{exercise.hints.length}
            </p>
            <p className="text-sm mt-1">{exercise.hints[hintIndex]}</p>
          </CardContent>
        </Card>
      )}

      {error && (
        <Card className="border-error-500/50">
          <CardContent className="p-4 text-sm text-error-600">{error}</CardContent>
        </Card>
      )}

      {result && (
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              {result.passed ? (
                <CheckCircle className="h-5 w-5 text-success-500" />
              ) : (
                <XCircle className="h-5 w-5 text-error-500" />
              )}
              <CardTitle className="text-lg">
                {result.passed ? 'All Tests Passed!' : 'Some Tests Failed'}
              </CardTitle>
              <Badge variant={result.passed ? 'success' : 'error'}>
                {result.passed_tests}/{result.total_tests} passed
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-3">Score: {Math.round(result.score)}%</p>
            <div className="space-y-2">
              {result.test_results.map((test, i) => (
                <div key={i} className="flex items-start gap-2 text-sm">
                  {test.passed ? (
                    <CheckCircle className="h-4 w-4 text-success-500 mt-0.5 flex-shrink-0" />
                  ) : (
                    <XCircle className="h-4 w-4 text-error-500 mt-0.5 flex-shrink-0" />
                  )}
                  <div>
                    <p className="font-medium">{test.test_case?.description || `Test ${i + 1}`}</p>
                    {!test.passed && (
                      <div className="text-xs text-muted-foreground mt-1 space-y-1">
                        <p>Expected: <code className="bg-secondary px-1 rounded">{String(test.test_case?.expected_output ?? '')}</code></p>
                        <p>Actual: <code className="bg-secondary px-1 rounded">{test.actual_output}</code></p>
                        {test.error && <p className="text-error-500">{test.error}</p>}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
            {result.feedback && (
              <div className="mt-4 p-3 rounded-lg bg-secondary">
                <p className="text-sm font-medium mb-1">Feedback</p>
                <p className="text-sm text-muted-foreground">{result.feedback}</p>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
