'use client'

import { motion } from 'framer-motion'
import { ArrowUpIcon, ArrowDownIcon, MinusIcon } from '@heroicons/react/24/outline'

interface MetricCardProps {
  title: string
  value: string
  change?: string
  changeType?: 'positive' | 'negative' | 'neutral'
  icon: React.ComponentType<{ className?: string }>
  subtitle?: string
  loading?: boolean
}

export default function MetricCard({
  title,
  value,
  change,
  changeType = 'neutral',
  icon: Icon,
  subtitle,
  loading = false
}: MetricCardProps) {
  const getChangeColor = () => {
    switch (changeType) {
      case 'positive':
        return 'text-green-600 bg-green-50'
      case 'negative':
        return 'text-red-600 bg-red-50'
      default:
        return 'text-gray-600 bg-gray-50'
    }
  }

  const getChangeIcon = () => {
    switch (changeType) {
      case 'positive':
        return <ArrowUpIcon className="h-3 w-3" />
      case 'negative':
        return <ArrowDownIcon className="h-3 w-3" />
      default:
        return <MinusIcon className="h-3 w-3" />
    }
  }

  if (loading) {
    return (
      <div className="metric-card animate-pulse">
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <div className="h-4 bg-gray-200 rounded w-24"></div>
            <div className="h-8 bg-gray-200 rounded w-32"></div>
            <div className="h-3 bg-gray-200 rounded w-20"></div>
          </div>
          <div className="h-12 w-12 bg-gray-200 rounded-lg"></div>
        </div>
      </div>
    )
  }

  return (
    <motion.div
      whileHover={{ y: -2, boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)' }}
      transition={{ type: 'spring', stiffness: 300 }}
      className="metric-card group cursor-pointer"
    >
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600 group-hover:text-gray-700 transition-colors">
            {title}
          </p>
          <div className="mt-2">
            <p className="text-3xl font-bold text-gray-900 group-hover:text-blue-600 transition-colors">
              ${value}
            </p>
            {subtitle && (
              <p className="text-xs text-gray-500 mt-1">{subtitle}</p>
            )}
          </div>
          {change && (
            <div className="mt-3">
              <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getChangeColor()}`}>
                {getChangeIcon()}
                <span className="ml-1">{change}</span>
              </div>
            </div>
          )}
        </div>
        <div className="flex-shrink-0">
          <div className="h-12 w-12 bg-blue-50 rounded-lg flex items-center justify-center group-hover:bg-blue-100 transition-colors">
            <Icon className="h-6 w-6 text-blue-600" />
          </div>
        </div>
      </div>
    </motion.div>
  )
}