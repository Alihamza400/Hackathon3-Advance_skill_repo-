'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useAuthStore } from '@/hooks/useAuth'
import { Button } from '@/components/ui/Button'
import { getInitials } from '@/lib/utils'
import { Menu, X, GraduationCap } from 'lucide-react'

export function Navbar() {
  const { user, logout } = useAuthStore()
  const [menuOpen, setMenuOpen] = useState(false)

  return (
    <header className="sticky top-0 z-40 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex h-16 items-center justify-between px-4">
        <div className="flex items-center gap-3">
          <button
            className="lg:hidden p-2 hover:bg-accent rounded-lg"
            onClick={() => setMenuOpen(!menuOpen)}
          >
            {menuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
          <Link href="/" className="group flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-600 to-purple-600 shadow-lg shadow-blue-500/20 transition-all duration-300 group-hover:scale-110 group-hover:shadow-blue-500/40">
              <GraduationCap className="h-4 w-4 text-white" />
            </div>
            <span className="font-bold text-lg hidden sm:inline">Learn<span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">Flow</span></span>
          </Link>
        </div>

        <div className="flex items-center gap-3">
          {user ? (
            <>
              <Link href="/dashboard">
                <Button variant="ghost" size="sm">Dashboard</Button>
              </Link>
              <Link href="/learn">
                <Button variant="ghost" size="sm">Learn</Button>
              </Link>
              <Link
                href="/profile"
                className="flex items-center gap-2 px-2 py-1 rounded-lg hover:bg-accent transition-colors"
              >
                <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center text-sm font-medium text-primary">
                  {getInitials(user.full_name)}
                </div>
                <span className="text-sm font-medium hidden md:inline">{user.full_name}</span>
              </Link>
              <Button variant="outline" size="sm" onClick={logout}>Logout</Button>
            </>
          ) : (
            <>
              <Link href="/login"><Button variant="ghost" size="sm">Login</Button></Link>
              <Link href="/register"><Button size="sm">Get Started</Button></Link>
            </>
          )}
        </div>
      </div>

      {menuOpen && (
        <div className="lg:hidden border-t p-4 space-y-2 bg-background">
          <Link href="/dashboard" className="block px-3 py-2 rounded-lg hover:bg-accent text-sm">Dashboard</Link>
          <Link href="/learn" className="block px-3 py-2 rounded-lg hover:bg-accent text-sm">Learning</Link>
          <Link href="/exercises" className="block px-3 py-2 rounded-lg hover:bg-accent text-sm">Exercises</Link>
          <Link href="/progress" className="block px-3 py-2 rounded-lg hover:bg-accent text-sm">Progress</Link>
        </div>
      )}
    </header>
  )
}
