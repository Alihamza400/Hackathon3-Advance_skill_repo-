'use client'

import { Card, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card'
import { CodeEditor } from '@/components/learn/CodeEditor'
import { Code } from 'lucide-react'

export default function CodeEditorPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Code Editor</h1>
        <p className="text-muted-foreground">Write, run, and test Python code in your browser</p>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Code className="h-5 w-5 text-primary" />
            <CardTitle>Python Playground</CardTitle>
            <CardDescription>Safe sandboxed execution environment</CardDescription>
          </div>
        </CardHeader>
      </Card>

      <CodeEditor height="500px" />
    </div>
  )
}
