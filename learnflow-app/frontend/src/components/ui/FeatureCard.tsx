'use client'

import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'
import type { LucideIcon } from 'lucide-react'

interface FeatureCardProps {
  icon: LucideIcon
  title: string
  description: string
  index: number
  className?: string
}

export function FeatureCard({ icon: Icon, title, description, index, className }: FeatureCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-50px' }}
      transition={{ duration: 0.5, delay: index * 0.1 }}
      className={cn(
        'group relative overflow-hidden rounded-2xl border p-6',
        'bg-gradient-to-br from-card to-card/50',
        'hover:shadow-[0_0_30px_hsl(var(--primary)/0.15)]',
        'transition-all duration-500 hover:-translate-y-1',
        'before:absolute before:inset-0 before:bg-[radial-gradient(circle_at_50%_-20%,hsl(var(--primary)/0.08),transparent_60%)]',
        'before:opacity-0 before:transition-opacity before:duration-500',
        'hover:before:opacity-100',
        className
      )}
    >
      <div className="relative z-10">
        <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-primary/20 to-primary/5 ring-1 ring-primary/20 transition-all duration-500 group-hover:scale-110 group-hover:shadow-[0_0_20px_hsl(var(--primary)/0.3)]">
          <Icon className="h-6 w-6 text-primary transition-transform duration-500 group-hover:scale-110" />
        </div>
        <h3 className="mb-2 text-lg font-semibold">{title}</h3>
        <p className="text-sm leading-relaxed text-muted-foreground">{description}</p>
      </div>
      <div className="absolute -bottom-6 -right-6 h-20 w-20 rounded-full bg-primary/5 blur-2xl transition-all duration-500 group-hover:bg-primary/10 group-hover:scale-150" />
    </motion.div>
  )
}
