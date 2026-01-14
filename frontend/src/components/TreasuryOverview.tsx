'use client'

import { useState, useRef } from 'react'
import { motion, useInView } from 'framer-motion'
import { 
  BanknotesIcon, 
  ChartPieIcon, 
  GlobeAltIcon,
  ArrowTrendingUpIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'

interface TreasuryOverviewProps {
  data: any
}

export default function TreasuryOverview({ data }: TreasuryOverviewProps) {
  const [selectedEntity, setSelectedEntity] = useState('all')
  const containerRef = useRef(null)
  const isInView = useInView(containerRef, { once: true, margin: "-100px" })

  // Mock data for demonstration
  const entities = [
    { id: 'all', name: 'All Entities', flag: '🌍' },
    { id: 'us', name: 'US Headquarters', flag: '🇺🇸' },
    { id: 'eu', name: 'Europe Ltd.', flag: '🇪🇺' },
    { id: 'apac', name: 'Asia Pacific', flag: '🇸🇬' },
    { id: 'ca', name: 'Canada Corp.', flag: '🇨🇦' },
    { id: 'jp', name: 'Japan KK', flag: '🇯🇵' },
  ]

  const cashPositions = [
    { type: 'Checking', amount: 45000000, percentage: 15, yield: 0.5 },
    { type: 'Savings', amount: 75000000, percentage: 25, yield: 1.5 },
    { type: 'Money Market', amount: 105000000, percentage: 35, yield: 2.5 },
    { type: 'Certificates of Deposit', amount: 75000000, percentage: 25, yield: 3.5 },
  ]

  const investments = [
    { type: 'US Treasury 2Y Note', amount: 50000000, yield: 4.5, maturity: '2026-03-15' },
    { type: 'Money Market Fund', amount: 75000000, yield: 2.8, maturity: 'Daily' },
    { type: 'Corporate Bond - Apple', amount: 25000000, yield: 3.8, maturity: '2027-06-01' },
    { type: 'EUR Corporate Bond', amount: 30000000, yield: 3.2, maturity: '2025-12-15' },
    { type: 'Commercial Paper', amount: 20656000, yield: 1.5, maturity: '2024-08-30' },
  ]

  const alerts = [
    {
      id: 1,
      type: 'opportunity',
      title: 'Cash Optimization Opportunity',
      message: 'Move $15M from low-yield checking to money market for +$375K annual yield',
      priority: 'high',
      amount: 375000
    },
    {
      id: 2,
      type: 'risk',
      title: 'FX Exposure Alert',
      message: 'EUR exposure increased 12% - consider additional hedging',
      priority: 'medium',
      amount: null
    },
    {
      id: 3,
      type: 'maturity',
      title: 'Investment Maturity',
      message: 'Commercial Paper matures in 30 days - reinvestment needed',
      priority: 'low',
      amount: 20656000
    }
  ]

  return (
    <div className="space-y-6">
      {/* Entity Selector */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Entity View</h3>
        <div className="flex flex-wrap gap-2">
          {entities.map((entity) => (
            <button
              key={entity.id}
              onClick={() => setSelectedEntity(entity.id)}
              className={`flex items-center px-4 py-2 rounded-lg border transition-colors ${
                selectedEntity === entity.id
                  ? 'bg-blue-50 border-blue-200 text-blue-700'
                  : 'bg-white border-gray-200 text-gray-700 hover:bg-gray-50'
              }`}
            >
              <span className="mr-2">{entity.flag}</span>
              {entity.name}
            </button>
          ))}
        </div>
      </div>

      <div ref={containerRef} className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Cash Allocation - slides in from left */}
        <motion.div 
          className="chart-container relative cursor-pointer"
          initial={{ opacity: 0, x: -200 }}
          animate={isInView ? { opacity: 1, x: 0 } : { opacity: 0, x: -200 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          whileHover={{ 
            scale: 1.02, 
            boxShadow: "0 0 30px rgba(59, 130, 246, 0.4), 0 0 60px rgba(59, 130, 246, 0.2)",
            transition: { duration: 0.3 }
          }}
          whileTap={{ scale: 0.98 }}
          style={{ transformOrigin: "center" }}
        >
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-medium text-gray-900">Cash Allocation</h3>
            <BanknotesIcon className="h-6 w-6 text-blue-600" />
          </div>
          
          <div className="space-y-4">
            {cashPositions.map((position, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-gray-900">
                      {position.type}
                    </span>
                    <span className="text-sm text-gray-600">
                      {position.yield}% APY
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${position.percentage}%` }}
                    ></div>
                  </div>
                  <div className="flex items-center justify-between mt-1">
                    <span className="text-xs text-gray-500">
                      {position.percentage}%
                    </span>
                    <span className="text-xs font-medium text-gray-900">
                      ${position.amount.toLocaleString()}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          <div className="mt-6 pt-4 border-t border-gray-200">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-900">Total Cash</span>
              <span className="text-lg font-semibold text-gray-900">
                $300,000,000
              </span>
            </div>
            <div className="flex items-center justify-between mt-1">
              <span className="text-xs text-gray-500">Weighted Average Yield</span>
              <span className="text-sm font-medium text-green-600">2.1%</span>
            </div>
          </div>
        </motion.div>

        {/* Investment Portfolio - slides in from right */}
        <motion.div 
          className="chart-container relative cursor-pointer"
          initial={{ opacity: 0, x: 200 }}
          animate={isInView ? { opacity: 1, x: 0 } : { opacity: 0, x: 200 }}
          transition={{ duration: 0.8, ease: "easeOut", delay: 0.2 }}
          whileHover={{ 
            scale: 1.02, 
            boxShadow: "0 0 30px rgba(59, 130, 246, 0.4), 0 0 60px rgba(59, 130, 246, 0.2)",
            transition: { duration: 0.3 }
          }}
          whileTap={{ scale: 0.98 }}
          style={{ transformOrigin: "center" }}
        >
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-medium text-gray-900">Investment Portfolio</h3>
            <ChartPieIcon className="h-6 w-6 text-blue-600" />
          </div>
          
          <div className="space-y-3">
            {investments.map((investment, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex-1">
                  <div className="text-sm font-medium text-gray-900">
                    {investment.type}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    Maturity: {investment.maturity}
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-medium text-gray-900">
                    ${investment.amount.toLocaleString()}
                  </div>
                  <div className="text-xs text-green-600">
                    {investment.yield}% yield
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          <div className="mt-6 pt-4 border-t border-gray-200">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-900">Total Investments</span>
              <span className="text-lg font-semibold text-gray-900">
                $200,656,000
              </span>
            </div>
            <div className="flex items-center justify-between mt-1">
              <span className="text-xs text-gray-500">Portfolio Yield</span>
              <span className="text-sm font-medium text-green-600">3.2%</span>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Alerts and Recommendations */}
      <div className="chart-container">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-medium text-gray-900">Alerts & Recommendations</h3>
          <ExclamationTriangleIcon className="h-6 w-6 text-amber-600" />
        </div>
        
        <div className="space-y-4">
          {alerts.map((alert) => (
            <div
              key={alert.id}
              className={`p-4 rounded-lg border-l-4 ${
                alert.priority === 'high'
                  ? 'bg-red-50 border-red-400'
                  : alert.priority === 'medium'
                  ? 'bg-yellow-50 border-yellow-400'
                  : 'bg-blue-50 border-blue-400'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h4 className="text-sm font-medium text-gray-900">
                    {alert.title}
                  </h4>
                  <p className="text-sm text-gray-600 mt-1">
                    {alert.message}
                  </p>
                  {alert.amount && (
                    <p className="text-sm font-medium text-green-600 mt-2">
                      Potential Impact: +${alert.amount.toLocaleString()}
                    </p>
                  )}
                </div>
                <div className="flex-shrink-0 ml-4">
                  <span
                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      alert.priority === 'high'
                        ? 'bg-red-100 text-red-800'
                        : alert.priority === 'medium'
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-blue-100 text-blue-800'
                    }`}
                  >
                    {alert.priority.toUpperCase()}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <button className="flex items-center justify-center p-4 bg-white rounded-lg shadow-sm border border-gray-200 hover:bg-gray-50 transition-colors">
          <ArrowTrendingUpIcon className="h-6 w-6 text-blue-600 mr-3" />
          <span className="text-sm font-medium text-gray-900">Optimize Cash</span>
        </button>
        <button className="flex items-center justify-center p-4 bg-white rounded-lg shadow-sm border border-gray-200 hover:bg-gray-50 transition-colors">
          <GlobeAltIcon className="h-6 w-6 text-blue-600 mr-3" />
          <span className="text-sm font-medium text-gray-900">Review FX Risk</span>
        </button>
        <button className="flex items-center justify-center p-4 bg-white rounded-lg shadow-sm border border-gray-200 hover:bg-gray-50 transition-colors">
          <ChartPieIcon className="h-6 w-6 text-blue-600 mr-3" />
          <span className="text-sm font-medium text-gray-900">Rebalance Portfolio</span>
        </button>
      </div>
    </div>
  )
}