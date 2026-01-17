'use client'

import { useState } from 'react'
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

export default function RiskDashboard({ data }: RiskDashboardProps) {
  const [selectedTimeframe, setSelectedTimeframe] = useState('1M')
  const [selectedRiskType, setSelectedRiskType] = useState('all')

  // Mock risk data for demonstration
  const varData = [
    { date: '2024-01-01', var1d: 2.1, var10d: 6.8, expectedShortfall: 2.8 },
    { date: '2024-01-02', var1d: 2.3, var10d: 7.1, expectedShortfall: 3.0 },
    { date: '2024-01-03', var1d: 2.0, var10d: 6.5, expectedShortfall: 2.7 },
    { date: '2024-01-04', var1d: 2.4, var10d: 7.5, expectedShortfall: 3.2 },
    { date: '2024-01-05', var1d: 2.2, var10d: 7.0, expectedShortfall: 2.9 },
    { date: '2024-01-06', var1d: 2.5, var10d: 7.8, expectedShortfall: 3.3 },
    { date: '2024-01-07', var1d: 2.1, var10d: 6.9, expectedShortfall: 2.8 }
  ]

  const riskBreakdown = [
    { name: 'Credit Risk', value: 45, color: '#3B82F6' },
    { name: 'Market Risk', value: 30, color: '#EF4444' },
    { name: 'FX Risk', value: 15, color: '#F59E0B' },
    { name: 'Liquidity Risk', value: 10, color: '#10B981' }
  ]

  const fxExposures = [
    { currency: 'EUR', exposure: 45000000, hedged: 75, unhedged: 25, var: 280000 },
    { currency: 'JPY', exposure: 15000000, hedged: 50, unhedged: 50, var: 120000 },
    { currency: 'CAD', exposure: 25000000, hedged: 60, unhedged: 40, var: 95000 },
    { currency: 'SGD', exposure: 35000000, hedged: 40, unhedged: 60, var: 180000 }
  ]

  const stressScenarios = [
    {
      name: 'Interest Rate Shock (+200bp)',
      impact: -8500000,
      probability: 0.05,
      description: 'Parallel shift in yield curve'
    },
    {
      name: 'Credit Spread Widening (+100bp)',
      impact: -3200000,
      probability: 0.10,
      description: 'Corporate bond spread expansion'
    },
    {
      name: 'FX Volatility Spike (2x)',
      impact: -1800000,
      probability: 0.15,
      description: 'Major currency pair volatility'
    },
    {
      name: 'Liquidity Crisis',
      impact: -12000000,
      probability: 0.02,
      description: 'Market liquidity dries up'
    }
  ]

  const riskAlerts = [
    {
      id: 1,
      type: 'high',
      title: 'VaR Limit Breach Warning',
      message: 'Portfolio VaR approaching 80% of limit ($3M threshold)',
      timestamp: '2024-01-07T10:30:00Z',
      entity: 'EU-LTD'
    },
    {
      id: 2,
      type: 'medium',
      title: 'FX Exposure Increase',
      message: 'EUR exposure increased 12% this week, consider additional hedging',
      timestamp: '2024-01-07T09:15:00Z',
      entity: 'All'
    },
    {
      id: 3,
      type: 'low',
      title: 'Credit Rating Change',
      message: 'Corporate bond issuer downgraded from AA- to A+',
      timestamp: '2024-01-07T08:45:00Z',
      entity: 'US-HQ'
    }
  ]

  return (
    <div className="space-y-6">
      {/* Risk Controls */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
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
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* VaR Trend Chart */}
        <div className="chart-container">
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
            <div>
              <div className="text-2xl font-semibold text-blue-600">$2.45M</div>
              <div className="text-sm text-gray-500">1-Day VaR (95%)</div>
            </div>
            <div>
              <div className="text-2xl font-semibold text-red-600">$7.75M</div>
              <div className="text-sm text-gray-500">10-Day VaR (95%)</div>
            </div>
            <div>
              <div className="text-2xl font-semibold text-yellow-600">$3.2M</div>
              <div className="text-sm text-gray-500">Expected Shortfall</div>
            </div>
          </div>
        </div>

        {/* Risk Breakdown */}
        <div className="chart-container">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-medium text-gray-900">Risk Breakdown</h3>
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
            {riskBreakdown.map((item, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex items-center">
                  <div 
                    className="w-3 h-3 rounded-full mr-2" 
                    style={{ backgroundColor: item.color }}
                  ></div>
                  <span className="text-sm text-gray-700">{item.name}</span>
                </div>
                <span className="text-sm font-medium text-gray-900">{item.value}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* FX Exposure Analysis */}
      <div className="chart-container">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-medium text-gray-900">Foreign Exchange Risk</h3>
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
      </div>

      {/* Stress Testing */}
      <div className="chart-container">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-medium text-gray-900">Stress Test Scenarios</h3>
          <ExclamationTriangleIcon className="h-6 w-6 text-amber-600" />
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {stressScenarios.map((scenario, index) => (
            <div key={index} className="p-4 border border-gray-200 rounded-lg">
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
            </div>
          ))}
        </div>
      </div>

      {/* Risk Alerts */}
      <div className="chart-container">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-medium text-gray-900">Risk Alerts</h3>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
            <span className="text-sm text-red-600 font-medium">
              {riskAlerts.filter(alert => alert.type === 'high').length} Critical
            </span>
          </div>
        </div>
        
        <div className="space-y-3">
          {riskAlerts.map((alert) => (
            <div
              key={alert.id}
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
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
  