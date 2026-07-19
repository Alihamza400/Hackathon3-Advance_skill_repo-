'use client'

import { useState, useCallback } from 'react'
import dynamic from 'next/dynamic'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import { Spinner } from '@/components/ui/Spinner'
import { api } from '@/lib/api'
import { Play, RotateCcw, Loader2 } from 'lucide-react'
import type { CodeExecutionResult } from '@/types'

const MonacoEditor = dynamic(() => import('@monaco-editor/react'), {
  loading: () => (
    <div className="h-64 flex items-center justify-center bg-secondary/50 rounded-lg">
      <Spinner />
    </div>
  ),
  ssr: false,
})

interface CodeEditorProps {
  initialCode?: string
  readOnly?: boolean
  onChange?: (code: string) => void
  height?: string
  language?: string
  showControls?: boolean
}

export function CodeEditor({
  initialCode = '# Write your Python code here\n',
  readOnly = false,
  onChange,
  height = '400px',
  language = 'python',
  showControls = true,
}: CodeEditorProps) {
  const [code, setCode] = useState(initialCode)
  const [result, setResult] = useState<CodeExecutionResult | null>(null)
  const [executing, setExecuting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleChange = useCallback((value: string | undefined) => {
    const newCode = value || ''
    setCode(newCode)
    onChange?.(newCode)
  }, [onChange])

  const handleRun = async () => {
    setExecuting(true)
    setError(null)
    setResult(null)
    try {
      const res = await api.executeCode(code)
      setResult(res)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Execution failed')
    } finally {
      setExecuting(false)
    }
  }

  const handleReset = () => {
    setCode(initialCode)
    setResult(null)
    setError(null)
  }

  return (
    <div className="space-y-3">
      <div className="rounded-lg border overflow-hidden">
        <MonacoEditor
          height={height}
          language={language}
          value={code}
          onChange={handleChange}
          options={{
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
            fontSize: 14,
            lineNumbers: 'on',
            readOnly,
            automaticLayout: true,
            tabSize: 4,
            wordWrap: 'on',
            theme: 'vs-dark',
          }}
        />
      </div>

      {showControls && (
        <div className="flex items-center gap-2">
          <Button onClick={handleRun} loading={executing} size="sm">
            <Play className="h-4 w-4 mr-1" />
            Run
          </Button>
          <Button variant="ghost" size="sm" onClick={handleReset}>
            <RotateCcw className="h-4 w-4 mr-1" />
            Reset
          </Button>
          {executing && (
            <span className="text-sm text-muted-foreground flex items-center gap-1">
              <Loader2 className="h-3 w-3 animate-spin" /> Executing...
            </span>
          )}
        </div>
      )}

      {error && (
        <Card className="p-4 border-error-500/50 bg-error-50 dark:bg-error-500/10">
          <pre className="text-sm text-error-600 whitespace-pre-wrap font-mono">{error}</pre>
        </Card>
      )}

      {result && (
        <div className="space-y-2">
          {result.stdout && (
            <Card className="p-4">
              <p className="text-xs font-medium text-muted-foreground mb-1">Output</p>
              <pre className="text-sm font-mono whitespace-pre-wrap">{result.stdout}</pre>
            </Card>
          )}
          {result.stderr && (
            <Card className="p-4 border-error-500/50 bg-error-50 dark:bg-error-500/10">
              <p className="text-xs font-medium text-error-600 mb-1">Error</p>
              <pre className="text-sm text-error-600 font-mono whitespace-pre-wrap">{result.stderr}</pre>
            </Card>
          )}
          {result.execution_time_ms > 0 && (
            <p className="text-xs text-muted-foreground">
              Completed in {result.execution_time_ms}ms (exit code: {result.returncode})
            </p>
          )}
        </div>
      )}
    </div>
  )
}
