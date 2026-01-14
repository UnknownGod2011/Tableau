'use client'

import { ReactNode } from 'react'
import { motion } from 'framer-motion'
import AnimatedCounter from './AnimatedCounter'

type TrendDirection = 'up' | 'down' | 'neutral'
type StatusType = 'success' | 'warning' | 'danger' | 'neutral'

interface KPICardProps {
  title: string
  value: number
  prefix?: string
  suffix?: string
  trend?: {
    value: number
    direction: TrendDirection
    label?: string
  }
  status?: StatusType
  icon?: ReactNode
  sparkline?: number[]
  onClick?: () => void
  loading?: boolean
}

export default function KPICard({
  title,
  value,
  prefix = '',
  suffix = '',
  trend,
  status = 'neutral',
  icon,
  sparkline,
  onClick,
  loading = false
}: KPICardProps) {
  const statusColors = {
    success: { border: 'border-green-200', glow: 'shadow-green-100', accent: 'text-green-600', bg: 'bg-green-50' },
    warning: { border: 'border-amber-200', glow: 'shadow-amber-100', accent: 'text-amber-600', bg: 'bg-amber-50' },
    danger: { border: 'border-red-200', glow: 'shadow-red-100', accent: 'text-red-600', bg: 'bg-red-50' },
    neutral: { border: 'border-gray-200', glow: 'shadow-gray-100', accent: 'text-blue-600', bg: 'bg-blue-50' }
  }

  const trendColors = {
    up: 'text-green-600',
    down: 'text-red-600',
    neutral: 'text-gray-600'
  }

  const { border, glow, accent, bg } = statusColors[status]

  if (loading) {
    return (
      <div className={`bg-white rounded-xl ${border} border p-6 animate-pulse`}>
        <div className="h-4 bg-gray-200 rounded w-1/2 mb-4" />
        <div className="h-8 bg-gray-200 rounded w-3/4 mb-2" />
        <div className="h-3 bg-gray-200 rounded w-1/3" />
      </div>
    )
  }

  return (
    <motion.div
      className={`bg-white rounded-xl ${border} border p-6 cursor-pointer transition-all duration-300`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ 
        y: -4, 
        boxShadow: '0 20px 40px -15px rgba(0,0,0,0.1)',
        borderColor: status === 'neutral' ? '#93c5fd' : undefined
      }}
      onClick={onClick}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-2">
          <motion.span 
            className="text-sm font-medium text-gray-600"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.1 }}
          >
            {title}
          </motion.span>
          {status !== 'neutral' && (
            <motion.div
              className={`w-2 h-2 rounded-full ${status === 'success' ? 'bg-green-500' : status === 'warning' ? 'bg-amber-500' : 'bg-red-500'}`}
              animate={{ scale: [1, 1.2, 1], opacity: [1, 0.7, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
            />
          )}
        </div>
        {icon && (
          <motion.div 
            className={`p-2 ${bg} rounded-lg`}
            whileHover={{ scale: 1.1, rotate: 5 }}
          >
            {icon}
          </motion.div>
        )}
      </div>

      <div className="mb-2">
        <AnimatedCounter
          value={value}
          prefix={prefix}
          suffix={suffix}
          className="text-3xl font-bold text-gray-900"
          duration={1.5}
        />
      </div>

      {trend && (
        <motion.div 
          className="flex items-center space-x-2"
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
        >
          <span className={`text-sm font-medium ${trendColors[trend.direction]}`}>
            {trend.direction === 'up' ? '↑' : trend.direction === 'down' ? '↓' : '→'} {Math.abs(trend.value)}%
          </span>
          {trend.label && (
            <span className="text-xs text-gray-500">{trend.label}</span>
          )}
        </motion.div>
      )}

      {sparkline && sparkline.length > 0 && (
        <motion.div 
          className="mt-4 h-10 flex items-end space-x-0.5"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
        >
          {sparkline.map((val, i) => {
            const maxVal = Math.max(...sparkline)
            const height = (val / maxVal) * 100
            return (
              <motion.div
                key={i}
                className={`flex-1 ${accent.replace('text-', 'bg-')} bg-opacity-60 rounded-sm`}
                initial={{ height: 0 }}
                animate={{ height: `${height}%` }}
                transition={{ duration: 0.5, delay: i * 0.05 }}
              />
            )
          })}
        </motion.div>
      )}
    </motion.div>
  )
}
