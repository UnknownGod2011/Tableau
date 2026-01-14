'use client'

import { ReactNode } from 'react'
import { motion } from 'framer-motion'

interface GlowCardProps {
  children: ReactNode
  className?: string
  glowColor?: string
  intensity?: 'low' | 'medium' | 'high'
  hoverEffect?: boolean
  onClick?: () => void
}

export default function GlowCard({
  children,
  className = '',
  glowColor = 'blue',
  intensity = 'medium',
  hoverEffect = true,
  onClick
}: GlowCardProps) {
  const glowColors: Record<string, string> = {
    blue: 'rgba(59, 130, 246, VAR)',
    green: 'rgba(34, 197, 94, VAR)',
    red: 'rgba(239, 68, 68, VAR)',
    amber: 'rgba(245, 158, 11, VAR)',
    purple: 'rgba(139, 92, 246, VAR)',
    cyan: 'rgba(6, 182, 212, VAR)'
  }

  const intensityValues = {
    low: { shadow: 0.1, hover: 0.2 },
    medium: { shadow: 0.15, hover: 0.3 },
    high: { shadow: 0.25, hover: 0.4 }
  }

  const { shadow, hover } = intensityValues[intensity]
  const baseGlow = glowColors[glowColor]?.replace('VAR', String(shadow)) || glowColors.blue.replace('VAR', String(shadow))
  const hoverGlow = glowColors[glowColor]?.replace('VAR', String(hover)) || glowColors.blue.replace('VAR', String(hover))

  return (
    <motion.div
      className={`relative bg-white rounded-xl border border-gray-200 overflow-hidden ${className}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={hoverEffect ? { 
        y: -4,
        boxShadow: `0 20px 40px -10px ${hoverGlow}, 0 10px 20px -5px rgba(0,0,0,0.1)`
      } : {}}
      style={{
        boxShadow: `0 10px 30px -10px ${baseGlow}, 0 4px 10px -2px rgba(0,0,0,0.05)`
      }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      onClick={onClick}
    >
      {/* Subtle gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-white via-transparent to-gray-50/50 pointer-events-none" />
      
      {/* Content */}
      <div className="relative z-10">
        {children}
      </div>
    </motion.div>
  )
}
