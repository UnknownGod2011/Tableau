'use client'

import { useState, useEffect } from 'react'
import { 
  ChartBarIcon, 
  CurrencyDollarIcon, 
  ShieldCheckIcon,
  ChatBubbleLeftRightIcon,
  ArrowTrendingUpIcon,
  SparklesIcon,
  EyeIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline'
import AdvancedCharts from '@/components/AdvancedCharts'
import TreasuryOverview from '@/components/TreasuryOverview'
import RiskDashboard from '@/components/RiskDashboard'

export default function HomePage() {
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('overview')
  const [animatedValues, setAnimatedValues] = useState({
    totalCash: 0,
    totalInvestments: 0,
    portfolioVar: 0,
    yieldOptimization: 0
  })

  useEffect(() => {
    const timer = setTimeout(() => {
      setLoading(false)
      // Start number animations
      animateNumbers()
    }, 2000)
    return () => clearTimeout(timer)
  }, [])

  const animateNumbers = () => {
    const targets = {
      totalCash: 300000000,
      totalInvestments: 200660000,
      portfolioVar: 2450000,
      yieldOptimization: 1250000
    }

    const duration = 2000
    const steps = 60
    const stepDuration = duration / steps

    let currentStep = 0
    const interval = setInterval(() => {
      currentStep++
      const progress = currentStep / steps
      const easeOutQuart = 1 - Math.pow(1 - progress, 4)

      setAnimatedValues({
        totalCash: Math.floor(targets.totalCash * easeOutQuart),
        totalInvestments: Math.floor(targets.totalInvestments * easeOutQuart),
        portfolioVar: Math.floor(targets.portfolioVar * easeOutQuart),
        yieldOptimization: Math.floor(targets.yieldOptimization * easeOutQuart)
      })

      if (currentStep >= steps) {
        clearInterval(interval)
        setAnimatedValues(targets)
      }
    }, stepDuration)
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center">
        <div className="text-center">
          {/* Sophisticated Loading Animation */}
          <div className="relative">
            <div className="animate-spin rounded-full h-32 w-32 border-4 border-transparent bg-gradient-to-r from-blue-500 to-purple-600 bg-clip-border mx-auto"></div>
            <div className="absolute inset-0 animate-spin rounded-full h-32 w-32 border-4 border-transparent bg-gradient-to-r from-purple-500 to-blue-600 bg-clip-border mx-auto" style={{ animationDirection: 'reverse', animationDuration: '3s' }}></div>
            <div className="absolute inset-4 bg-white rounded-full flex items-center justify-center">
              <SparklesIcon className="h-12 w-12 text-blue-600 animate-pulse" />
            </div>
          </div>
          
          <h2 className="text-3xl font-bold text-gray-900 mt-6">Loading TreasuryIQ</h2>
          <p className="text-gray-600 mt-2">Initializing advanced treasury analytics...</p>
          
          {/* Multi-stage Progress */}
          <div className="mt-8 space-y-3">
            <div className="flex items-center justify-center space-x-2">
              <div className="w-3 h-3 bg-blue-600 rounded-full animate-bounce"></div>
              <span className="text-sm text-gray-600">Loading market data</span>
            </div>
            <div className="flex items-center justify-center space-x-2">
              <div className="w-3 h-3 bg-green-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              <span className="text-sm text-gray-600">Calculating risk metrics</span>
            </div>
            <div className="flex items-center justify-center space-x-2">
              <div className="w-3 h-3 bg-purple-600 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
              <span className="text-sm text-gray-600">Initializing AI insights</span>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-blue-50">
      {/* Enhanced Header */}
      <div className="bg-white shadow-lg border-b border-gray-200 backdrop-blur-sm bg-white/95">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                TreasuryIQ
              </h1>
              <p className="text-gray-600 mt-1">AI-Powered Corporate Treasury Management</p>
            </div>
            <div className="flex items-center space-x-6">
              <div className="text-right">
                <p className="text-sm text-gray-500">GlobalTech Industries</p>
                <p className="text-xl font-bold text-gray-900">$500.66M Portfolio</p>
              </div>
              <div className="flex items-center space-x-2 bg-green-50 px-3 py-2 rounded-full">
                <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm font-medium text-green-700">Live Data</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            {[
              { id: 'overview', name: 'Treasury Overview', icon: CurrencyDollarIcon },
              { id: 'analytics', name: 'Advanced Analytics', icon: ChartBarIcon },
              { id: 'risk', name: 'Risk Dashboard', icon: ShieldCheckIcon },
              { id: 'ai', name: 'AI Insights', icon: ChatBubbleLeftRightIcon }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <tab.icon className="h-5 w-5" />
                <span>{tab.name}</span>
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Enhanced Animated Metric Cards */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Total Cash Card */}
          <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6 hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-2">
                  <p className="text-sm font-medium text-gray-600">Total Cash</p>
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                </div>
                <p className="text-3xl font-bold text-gray-900 mb-1 font-mono">
                  ${animatedValues.totalCash.toLocaleString()}
                </p>
                <p className="text-xs text-gray-500">Across all entities</p>
                <div className="flex items-center mt-3">
                  <ArrowTrendingUpIcon className="h-4 w-4 text-green-500 mr-1" />
                  <span className="text-sm font-medium text-green-600">+2.3%</span>
                  <span className="text-xs text-gray-500 ml-1">vs last month</span>
                </div>
                {/* Mini Sparkline */}
                <div className="mt-3 h-8 flex items-end space-x-1">
                  {[65, 70, 68, 75, 72, 78, 82, 85, 88, 92].map((height, index) => (
                    <div
                      key={index}
                      className="bg-green-200 rounded-sm flex-1 transition-all duration-300"
                      style={{ height: `${height}%` }}
                    ></div>
                  ))}
                </div>
              </div>
              <div className="flex flex-col items-center">
                <div className="relative">
                  <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center">
                    <CurrencyDollarIcon className="h-8 w-8 text-white" />
                  </div>
                  <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full animate-ping"></div>
                </div>
              </div>
            </div>
          </div>

          {/* Total Investments Card */}
          <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6 hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-2">
                  <p className="text-sm font-medium text-gray-600">Total Investments</p>
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                </div>
                <p className="text-3xl font-bold text-gray-900 mb-1 font-mono">
                  ${animatedValues.totalInvestments.toLocaleString()}
                </p>
                <p className="text-xs text-gray-500">Fixed income portfolio</p>
                <div className="flex items-center mt-3">
                  <ArrowTrendingUpIcon className="h-4 w-4 text-green-500 mr-1" />
                  <span className="text-sm font-medium text-green-600">+1.8%</span>
                  <span className="text-xs text-gray-500 ml-1">vs last month</span>
                </div>
                {/* Mini Sparkline */}
                <div className="mt-3 h-8 flex items-end space-x-1">
                  {[55, 58, 62, 65, 68, 70, 73, 75, 78, 80].map((height, index) => (
                    <div
                      key={index}
                      className="bg-blue-200 rounded-sm flex-1 transition-all duration-300"
                      style={{ height: `${height}%` }}
                    ></div>
                  ))}
                </div>
              </div>
              <div className="flex flex-col items-center">
                <div className="relative">
                  <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-green-600 rounded-full flex items-center justify-center">
                    <ChartBarIcon className="h-8 w-8 text-white" />
                  </div>
                  <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full animate-ping"></div>
                </div>
              </div>
            </div>
          </div>

          {/* Portfolio VaR Card */}
          <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6 hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-2">
                  <p className="text-sm font-medium text-gray-600">Portfolio VaR (1D)</p>
                  <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse"></div>
                </div>
                <p className="text-3xl font-bold text-gray-900 mb-1 font-mono">
                  ${animatedValues.portfolioVar.toLocaleString()}
                </p>
                <p className="text-xs text-gray-500">95% confidence level</p>
                <div className="flex items-center mt-3">
                  <ArrowTrendingUpIcon className="h-4 w-4 text-red-500 mr-1 transform rotate-180" />
                  <span className="text-sm font-medium text-red-600">-5.2%</span>
                  <span className="text-xs text-gray-500 ml-1">vs last month</span>
                </div>
                {/* Mini Sparkline */}
                <div className="mt-3 h-8 flex items-end space-x-1">
                  {[85, 82, 78, 75, 72, 70, 68, 65, 62, 60].map((height, index) => (
                    <div
                      key={index}
                      className="bg-red-200 rounded-sm flex-1 transition-all duration-300"
                      style={{ height: `${height}%` }}
                    ></div>
                  ))}
                </div>
              </div>
              <div className="flex flex-col items-center">
                <div className="relative">
                  <div className="w-16 h-16 bg-gradient-to-br from-red-500 to-red-600 rounded-full flex items-center justify-center">
                    <ShieldCheckIcon className="h-8 w-8 text-white" />
                  </div>
                  <div className="absolute -top-1 -right-1 w-4 h-4 bg-yellow-500 rounded-full animate-ping"></div>
                </div>
              </div>
            </div>
          </div>

          {/* Yield Optimization Card */}
          <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6 hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-2">
                  <p className="text-sm font-medium text-gray-600">Yield Optimization</p>
                  <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse"></div>
                </div>
                <p className="text-3xl font-bold text-gray-900 mb-1 font-mono">
                  ${animatedValues.yieldOptimization.toLocaleString()}
                </p>
                <p className="text-xs text-gray-500">Annual improvement potential</p>
                <div className="flex items-center mt-3">
                  <SparklesIcon className="h-4 w-4 text-purple-500 mr-1" />
                  <span className="text-sm font-medium text-purple-600">New</span>
                  <span className="text-xs text-gray-500 ml-1">opportunity</span>
                </div>
                {/* Mini Sparkline */}
                <div className="mt-3 h-8 flex items-end space-x-1">
                  {[45, 50, 55, 60, 65, 70, 75, 80, 85, 90].map((height, index) => (
                    <div
                      key={index}
                      className="bg-purple-200 rounded-sm flex-1 transition-all duration-300"
                      style={{ height: `${height}%` }}
                    ></div>
                  ))}
                </div>
              </div>
              <div className="flex flex-col items-center">
                <div className="relative">
                  <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-purple-600 rounded-full flex items-center justify-center">
                    <SparklesIcon className="h-8 w-8 text-white" />
                  </div>
                  <div className="absolute -top-1 -right-1 w-4 h-4 bg-purple-500 rounded-full animate-ping"></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Dynamic Content Based on Active Tab */}
        <div className="space-y-8">
          {activeTab === 'overview' && (
            <TreasuryOverview data={{}} />
          )}
          
          {activeTab === 'analytics' && (
            <div className="space-y-8">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <AdvancedCharts 
                  type="cashFlow" 
                  title="Cash Flow Analysis & Forecasting"
                  height={400}
                />
                <AdvancedCharts 
                  type="performance" 
                  title="Portfolio Performance Attribution"
                  height={400}
                />
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <AdvancedCharts 
                  type="allocation" 
                  title="Asset Allocation & Composition"
                  height={400}
                />
                <AdvancedCharts 
                  type="correlation" 
                  title="Asset Correlation Matrix"
                  height={400}
                />
              </div>
            </div>
          )}
          
          {activeTab === 'risk' && (
            <div className="space-y-8">
              <RiskDashboard data={{}} />
              <AdvancedCharts 
                type="riskMetrics" 
                title="Advanced Risk Metrics & VaR Analysis"
                height={500}
              />
            </div>
          )}
          
          {activeTab === 'ai' && (
            <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-8">
              <div className="text-center">
                <div className="relative inline-block">
                  <ChatBubbleLeftRightIcon className="h-24 w-24 text-blue-600 mx-auto mb-6" />
                  <div className="absolute -top-2 -right-2 w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                    <SparklesIcon className="h-4 w-4 text-white" />
                  </div>
                </div>
                <h2 className="text-3xl font-bold text-gray-900 mb-4">
                  AI-Powered Treasury Insights
                </h2>
                <p className="text-lg text-gray-600 mb-8">
                  Conversational AI assistant powered by Salesforce Agentforce for intelligent treasury management.
                </p>
                
                {/* AI Insight Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                  <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-lg border border-blue-200">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold text-blue-900">Cash Optimization</h3>
                      <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
                    </div>
                    <p className="text-blue-800 mb-3">
                      Move $15M from low-yield checking to money market funds
                    </p>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-blue-600">Potential Impact</span>
                      <span className="font-bold text-blue-900">+$375K annually</span>
                    </div>
                  </div>
                  
                  <div className="bg-gradient-to-br from-green-50 to-green-100 p-6 rounded-lg border border-green-200">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold text-green-900">Risk Mitigation</h3>
                      <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                    </div>
                    <p className="text-green-800 mb-3">
                      EUR exposure increased 12% - consider additional hedging
                    </p>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-green-600">Risk Reduction</span>
                      <span className="font-bold text-green-900">-$280K VaR</span>
                    </div>
                  </div>
                  
                  <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-6 rounded-lg border border-purple-200">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold text-purple-900">Market Opportunity</h3>
                      <div className="w-3 h-3 bg-purple-500 rounded-full animate-pulse"></div>
                    </div>
                    <p className="text-purple-800 mb-3">
                      Treasury rates favorable for 6-month CD placement
                    </p>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-purple-600">Yield Enhancement</span>
                      <span className="font-bold text-purple-900">+0.75% APY</span>
                    </div>
                  </div>
                </div>
                
                <button className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-3 rounded-lg font-medium hover:from-blue-700 hover:to-purple-700 transition-all duration-300 transform hover:scale-105">
                  Start AI Conversation
                </button>
              </div>
            </div>
          )}
        </div>

        {/* System Status Footer */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center space-x-3 mb-4">
              <CheckCircleIcon className="h-6 w-6 text-green-500" />
              <h3 className="text-lg font-semibold text-gray-900">System Health</h3>
            </div>
            <div className="space-y-3">
              {[
                { name: 'Backend API', status: 'Active', color: 'green' },
                { name: 'Tableau Integration', status: 'Connected', color: 'green' },
                { name: 'AI Assistant', status: 'Ready', color: 'green' },
                { name: 'Real-time Data', status: 'Streaming', color: 'green' }
              ].map((item, index) => (
                <div key={index} className="flex justify-between items-center">
                  <span className="text-gray-600">{item.name}</span>
                  <div className="flex items-center space-x-2">
                    <div className={`w-2 h-2 bg-${item.color}-500 rounded-full animate-pulse`}></div>
                    <span className={`text-${item.color}-600 font-medium text-sm`}>✓ {item.status}</span>
                  </div>
                </div>
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
              ].map((action, index) => (
                <button
                  key={index}
                  className="w-full text-left p-3 bg-gray-50 rounded-lg hover:bg-blue-50 hover:border-blue-200 border border-transparent transition-all duration-200"
                >
                  <div className="font-medium text-gray-900">{action.name}</div>
                  <div className="text-sm text-gray-600">{action.desc}</div>
                </button>
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
              ].map((item, index) => (
                <div key={index} className="flex items-start space-x-3">
                  <div className="w-2 h-2 bg-purple-500 rounded-full mt-2 animate-pulse"></div>
                  <div className="flex-1">
                    <p className="text-sm text-gray-900">{item.insight}</p>
                    <p className="text-xs text-gray-500">{item.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}