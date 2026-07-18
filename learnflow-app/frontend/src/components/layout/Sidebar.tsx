'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import {
  LayoutDashboard,
  BookOpen,
  Code,
  FileCode,
  Trophy,
  Settings,
  LogOut,
  GraduationCap,
} from 'lucide-react'
import { useAuthStore } from '@/hooks/useAuth'

const navItems = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/learn', label: 'Learning', icon: BookOpen },
  { href: '/code-editor', label: 'Code Editor', icon: Code },
  { href: '/exercises', label: 'Exercises', icon: FileCode },
  { href: '/progress', label: 'Progress', icon: Trophy },
]

interface SidebarProps {
  collapsed?: boolean
  onClose?: () => void
}

export function Sidebar({ collapsed, onClose }: SidebarProps) {
  const pathname = usePathname()
  const { user, logout } = useAuthStore()

  return (
    <aside
      className={cn(
        'flex h-full flex-col bg-card border-r transition-all duration-300 relative',
        'before:absolute before:inset-0 before:bg-gradient-to-b before:from-primary/5 before:via-transparent before:to-transparent before:pointer-events-none',
        collapsed ? 'w-16' : 'w-64'
      )}
    >
      <div className="relative flex items-center gap-3 px-4 h-16 border-b bg-gradient-to-r from-primary/5 to-transparent">
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-primary/60 shadow-lg">
          <GraduationCap className="h-5 w-5 text-white" />
        </div>
        {!collapsed && (
          <span className="font-bold text-lg bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text text-transparent">LearnFlow</span>
        )}
      </div>

      <nav className="flex-1 p-3 space-y-1">
        {navItems.map(({ href, label, icon: Icon }) => {
          const isActive = pathname === href || pathname.startsWith(href + '/')
          return (
            <Link
              key={href}
              href={href}
              onClick={onClose}
              className={cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary/10 text-primary'
                  : 'text-secondary-foreground hover:bg-accent hover:text-accent-foreground'
              )}
            >
              <Icon className="h-5 w-5 flex-shrink-0" />
              {!collapsed && <span>{label}</span>}
            </Link>
          )
        })}
      </nav>

      <div className="p-3 border-t space-y-1">
        <Link
          href="/settings"
          onClick={onClose}
          className={cn(
            'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
            'text-secondary-foreground hover:bg-accent hover:text-accent-foreground'
          )}
        >
          <Settings className="h-5 w-5 flex-shrink-0" />
          {!collapsed && <span>Settings</span>}
        </Link>
        <button
          onClick={logout}
          className={cn(
            'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors w-full',
            'text-secondary-foreground hover:bg-accent hover:text-accent-foreground'
          )}
        >
          <LogOut className="h-5 w-5 flex-shrink-0" />
          {!collapsed && <span>Logout</span>}
        </button>
        {!collapsed && user && (
          <div className="px-3 py-2 mt-2">
            <p className="text-xs text-muted-foreground truncate">{user.email}</p>
            <p className="text-xs capitalize text-muted-foreground">{user.role}</p>
          </div>
        )}
      </div>
    </aside>
  )
}
