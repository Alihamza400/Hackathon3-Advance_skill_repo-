'use client'

import { useState, useCallback } from 'react'
import { useSearchParams } from 'next/navigation'
import { ChatInterface } from '@/components/learn/ChatInterface'
import { ConceptViewer } from '@/components/learn/ConceptViewer'
import { CodeEditor } from '@/components/learn/CodeEditor'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { MessageSquare, BookOpen, Code } from 'lucide-react'

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

  const handleTabChange = useCallback((tab: Tab) => {
    setActiveTab(tab)
  }, [])

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Learning Studio</h1>
        <p className="text-muted-foreground">Chat with AI, explore concepts, and write code</p>
      </div>

      <div className="flex gap-1 p-1 rounded-xl bg-gradient-to-r from-secondary via-secondary to-primary/5 w-fit shadow-inner">
        {tabs.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => handleTabChange(id)}
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
      </div>

      {activeTab === 'chat' && <ChatInterface />}
      {activeTab === 'concepts' && <ConceptViewer initialConcept={initialConcept} />}
      {activeTab === 'editor' && (
        <Card>
          <CardHeader>
            <CardTitle>Code Editor</CardTitle>
          </CardHeader>
          <CardContent>
            <CodeEditor />
          </CardContent>
        </Card>
      )}
    </div>
  )
}
