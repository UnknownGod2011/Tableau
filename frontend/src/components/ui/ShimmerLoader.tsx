'use client'

import { motion } from 'framer-motion'

interface ShimmerLoaderProps {
  width?: string
  height?: string
  className?: string
  rounded?: 'none' | 'sm' | 'md' | 'lg' | 'full'
}

export default function ShimmerLoader({
  width = '100%',
  height = '20px',
  className = '',
  rounded = 'md'
}: ShimmerLoaderProps) {
  const roundedClass = {
    none: 'rounded-none',
    sm: 'rounded-sm',
    md: 'rounded-md',
    lg: 'rounded-lg',
    full: 'rounded-full'
  }

  return (
    <div 
      className={`relative overflow-hidden bg-gray-200 ${roundedClass[rounded]} ${className}`}
      style={{ width, height }}
    >
      <motion.div
        className="absolute inset-0 bg-gradient-to-r from-transparent via-white/60 to-transparent"
        animate={{ x: ['-100%', '100%'] }}
        transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
      />
    </div>
  )
}

export function CardShimmer() {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
      <div className="flex items-center justify-between">
        <ShimmerLoader width="120px" height="16px" />
        <ShimmerLoader width="40px" height="40px" rounded="full" />
      </div>
      <ShimmerLoader width="80%" height="32px" />
      <ShimmerLoader width="60%" height="14px" />
      <div className="flex space-x-2 pt-2">
        <ShimmerLoader width="60px" height="24px" rounded="full" />
        <ShimmerLoader width="80px" height="24px" rounded="full" />
      </div>
    </div>
  )
}

export function TableShimmer({ rows = 5 }: { rows?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex items-center space-x-4">
          <ShimmerLoader width="40px" height="40px" rounded="lg" />
          <div className="flex-1 space-y-2">
            <ShimmerLoader width="70%" height="14px" />
            <ShimmerLoader width="40%" height="12px" />
          </div>
          <ShimmerLoader width="80px" height="24px" rounded="full" />
        </div>
      ))}
    </div>
  )
}
