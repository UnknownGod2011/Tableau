'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  CpuChipIcon,
  ClockIcon,
  ServerIcon,
  SignalIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline'
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

interface PerformanceMetric {
  name: string
  value: number
  unit: string
  status: 'good' | 'warning' | 'critical'
  trend: 'up' | 'down' | 'stable'
  history: Array<{ timestamp: string; value: number }>
}

interface SystemHealth {
  overall: 'healthy' | 'degraded' | 'critical'
  services: Array<{
    name: string
    status: 'online' | 'offline' | 'degraded'
    responseTime: number
    uptime: number
  }>
}

export default function PerformanceMonitor() {
  const [isOpen, setIsOpen] = useState(false)
  const [metrics, setMetrics] = useState<PerformanceMetric[]>([])
  const [systemHealth, setSystemHealth] = useState<SystemHealth>({
    overall: 'healthy',
    services: []
  })

  // Generate mock performance data
  useEffect(() => {
    const generateMetrics = () => {
      const now = new Date()
      const history = Array.from({ length: 20 }, (_, i) => ({
        timestamp: new Date(now.getTime() - (19 - i) * 60000).toISOString(),
        value: Math.random() * 100
      }))

      return [
        {
          name: 'API Response Time',
          value: 145,
          unit: 'ms',
          status: 'good' as const,
          trend: 'stable' as const,
          history: history.map(h => ({ ...h, value: 100 + Math.random() * 100 }))
        },
        {
          name: 'Database Query Time',
          value: 23,
          unit: 'ms',
          status: 'good' as const,
          trend: 'down' as const,
          history: history.map(h => ({ ...h, value: 20 + Math.random() * 30 }))
        },
        {
          name: 'Memory Usage',
          value: 67,
          unit: '%',
          status: 'warning' as const,
          trend: 'up' as const,
          history: history.map(h => ({ ...h, value: 60 + Math.random() * 20 }))
        },
        {
          name: 'CPU Usage',
          value: 34,
          unit: '%',
          status: 'good' as const,
          trend: 'stable' as const,
          history: history.map(h => ({ ...h, value: 30 + Math.random() * 20 }))
        },
        {
          name: 'Active Connections',
          value: 1247,
          unit: 'conn',
          status: 'good' as const,
          trend: 'up' as const,
          history: history.map(h => ({ ...h, value: 1000 + Math.random() * 500 }))
        },
        {
          name: 'Error Rate',
          value: 0.12,
          unit: '%',
          status: 'good' as const,
          trend: 'down' as const,
          history: history.map(h => ({ ...h, value: Math.random() * 0.5 }))
        }
      ]
    }

    const generateSystemHealth = (): SystemHealth => ({
      overall: 'healthy',
      services: [
        { name: 'API Gateway', status: 'online', responseTime: 45, uptime: 99.98 },
        { name: 'Database', status: 'online', responseTime: 12, uptime: 99.95 },
        { name: 'Redis Cache', status: 'online', responseTime: 3, uptime: 99.99 },
        { name: 'AI Service', status: 'online', responseTime: 234, uptime: 99.87 },
        { name: 'WebSocket', status: 'online', responseTime: 8, uptime: 99.92 },
        { name: 'File Storage', status: 'degraded', responseTime: 156, uptime: 98.45 }
      ]
    })

    setMetrics(generateMetrics())
    setSystemHealth(generateSystemHealth())

    // Update metrics every 30 seconds
    const interval = setInterval(() => {
      setMetrics(generateMetrics())
      setSystemHealth(generateSystemHealth())
    }, 30000)

    return () => clearInterval(interval)
  }, [])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'good':
      case 'online':
      case 'healthy':
        return 'text-green-600 bg-green-50'
      case 'warning':
      case 'degraded':
        return 'text-yellow-600 bg-yellow-50'
      case 'critical':
      case 'offline':
        return 'text-red-600 bg-red-50'
      default:
        return 'text-gray-600 bg-gray-50'
    }
  }

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up':
        return '↗'
      case 'down':
        return '↘'
      default:
        return '→'
    }
  }

  const formatValue = (value: number, unit: string) => {
    if (unit === 'ms' || unit === 'conn') {
      return Math.round(value).toLocaleString()
    }
    if (unit === '%') {
      return value.toFixed(1)
    }
    return value.toFixed(2)
  }

  return (
    <>
      {/* Performance Monitor Button */}
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-4 left-4 p-3 bg-white rounded-full shadow-lg border border-gray-200 hover:shadow-xl transition-all duration-200 z-30"
        title="Performance Monitor"
      >
        <CpuChipIcon className="h-6 w-6 text-blue-600" />
      </button>

      {/* Performance Panel */}
      {isOpen && (
        <motion.div
          initial={{ opacity: 0, x: -300 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -300 }}
          className="fixed left-4 bottom-20 w-96 bg-white rounded-lg shadow-xl border border-gray-200 z-40 max-h-[80vh] overflow-hidden"
        >
          {/* Header */}
          <div className="px-4 py-3 border-b border-gray-200 bg-gray-50">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <CpuChipIcon className="h-5 w-5 text-blue-600" />
                <h3 className="font-medium text-gray-900">Performance Monitor</h3>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ×
              </button>
            </div>
            <div className="flex items-center space-x-2 mt-2">
              <div className={`w-2 h-2 rounded-full ${
                systemHealth.overall === 'healthy' ? 'bg-green-500' :
                systemHealth.overall === 'degraded' ? 'bg-yellow-500' : 'bg-red-500'
              }`} />
              <span className="text-sm text-gray-600">
                System {systemHealth.overall}
              </span>
              <span className="text-xs text-gray-500">
                Last updated: {new Date().toLocaleTimeString()}
              </span>
            </div>
          </div>

          <div className="max-h-96 overflow-y-auto">
            {/* Key Metrics */}
            <div className="p-4 space-y-3">
              <h4 className="text-sm font-medium text-gray-900">Key Metrics</h4>
              {metrics.slice(0, 4).map((metric, index) => (
                <div key={metric.name} className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
                  <div className="flex-1">
                    <div className="text-sm font-medium text-gray-900">{metric.name}</div>
                    <div className="flex items-center space-x-2">
                      <span className="text-lg font-semibold text-gray-900">
                        {formatValue(metric.value, metric.unit)}
                      </span>
                      <span className="text-sm text-gray-500">{metric.unit}</span>
                      <span className="text-sm">{getTrendIcon(metric.trend)}</span>
                    </div>
                  </div>
                  <div className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(metric.status)}`}>
                    {metric.status}
                  </div>
                </div>
              ))}
            </div>

            {/* Performance Chart */}
            <div className="p-4 border-t border-gray-200">
              <h4 className="text-sm font-medium text-gray-900 mb-3">Response Time Trend</h4>
              <div className="h-32">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={metrics[0]?.history || []}>
                    <defs>
                      <linearGradient id="responseTimeGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <XAxis 
                      dataKey="timestamp" 
                      tickFormatter={(value) => new Date(value).toLocaleTimeString('en-US', { 
                        hour: '2-digit', 
                        minute: '2-digit' 
                      })}
                      fontSize={10}
                    />
                    <YAxis fontSize={10} />
                    <Tooltip 
                      formatter={(value: any) => [`${Math.round(value)}ms`, 'Response Time']}
                      labelFormatter={(value) => new Date(value).toLocaleTimeString()}
                    />
                    <Area
                      type="monotone"
                      dataKey="value"
                      stroke="#3B82F6"
                      strokeWidth={2}
                      fillOpacity={1}
                      fill="url(#responseTimeGradient)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Service Status */}
            <div className="p-4 border-t border-gray-200">
              <h4 className="text-sm font-medium text-gray-900 mb-3">Service Status</h4>
              <div className="space-y-2">
                {systemHealth.services.map((service, index) => (
                  <div key={service.name} className="flex items-center justify-between text-sm">
                    <div className="flex items-center space-x-2">
                      <div className={`w-2 h-2 rounded-full ${
                        service.status === 'online' ? 'bg-green-500' :
                        service.status === 'degraded' ? 'bg-yellow-500' : 'bg-red-500'
                      }`} />
                      <span className="text-gray-900">{service.name}</span>
                    </div>
                    <div className="flex items-center space-x-3 text-xs text-gray-500">
                      <span>{service.responseTime}ms</span>
                      <span>{service.uptime.toFixed(2)}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Quick Actions */}
            <div className="p-4 border-t border-gray-200 bg-gray-50">
              <div className="grid grid-cols-2 gap-2">
                <button className="px-3 py-2 text-xs bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors">
                  View Logs
                </button>
                <button className="px-3 py-2 text-xs border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors">
                  Export Report
                </button>
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </>
  )
}