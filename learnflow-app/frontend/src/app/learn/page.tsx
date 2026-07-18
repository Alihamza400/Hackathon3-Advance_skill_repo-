'use client'

import { useState, useCallback } from 'react'
import { motion } from 'framer-motion'
import { useSearchParams } from 'next/navigation'
import { ChatInterface } from '@/components/learn/ChatInterface'
import { ConceptViewer } from '@/components/learn/ConceptViewer'
import { CodeEditor } from '@/components/learn/CodeEditor'
import { MessageSquare, BookOpen, Code, Sparkles } from 'lucide-react'

type Tab = 'chat' | 'concepts' | 'editor'

export default function LearnPage() {
  const searchParams = useSearchParams()
  const initialConcept = searchParams.get('concept') || ''
  const [activeTab, setActiveTab] = useState<Tab>(initialConcept ? 'concepts' : 'chat')
  const tabs: { id: Tab; label: string; icon: typeof MessageSquare }[] = [
    { id: 'chat', label: 'AI Chat', icon: MessageSquare },
    { id: 'concepts', label: 'Concepts', icon: BookOpen },
    { id: 'editor', label: 'Code Editor', icon: Code },
  ]

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <div className="mb-2 inline-flex items-center gap-1.5 rounded-full border border-blue-500/20 bg-gradient-to-r from-blue-500/10 to-purple-500/10 px-3 py-1 text-xs">
          <Sparkles className="h-3 w-3 text-blue-500" />
          <span className="bg-gradient-to-r from-blue-500 to-purple-500 bg-clip-text text-transparent font-medium">Learning Studio</span>
        </div>
        <h1 className="text-3xl font-bold">Learning Studio</h1>
        <p className="text-muted-foreground">Chat with AI, explore concepts, and write code</p>
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
        className="flex gap-1 p-1 rounded-xl bg-gradient-to-r from-blue-500/10 via-secondary to-purple-500/10 w-fit shadow-inner">
        {tabs.map(({ id, label, icon: Icon }) => (
          <button key={id} onClick={() => setActiveTab(id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${
              activeTab === id ? 'bg-background text-foreground shadow-md' : 'text-muted-foreground hover:text-foreground hover:bg-white/50 dark:hover:bg-white/5'
            }`}
          ><Icon className="h-4 w-4" />{label}</button>
        ))}
      </motion.div>

      <motion.div key={activeTab} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.2 }}>
        {activeTab === 'chat' && <ChatInterface />}
        {activeTab === 'concepts' && <ConceptViewer initialConcept={initialConcept} />}
        {activeTab === 'editor' && (
          <div className="relative overflow-hidden rounded-2xl border border-white/20 bg-gradient-to-br from-white/80 to-white/40 dark:from-white/5 dark:to-white/[0.02] backdrop-blur-xl p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-blue-600 to-purple-600 shadow-lg">
                <Code className="h-4 w-4 text-white" />
              </div>
              <div><h3 className="font-semibold">Python Playground</h3><p className="text-xs text-muted-foreground">Safe sandboxed execution</p></div>
            </div>
            <CodeEditor />
          </div>
        )}
      </motion.div>
    </div>
  )
}
