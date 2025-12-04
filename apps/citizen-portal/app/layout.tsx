import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { NovaCoreShell } from '@/components/NovaCoreShell'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'NovaCore Citizen Portal',
  description: 'SiyahKare Republic için NovaCore Citizen Console',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="tr" className="dark">
      <body className={inter.className}>
        <NovaCoreShell>{children}</NovaCoreShell>
      </body>
    </html>
  )
}
