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

    function resize() {
      if (!canvas) return
      canvas.width = canvas.offsetWidth * (typeof window !== 'undefined' ? window.devicePixelRatio : 1)
      canvas.height = canvas.offsetHeight * (typeof window !== 'undefined' ? window.devicePixelRatio : 1)
      ctx!.scale(typeof window !== 'undefined' ? window.devicePixelRatio : 1, typeof window !== 'undefined' ? window.devicePixelRatio : 1)
    }

    resize()
    window.addEventListener('resize', resize)

    const handleMouse = (e: MouseEvent) => {
      const rect = canvas!.getBoundingClientRect()
      mouseX = e.clientX - rect.left
      mouseY = e.clientY - rect.top
    }
    window.addEventListener('mousemove', handleMouse)

    function draw(time: number) {
      if (!canvas || !ctx) return
      const w = canvas.offsetWidth
      const h = canvas.offsetHeight
      ctx.clearRect(0, 0, w, h)

      for (let x = spacing / 2; x < w; x += spacing) {
        for (let y = spacing / 2; y < h; y += spacing) {
          const dx = x - mouseX
          const dy = y - mouseY
          const dist = Math.sqrt(dx * dx + dy * dy)
          const maxDist = 150
          const pulse = Math.sin((x + y) * 0.02 + time * 0.001) * 0.3 + 0.7
          let alpha = pulse * 0.3

          if (dist < maxDist) {
            alpha = Math.max(alpha, (1 - dist / maxDist) * 0.8)
          }

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

  return (
    <canvas
      ref={canvasRef}
      className={cn('pointer-events-none absolute inset-0', className)}
      aria-hidden="true"
    />
  )
}
