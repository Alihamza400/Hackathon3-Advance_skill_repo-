'use client'

import { type HTMLAttributes } from 'react'
import { cn } from '@/lib/utils'

interface GlassCardProps extends HTMLAttributes<HTMLDivElement> {
  hover?: boolean
  glow?: boolean
}

export function GlassCard({ className, hover, glow, children, ...props }: GlassCardProps) {
  return (
    <div
      className={cn(
        'relative overflow-hidden rounded-2xl border border-white/20 dark:border-white/10',
        'bg-gradient-to-br from-white/80 to-white/40 dark:from-white/5 dark:to-white/[0.02]',
        'backdrop-blur-xl shadow-xl',
        hover && 'transition-all duration-500 hover:shadow-2xl hover:-translate-y-1',
        glow && 'hover:shadow-[0_0_30px_hsl(var(--primary)/0.3)]',
        className
      )}
      {...props}
    >
      <div className="absolute inset-0 bg-gradient-to-br from-transparent via-white/5 to-transparent pointer-events-none" />
      <div className="relative z-10">{children}</div>
    </div>
  )
}

export function GlassCardContent({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return <div className={cn('p-6', className)} {...props} />
}
