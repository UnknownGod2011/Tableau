'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  ChartBarIcon,
  ShieldCheckIcon,
  DocumentCheckIcon,
  ClockIcon,
  CogIcon,
  BellIcon,
  UserGroupIcon,
  GlobeAltIcon,
  ServerIcon,
  LockClosedIcon
} from '@heroicons/react/24/outline'
import AdvancedCharts from './AdvancedCharts'
import AuditTrail from './AuditTrail'
import ComplianceReporting from './ComplianceReporting'
import PerformanceMonitor from './PerformanceMonitor'
import ExportCenter from './ExportCenter'
import SettingsPanel from './SettingsPanel'
import { useTreasuryStore } from '@/store/treasuryStore'

interface DashboardWidget {
  id: string
  title: string
  component: React.ComponentType<any>
  icon: React.ComponentType<{ className?: string }>
  description: string
  category: 'analytics' | 'compliance' | 'operations' | 'security'
  size: 'small' | 'medium' | 'large' | 'full'
  enabled: boolean
}

export default function EnterpriseDashboard() {
  const [activeWidgets, setActiveWidgets] = useState<string[]>([])
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [dashboardLayout, setDashboardLayout] = useState<'grid' | 'list'>('grid')
  const { theme } = useTreasuryStore()

  const widgets: DashboardWidget[] = [
    {
      id: 'cash-flow-analysis',
      title: 'Cash Flow Analysis',
      component: () => <AdvancedCharts type="cashFlow" title="Cash Flow Trends" height={300} />,
      icon: ChartBarIcon,
      description: 'Real-time cash flow monitoring and forecasting',
      category: 'analytics',
      size: 'large',
      enabled: true
    },
    {
      id: 'risk-metrics',
      title: 'Risk Metrics',
      component: () => <AdvancedCharts type="riskMetrics" title="Risk Dashboard" height={300} />,
      icon: ShieldCheckIcon,
      description: 'VaR, stress testing, and risk limit monitoring',
      category: 'analytics',
      size: 'large',
      enabled: true
    },
    {
      id: 'portfolio-allocation',
      title: 'Portfolio Allocation',
      component: () => <AdvancedCharts type="allocation" title="Asset Allocation" height={350} />,
      icon: ChartBarIcon,
      description: 'Investment portfolio breakdown and optimization',
      category: 'analytics',
      size: 'medium',
      enabled: true
    },
    {
      id: 'performance-attribution',
      title: 'Performance Attribution',
      component: () => <AdvancedCharts type="performance" title="Performance Analysis" height={300} />,
      icon: ChartBarIcon,
      description: 'Portfolio performance vs benchmarks',
      category: 'analytics',
      size: 'medium',
      enabled: true
    },
    {
      id: 'compliance-reporting',
      title: 'Compliance Reporting',
      component: ComplianceReporting,
      icon: DocumentCheckIcon,
      description: 'Regulatory compliance and audit management',
      category: 'compliance',
      size: 'full',
      enabled: true
    },
    {
      id: 'audit-trail',
      title: 'Audit Trail',
      component: AuditTrail,
      icon: ClockIcon,
      description: 'Security and compliance activity logging',
      category: 'security',
      size: 'full',
      enabled: true
    },
    {
      id: 'system-performance',
      title: 'System Performance',
      component: PerformanceMonitor,
      icon: ServerIcon,
      description: 'Real-time system health and performance metrics',
      category: 'operations',
      size: 'small',
      enabled: false
    }
  ]

  const categories = [
    { id: 'all', name: 'All Widgets', icon: GlobeAltIcon },
    { id: 'analytics', name: 'Analytics', icon: ChartBarIcon },
    { id: 'compliance', name: 'Compliance', icon: DocumentCheckIcon },
    { id: 'operations', name: 'Operations', icon: CogIcon },
    { id: 'security', name: 'Security', icon: LockClosedIcon }
  ]

  useEffect(() => {
    // Initialize with enabled widgets
    setActiveWidgets(widgets.filter(w => w.enabled).map(w => w.id))
  }, [])

  const filteredWidgets = selectedCategory === 'all' 
    ? widgets 
    : widgets.filter(w => w.category === selectedCategory)

  const toggleWidget = (widgetId: string) => {
    setActiveWidgets(prev => 
      prev.includes(widgetId)
        ? prev.filter(id => id !== widgetId)
        : [...prev, widgetId]
    )
  }

  const getGridClasses = (size: string) => {
    switch (size) {
      case 'small':
        return 'col-span-1 row-span-1'
      case 'medium':
        return 'col-span-1 lg:col-span-2 row-span-1'
      case 'large':
        return 'col-span-1 lg:col-span-3 row-span-1'
      case 'full':
        return 'col-span-1 lg:col-span-4 row-span-2'
      default:
        return 'col-span-1 row-span-1'
    }
  }

  const renderWidget = (widget: DashboardWidget) => {
    const Component = widget.component
    return (
      <motion.div
        key={widget.id}
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        transition={{ duration: 0.3 }}
        className={`bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden ${
          dashboardLayout === 'grid' ? getGridClasses(widget.size) : 'mb-6'
        }`}
      >
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="h-8 w-8 bg-blue-50 rounded-lg flex items-center justify-center">
                <widget.icon className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">{widget.title}</h3>
                <p className="text-sm text-gray-600">{widget.description}</p>
              </div>
            </div>
            <button
              onClick={() => toggleWidget(widget.id)}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              ×
            </button>
          </div>
          <Component />
        </div>
      </motion.div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Enterprise Dashboard</h1>
          <p className="text-gray-600 mt-1">
            Comprehensive treasury management and compliance monitoring
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <ExportCenter />
          <SettingsPanel />
          <div className="flex items-center space-x-2 bg-white rounded-lg border border-gray-200 p-1">
            <button
              onClick={() => setDashboardLayout('grid')}
              className={`p-2 rounded transition-colors ${
                dashboardLayout === 'grid' 
                  ? 'bg-blue-100 text-blue-600' 
                  : 'text-gray-400 hover:text-gray-600'
              }`}
            >
              <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                <path d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM11 13a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
              </svg>
            </button>
            <button
              onClick={() => setDashboardLayout('list')}
              className={`p-2 rounded transition-colors ${
                dashboardLayout === 'list' 
                  ? 'bg-blue-100 text-blue-600' 
                  : 'text-gray-400 hover:text-gray-600'
              }`}
            >
              <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Category Filter */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-1">
            {categories.map((category) => {
              const Icon = category.icon
              return (
                <button
                  key={category.id}
                  onClick={() => setSelectedCategory(category.id)}
                  className={`flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    selectedCategory === category.id
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  }`}
                >
                  <Icon className="h-4 w-4 mr-2" />
                  {category.name}
                </button>
              )
            })}
          </div>
          
          <div className="text-sm text-gray-600">
            {activeWidgets.length} of {filteredWidgets.length} widgets active
          </div>
        </div>
      </div>

      {/* Widget Selector */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
        <h3 className="text-sm font-medium text-gray-900 mb-3">Available Widgets</h3>
        <div className="flex flex-wrap gap-2">
          {filteredWidgets.map((widget) => (
            <button
              key={widget.id}
              onClick={() => toggleWidget(widget.id)}
              className={`flex items-center px-3 py-2 rounded-lg text-sm font-medium border transition-all ${
                activeWidgets.includes(widget.id)
                  ? 'bg-blue-50 border-blue-200 text-blue-700'
                  : 'bg-gray-50 border-gray-200 text-gray-600 hover:bg-gray-100'
              }`}
            >
              <widget.icon className="h-4 w-4 mr-2" />
              {widget.title}
              {activeWidgets.includes(widget.id) && (
                <span className="ml-2 text-xs">✓</span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Dashboard Content */}
      <div className={
        dashboardLayout === 'grid' 
          ? 'grid grid-cols-1 lg:grid-cols-4 gap-6 auto-rows-min'
          : 'space-y-6'
      }>
        <AnimatePresence>
          {filteredWidgets
            .filter(widget => activeWidgets.includes(widget.id))
            .map(widget => renderWidget(widget))}
        </AnimatePresence>
      </div>

      {/* Empty State */}
      {activeWidgets.length === 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center py-12"
        >
          <ChartBarIcon className="h-12 w-12 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No widgets active</h3>
          <p className="text-gray-600 mb-4">
            Select widgets from the available options above to customize your dashboard
          </p>
          <button
            onClick={() => setActiveWidgets(widgets.filter(w => w.enabled).map(w => w.id))}
            className="btn-primary"
          >
            Load Default Widgets
          </button>
        </motion.div>
      )}

      {/* Performance Monitor (Always visible) */}
      <PerformanceMonitor />
    </div>
  )
}