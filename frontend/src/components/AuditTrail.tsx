'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  ClockIcon,
  UserIcon,
  DocumentTextIcon,
  ShieldCheckIcon,
  EyeIcon,
  FunnelIcon,
  MagnifyingGlassIcon,
  ArrowDownTrayIcon
} from '@heroicons/react/24/outline'
import { formatDateTime, formatRelativeTime } from '@/lib/utils'

interface AuditEvent {
  id: string
  timestamp: string
  userId: string
  userName: string
  userRole: string
  action: string
  resource: string
  resourceId: string
  details: Record<string, any>
  ipAddress: string
  userAgent: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  category: 'authentication' | 'data_access' | 'configuration' | 'transaction' | 'system'
}

export default function AuditTrail() {
  const [events, setEvents] = useState<AuditEvent[]>([])
  const [filteredEvents, setFilteredEvents] = useState<AuditEvent[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [selectedSeverity, setSelectedSeverity] = useState<string>('all')
  const [dateRange, setDateRange] = useState('7d')

  // Mock audit events
  useEffect(() => {
    const mockEvents: AuditEvent[] = [
      {
        id: '1',
        timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
        userId: 'user_001',
        userName: 'Sarah Chen',
        userRole: 'Treasury Manager',
        action: 'PORTFOLIO_VIEW',
        resource: 'portfolio',
        resourceId: 'us-hq',
        details: { entityName: 'US Headquarters', portfolioValue: 250000000 },
        ipAddress: '192.168.1.100',
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        severity: 'low',
        category: 'data_access'
      },
      {
        id: '2',
        timestamp: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
        userId: 'user_002',
        userName: 'Michael Rodriguez',
        userRole: 'Risk Analyst',
        action: 'RISK_CALCULATION',
        resource: 'risk_model',
        resourceId: 'var_model_001',
        details: { modelType: 'VaR', confidence: 95, result: 2450000 },
        ipAddress: '192.168.1.101',
        userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        severity: 'medium',
        category: 'transaction'
      },
      {
        id: '3',
        timestamp: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
        userId: 'user_003',
        userName: 'Emily Johnson',
        userRole: 'System Administrator',
        action: 'CONFIG_UPDATE',
        resource: 'system_settings',
        resourceId: 'notification_config',
        details: { setting: 'risk_alert_threshold', oldValue: 3000000, newValue: 2500000 },
        ipAddress: '192.168.1.102',
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        severity: 'high',
        category: 'configuration'
      },
      {
        id: '4',
        timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        userId: 'user_001',
        userName: 'Sarah Chen',
        userRole: 'Treasury Manager',
        action: 'LOGIN_SUCCESS',
        resource: 'authentication',
        resourceId: 'session_12345',
        details: { loginMethod: '2FA', location: 'New York, NY' },
        ipAddress: '192.168.1.100',
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        severity: 'low',
        category: 'authentication'
      },
      {
        id: '5',
        timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
        userId: 'system',
        userName: 'System',
        userRole: 'System',
        action: 'DATA_BACKUP',
        resource: 'database',
        resourceId: 'treasury_db',
        details: { backupSize: '2.3GB', duration: '45s', status: 'success' },
        ipAddress: '127.0.0.1',
        userAgent: 'TreasuryIQ-BackupService/1.0',
        severity: 'low',
        category: 'system'
      },
      {
        id: '6',
        timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
        userId: 'user_004',
        userName: 'David Kim',
        userRole: 'Compliance Officer',
        action: 'EXPORT_DATA',
        resource: 'compliance_report',
        resourceId: 'monthly_report_202412',
        details: { reportType: 'regulatory', format: 'PDF', recordCount: 15420 },
        ipAddress: '192.168.1.103',
        userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        severity: 'medium',
        category: 'data_access'
      }
    ]

    setEvents(mockEvents)
    setFilteredEvents(mockEvents)
    setLoading(false)
  }, [])

  // Filter events based on search and filters
  useEffect(() => {
    let filtered = events

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(event =>
        event.userName.toLowerCase().includes(searchTerm.toLowerCase()) ||
        event.action.toLowerCase().includes(searchTerm.toLowerCase()) ||
        event.resource.toLowerCase().includes(searchTerm.toLowerCase()) ||
        JSON.stringify(event.details).toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    // Category filter
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(event => event.category === selectedCategory)
    }

    // Severity filter
    if (selectedSeverity !== 'all') {
      filtered = filtered.filter(event => event.severity === selectedSeverity)
    }

    // Date range filter
    const now = new Date()
    const cutoffDate = new Date()
    switch (dateRange) {
      case '1h':
        cutoffDate.setHours(now.getHours() - 1)
        break
      case '24h':
        cutoffDate.setDate(now.getDate() - 1)
        break
      case '7d':
        cutoffDate.setDate(now.getDate() - 7)
        break
      case '30d':
        cutoffDate.setDate(now.getDate() - 30)
        break
    }
    
    filtered = filtered.filter(event => new Date(event.timestamp) >= cutoffDate)

    setFilteredEvents(filtered)
  }, [events, searchTerm, selectedCategory, selectedSeverity, dateRange])

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200'
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      default:
        return 'bg-green-100 text-green-800 border-green-200'
    }
  }

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'authentication':
        return <ShieldCheckIcon className="h-4 w-4" />
      case 'data_access':
        return <EyeIcon className="h-4 w-4" />
      case 'configuration':
        return <DocumentTextIcon className="h-4 w-4" />
      case 'transaction':
        return <ClockIcon className="h-4 w-4" />
      default:
        return <UserIcon className="h-4 w-4" />
    }
  }

  const exportAuditLog = () => {
    const csvContent = [
      ['Timestamp', 'User', 'Action', 'Resource', 'Severity', 'IP Address', 'Details'].join(','),
      ...filteredEvents.map(event => [
        event.timestamp,
        event.userName,
        event.action,
        event.resource,
        event.severity,
        event.ipAddress,
        JSON.stringify(event.details).replace(/,/g, ';')
      ].join(','))
    ].join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `audit_trail_${new Date().toISOString().split('T')[0]}.csv`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Audit Trail</h3>
            <p className="text-sm text-gray-600 mt-1">
              Security and compliance activity log
            </p>
          </div>
          <button
            onClick={exportAuditLog}
            className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
            Export
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Search */}
          <div className="relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search events..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-full"
            />
          </div>

          {/* Category Filter */}
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="all">All Categories</option>
            <option value="authentication">Authentication</option>
            <option value="data_access">Data Access</option>
            <option value="configuration">Configuration</option>
            <option value="transaction">Transaction</option>
            <option value="system">System</option>
          </select>

          {/* Severity Filter */}
          <select
            value={selectedSeverity}
            onChange={(e) => setSelectedSeverity(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="all">All Severities</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>

          {/* Date Range */}
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="1h">Last Hour</option>
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
          </select>
        </div>
      </div>

      {/* Events List */}
      <div className="max-h-96 overflow-y-auto">
        {loading ? (
          <div className="p-8 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-500">Loading audit events...</p>
          </div>
        ) : filteredEvents.length === 0 ? (
          <div className="p-8 text-center">
            <ClockIcon className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">No audit events found</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            <AnimatePresence>
              {filteredEvents.map((event, index) => (
                <motion.div
                  key={event.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ delay: index * 0.05 }}
                  className="px-6 py-4 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-start space-x-4">
                    {/* Icon */}
                    <div className="flex-shrink-0 mt-1">
                      <div className="h-8 w-8 bg-gray-100 rounded-full flex items-center justify-center">
                        {getCategoryIcon(event.category)}
                      </div>
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <p className="text-sm font-medium text-gray-900">
                            {event.userName}
                          </p>
                          <span className="text-sm text-gray-500">•</span>
                          <p className="text-sm text-gray-600">{event.action}</p>
                          <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border ${getSeverityColor(event.severity)}`}>
                            {event.severity}
                          </span>
                        </div>
                        <div className="text-right">
                          <p className="text-xs text-gray-500">
                            {formatRelativeTime(event.timestamp)}
                          </p>
                          <p className="text-xs text-gray-400">
                            {formatDateTime(event.timestamp)}
                          </p>
                        </div>
                      </div>

                      <div className="mt-1">
                        <p className="text-sm text-gray-600">
                          {event.resource} • {event.resourceId}
                        </p>
                      </div>

                      {/* Details */}
                      {Object.keys(event.details).length > 0 && (
                        <div className="mt-2 p-2 bg-gray-50 rounded text-xs">
                          <div className="grid grid-cols-2 gap-2">
                            {Object.entries(event.details).map(([key, value]) => (
                              <div key={key}>
                                <span className="font-medium text-gray-600">{key}:</span>{' '}
                                <span className="text-gray-800">
                                  {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Metadata */}
                      <div className="mt-2 flex items-center space-x-4 text-xs text-gray-500">
                        <span>IP: {event.ipAddress}</span>
                        <span>Role: {event.userRole}</span>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="px-6 py-3 border-t border-gray-200 bg-gray-50">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <span>
            Showing {filteredEvents.length} of {events.length} events
          </span>
          <span>
            Retention: 90 days • Compliance: SOX, SOC 2
          </span>
        </div>
      </div>
    </div>
  )
}