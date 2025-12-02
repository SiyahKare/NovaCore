import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { AuroraShell } from '@/components/AuroraShell'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Aurora Citizen Portal',
  description: 'Your gateway to the Aurora State Network',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className={inter.className}>
        <AuroraShell>{children}</AuroraShell>
      </body>
    </html>
  )
}

