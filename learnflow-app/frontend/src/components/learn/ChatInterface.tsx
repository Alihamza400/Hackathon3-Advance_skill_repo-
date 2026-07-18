'use client'

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { GlassCard } from '@/components/ui/GlassCard'
import { GlowButton } from '@/components/ui/GlowButton'
import { api } from '@/lib/api'
import { formatRelativeTime } from '@/lib/utils'
import { Send, Bot, User, Sparkles } from 'lucide-react'
import type { ChatMessage } from '@/types'

const quickPrompts = [
  'explain polymorphism', 'debug: print(1/0)',
  'how do lists work?', 'generate exercise on functions',
]

export function ChatInterface() {
  const [messages, setMessages] = useState<ChatMessage[]>([{
    id: 'welcome',
    role: 'assistant',
    content: '## 🎓 LearnFlow AI Tutor\n\nI can help you:\n- **Explain** anything — "explain polymorphism"\n- **Debug** code — paste code with errors\n- **Practice** — "generate an exercise on lists"\n\nPowered by AI via OpenRouter. Ask anything!',
    timestamp: new Date().toISOString(),
  }])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  async function handleSend() {
    const query = input.trim()
    if (!query || loading) return

    const userMsg: ChatMessage = { id: Date.now().toString(), role: 'user', content: query, timestamp: new Date().toISOString() }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      const token = localStorage.getItem('access_token')
      const resp = await fetch('/api/concepts/explain', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ concept: query.replace(/^(explain|what is|how does|tell me about)\s+/i, '').trim(), level: 'beginner' }),
      })

      if (resp.ok) {
        const data = await resp.json()
        const e = data.explanation
        let content = `## 📚 ${e.concept.charAt(0).toUpperCase() + e.concept.slice(1)}\n\n**${e.definition}**\n\n${e.explanation}\n`
        if (e.code_examples?.length) {
          content += '\n### Code Examples\n'
          for (const ex of e.code_examples) content += `\n**${ex.title}**\n\`\`\`python\n${ex.code}\n\`\`\`\n${ex.explanation}\n`
        }
        if (e.key_points?.length) content += `\n### Key Points\n- ${e.key_points.slice(0, 3).join('\n- ')}\n`
        if (e.related_concepts?.length) content += `\n*Related: ${e.related_concepts.join(', ')}*\n`
        content += `\n---\n*${e.metadata?.source === 'llm' ? '🤖 AI-generated' : '📖 From knowledge base'}*`
        setMessages(prev => [...prev, { id: (Date.now() + 1).toString(), role: 'assistant', content, timestamp: new Date().toISOString() }])
      } else {
        setMessages(prev => [...prev, {
          id: (Date.now() + 1).toString(), role: 'assistant',
          content: 'I couldn\'t find that concept. Try being more specific, or ask me about variables, functions, classes, decorators, recursion, etc.',
          timestamp: new Date().toISOString(),
        }])
      }
    } catch (e) {
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(), role: 'assistant',
        content: e instanceof Error ? `Error: ${e.message}` : 'Something went wrong.',
        timestamp: new Date().toISOString(),
      }])
    } finally { setLoading(false) }
  }

  return (
    <GlassCard className="flex flex-col h-[600px]">
      <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-hide">
        <AnimatePresence>
          {messages.map((msg) => (
            <motion.div key={msg.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
              className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : ''}`}>
              {msg.role !== 'user' && (
                <div className="h-8 w-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center flex-shrink-0 shadow-md">
                  <Bot className="h-4 w-4 text-white" />
                </div>
              )}
              <div className={`max-w-[80%] ${msg.role === 'user' ? 'order-1' : ''}`}>
                <div className={`rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                  msg.role === 'user'
                    ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white'
                    : 'bg-secondary/80 border border-white/10'
                }`}>
                  <div className="prose prose-sm max-w-none whitespace-pre-wrap [&_code]:bg-muted [&_code]:px-1 [&_code]:rounded [&_pre]:bg-muted [&_pre]:p-3 [&_pre]:rounded-lg">{msg.content}</div>
                </div>
                <p className={`text-xs text-muted-foreground mt-1 ${msg.role === 'user' ? 'text-right' : ''}`}>
                  {formatRelativeTime(msg.timestamp)}
                </p>
              </div>
              {msg.role === 'user' && (
                <div className="h-8 w-8 rounded-full bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center flex-shrink-0 shadow-md">
                  <User className="h-4 w-4 text-white" />
                </div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>

        {loading && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex gap-3">
            <div className="h-8 w-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center">
              <Bot className="h-4 w-4 text-white" />
            </div>
            <div className="bg-secondary/80 rounded-2xl px-4 py-3 text-sm border border-white/10 flex items-center gap-3">
              <div className="flex gap-1">
                <span className="h-2 w-2 rounded-full bg-blue-500 animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="h-2 w-2 rounded-full bg-purple-500 animate-bounce" style={{ animationDelay: '150ms' }} />
                <span className="h-2 w-2 rounded-full bg-blue-500 animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
              AI is thinking...
            </div>
          </motion.div>
        )}

        {/* Quick prompts */}
        {messages.length === 1 && !loading && (
          <div className="flex flex-wrap gap-2 pt-2">
            {quickPrompts.map(p => (
              <button key={p} onClick={() => { setInput(p); setTimeout(handleSend, 100) }}
                className="px-3 py-1.5 rounded-full bg-secondary/60 border border-white/10 text-xs text-muted-foreground hover:text-foreground hover:bg-accent transition-all">
                {p}
              </button>
            ))}
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="border-t border-white/10 p-4">
        <div className="flex gap-2">
          <input type="text" value={input} onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSend()}
            placeholder="Ask about any Python concept..."
            className="flex-1 h-12 rounded-xl border border-white/20 bg-gradient-to-r from-white/50 to-white/30 dark:from-white/5 dark:to-white/[0.02] backdrop-blur px-4 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/50"
            disabled={loading} />
          <GlowButton onClick={handleSend} disabled={loading || !input.trim()} size="sm">
            <Send className="h-4 w-4" />
          </GlowButton>
        </div>
      </div>
    </GlassCard>
  )
}
