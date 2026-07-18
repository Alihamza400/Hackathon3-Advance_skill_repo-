'use client'

import { useState, useRef, useEffect } from 'react'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Spinner } from '@/components/ui/Spinner'
import { api } from '@/lib/api'
import { formatRelativeTime } from '@/lib/utils'
import { Send, Bot, User, Lightbulb, Bug, Code, FileCode, BarChart3 } from 'lucide-react'
import type { ChatMessage, TriageResponse } from '@/types'

const queryIcons = {
  explain: Lightbulb,
  debug: Bug,
  code_review: Code,
  exercise: FileCode,
  progress: BarChart3,
  general: Bot,
}

function getQueryIcon(type: string) {
  const Icon = queryIcons[type as keyof typeof queryIcons] || Bot
  return <Icon className="h-5 w-5" />
}

export function ChatInterface() {
  const [messages, setMessages] = useState<ChatMessage[]>([{
    id: 'welcome',
    role: 'assistant',
    content: 'Hello! I\'m your AI Python tutor. Ask me anything about Python — I can explain concepts, debug code, review code, generate exercises, or track your progress. What would you like help with?',
    timestamp: new Date().toISOString(),
  }])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [thinking, setThinking] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, thinking])

  async function handleSend() {
    const query = input.trim()
    if (!query || loading) return

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: query,
      timestamp: new Date().toISOString(),
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)
    setThinking('Analyzing your query...')

    try {
      const triage: TriageResponse = await api.triageQuery({ query })
      setThinking(`Routing to ${triage.routed_to}...`)

      let responseContent = ''
      switch (triage.query_type) {
        case 'explain': {
          const explain = await api.explainConcept(query)
          responseContent = formatExplanation(explain)
          break
        }
        case 'debug': {
          const debug = await api.debugCode(query)
          responseContent = formatDebugResult(debug)
          break
        }
        case 'code_review': {
          const review = await api.reviewCode(query)
          responseContent = formatCodeReview(review)
          break
        }
        case 'exercise': {
          const exercises = await api.generateExercises('python')
          responseContent = formatExercises(exercises)
          break
        }
        case 'progress': {
          const dash = await api.getDashboard()
          responseContent = formatDashboard(dash)
          break
        }
        default: {
          responseContent = `I understood your question as a general query. Here's what I found:\n\n${triage.reasoning}\n\nCould you be more specific? I can help with explaining concepts, debugging code, code review, exercises, or tracking progress.`
        }
      }

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: responseContent,
        timestamp: new Date().toISOString(),
        metadata: { query_type: triage.query_type, routed_to: triage.routed_to },
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (e) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: e instanceof Error ? `Error: ${e.message}` : 'Something went wrong. Please try again.',
        timestamp: new Date().toISOString(),
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
      setThinking(null)
    }
  }

  return (
    <Card className="flex flex-col h-[600px]">
      <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : ''}`}>
            {msg.role !== 'user' && (
              <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                <Bot className="h-4 w-4 text-primary" />
              </div>
            )}
            <div className={`max-w-[80%] ${msg.role === 'user' ? 'order-1' : ''}`}>
              <div
                className={`rounded-xl px-4 py-2.5 text-sm ${
                  msg.role === 'user'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-secondary'
                }`}
              >
                <div className="prose prose-sm max-w-none whitespace-pre-wrap">
                  {msg.content}
                </div>
              </div>
              <p className={`text-xs text-muted-foreground mt-1 ${msg.role === 'user' ? 'text-right' : ''}`}>
                {formatRelativeTime(msg.timestamp)}
                {(msg.metadata?.query_type as string) && (
                  <span className="ml-2 inline-flex items-center gap-1">
                    {getQueryIcon(msg.metadata?.query_type as string)}
                  </span>
                )}
              </p>
            </div>
            {msg.role === 'user' && (
              <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
                <User className="h-4 w-4 text-white" />
              </div>
            )}
          </div>
        ))}

        {thinking && (
          <div className="flex gap-3">
            <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
              <Bot className="h-4 w-4 text-primary" />
            </div>
            <div className="bg-secondary rounded-xl px-4 py-2.5 text-sm flex items-center gap-2">
              <Spinner size="sm" />
              {thinking}
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </CardContent>

      <div className="border-t p-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSend()}
            placeholder="Ask about Python concepts, debugging, code review..."
            className="flex-1 h-10 rounded-lg border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            disabled={loading}
          />
          <Button onClick={handleSend} disabled={loading || !input.trim()} size="sm">
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </Card>
  )
}

function formatExplanation(explain: { explanation: { definition: string; explanation: string; key_points: string[]; code_examples: { title: string; code: string; explanation: string }[]; common_mistakes: string[]; related_concepts: string[]; analogies: string[] } }): string {
  const e = explain.explanation
  let text = `## ${e.definition}\n\n${e.explanation}\n`

  if (e.analogies.length) {
    text += `\n### 💡 Analogies\n- ${e.analogies.join('\n- ')}\n`
  }

  if (e.key_points.length) {
    text += `\n### Key Points\n- ${e.key_points.join('\n- ')}\n`
  }

  if (e.code_examples.length) {
    text += `\n### Code Examples\n`
    for (const ex of e.code_examples) {
      text += `\n**${ex.title}**\n\`\`\`python\n${ex.code}\n\`\`\`\n${ex.explanation}\n`
    }
  }

  if (e.common_mistakes.length) {
    text += `\n### Common Mistakes\n- ${e.common_mistakes.join('\n- ')}\n`
  }

  if (e.related_concepts.length) {
    text += `\n### Related Concepts\n${e.related_concepts.join(', ')}\n`
  }

  return text
}

function formatDebugResult(debug: { error_type: string; error_message: string; explanation: string; suggestion: string; hints: string[]; line_number?: number }): string {
  let text = `### 🔍 Debug Analysis\n\n`
  text += `**Error Type:** ${debug.error_type}\n`
  if (debug.line_number) text += `**Line:** ${debug.line_number}\n`
  text += `**Message:** ${debug.error_message}\n\n`
  text += `**Explanation:** ${debug.explanation}\n\n`
  text += `**Suggestion:** ${debug.suggestion}\n`
  if (debug.hints.length) {
    text += `\n**Hints:**\n- ${debug.hints.join('\n- ')}\n`
  }
  return text
}

function formatCodeReview(review: { issues: { severity: string; category: string; line: number; message: string; suggestion?: string }[]; summary: { total_issues: number; overall_score: number } }): string {
  let text = `### 📝 Code Review\n\n`
  text += `**Score:** ${review.summary.overall_score}/100 | **Issues Found:** ${review.summary.total_issues}\n\n`

  for (const issue of review.issues) {
    text += `**Line ${issue.line}** [${issue.severity.toUpperCase()}] [${issue.category}]\n`
    text += `${issue.message}\n`
    if (issue.suggestion) text += `  → ${issue.suggestion}\n`
    text += '\n'
  }

  return text
}

function formatExercises(exercises: { id: string; title: string; description: string; difficulty: string; topic: string; time_estimate_minutes: number }[]): string {
  let text = `### 📚 Practice Exercises\n\n`
  for (const ex of exercises) {
    text += `**${ex.title}** (${ex.difficulty})\n`
    text += `${ex.description}\n`
    text += `Topic: ${ex.topic} | Est. ${ex.time_estimate_minutes}min\n\n`
  }
  return text
}

function formatDashboard(dash: { overall_mastery: number; streak: { current_streak: number; longest_streak: number }; concepts_mastered: number; total_exercises: number; passed_exercises: number }): string {
  return `### 📊 Your Progress\n\n` +
    `**Overall Mastery:** ${Math.round(dash.overall_mastery)}%\n` +
    `**Current Streak:** ${dash.streak.current_streak} days\n` +
    `**Longest Streak:** ${dash.streak.longest_streak} days\n` +
    `**Concepts Mastered:** ${dash.concepts_mastered}\n` +
    `**Exercises:** ${dash.passed_exercises}/${dash.total_exercises} passed\n\n` +
    `Keep up the great work! 🎉`
}
