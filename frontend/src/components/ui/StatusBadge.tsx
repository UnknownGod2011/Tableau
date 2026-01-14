'use client'

import { motion } from 'framer-motion'

type StatusType = 'success' | 'warning' | 'danger' | 'info' | 'neutral'

interface StatusBadgeProps {
  status: StatusType
  label: string
  animated?: boolean
  size?: 'sm' | 'md' | 'lg'
}

const statusConfig = {
  success: {
    bg: 'bg-green-100',
    text: 'text-green-800',
    border: 'border-green-200',
    dot: 'bg-green-500'
  },
  warning: {
    bg: 'bg-amber-100',
    text: 'text-amber-800',
    border: 'border-amber-200',
    dot: 'bg-amber-500'
  },
  danger: {
    bg: 'bg-red-100',
    text: 'text-red-800',
    border: 'border-red-200',
    dot: 'bg-red-500'
  },
  info: {
    bg: 'bg-blue-100',
    text: 'text-blue-800',
    border: 'border-blue-200',
    dot: 'bg-blue-500'
  },
  neutral: {
    bg: 'bg-gray-100',
    text: 'text-gray-800',
    border: 'border-gray-200',
    dot: 'bg-gray-500'
  }
}

const sizeConfig = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-2.5 py-1 text-sm',
  lg: 'px-3 py-1.5 text-base'
}

export default function StatusBadge({ 
  status, 
  label, 
  animated = true,
  size = 'md'
}: StatusBadgeProps) {
  const config = statusConfig[status]
  const sizeClass = sizeConfig[size]

  return (
    <motion.span
      className={`inline-flex items-center space-x-1.5 ${config.bg} ${config.text} ${config.border} border rounded-full ${sizeClass} font-medium`}
      initial={animated ? { opacity: 0, scale: 0.9 } : {}}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ scale: 1.05 }}
      transition={{ duration: 0.2 }}
    >
      <motion.span 
        className={`w-1.5 h-1.5 ${config.dot} rounded-full`}
        animate={animated && (status === 'warning' || status === 'danger') ? { 
          scale: [1, 1.3, 1],
          opacity: [1, 0.7, 1]
        } : {}}
        transition={{ duration: 1.5, repeat: Infinity }}
      />
      <span>{label}</span>
    </motion.span>
  )
}
