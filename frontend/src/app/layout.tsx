import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'TreasuryIQ - AI-Powered Corporate Treasury Management',
  description: 'Advanced treasury management platform with AI insights and Tableau integration',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50 antialiased">
        {children}
      </body>
    </html>
  )
}