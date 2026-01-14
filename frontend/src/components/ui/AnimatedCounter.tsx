'use client'

import { useEffect, useState, useRef } from 'react'
import { motion, useInView } from 'framer-motion'

interface AnimatedCounterProps {
  value: number
  prefix?: string
  suffix?: string
  duration?: number
  decimals?: number
  className?: string
  formatFn?: (value: number) => string
}

export default function AnimatedCounter({
  value,
  prefix = '',
  suffix = '',
  duration = 2,
  decimals = 0,
  className = '',
  formatFn
}: AnimatedCounterProps) {
  const [displayValue, setDisplayValue] = useState(0)
  const ref = useRef<HTMLSpanElement>(null)
  const isInView = useInView(ref, { once: true })
  const previousValue = useRef(0)

  useEffect(() => {
    if (!isInView) return

    const startValue = previousValue.current
    const endValue = value
    const startTime = performance.now()
    const durationMs = duration * 1000

    const animate = (currentTime: number) => {
      const elapsed = currentTime - startTime
      const progress = Math.min(elapsed / durationMs, 1)
      
      // Ease out quart
      const easeProgress = 1 - Math.pow(1 - progress, 4)
      const currentValue = startValue + (endValue - startValue) * easeProgress

      setDisplayValue(currentValue)

      if (progress < 1) {
        requestAnimationFrame(animate)
      } else {
        previousValue.current = endValue
      }
    }

    requestAnimationFrame(animate)
  }, [value, duration, isInView])

  const formattedValue = formatFn 
    ? formatFn(displayValue) 
    : displayValue.toFixed(decimals).replace(/\B(?=(\d{3})+(?!\d))/g, ',')

  return (
    <motion.span
      ref={ref}
      className={className}
      initial={{ opacity: 0, y: 10 }}
      animate={isInView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.5 }}
    >
      {prefix}{formattedValue}{suffix}
    </motion.span>
  )
}
