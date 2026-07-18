'use client'

import { motion } from 'framer-motion'
import { GlassCard, GlassCardContent } from '@/components/ui/GlassCard'
import { CodeEditor } from '@/components/learn/CodeEditor'
import { Code, Sparkles, Terminal } from 'lucide-react'

const container = { hidden: {}, show: { transition: { staggerChildren: 0.12 } } }
const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } }

export default function CodeEditorPage() {
  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-6">
      <motion.div variants={item}>
        <div className="mb-2 inline-flex items-center gap-1.5 rounded-full border border-primary/20 bg-primary/5 px-3 py-1 text-xs">
          <Sparkles className="h-3 w-3 text-primary" />
          <span>Code Editor</span>
        </div>
        <h1 className="text-3xl font-bold">Code Editor</h1>
        <p className="text-muted-foreground">Write, run, and test Python code in your browser</p>
      </motion.div>

      <motion.div variants={item}>
        <GlassCard>
          <GlassCardContent>
            <div className="flex items-center gap-3 mb-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-primary/20 to-primary/5 ring-1 ring-primary/20">
                <Terminal className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h3 className="text-lg font-semibold">Python Playground</h3>
                <p className="text-sm text-muted-foreground">
                  Execute code in a secure sandbox with automatic resource limits
                </p>
              </div>
            </div>
            <div className="grid grid-cols-3 gap-3 mb-4 text-xs text-muted-foreground">
              <div className="flex items-center gap-1.5 rounded-lg border px-3 py-2">
                <Code className="h-3.5 w-3.5 text-primary" />
                Python 3.12
              </div>
              <div className="flex items-center gap-1.5 rounded-lg border px-3 py-2">
                <Terminal className="h-3.5 w-3.5 text-success-500" />
                5s timeout
              </div>
              <div className="flex items-center gap-1.5 rounded-lg border px-3 py-2">
                <Code className="h-3.5 w-3.5 text-warning-500" />
                50MB memory
              </div>
            </div>
            <CodeEditor height="500px" />
          </GlassCardContent>
        </GlassCard>
      </motion.div>
    </motion.div>
  )
}
