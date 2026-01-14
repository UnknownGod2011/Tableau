'use client'

import { useState } from 'react'
import {
  Line,
  AreaChart,
  Area,
  Bar,
  ComposedChart,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  ScatterChart,
  Scatter
} from 'recharts'
import { motion } from 'framer-motion'

interface AdvancedChartsProps {
  data?: any
  type: 'cashFlow' | 'riskMetrics' | 'performance' | 'allocation' | 'correlation'
  title: string
  height?: number
}

export default function AdvancedCharts({ 
  data, 
  type, 
  title, 
  height = 400 
}: AdvancedChartsProps) {
  const [selectedMetric, setSelectedMetric] = useState('all')
  const [timeRange, setTimeRange] = useState('1Y')

  // Mock data generators for different chart types
  const generateCashFlowData = () => {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    return months.map((month, index) => ({
      month,
      inflow: 15000000 + Math.random() * 10000000,
      outflow: 12000000 + Math.random() * 8000000,
      netFlow: 3000000 + Math.random() * 5000000,
      forecast: 3500000 + Math.random() * 4000000,
      confidence: 0.75 + Math.random() * 0.2
    }))
  }

  const generateRiskMetricsData = () => {
    const dates = Array.from({ length: 30 }, (_, i) => {
      const date = new Date()
      date.setDate(date.getDate() - (29 - i))
      return date.toISOString().split('T')[0]
    })
    
    return dates.map(date => ({
      date,
      var95: 2000000 + Math.random() * 1000000,
      var99: 3000000 + Math.random() * 1500000,
      expectedShortfall: 2500000 + Math.random() * 1200000,
      creditRisk: 800000 + Math.random() * 400000,
      marketRisk: 1200000 + Math.random() * 600000,
      fxRisk: 400000 + Math.random() * 300000,
      volatility: 0.15 + Math.random() * 0.1
    }))
  }

  const generatePerformanceData = () => {
    const periods = ['Q1 2023', 'Q2 2023', 'Q3 2023', 'Q4 2023', 'Q1 2024']
    return periods.map(period => ({
      period,
      portfolio: 3.2 + Math.random() * 2,
      benchmark: 2.8 + Math.random() * 1.5,
      excess: 0.4 + Math.random() * 1,
      sharpeRatio: 1.2 + Math.random() * 0.8,
      maxDrawdown: -2.1 + Math.random() * 1.5,
      volatility: 8.5 + Math.random() * 3
    }))
  }

  const generateAllocationData = () => [
    { name: 'Cash & Equivalents', value: 300000000, percentage: 60, color: '#3B82F6' },
    { name: 'Government Bonds', value: 100000000, percentage: 20, color: '#10B981' },
    { name: 'Corporate Bonds', value: 75000000, percentage: 15, color: '#F59E0B' },
    { name: 'Money Market Funds', value: 25000000, percentage: 5, color: '#EF4444' }
  ]

  const generateCorrelationData = () => {
    const assets = ['USD Cash', 'EUR Cash', 'Treasury 2Y', 'Corp Bonds', 'Money Market']
    const data = []
    
    for (let i = 0; i < assets.length; i++) {
      for (let j = 0; j < assets.length; j++) {
        data.push({
          x: i,
          y: j,
          asset1: assets[i],
          asset2: assets[j],
          correlation: i === j ? 1 : Math.random() * 2 - 1,
          value: i === j ? 100 : Math.abs(Math.random() * 2 - 1) * 100
        })
      }
    }
    
    return data
  }

  const renderChart = () => {
    switch (type) {
      case 'cashFlow':
        const cashFlowData = generateCashFlowData()
        return (
          <ResponsiveContainer width="100%" height={height}>
            <ComposedChart data={cashFlowData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis 
                dataKey="month" 
                stroke="#6B7280"
                fontSize={12}
              />
              <YAxis 
                stroke="#6B7280"
                fontSize={12}
                tickFormatter={(value) => `$${(value / 1000000).toFixed(0)}M`}
              />
              <Tooltip 
                formatter={(value: any, name: string) => [
                  `$${(value / 1000000).toFixed(1)}M`, 
                  name.charAt(0).toUpperCase() + name.slice(1)
                ]}
                labelStyle={{ color: '#374151' }}
                contentStyle={{ 
                  backgroundColor: '#FFFFFF', 
                  border: '1px solid #E5E7EB',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                }}
              />
              <Legend />
              <Bar dataKey="inflow" fill="#10B981" name="Cash Inflow" radius={[2, 2, 0, 0]} />
              <Bar dataKey="outflow" fill="#EF4444" name="Cash Outflow" radius={[2, 2, 0, 0]} />
              <Line 
                type="monotone" 
                dataKey="netFlow" 
                stroke="#3B82F6" 
                strokeWidth={3}
                name="Net Flow"
                dot={{ fill: '#3B82F6', strokeWidth: 2, r: 4 }}
              />
              <Line 
                type="monotone" 
                dataKey="forecast" 
                stroke="#F59E0B" 
                strokeWidth={2}
                strokeDasharray="5 5"
                name="Forecast"
                dot={{ fill: '#F59E0B', strokeWidth: 2, r: 3 }}
              />
            </ComposedChart>
          </ResponsiveContainer>
        )

      case 'riskMetrics':
        const riskData = generateRiskMetricsData()
        return (
          <ResponsiveContainer width="100%" height={height}>
            <AreaChart data={riskData}>
              <defs>
                <linearGradient id="var95Gradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="var99Gradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#EF4444" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#EF4444" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis 
                dataKey="date" 
                stroke="#6B7280"
                fontSize={12}
                tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
              />
              <YAxis 
                stroke="#6B7280"
                fontSize={12}
                tickFormatter={(value) => `$${(value / 1000000).toFixed(1)}M`}
              />
              <Tooltip 
                formatter={(value: any, name: string) => [
                  `$${(value / 1000000).toFixed(2)}M`, 
                  name
                ]}
                labelFormatter={(value) => new Date(value).toLocaleDateString()}
                contentStyle={{ 
                  backgroundColor: '#FFFFFF', 
                  border: '1px solid #E5E7EB',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                }}
              />
              <Legend />
              <Area
                type="monotone"
                dataKey="var95"
                stroke="#3B82F6"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#var95Gradient)"
                name="VaR 95%"
              />
              <Area
                type="monotone"
                dataKey="var99"
                stroke="#EF4444"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#var99Gradient)"
                name="VaR 99%"
              />
              <Line 
                type="monotone" 
                dataKey="expectedShortfall" 
                stroke="#F59E0B" 
                strokeWidth={2}
                name="Expected Shortfall"
              />
            </AreaChart>
          </ResponsiveContainer>
        )

      case 'performance':
        const performanceData = generatePerformanceData()
        return (
          <ResponsiveContainer width="100%" height={height}>
            <ComposedChart data={performanceData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis dataKey="period" stroke="#6B7280" fontSize={12} />
              <YAxis 
                yAxisId="left"
                stroke="#6B7280"
                fontSize={12}
                tickFormatter={(value) => `${value.toFixed(1)}%`}
              />
              <YAxis 
                yAxisId="right"
                orientation="right"
                stroke="#6B7280"
                fontSize={12}
                tickFormatter={(value) => value.toFixed(1)}
              />
              <Tooltip 
                formatter={(value: any, name: string) => [
                  name.includes('Ratio') ? value.toFixed(2) : `${value.toFixed(1)}%`, 
                  name
                ]}
                contentStyle={{ 
                  backgroundColor: '#FFFFFF', 
                  border: '1px solid #E5E7EB',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                }}
              />
              <Legend />
              <Bar yAxisId="left" dataKey="portfolio" fill="#3B82F6" name="Portfolio Return" radius={[2, 2, 0, 0]} />
              <Bar yAxisId="left" dataKey="benchmark" fill="#10B981" name="Benchmark Return" radius={[2, 2, 0, 0]} />
              <Line 
                yAxisId="right"
                type="monotone" 
                dataKey="sharpeRatio" 
                stroke="#F59E0B" 
                strokeWidth={3}
                name="Sharpe Ratio"
                dot={{ fill: '#F59E0B', strokeWidth: 2, r: 4 }}
              />
            </ComposedChart>
          </ResponsiveContainer>
        )

      case 'allocation':
        const allocationData = generateAllocationData()
        return (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-full">
            <ResponsiveContainer width="100%" height={height * 0.8}>
              <PieChart>
                <Pie
                  data={allocationData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={120}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {allocationData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  formatter={(value: any) => [`$${(value / 1000000).toFixed(0)}M`, 'Value']}
                  contentStyle={{ 
                    backgroundColor: '#FFFFFF', 
                    border: '1px solid #E5E7EB',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
            <div className="space-y-4">
              {allocationData.map((item, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                >
                  <div className="flex items-center">
                    <div 
                      className="w-4 h-4 rounded-full mr-3" 
                      style={{ backgroundColor: item.color }}
                    />
                    <div>
                      <div className="font-medium text-gray-900">{item.name}</div>
                      <div className="text-sm text-gray-500">{item.percentage}% of portfolio</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-semibold text-gray-900">
                      ${(item.value / 1000000).toFixed(0)}M
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        )

      case 'correlation':
        const correlationData = generateCorrelationData()
        return (
          <ResponsiveContainer width="100%" height={height}>
            <ScatterChart data={correlationData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis 
                type="number" 
                dataKey="x" 
                domain={[-0.5, 4.5]}
                tickFormatter={(value) => ['USD Cash', 'EUR Cash', 'Treasury 2Y', 'Corp Bonds', 'Money Market'][value] || ''}
                stroke="#6B7280"
                fontSize={12}
              />
              <YAxis 
                type="number" 
                dataKey="y" 
                domain={[-0.5, 4.5]}
                tickFormatter={(value) => ['USD Cash', 'EUR Cash', 'Treasury 2Y', 'Corp Bonds', 'Money Market'][value] || ''}
                stroke="#6B7280"
                fontSize={12}
              />
              <Tooltip 
                formatter={(value: any, name: string, props: any) => [
                  props.payload.correlation.toFixed(3), 
                  `${props.payload.asset1} vs ${props.payload.asset2}`
                ]}
                contentStyle={{ 
                  backgroundColor: '#FFFFFF', 
                  border: '1px solid #E5E7EB',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                }}
              />
              <Scatter 
                dataKey="value" 
                fill="#3B82F6"
              />
            </ScatterChart>
          </ResponsiveContainer>
        )

      default:
        return <div>Chart type not supported</div>
    }
  }

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="chart-container"
    >
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        <div className="flex items-center space-x-3">
          {type === 'riskMetrics' && (
            <select
              value={selectedMetric}
              onChange={(e) => setSelectedMetric(e.target.value)}
              className="form-select text-sm"
            >
              <option value="all">All Metrics</option>
              <option value="var">VaR Only</option>
              <option value="credit">Credit Risk</option>
              <option value="market">Market Risk</option>
            </select>
          )}
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="form-select text-sm"
          >
            <option value="1M">1 Month</option>
            <option value="3M">3 Months</option>
            <option value="6M">6 Months</option>
            <option value="1Y">1 Year</option>
            <option value="2Y">2 Years</option>
          </select>
        </div>
      </div>
      
      <div className="relative">
        {renderChart()}
      </div>
      
      {/* Chart insights */}
      <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h4 className="text-sm font-medium text-blue-800">Key Insights</h4>
            <div className="mt-1 text-sm text-blue-700">
              {type === 'cashFlow' && "Cash flows show strong seasonal patterns with Q4 typically showing highest inflows."}
              {type === 'riskMetrics' && "Risk metrics are within acceptable ranges, with VaR trending downward over the past month."}
              {type === 'performance' && "Portfolio consistently outperforming benchmark with strong risk-adjusted returns."}
              {type === 'allocation' && "Current allocation aligns with strategic targets, with slight overweight in cash positions."}
              {type === 'correlation' && "Asset correlations remain stable, providing good diversification benefits."}
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  )
}