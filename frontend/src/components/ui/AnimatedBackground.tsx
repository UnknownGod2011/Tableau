'use client'

import { motion } from 'framer-motion'

interface AnimatedBackgroundProps {
  variant?: 'gradient' | 'dots' | 'grid' | 'waves'
  intensity?: 'subtle' | 'medium' | 'strong'
}

export default function AnimatedBackground({ 
  variant = 'gradient',
  intensity = 'subtle'
}: AnimatedBackgroundProps) {
  const opacityMap = {
    subtle: 0.3,
    medium: 0.5,
    strong: 0.7
  }

  if (variant === 'gradient') {
    return (
      <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute -top-1/2 -left-1/2 w-full h-full"
          style={{
            background: `radial-gradient(circle, rgba(59, 130, 246, ${opacityMap[intensity] * 0.15}) 0%, transparent 50%)`,
          }}
          animate={{
            x: [0, 100, 0],
            y: [0, 50, 0],
          }}
          transition={{ duration: 20, repeat: Infinity, ease: "easeInOut" }}
        />
        <motion.div
          className="absolute -bottom-1/2 -right-1/2 w-full h-full"
          style={{
            background: `radial-gradient(circle, rgba(139, 92, 246, ${opacityMap[intensity] * 0.1}) 0%, transparent 50%)`,
          }}
          animate={{
            x: [0, -80, 0],
            y: [0, -60, 0],
          }}
          transition={{ duration: 25, repeat: Infinity, ease: "easeInOut" }}
        />
      </div>
    )
  }

  if (variant === 'dots') {
    return (
      <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
        <svg className="w-full h-full" style={{ opacity: opacityMap[intensity] * 0.3 }}>
          <defs>
            <pattern id="dots" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">
              <circle cx="2" cy="2" r="1" fill="currentColor" className="text-gray-400" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#dots)" />
        </svg>
      </div>
    )
  }

  if (variant === 'grid') {
    return (
      <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
        <svg className="w-full h-full" style={{ opacity: opacityMap[intensity] * 0.2 }}>
          <defs>
            <pattern id="grid" x="0" y="0" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="currentColor" strokeWidth="0.5" className="text-gray-300" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid)" />
        </svg>
      </div>
    )
  }

  return null
}
