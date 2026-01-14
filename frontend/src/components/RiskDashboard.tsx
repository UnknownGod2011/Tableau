'use client'

import { useState, useRef, useMemo } from 'react'
import { motion, useInView, AnimatePresence } from 'framer-motion'
import { 
  ShieldCheckIcon,
  ExclamationTriangleIcon,
  ChartBarIcon,
  GlobeAltIcon
} from '@heroicons/react/24/outline'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

interface RiskDashboardProps {
  data: any
}

// Data sets for different timeframes
const varDataByTimeframe: Record<string, any[]> = {
  '1D': [
    { date: '2024-01-07 09:00', var1d: 2.1, var10d: 6.8, expectedShortfall: 2.8 },
    { date: '2024-01-07 12:00', var1d: 2.2, var10d: 6.9, expectedShortfall: 2.9 },
    { date: '2024-01-07 15:00', var1d: 2.3, var10d: 7.0, expectedShortfall: 3.0 },
    { date: '2024-01-07 18:00', var1d: 2.1, var10d: 6.7, expectedShortfall: 2.8 },
  ],
  '1W': [
    { date: '2024-01-01', var1d: 2.0, var10d: 6.5, expectedShortfall: 2.7 },
    { date: '2024-01-02', var1d: 2.2, var10d: 6.8, expectedShortfall: 2.9 },
    { date: '2024-01-03', var1d: 2.1, var10d: 6.6, expectedShortfall: 2.8 },
    { date: '2024-01-04', var1d: 2.3, var10d: 7.0, expectedShortfall: 3.0 },
    { date: '2024-01-05', var1d: 2.4, var10d: 7.2, expectedShortfall: 3.1 },
    { date: '2024-01-06', var1d: 2.2, var10d: 6.9, expectedShortfall: 2.9 },
    { date: '2024-01-07', var1d: 2.1, var10d: 6.8, expectedShortfall: 2.8 },
  ],
  '1M': [
    { date: '2024-01-01', var1d: 2.1, var10d: 6.8, expectedShortfall: 2.8 },
    { date: '2024-01-08', var1d: 2.3, var10d: 7.1, expectedShortfall: 3.0 },
    { date: '2024-01-15', var1d: 2.0, var10d: 6.5, expectedShortfall: 2.7 },
    { date: '2024-01-22', var1d: 2.4, var10d: 7.5, expectedShortfall: 3.2 },
    { date: '2024-01-29', var1d: 2.2, var10d: 7.0, expectedShortfall: 2.9 },
  ],
  '3M': [
    { date: '2023-11-01', var1d: 1.8, var10d: 5.8, expectedShortfall: 2.4 },
    { date: '2023-11-15', var1d: 1.9, var10d: 6.1, expectedShortfall: 2.5 },
    { date: '2023-12-01', var1d: 2.0, var10d: 6.4, expectedShortfall: 2.6 },
    { date: '2023-12-15', var1d: 2.2, var10d: 6.9, expectedShortfall: 2.9 },
    { date: '2024-01-01', var1d: 2.1, var10d: 6.8, expectedShortfall: 2.8 },
    { date: '2024-01-15', var1d: 2.3, var10d: 7.2, expectedShortfall: 3.0 },
  ],
  '1Y': [
    { date: '2023-02-01', var1d: 1.5, var10d: 4.8, expectedShortfall: 2.0 },
    { date: '2023-04-01', var1d: 1.7, var10d: 5.4, expectedShortfall: 2.2 },
    { date: '2023-06-01', var1d: 1.9, var10d: 6.0, expectedShortfall: 2.5 },
    { date: '2023-08-01', var1d: 2.1, var10d: 6.6, expectedShortfall: 2.7 },
    { date: '2023-10-01', var1d: 2.0, var10d: 6.4, expectedShortfall: 2.6 },
    { date: '2023-12-01', var1d: 2.2, var10d: 6.9, expectedShortfall: 2.9 },
    { date: '2024-01-01', var1d: 2.1, var10d: 6.8, expectedShortfall: 2.8 },
  ],
}

// Risk breakdown by type
const riskBreakdownByType: Record<string, any[]> = {
  all: [
    { name: 'Credit Risk', value: 45, color: '#3B82F6' },
    { name: 'Market Risk', value: 30, color: '#EF4444' },
    { name: 'FX Risk', value: 15, color: '#F59E0B' },
    { name: 'Liquidity Risk', value: 10, color: '#10B981' },
  ],
  market: [
    { name: 'Equity Risk', value: 40, color: '#3B82F6' },
    { name: 'Interest Rate Risk', value: 35, color: '#EF4444' },
    { name: 'Commodity Risk', value: 15, color: '#F59E0B' },
    { name: 'Volatility Risk', value: 10, color: '#10B981' },
  ],
  credit: [
    { name: 'Counterparty Risk', value: 50, color: '#3B82F6' },
    { name: 'Default Risk', value: 25, color: '#EF4444' },
    { name: 'Spread Risk', value: 15, color: '#F59E0B' },
    { name: 'Migration Risk', value: 10, color: '#10B981' },
  ],
  fx: [
    { name: 'EUR Exposure', value: 38, color: '#3B82F6' },
    { name: 'JPY Exposure', value: 25, color: '#EF4444' },
    { name: 'CAD Exposure', value: 22, color: '#F59E0B' },
    { name: 'SGD Exposure', value: 15, color: '#10B981' },
  ],
  liquidity: [
    { name: 'Funding Risk', value: 45, color: '#3B82F6' },
    { name: 'Market Liquidity', value: 30, color: '#EF4444' },
    { name: 'Asset Liquidity', value: 15, color: '#F59E0B' },
    { name: 'Concentration Risk', value: 10, color: '#10B981' },
  ],
}

// VaR summary by timeframe
const varSummaryByTimeframe: Record<string, { var1d: string; var10d: string; es: string }> = {
  '1D': { var1d: '$2.15M', var10d: '$6.85M', es: '$2.85M' },
  '1W': { var1d: '$2.19M', var10d: '$6.97M', es: '$2.89M' },
  '1M': { var1d: '$2.20M', var10d: '$6.98M', es: '$2.92M' },
  '3M': { var1d: '$2.05M', var10d: '$6.50M', es: '$2.70M' },
  '1Y': { var1d: '$1.93M', var10d: '$6.13M', es: '$2.53M' },
}

// FX exposures by risk type filter
const fxExposuresByType: Record<string, any[]> = {
  all: [
    { currency: 'EUR', exposure: 45000000, hedged: 75, unhedged: 25, var: 280000 },
    { currency: 'JPY', exposure: 15000000, hedged: 50, unhedged: 50, var: 120000 },
    { currency: 'CAD', exposure: 25000000, hedged: 60, unhedged: 40, var: 95000 },
    { currency: 'SGD', exposure: 35000000, hedged: 40, unhedged: 60, var: 180000 },
  ],
  fx: [
    { currency: 'EUR', exposure: 45000000, hedged: 75, unhedged: 25, var: 280000 },
    { currency: 'JPY', exposure: 15000000, hedged: 50, unhedged: 50, var: 120000 },
    { currency: 'CAD', exposure: 25000000, hedged: 60, unhedged: 40, var: 95000 },
    { currency: 'SGD', exposure: 35000000, hedged: 40, unhedged: 60, var: 180000 },
    { currency: 'GBP', exposure: 18000000, hedged: 65, unhedged: 35, var: 85000 },
    { currency: 'CHF', exposure: 12000000, hedged: 80, unhedged: 20, var: 45000 },
  ],
  market: [
    { currency: 'EUR', exposure: 45000000, hedged: 75, unhedged: 25, var: 350000 },
    { currency: 'JPY', exposure: 15000000, hedged: 50, unhedged: 50, var: 180000 },
  ],
  credit: [
    { currency: 'EUR', exposure: 30000000, hedged: 80, unhedged: 20, var: 150000 },
    { currency: 'CAD', exposure: 20000000, hedged: 70, unhedged: 30, var: 80000 },
  ],
  liquidity: [
    { currency: 'EUR', exposure: 25000000, hedged: 60, unhedged: 40, var: 200000 },
    { currency: 'SGD', exposure: 20000000, hedged: 45, unhedged: 55, var: 160000 },
  ],
}

// Stress scenarios by risk type
const stressScenariosByType: Record<string, any[]> = {
  all: [
    { name: 'Interest Rate Shock (+200bp)', impact: -8500000, probability: 0.05, description: 'Parallel shift in yield curve' },
    { name: 'Credit Spread Widening (+100bp)', impact: -3200000, probability: 0.10, description: 'Corporate bond spread expansion' },
    { name: 'FX Volatility Spike (2x)', impact: -1800000, probability: 0.15, description: 'Major currency pair volatility' },
    { name: 'Liquidity Crisis', impact: -12000000, probability: 0.02, description: 'Market liquidity dries up' },
  ],
  market: [
    { name: 'Equity Market Crash (-30%)', impact: -15000000, probability: 0.03, description: 'Major equity market correction' },
    { name: 'Interest Rate Shock (+200bp)', impact: -8500000, probability: 0.05, description: 'Parallel shift in yield curve' },
    { name: 'Commodity Price Spike (+50%)', impact: -2500000, probability: 0.08, description: 'Energy and commodity surge' },
    { name: 'Volatility Regime Change', impact: -4200000, probability: 0.12, description: 'VIX spikes above 40' },
  ],
  credit: [
    { name: 'Credit Spread Widening (+100bp)', impact: -3200000, probability: 0.10, description: 'Corporate bond spread expansion' },
    { name: 'Major Counterparty Default', impact: -18000000, probability: 0.01, description: 'Top 5 counterparty fails' },
    { name: 'Rating Downgrade Wave', impact: -5500000, probability: 0.07, description: 'Multiple issuer downgrades' },
    { name: 'Sovereign Debt Crisis', impact: -9800000, probability: 0.04, description: 'EM sovereign defaults' },
  ],
  fx: [
    { name: 'FX Volatility Spike (2x)', impact: -1800000, probability: 0.15, description: 'Major currency pair volatility' },
    { name: 'EUR/USD Parity', impact: -3500000, probability: 0.08, description: 'Euro drops to dollar parity' },
    { name: 'JPY Intervention', impact: -2200000, probability: 0.12, description: 'BOJ currency intervention' },
    { name: 'EM Currency Crisis', impact: -4100000, probability: 0.06, description: 'Emerging market FX collapse' },
  ],
  liquidity: [
    { name: 'Liquidity Crisis', impact: -12000000, probability: 0.02, description: 'Market liquidity dries up' },
    { name: 'Funding Stress', impact: -6500000, probability: 0.05, description: 'Short-term funding unavailable' },
    { name: 'Asset Fire Sale', impact: -8200000, probability: 0.03, description: 'Forced liquidation scenario' },
    { name: 'Repo Market Freeze', impact: -4800000, probability: 0.04, description: 'Repo market dysfunction' },
  ],
}

// Risk alerts by type
const riskAlertsByType: Record<string, any[]> = {
  all: [
    { id: 1, type: 'high', title: 'VaR Limit Breach Warning', message: 'Portfolio VaR approaching 80% of limit ($3M threshold)', timestamp: '2024-01-07T10:30:00Z', entity: 'EU-LTD' },
    { id: 2, type: 'medium', title: 'FX Exposure Increase', message: 'EUR exposure increased 12% this week, consider additional hedging', timestamp: '2024-01-07T09:15:00Z', entity: 'All' },
    { id: 3, type: 'low', title: 'Credit Rating Change', message: 'Corporate bond issuer downgraded from AA- to A+', timestamp: '2024-01-07T08:45:00Z', entity: 'US-HQ' },
  ],
  market: [
    { id: 1, type: 'high', title: 'Volatility Spike Detected', message: 'VIX increased 25% in last 24 hours, review equity positions', timestamp: '2024-01-07T11:00:00Z', entity: 'All' },
    { id: 2, type: 'medium', title: 'Interest Rate Sensitivity', message: 'Duration exposure exceeds target by 0.5 years', timestamp: '2024-01-07T09:30:00Z', entity: 'US-HQ' },
  ],
  credit: [
    { id: 1, type: 'high', title: 'Counterparty Exposure Alert', message: 'Single counterparty exposure exceeds 10% limit', timestamp: '2024-01-07T10:45:00Z', entity: 'EU-LTD' },
    { id: 2, type: 'low', title: 'Credit Rating Change', message: 'Corporate bond issuer downgraded from AA- to A+', timestamp: '2024-01-07T08:45:00Z', entity: 'US-HQ' },
  ],
  fx: [
    { id: 1, type: 'high', title: 'Unhedged FX Exposure', message: 'SGD exposure 60% unhedged, exceeds 50% policy limit', timestamp: '2024-01-07T10:15:00Z', entity: 'APAC' },
    { id: 2, type: 'medium', title: 'FX Exposure Increase', message: 'EUR exposure increased 12% this week, consider additional hedging', timestamp: '2024-01-07T09:15:00Z', entity: 'All' },
  ],
  liquidity: [
    { id: 1, type: 'medium', title: 'Liquidity Buffer Low', message: 'Available liquidity at 85% of minimum requirement', timestamp: '2024-01-07T09:00:00Z', entity: 'JP-KK' },
    { id: 2, type: 'low', title: 'Maturity Concentration', message: '35% of investments mature within 30 days', timestamp: '2024-01-07T08:30:00Z', entity: 'All' },
  ],
}

export default function RiskDashboard({ data }: RiskDashboardProps) {
  const [selectedTimeframe, setSelectedTimeframe] = useState('1M')
  const [selectedRiskType, setSelectedRiskType] = useState('all')
  const containerRef = useRef<HTMLDivElement>(null)
  const isInView = useInView(containerRef, { once: true, margin: "-50px" })

  // Get filtered data based on selections
  const varData = useMemo(() => varDataByTimeframe[selectedTimeframe] || varDataByTimeframe['1M'], [selectedTimeframe])
  const riskBreakdown = useMemo(() => riskBreakdownByType[selectedRiskType] || riskBreakdownByType['all'], [selectedRiskType])
  const fxExposures = useMemo(() => fxExposuresByType[selectedRiskType] || fxExposuresByType['all'], [selectedRiskType])
  const stressScenarios = useMemo(() => stressScenariosByType[selectedRiskType] || stressScenariosByType['all'], [selectedRiskType])
  const riskAlerts = useMemo(() => riskAlertsByType[selectedRiskType] || riskAlertsByType['all'], [selectedRiskType])
  const varSummary = useMemo(() => varSummaryByTimeframe[selectedTimeframe] || varSummaryByTimeframe['1M'], [selectedTimeframe])

  return (
    <div ref={containerRef} className="space-y-6">
      {/* Risk Controls */}
      <motion.div 
        className="bg-white rounded-lg shadow-sm border border-gray-200 p-4"
        initial={{ opacity: 0, y: 20 }}
        animate={isInView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.5 }}
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Risk Analysis Controls</h3>
          <div className="flex items-center space-x-4">
            <select
              value={selectedTimeframe}
              onChange={(e) => setSelectedTimeframe(e.target.value)}
              className="text-sm border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="1D">1 Day</option>
              <option value="1W">1 Week</option>
              <option value="1M">1 Month</option>
              <option value="3M">3 Months</option>
              <option value="1Y">1 Year</option>
            </select>
            <select
              value={selectedRiskType}
              onChange={(e) => setSelectedRiskType(e.target.value)}
              className="text-sm border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="all">All Risk Types</option>
              <option value="market">Market Risk</option>
              <option value="credit">Credit Risk</option>
              <option value="fx">FX Risk</option>
              <option value="liquidity">Liquidity Risk</option>
            </select>
          </div>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* VaR Trend Chart */}
        <motion.div 
          className="chart-container"
          initial={{ opacity: 0, x: -50 }}
          animate={isInView ? { opacity: 1, x: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-medium text-gray-900">Value at Risk Trends</h3>
            <ShieldCheckIcon className="h-6 w-6 text-blue-600" />
          </div>
          
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={varData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" tickFormatter={(value) => new Date(value).toLocaleDateString()} />
              <YAxis tickFormatter={(value) => `$${value}M`} />
              <Tooltip 
                formatter={(value: any, name: string) => [`$${value}M`, name]}
                labelFormatter={(value) => new Date(value).toLocaleDateString()}
              />
              <Line type="monotone" dataKey="var1d" stroke="#3B82F6" strokeWidth={2} name="1-Day VaR" />
              <Line type="monotone" dataKey="var10d" stroke="#EF4444" strokeWidth={2} name="10-Day VaR" />
              <Line type="monotone" dataKey="expectedShortfall" stroke="#F59E0B" strokeWidth={2} name="Expected Shortfall" />
            </LineChart>
          </ResponsiveContainer>
          
          <div className="mt-4 grid grid-cols-3 gap-4 text-center">
            <motion.div
              key={`var1d-${selectedTimeframe}`}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              <div className="text-2xl font-semibold text-blue-600">{varSummary.var1d}</div>
              <div className="text-sm text-gray-500">1-Day VaR (95%)</div>
            </motion.div>
            <motion.div
              key={`var10d-${selectedTimeframe}`}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: 0.1 }}
            >
              <div className="text-2xl font-semibold text-red-600">{varSummary.var10d}</div>
              <div className="text-sm text-gray-500">10-Day VaR (95%)</div>
            </motion.div>
            <motion.div
              key={`es-${selectedTimeframe}`}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: 0.2 }}
            >
              <div className="text-2xl font-semibold text-yellow-600">{varSummary.es}</div>
              <div className="text-sm text-gray-500">Expected Shortfall</div>
            </motion.div>
          </div>
        </motion.div>

        {/* Risk Breakdown */}
        <motion.div 
          className="chart-container"
          initial={{ opacity: 0, x: 50 }}
          animate={isInView ? { opacity: 1, x: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900">Risk Breakdown</h3>
              <motion.p 
                key={selectedRiskType}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-sm text-gray-500"
              >
                {selectedRiskType === 'all' ? 'All Risk Types' : 
                 selectedRiskType === 'market' ? 'Market Risk Components' :
                 selectedRiskType === 'credit' ? 'Credit Risk Components' :
                 selectedRiskType === 'fx' ? 'FX Risk by Currency' :
                 'Liquidity Risk Components'}
              </motion.p>
            </div>
            <ChartBarIcon className="h-6 w-6 text-blue-600" />
          </div>
          
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={riskBreakdown}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={120}
                paddingAngle={5}
                dataKey="value"
              >
                {riskBreakdown.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip formatter={(value: any) => [`${value}%`, 'Risk Contribution']} />
            </PieChart>
          </ResponsiveContainer>
          
          <div className="mt-4 space-y-2">
            <AnimatePresence mode="wait">
              {riskBreakdown.map((item, index) => (
                <motion.div 
                  key={`${selectedRiskType}-${item.name}`} 
                  className="flex items-center justify-between"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ duration: 0.3, delay: index * 0.05 }}
                >
                  <div className="flex items-center">
                    <div 
                      className="w-3 h-3 rounded-full mr-2" 
                      style={{ backgroundColor: item.color }}
                    ></div>
                    <span className="text-sm text-gray-700">{item.name}</span>
                  </div>
                  <span className="text-sm font-medium text-gray-900">{item.value}%</span>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </motion.div>
      </div>

      {/* FX Exposure Analysis */}
      <motion.div 
        className="chart-container"
        initial={{ opacity: 0, y: 30 }}
        animate={isInView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.6, delay: 0.3 }}
      >
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-lg font-medium text-gray-900">Foreign Exchange Risk</h3>
            <motion.p 
              key={`fx-${selectedRiskType}`}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-sm text-gray-500"
            >
              {fxExposures.length} currency exposures • {selectedRiskType === 'all' ? 'All types' : `${selectedRiskType} focus`}
            </motion.p>
          </div>
          <GlobeAltIcon className="h-6 w-6 text-blue-600" />
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Currency
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Exposure
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Hedged
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Unhedged
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  VaR Impact
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Action
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {fxExposures.map((fx, index) => (
                <tr key={index}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="text-sm font-medium text-gray-900">{fx.currency}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">${fx.exposure.toLocaleString()}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                        <div 
                          className="bg-green-600 h-2 rounded-full" 
                          style={{ width: `${fx.hedged}%` }}
                        ></div>
                      </div>
                      <span className="text-sm text-gray-900">{fx.hedged}%</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      fx.unhedged > 50 ? 'bg-red-100 text-red-800' : 
                      fx.unhedged > 30 ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'
                    }`}>
                      {fx.unhedged}%
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${fx.var.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button className="text-blue-600 hover:text-blue-900">
                      {fx.unhedged > 50 ? 'Add Hedge' : 'Optimize'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>

      {/* Stress Testing */}
      <motion.div 
        className="chart-container"
        initial={{ opacity: 0, y: 30 }}
        animate={isInView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.6, delay: 0.4 }}
      >
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-lg font-medium text-gray-900">Stress Test Scenarios</h3>
            <motion.p 
              key={`stress-${selectedRiskType}`}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-sm text-gray-500"
            >
              {selectedRiskType === 'all' ? 'Combined scenarios' : `${selectedRiskType.charAt(0).toUpperCase() + selectedRiskType.slice(1)} risk scenarios`}
            </motion.p>
          </div>
          <ExclamationTriangleIcon className="h-6 w-6 text-amber-600" />
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <AnimatePresence mode="wait">
            {stressScenarios.map((scenario, index) => (
              <motion.div 
                key={`${selectedRiskType}-${scenario.name}`} 
                className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ duration: 0.3, delay: index * 0.05 }}
              >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h4 className="text-sm font-medium text-gray-900">{scenario.name}</h4>
                  <p className="text-xs text-gray-600 mt-1">{scenario.description}</p>
                  <div className="mt-3 flex items-center justify-between">
                    <div>
                      <span className="text-lg font-semibold text-red-600">
                        ${Math.abs(scenario.impact).toLocaleString()}
                      </span>
                      <span className="text-sm text-gray-500 ml-1">loss</span>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-gray-900">
                        {(scenario.probability * 100).toFixed(1)}%
                      </div>
                      <div className="text-xs text-gray-500">probability</div>
                    </div>
                  </div>
                </div>
              </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </motion.div>

      {/* Risk Alerts */}
      <motion.div 
        className="chart-container"
        initial={{ opacity: 0, y: 30 }}
        animate={isInView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.6, delay: 0.5 }}
      >
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-lg font-medium text-gray-900">Risk Alerts</h3>
            <motion.p 
              key={`alerts-${selectedRiskType}`}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-sm text-gray-500"
            >
              {selectedRiskType === 'all' ? 'All alert types' : `${selectedRiskType.charAt(0).toUpperCase() + selectedRiskType.slice(1)} related alerts`}
            </motion.p>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
            <span className="text-sm text-red-600 font-medium">
              {riskAlerts.filter(alert => alert.type === 'high').length} Critical
            </span>
          </div>
        </div>
        
        <div className="space-y-3">
          <AnimatePresence mode="wait">
            {riskAlerts.map((alert, index) => (
              <motion.div
                key={`${selectedRiskType}-${alert.id}`}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ duration: 0.3, delay: index * 0.05 }}
                className={`p-4 rounded-lg border-l-4 ${
                  alert.type === 'high'
                    ? 'bg-red-50 border-red-400'
                    : alert.type === 'medium'
                    ? 'bg-yellow-50 border-yellow-400'
                    : 'bg-blue-50 border-blue-400'
                }`}
              >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center">
                    <h4 className="text-sm font-medium text-gray-900">
                      {alert.title}
                    </h4>
                    <span className="ml-2 text-xs text-gray-500">
                      {alert.entity}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">
                    {alert.message}
                  </p>
                  <p className="text-xs text-gray-500 mt-2">
                    {new Date(alert.timestamp).toLocaleString()}
                  </p>
                </div>
                <div className="flex-shrink-0 ml-4">
                  <span
                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      alert.type === 'high'
                        ? 'bg-red-100 text-red-800'
                        : alert.type === 'medium'
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-blue-100 text-blue-800'
                    }`}
                  >
                    {alert.type.toUpperCase()}
                  </span>
                </div>
              </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </motion.div>
    </div>
  )
}