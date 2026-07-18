'use client'

import { AnimatedGrid } from '@/components/ui/AnimatedGrid'
import { Spotlight } from '@/components/ui/Spotlight'
import { LoginForm } from '@/components/auth/LoginForm'

export default function LoginPage() {
  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-primary-50/50 via-background to-secondary-50/50 dark:from-primary-950/20 dark:via-background dark:to-secondary-950/20" />
      <AnimatedGrid className="opacity-40" spacing={36} />
      <Spotlight className="-top-20 -left-20" size={400} />
      <div className="relative z-10 w-full max-w-md">
        <div className="mx-4 rounded-2xl border border-white/20 bg-white/80 p-1 shadow-2xl backdrop-blur-xl dark:bg-white/5">
          <LoginForm />
        </div>
      </div>
    </div>
  )
}
