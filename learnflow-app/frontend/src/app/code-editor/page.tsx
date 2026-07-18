'use client'

import { motion } from 'framer-motion'
import { CodeEditor } from '@/components/learn/CodeEditor'
import { Code, Sparkles, Terminal, Shield } from 'lucide-react'

export default function CodeEditorPage() {
  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <div className="mb-2 inline-flex items-center gap-1.5 rounded-full border border-amber-500/20 bg-gradient-to-r from-amber-500/10 to-rose-500/10 px-3 py-1 text-xs">
          <Sparkles className="h-3 w-3 text-amber-500" />
          <span className="bg-gradient-to-r from-amber-500 to-rose-500 bg-clip-text text-transparent font-medium">Code Editor</span>
        </div>
        <h1 className="text-3xl font-bold">Code Editor</h1>
        <p className="text-muted-foreground">Write, run, and test Python code in your browser</p>
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
        className="relative overflow-hidden rounded-2xl border border-white/20 bg-gradient-to-br from-white/80 to-white/40 dark:from-white/5 dark:to-white/[0.02] backdrop-blur-xl p-6">
        <div className="absolute inset-0 bg-gradient-to-br from-amber-500/5 via-transparent to-rose-500/5" />
        <div className="relative">
          <div className="flex items-center gap-3 mb-4">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-amber-500 to-rose-500 shadow-lg">
              <Terminal className="h-5 w-5 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-semibold">Python Playground</h3>
              <p className="text-sm text-muted-foreground">Execute code in a secure sandbox with automatic resource limits</p>
            </div>
          </div>
          <div className="grid grid-cols-3 gap-3 mb-4">
            {[
              { icon: Code, label: 'Python 3.12', gradient: 'from-blue-500 to-purple-500' },
              { icon: Terminal, label: '5s timeout', gradient: 'from-emerald-500 to-blue-500' },
              { icon: Shield, label: '50MB memory', gradient: 'from-amber-500 to-rose-500' },
            ].map(({ icon: Icon, label, gradient }) => (
              <div key={label} className="flex items-center gap-2 rounded-xl border border-white/20 bg-gradient-to-r from-white/50 to-white/30 dark:from-white/5 dark:to-white/[0.02] px-3 py-2 text-xs">
                <div className={`flex h-6 w-6 items-center justify-center rounded-md bg-gradient-to-br ${gradient}`}>
                  <Icon className="h-3 w-3 text-white" />
                </div>
                <span className="text-muted-foreground">{label}</span>
              </div>
            ))}
          </div>
          <CodeEditor height="500px" />
        </div>
      </motion.div>
    </div>
  )
}
