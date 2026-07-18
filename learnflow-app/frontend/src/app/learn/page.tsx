'use client'

import { useState, useCallback } from 'react'
import { motion } from 'framer-motion'
import { useSearchParams } from 'next/navigation'
import { ChatInterface } from '@/components/learn/ChatInterface'
import { ConceptViewer } from '@/components/learn/ConceptViewer'
import { CodeEditor } from '@/components/learn/CodeEditor'
import { GlassCard, GlassCardContent } from '@/components/ui/GlassCard'
import { MessageSquare, BookOpen, Code, Sparkles } from 'lucide-react'

type Tab = 'chat' | 'concepts' | 'editor'

const container = { hidden: {}, show: { transition: { staggerChildren: 0.1 } } }
const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } }

export default function LearnPage() {
  const searchParams = useSearchParams()
  const initialConcept = searchParams.get('concept') || ''
  const [activeTab, setActiveTab] = useState<Tab>(initialConcept ? 'concepts' : 'chat')

  const tabs: { id: Tab; label: string; icon: typeof MessageSquare }[] = [
    { id: 'chat', label: 'AI Chat', icon: MessageSquare },
    { id: 'concepts', label: 'Concepts', icon: BookOpen },
    { id: 'editor', label: 'Code Editor', icon: Code },
  ]

  const handleTabChange = useCallback((tab: Tab) => setActiveTab(tab), [])

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-6">
      <motion.div variants={item}>
        <div className="mb-2 inline-flex items-center gap-1.5 rounded-full border border-primary/20 bg-primary/5 px-3 py-1 text-xs">
          <Sparkles className="h-3 w-3 text-primary" />
          <span>Learning Studio</span>
        </div>
        <h1 className="text-3xl font-bold">Learning Studio</h1>
        <p className="text-muted-foreground">Chat with AI, explore concepts, and write code</p>
      </motion.div>

      <motion.div variants={item} className="flex gap-1 p-1 rounded-xl bg-gradient-to-r from-secondary via-secondary to-primary/5 w-fit shadow-inner">
        {tabs.map(({ id, label, icon: Icon }) => (
          <button key={id} onClick={() => handleTabChange(id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${
              activeTab === id
                ? 'bg-background text-foreground shadow-md'
                : 'text-muted-foreground hover:text-foreground hover:bg-white/50 dark:hover:bg-white/5'
            }`}
          >
            <Icon className="h-4 w-4" />
            {label}
          </button>
        ))}
      </motion.div>

      <motion.div variants={item} key={activeTab}>
        {activeTab === 'chat' && <ChatInterface />}
        {activeTab === 'concepts' && <ConceptViewer initialConcept={initialConcept} />}
        {activeTab === 'editor' && (
          <GlassCard>
            <GlassCardContent>
              <div className="flex items-center gap-2 mb-4">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-primary/20 to-primary/5">
                  <Code className="h-4 w-4 text-primary" />
                </div>
                <div>
                  <h3 className="font-semibold">Python Playground</h3>
                  <p className="text-xs text-muted-foreground">Safe sandboxed execution environment</p>
                </div>
              </div>
              <CodeEditor />
            </GlassCardContent>
          </GlassCard>
        )}
      </motion.div>
    </motion.div>
  )
}
