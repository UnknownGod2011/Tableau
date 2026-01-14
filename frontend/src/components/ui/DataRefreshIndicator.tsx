'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ArrowPathIcon, CheckCircleIcon } from '@heroicons/react/24/outline'

interface DataRefreshIndicatorProps {
  lastUpdated?: Date
  autoRefreshInterval?: number // in seconds
  onRefresh?: () => void
  isRefreshing?: boolean
}

export default function DataRefreshIndicator({
  lastUpdated = new Date(),
  autoRefreshInterval = 30,
  onRefresh,
  isRefreshing = false
}: DataRefreshIndicatorProps) {
  const [timeAgo, setTimeAgo] = useState('Just now')
  const [showSuccess, setShowSuccess] = useState(false)

  useEffect(() => {
    const updateTimeAgo = () => {
      const seconds = Math.floor((new Date().getTime() - lastUpdated.getTime()) / 1000)
      if (seconds < 5) setTimeAgo('Just now')
      else if (seconds < 60) setTimeAgo(`${seconds}s ago`)
      else if (seconds < 3600) setTimeAgo(`${Math.floor(seconds / 60)}m ago`)
      else setTimeAgo(`${Math.floor(seconds / 3600)}h ago`)
    }

    updateTimeAgo()
    const interval = setInterval(updateTimeAgo, 1000)
    return () => clearInterval(interval)
  }, [lastUpdated])

  useEffect(() => {
    if (!isRefreshing && showSuccess) {
      const timer = setTimeout(() => setShowSuccess(false), 2000)
      return () => clearTimeout(timer)
    }
  }, [isRefreshing, showSuccess])

  const handleRefresh = () => {
    if (onRefresh && !isRefreshing) {
      onRefresh()
      setShowSuccess(true)
    }
  }

  return (
    <motion.div 
      className="flex items-center space-x-3 text-sm"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      <span className="text-gray-500">Updated {timeAgo}</span>
      
      <button
        onClick={handleRefresh}
        disabled={isRefreshing}
        className="flex items-center space-x-1 px-2 py-1 rounded-md hover:bg-gray-100 transition-colors disabled:opacity-50"
      >
        <AnimatePresence mode="wait">
          {isRefreshing ? (
            <motion.div
              key="refreshing"
              initial={{ opacity: 0, rotate: 0 }}
              animate={{ opacity: 1, rotate: 360 }}
              exit={{ opacity: 0 }}
              transition={{ rotate: { duration: 1, repeat: Infinity, ease: "linear" } }}
            >
              <ArrowPathIcon className="h-4 w-4 text-blue-600" />
            </motion.div>
          ) : showSuccess ? (
            <motion.div
              key="success"
              initial={{ opacity: 0, scale: 0.5 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.5 }}
            >
              <CheckCircleIcon className="h-4 w-4 text-green-600" />
            </motion.div>
          ) : (
            <motion.div
              key="idle"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              whileHover={{ rotate: 180 }}
              transition={{ duration: 0.3 }}
            >
              <ArrowPathIcon className="h-4 w-4 text-gray-600" />
            </motion.div>
          )}
        </AnimatePresence>
        <span className="text-gray-600">
          {isRefreshing ? 'Syncing...' : 'Refresh'}
        </span>
      </button>
    </motion.div>
  )
}
