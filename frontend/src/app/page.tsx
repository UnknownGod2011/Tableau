'use client'

import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  ChartBarIcon, 
  CurrencyDollarIcon, 
  ShieldCheckIcon,
  ChatBubbleLeftRightIcon,
  ArrowTrendingUpIcon,
  SparklesIcon,
  EyeIcon,
  CheckCircleIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline'
import AdvancedCharts from '@/components/AdvancedCharts'
import TreasuryOverview from '@/components/TreasuryOverview'
import RiskDashboard from '@/components/RiskDashboard'
import AIChat from '@/components/AIChat'
import Dock from '@/components/Dock'
import '@/components/Dock.css'
import GlareHover from '@/components/GlareHover'
import ShinyText from '@/components/ShinyText'
import LiveIndicator from '@/components/ui/LiveIndicator'
import DataRefreshIndicator from '@/components/ui/DataRefreshIndicator'
import AnimatedCounter from '@/components/ui/AnimatedCounter'

export default function HomePage() {
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('overview')
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [lastUpdated, setLastUpdated] = useState(new Date())
  const [kpiData, setKpiData] = useState({
    totalCash: 300000000,
    totalInvestments: 200660000,
    portfolioVar: 2450000,
    yieldOptimization: 1250000
  })

  const dockItems = [
    { icon: <CurrencyDollarIcon className="h-6 w-6" />, label: 'Treasury Overview', onClick: () => setActiveTab('overview'), className: activeTab === 'overview' ? 'active' : '' },
    { icon: <ChartBarIcon className="h-6 w-6" />, label: 'Advanced Analytics', onClick: () => setActiveTab('analytics'), className: activeTab === 'analytics' ? 'active' : '' },
    { icon: <ShieldCheckIcon className="h-6 w-6" />, label: 'Risk Dashboard', onClick: () => setActiveTab('risk'), className: activeTab === 'risk' ? 'active' : '' },
    { icon: <ChatBubbleLeftRightIcon className="h-6 w-6" />, label: 'AI Analytics', onClick: () => setActiveTab('ai'), className: activeTab === 'ai' ? 'active' : '' }
  ]

  useEffect(() => {
    const timer = setTimeout(() => setLoading(false), 2000)
    return () => clearTimeout(timer)
  }, [])

  const handleRefresh = useCallback(() => {
    setIsRefreshing(true)
    setTimeout(() => {
      setKpiData(prev => ({
        totalCash: prev.totalCash + Math.floor(Math.random() * 1000000 - 500000),
        totalInvestments: prev.totalInvestments + Math.floor(Math.random() * 500000 - 250000),
        portfolioVar: prev.portfolioVar + Math.floor(Math.random() * 100000 - 50000),
        yieldOptimization: prev.yieldOptimization + Math.floor(Math.random() * 50000)
      }))
      setLastUpdated(new Date())
      setIsRefreshing(false)
    }, 1500)
  }, [])

  const pageVariants = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -20 }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center">
        <motion.div 
          className="text-center"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
        >
          <div className="relative">
            <motion.div 
              className="h-32 w-32 rounded-full border-4 border-blue-200 mx-auto"
              animate={{ rotate: 360 }}
              transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            />
            <motion.div 
              className="absolute inset-0 h-32 w-32 rounded-full border-4 border-transparent border-t-blue-600 mx-auto"
              animate={{ rotate: -360 }}
              transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
            />
            <div className="absolute inset-4 bg-white rounded-full flex items-center justify-center shadow-lg">
              <motion.div animate={{ scale: [1, 1.2, 1] }} transition={{ duration: 2, repeat: Infinity }}>
                <SparklesIcon className="h-12 w-12 text-blue-600" />
              </motion.div>
            </div>
          </div>
          <motion.h2 
            className="text-3xl font-bold text-gray-900 mt-6"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            Loading TreasuryIQ
          </motion.h2>
          <motion.p 
            className="text-gray-600 mt-2"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
          >
            Initializing advanced treasury analytics...
          </motion.p>
          <div className="mt-8 space-y-3">
            {['Loading market data', 'Calculating risk metrics', 'Initializing AI insights'].map((text, i) => (
              <motion.div 
                key={i}
                className="flex items-center justify-center space-x-2"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.7 + i * 0.2 }}
              >
                <motion.div 
                  className={`w-3 h-3 rounded-full ${i === 0 ? 'bg-blue-600' : i === 1 ? 'bg-green-600' : 'bg-purple-600'}`}
                  animate={{ scale: [1, 1.3, 1] }}
                  transition={{ duration: 0.6, repeat: Infinity, delay: i * 0.2 }}
                />
                <span className="text-sm text-gray-600">{text}</span>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    )
  }

  return (
    <motion.div 
      className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-blue-50 pb-24"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      {/* Animated Background */}
      <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute -top-1/2 -left-1/2 w-full h-full"
          style={{ background: 'radial-gradient(circle, rgba(59, 130, 246, 0.05) 0%, transparent 50%)' }}
          animate={{ x: [0, 100, 0], y: [0, 50, 0] }}
          transition={{ duration: 20, repeat: Infinity, ease: "easeInOut" }}
        />
        <motion.div
          className="absolute -bottom-1/2 -right-1/2 w-full h-full"
          style={{ background: 'radial-gradient(circle, rgba(139, 92, 246, 0.03) 0%, transparent 50%)' }}
          animate={{ x: [0, -80, 0], y: [0, -60, 0] }}
          transition={{ duration: 25, repeat: Infinity, ease: "easeInOut" }}
        />
      </div>

      {/* Header */}
      <motion.div 
        className="bg-white/95 backdrop-blur-sm shadow-lg border-b border-gray-200 sticky top-0 z-40"
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div>
              <h1 className="text-4xl font-bold"><ShinyText speed={4}>TreasuryIQ</ShinyText></h1>
              <p className="text-gray-600 mt-1">AI-Powered Corporate Treasury Management</p>
            </div>
            <div className="flex items-center space-x-6">
              <DataRefreshIndicator lastUpdated={lastUpdated} onRefresh={handleRefresh} isRefreshing={isRefreshing} />
              <div className="text-right hidden md:block">
                <p className="text-sm text-gray-500">GlobalTech Industries</p>
                <p className="text-xl font-bold text-gray-900">$500.66M Portfolio</p>
              </div>
              <LiveIndicator status={isRefreshing ? 'syncing' : 'live'} label={isRefreshing ? 'SYNCING' : 'LIVE'} />
            </div>
          </div>
        </div>
      </motion.div>

      {/* KPI Cards */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {[
            { title: 'Total Cash', value: kpiData.totalCash, trend: 2.3, color: 'blue', sparkline: [65, 70, 68, 75, 72, 78, 82, 85, 88, 92], desc: 'Across all entities' },
            { title: 'Total Investments', value: kpiData.totalInvestments, trend: 1.8, color: 'green', sparkline: [55, 58, 62, 65, 68, 70, 73, 75, 78, 80], desc: 'Fixed income portfolio' },
            { title: 'Portfolio VaR (1D)', value: kpiData.portfolioVar, trend: -5.2, color: 'amber', sparkline: [85, 82, 78, 75, 72, 70, 68, 65, 62, 60], desc: '95% confidence level' },
            { title: 'Yield Optimization', value: kpiData.yieldOptimization, trend: 0, color: 'purple', sparkline: [45, 50, 55, 60, 65, 70, 75, 80, 85, 90], desc: 'Annual improvement', isNew: true }
          ].map((kpi, index) => (
            <motion.div
              key={kpi.title}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              <GlareHover className="shadow-lg hover:shadow-xl transition-all duration-300">
                <div className="p-6">
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-sm font-medium text-gray-600">{kpi.title}</p>
                    <motion.div 
                      className={`w-2 h-2 rounded-full ${kpi.trend >= 0 ? 'bg-green-500' : 'bg-amber-500'}`}
                      animate={{ scale: [1, 1.3, 1], opacity: [1, 0.7, 1] }}
                      transition={{ duration: 2, repeat: Infinity }}
                    />
                  </div>
                  <div className="text-3xl font-bold text-gray-900 mb-1 font-mono">
                    <AnimatedCounter value={kpi.value} prefix="$" duration={1.5} />
                  </div>
                  <p className="text-xs text-gray-500">{kpi.desc}</p>
                  <div className="flex items-center mt-3">
                    {kpi.isNew ? (
                      <>
                        <SparklesIcon className="h-4 w-4 text-purple-500 mr-1" />
                        <span className="text-sm font-medium text-purple-600">New opportunity</span>
                      </>
                    ) : (
                      <>
                        <ArrowTrendingUpIcon className={`h-4 w-4 mr-1 ${kpi.trend >= 0 ? 'text-green-500' : 'text-red-500 rotate-180'}`} />
                        <span className={`text-sm font-medium ${kpi.trend >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {kpi.trend >= 0 ? '+' : ''}{kpi.trend}%
                        </span>
                        <span className="text-xs text-gray-500 ml-1">vs last month</span>
                      </>
                    )}
                  </div>
                  <div className="mt-3 h-8 flex items-end space-x-0.5">
                    {kpi.sparkline.map((h, i) => (
                      <motion.div
                        key={i}
                        className={`flex-1 rounded-sm bg-${kpi.color}-200`}
                        initial={{ height: 0 }}
                        animate={{ height: `${h}%` }}
                        transition={{ duration: 0.5, delay: 0.5 + i * 0.05 }}
                      />
                    ))}
                  </div>
                </div>
              </GlareHover>
            </motion.div>
          ))}
        </div>

        {/* Tab Content with Page Transitions */}
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            variants={pageVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            transition={{ duration: 0.3 }}
            className="space-y-8"
          >
            {activeTab === 'overview' && <TreasuryOverview data={{}} />}
            
            {activeTab === 'analytics' && (
              <div className="space-y-8">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  <AdvancedCharts type="cashFlow" title="Cash Flow Analysis & Forecasting" height={400} />
                  <AdvancedCharts type="performance" title="Portfolio Performance Attribution" height={400} />
                </div>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  <AdvancedCharts type="allocation" title="Asset Allocation & Composition" height={400} />
                  <AdvancedCharts type="correlation" title="Asset Correlation Matrix" height={400} />
                </div>
              </div>
            )}
            
            {activeTab === 'risk' && (
              <div className="space-y-8">
                <RiskDashboard data={{}} />
                <AdvancedCharts type="riskMetrics" title="Advanced Risk Metrics & VaR Analysis" height={500} />
              </div>
            )}
            
            {activeTab === 'ai' && (
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
              >
                <AIChat />
              </motion.div>
            )}
          </motion.div>
        </AnimatePresence>

        {/* System Status Footer */}
        <motion.div 
          className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center space-x-3 mb-4">
              <CheckCircleIcon className="h-6 w-6 text-green-500" />
              <h3 className="text-lg font-semibold text-gray-900">System Health</h3>
            </div>
            <div className="space-y-3">
              {[
                { name: 'Backend API', status: 'Active' },
                { name: 'Tableau Integration', status: 'Connected' },
                { name: 'AI Assistant', status: 'Ready' },
                { name: 'Real-time Data', status: 'Streaming' }
              ].map((item, i) => (
                <motion.div 
                  key={item.name} 
                  className="flex justify-between items-center"
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.6 + i * 0.1 }}
                >
                  <span className="text-gray-600">{item.name}</span>
                  <div className="flex items-center space-x-2">
                    <motion.div 
                      className="w-2 h-2 bg-green-500 rounded-full"
                      animate={{ scale: [1, 1.3, 1] }}
                      transition={{ duration: 2, repeat: Infinity, delay: i * 0.3 }}
                    />
                    <span className="text-green-600 font-medium text-sm">✓ {item.status}</span>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center space-x-3 mb-4">
              <EyeIcon className="h-6 w-6 text-blue-600" />
              <h3 className="text-lg font-semibold text-gray-900">Quick Actions</h3>
            </div>
            <div className="space-y-3">
              {[
                { name: 'Optimize Cash Allocation', desc: 'AI-powered recommendations' },
                { name: 'Review Risk Exposure', desc: 'Multi-dimensional analysis' },
                { name: 'Generate Reports', desc: 'Automated compliance reports' }
              ].map((action, i) => (
                <motion.button
                  key={action.name}
                  className="w-full text-left p-3 bg-gray-50 rounded-lg border border-transparent hover:bg-blue-50 hover:border-blue-200 transition-all"
                  whileHover={{ x: 4 }}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.7 + i * 0.1 }}
                >
                  <div className="font-medium text-gray-900">{action.name}</div>
                  <div className="text-sm text-gray-600">{action.desc}</div>
                </motion.button>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center space-x-3 mb-4">
              <SparklesIcon className="h-6 w-6 text-purple-600" />
              <h3 className="text-lg font-semibold text-gray-900">Recent Insights</h3>
            </div>
            <div className="space-y-3">
              {[
                { time: '2 min ago', insight: 'Cash optimization opportunity identified' },
                { time: '15 min ago', insight: 'FX hedge recommendation updated' },
                { time: '1 hour ago', insight: 'Market volatility alert resolved' }
              ].map((item, i) => (
                <motion.div 
                  key={i} 
                  className="flex items-start space-x-3"
                  initial={{ opacity: 0, x: 10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.8 + i * 0.1 }}
                >
                  <motion.div 
                    className="w-2 h-2 bg-purple-500 rounded-full mt-2"
                    animate={{ scale: [1, 1.5, 1] }}
                    transition={{ duration: 3, repeat: Infinity, delay: i * 0.5 }}
                  />
                  <div className="flex-1">
                    <p className="text-sm text-gray-900">{item.insight}</p>
                    <p className="text-xs text-gray-500">{item.time}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.div>
      </div>

      <Dock items={dockItems} panelHeight={68} baseItemSize={50} magnification={70} distance={200} />
    </motion.div>
  )
}
