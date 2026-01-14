'use client'

import { motion } from 'framer-motion'

interface LiveIndicatorProps {
  label?: string
  status?: 'live' | 'syncing' | 'offline'
  showPulse?: boolean
  size?: 'sm' | 'md' | 'lg'
}

export default function LiveIndicator({ 
  label = 'LIVE', 
  status = 'live',
  showPulse = true,
  size = 'md'
}: LiveIndicatorProps) {
  const colors = {
    live: { bg: 'bg-green-500', text: 'text-green-700', ring: 'ring-green-400' },
    syncing: { bg: 'bg-amber-500', text: 'text-amber-700', ring: 'ring-amber-400' },
    offline: { bg: 'bg-red-500', text: 'text-red-700', ring: 'ring-red-400' }
  }

  const sizes = {
    sm: { dot: 'w-2 h-2', text: 'text-xs', padding: 'px-2 py-1' },
    md: { dot: 'w-3 h-3', text: 'text-sm', padding: 'px-3 py-1.5' },
    lg: { dot: 'w-4 h-4', text: 'text-base', padding: 'px-4 py-2' }
  }

  const { bg, text, ring } = colors[status]
  const { dot, text: textSize, padding } = sizes[size]

  return (
    <motion.div 
      className={`flex items-center space-x-2 bg-gray-50 ${padding} rounded-full border border-gray-200`}
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
    >
      <div className="relative">
        <motion.div 
          className={`${dot} ${bg} rounded-full`}
          animate={showPulse ? { scale: [1, 1.2, 1] } : {}}
          transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
        />
        {showPulse && status === 'live' && (
          <motion.div 
            className={`absolute inset-0 ${dot} ${bg} rounded-full`}
            animate={{ scale: [1, 2.5], opacity: [0.6, 0] }}
            transition={{ duration: 2, repeat: Infinity, ease: "easeOut" }}
          />
        )}
      </div>
      <span className={`${textSize} font-medium ${text}`}>{label}</span>
    </motion.div>
  )
}
