'use client'

import { Toaster } from 'react-hot-toast'
import { AppLayout } from '@/components/layout/AppLayout'

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <>
      <AppLayout>{children}</AppLayout>
      <Toaster
        position="bottom-right"
        toastOptions={{
          className: 'rounded-lg border shadow-md',
          duration: 4000,
        }}
      />
    </>
  )
}
