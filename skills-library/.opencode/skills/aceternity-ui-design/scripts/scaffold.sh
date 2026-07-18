#!/bin/bash
# Aceternity UI Design — Scaffold all animated components into a Next.js project
# Usage: bash scaffold.sh /path/to/nextjs-app

set -e

TARGET="${1:-.}"
UI_DIR="$TARGET/src/components/ui"
UTILS_FILE="$TARGET/src/lib/utils.ts"

echo "Scaffolding Aceternity UI components into $TARGET..."
mkdir -p "$UI_DIR"

# 1. Ensure framer-motion is installed
if ! grep -q '"framer-motion"' "$TARGET/package.json" 2>/dev/null; then
  echo "Installing framer-motion..."
  (cd "$TARGET" && npm install framer-motion)
fi

# 2. Ensure cn utility exists
if [ ! -f "$UTILS_FILE" ]; then
  mkdir -p "$(dirname "$UTILS_FILE")"
  cat > "$UTILS_FILE" << 'EOF'
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
EOF
  echo "Created cn utility at $UTILS_FILE"
fi

# 3. Write all component files
write_component() {
  cat > "$UI_DIR/$1" <&3
  echo "  ✓ $1"
}

# AnimatedGrid
write_component "AnimatedGrid.tsx" 3<< 'COMPONENT'
'use client'

import { useEffect, useRef } from 'react'
import { cn } from '@/lib/utils'

interface AnimatedGridProps {
  className?: string
  dotSize?: number
  spacing?: number
  fade?: boolean
}

export function AnimatedGrid({ className, dotSize = 1, spacing = 32, fade = true }: AnimatedGridProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    let animationId: number
    let mouseX = -1000
    let mouseY = -1000

    const resize = () => {
      if (!canvas) return
      canvas.width = canvas.offsetWidth * window.devicePixelRatio
      canvas.height = canvas.offsetHeight * window.devicePixelRatio
      ctx!.scale(window.devicePixelRatio, window.devicePixelRatio)
    }

    resize()
    window.addEventListener('resize', resize)

    const handleMouse = (e: MouseEvent) => {
      const rect = canvas!.getBoundingClientRect()
      mouseX = e.clientX - rect.left
      mouseY = e.clientY - rect.top
    }
    window.addEventListener('mousemove', handleMouse)

    const draw = (time: number) => {
      if (!canvas || !ctx) return
      const w = canvas.offsetWidth
      const h = canvas.offsetHeight
      ctx.clearRect(0, 0, w, h)

      for (let x = spacing / 2; x < w; x += spacing) {
        for (let y = spacing / 2; y < h; y += spacing) {
          const dx = x - mouseX
          const dy = y - mouseY
          const dist = Math.sqrt(dx * dx + dy * dy)
          const pulse = Math.sin((x + y) * 0.02 + time * 0.001) * 0.3 + 0.7
          let alpha = pulse * 0.3
          if (dist < 150) alpha = Math.max(alpha, (1 - dist / 150) * 0.8)
          if (fade) {
            const edgeDist = Math.min(x, w - x, y, h - y)
            alpha *= Math.min(1, edgeDist / (spacing * 2))
          }
          ctx.beginPath()
          ctx.arc(x, y, dotSize, 0, Math.PI * 2)
          ctx.fillStyle = `hsla(var(--primary), ${alpha})`
          ctx.fill()
        }
      }
      animationId = requestAnimationFrame(draw)
    }

    animationId = requestAnimationFrame(draw)
    return () => {
      cancelAnimationFrame(animationId)
      window.removeEventListener('resize', resize)
      window.removeEventListener('mousemove', handleMouse)
    }
  }, [dotSize, spacing, fade])

  return <canvas ref={canvasRef} className={cn('pointer-events-none absolute inset-0', className)} aria-hidden="true" />
}
COMPONENT

# Spotlight
write_component "Spotlight.tsx" 3<< 'COMPONENT'
'use client'

import { cn } from '@/lib/utils'

interface SpotlightProps {
  className?: string
  fill?: string
  size?: number
}

export function Spotlight({ className, fill = 'var(--primary)', size = 800 }: SpotlightProps) {
  return (
    <svg className={cn('pointer-events-none absolute z-0 animate-pulse-soft', className)}
      width={size} height={size * 1.2} viewBox={`0 0 ${size} ${size * 1.2}`} fill="none" aria-hidden="true">
      <g filter="url(#s)">
        <ellipse cx={size / 3} cy={size / 3} rx={size / 3} ry={size / 3.5} fill={fill} fillOpacity="0.15" />
      </g>
      <defs>
        <filter id="s"><feGaussianBlur stdDeviation={size / 10} result="blur" />
          <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
      </defs>
    </svg>
  )
}
COMPONENT

# Typewriter
write_component "Typewriter.tsx" 3<< 'COMPONENT'
'use client'

import { useState, useEffect } from 'react'
import { cn } from '@/lib/utils'

interface TypewriterProps {
  texts: string[]
  className?: string
  speed?: number
  deleteSpeed?: number
  pauseDuration?: number
}

export function Typewriter({ texts, className, speed = 80, deleteSpeed = 40, pauseDuration = 2000 }: TypewriterProps) {
  const [display, setDisplay] = useState('')
  const [textIdx, setTextIdx] = useState(0)
  const [charIdx, setCharIdx] = useState(0)
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    const t = texts[textIdx]
    const timeout = setTimeout(() => {
      if (!deleting) {
        if (charIdx < t.length) { setDisplay(t.slice(0, charIdx + 1)); setCharIdx(i => i + 1) }
        else { setTimeout(() => setDeleting(true), pauseDuration) }
      } else {
        if (charIdx > 0) { setDisplay(t.slice(0, charIdx - 1)); setCharIdx(i => i - 1) }
        else { setDeleting(false); setTextIdx(i => (i + 1) % texts.length) }
      }
    }, deleting ? deleteSpeed : speed)
    return () => clearTimeout(timeout)
  }, [charIdx, deleting, textIdx, texts, speed, deleteSpeed, pauseDuration])

  return (
    <span className={cn('inline-block', className)}>
      {display}<span className="ml-0.5 inline-block h-[1em] w-[2px] animate-pulse bg-primary" />
    </span>
  )
}
COMPONENT

# GlowButton
write_component "GlowButton.tsx" 3<< 'COMPONENT'
'use client'

import { forwardRef, type ButtonHTMLAttributes } from 'react'
import { cn } from '@/lib/utils'

interface GlowButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'outline'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
}

const GlowButton = forwardRef<HTMLButtonElement, GlowButtonProps>(
  ({ className, variant = 'primary', size = 'md', loading, disabled, children, ...props }, ref) => (
    <button ref={ref} disabled={disabled || loading}
      className={cn(
        'group relative inline-flex items-center justify-center overflow-hidden rounded-xl font-medium transition-all duration-300',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50',
        variant === 'primary' && ['bg-primary text-primary-foreground', 'hover:shadow-[0_0_20px_hsl(var(--primary)/0.5)]'],
        variant === 'outline' && ['border border-border bg-background text-foreground', 'hover:shadow-[0_0_15px_hsl(var(--primary)/0.2)]'],
        { 'h-9 px-4 text-xs': size === 'sm', 'h-11 px-6 text-sm': size === 'md', 'h-13 px-10 text-base': size === 'lg' },
        className
      )}
      {...props}>
      {variant === 'primary' && (
        <span className="absolute inset-0 -z-10 bg-[linear-gradient(45deg,transparent_25%,rgba(255,255,255,0.15)_50%,transparent_75%)] bg-[length:250%_250%] transition-all duration-700 group-hover:bg-[position:100%_0]" />
      )}
      {loading && <svg className="mr-2 h-4 w-4 animate-spin" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg>}
      <span className="relative z-10">{children}</span>
    </button>
  )
)
GlowButton.displayName = 'GlowButton'
export { GlowButton }
COMPONENT

# GlassCard
write_component "GlassCard.tsx" 3<< 'COMPONENT'
'use client'

import { cn } from '@/lib/utils'
import type { HTMLAttributes } from 'react'

interface GlassCardProps extends HTMLAttributes<HTMLDivElement> {
  hover?: boolean
  glow?: boolean
}

export function GlassCard({ className, hover, glow, children, ...props }: GlassCardProps) {
  return (
    <div className={cn(
      'relative overflow-hidden rounded-2xl border border-white/20 dark:border-white/10',
      'bg-gradient-to-br from-white/80 to-white/40 dark:from-white/5 dark:to-white/[0.02]',
      'backdrop-blur-xl shadow-xl',
      hover && 'transition-all duration-500 hover:shadow-2xl hover:-translate-y-1',
      glow && 'hover:shadow-[0_0_30px_hsl(var(--primary)/0.3)]',
      className
    )} {...props}>
      <div className="absolute inset-0 bg-gradient-to-br from-transparent via-white/5 to-transparent pointer-events-none" />
      <div className="relative z-10">{children}</div>
    </div>
  )
}

export function GlassCardContent({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return <div className={cn('p-6', className)} {...props} />
}
COMPONENT

# AnimatedCounter
write_component "AnimatedCounter.tsx" 3<< 'COMPONENT'
'use client'

import { useEffect, useRef, useState } from 'react'
import { cn } from '@/lib/utils'

interface AnimatedCounterProps {
  from?: number
  to: number
  duration?: number
  suffix?: string
  prefix?: string
  decimals?: number
}

export function AnimatedCounter({ from = 0, to, duration = 2000, suffix = '', prefix = '', decimals = 0 }: AnimatedCounterProps) {
  const [value, setValue] = useState(from)
  const ref = useRef<HTMLSpanElement>(null)
  const started = useRef(false)

  useEffect(() => {
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting && !started.current) {
        started.current = true
        const startTime = Date.now()
        const animate = () => {
          const elapsed = Date.now() - startTime
          const progress = Math.min(elapsed / duration, 1)
          const ease = 1 - Math.pow(1 - progress, 3)
          if (progress < 1) { setValue(from + (to - from) * ease); requestAnimationFrame(animate) }
          else setValue(to)
        }
        requestAnimationFrame(animate)
      }
    }, { threshold: 0.1 })
    if (ref.current) observer.observe(ref.current)
    return () => observer.disconnect()
  }, [from, to, duration])

  return <span ref={ref} className={cn('tabular-nums', className)}>{prefix}{value.toFixed(decimals)}{suffix}</span>
}
COMPONENT

# FeatureCard
write_component "FeatureCard.tsx" 3<< 'COMPONENT'
'use client'

import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'
import type { LucideIcon } from 'lucide-react'

interface FeatureCardProps {
  icon: LucideIcon
  title: string
  description: string
  index: number
}

export function FeatureCard({ icon: Icon, title, description, index }: FeatureCardProps) {
  return (
    <motion.div initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }} transition={{ duration: 0.5, delay: index * 0.1 }}
      className="group relative overflow-hidden rounded-2xl border p-6 bg-gradient-to-br from-card to-card/50
        transition-all duration-500 hover:-translate-y-1 hover:shadow-[0_0_30px_hsl(var(--primary)/0.15)]
        before:absolute before:inset-0 before:bg-[radial-gradient(circle_at_50%_-20%,hsl(var(--primary)/0.08),transparent_60%)]
        before:opacity-0 before:transition-opacity before:duration-500 hover:before:opacity-100">
      <div className="relative z-10">
        <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-primary/20 to-primary/5 ring-1 ring-primary/20
          transition-all duration-500 group-hover:scale-110 group-hover:shadow-[0_0_20px_hsl(var(--primary)/0.3)]">
          <Icon className="h-6 w-6 text-primary transition-transform duration-500 group-hover:scale-110" />
        </div>
        <h3 className="mb-2 text-lg font-semibold">{title}</h3>
        <p className="text-sm leading-relaxed text-muted-foreground">{description}</p>
      </div>
      <div className="absolute -bottom-6 -right-6 h-20 w-20 rounded-full bg-primary/5 blur-2xl transition-all duration-500 group-hover:bg-primary/10 group-hover:scale-150" />
    </motion.div>
  )
}
COMPONENT

echo ""
echo "✅ All Aceternity UI components scaffolded in $UI_DIR"
echo ""
echo "Components:"
ls -1 "$UI_DIR"/{AnimatedGrid,Spotlight,Typewriter,GlowButton,GlassCard,AnimatedCounter,FeatureCard}.tsx 2>/dev/null || true
echo ""
echo "Next step: import components in your pages"
echo "  import { AnimatedGrid } from '@/components/ui/AnimatedGrid'"
echo "  import { GlowButton } from '@/components/ui/GlowButton'"
