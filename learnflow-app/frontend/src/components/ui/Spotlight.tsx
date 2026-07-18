'use client'

import { cn } from '@/lib/utils'

interface SpotlightProps {
  className?: string
  fill?: string
  size?: number
}

export function Spotlight({ className, fill = 'var(--primary)', size = 800 }: SpotlightProps) {
  return (
    <svg
      className={cn('pointer-events-none absolute z-0 animate-pulse-soft', className)}
      width={size}
      height={size * 1.2}
      viewBox={`0 0 ${size} ${size * 1.2}`}
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      <g filter="url(#spotlight)">
        <ellipse
          cx={size / 3}
          cy={size / 3}
          rx={size / 3}
          ry={size / 3.5}
          fill={fill}
          fillOpacity="0.15"
        />
      </g>
      <defs>
        <filter id="spotlight">
          <feGaussianBlur stdDeviation={size / 10} result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>
    </svg>
  )
}
