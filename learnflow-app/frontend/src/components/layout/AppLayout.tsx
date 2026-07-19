'use client'

import { useState, useEffect, type ReactNode } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { Sidebar } from './Sidebar'
import { Navbar } from './Navbar'
import { useAuthStore } from '@/hooks/useAuth'
import { Spinner } from '@/components/ui/Spinner'
import { cn } from '@/lib/utils'

const authPages = ['/login', '/register']
const publicPages = ['/', ...authPages]

interface AppLayoutProps {
  children: ReactNode
}

export function AppLayout({ children }: AppLayoutProps) {
  const pathname = usePathname()
  const router = useRouter()
  const { user, initialized, initialize } = useAuthStore()
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)

  useEffect(() => {
    initialize()
  }, [initialize])

  const isAuthPage = authPages.includes(pathname)
  const isPublicPage = publicPages.includes(pathname)
  const isLanding = pathname === '/'

  if (!initialized) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Spinner size="lg" />
      </div>
    )
  }

  if (!user && !isPublicPage) {
    router.push('/login')
    return null
  }

  if (isLanding) {
    return <>{children}</>
  }

  if (isAuthPage) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 dark:from-secondary-950 dark:to-primary-950">
        {children}
      </div>
    )
  }

  return (
    <div className="flex h-screen overflow-hidden">
      <div className="hidden lg:flex">
        <Sidebar collapsed={sidebarCollapsed} />
      </div>
      <div className="flex-1 flex flex-col overflow-hidden">
        <Navbar />
        <main
          className={cn(
            'flex-1 overflow-y-auto p-4 md:p-6 lg:p-8',
            'bg-secondary-50/50 dark:bg-secondary-950/50'
          )}
        >
          {children}
        </main>
      </div>
    </div>
  )
}
