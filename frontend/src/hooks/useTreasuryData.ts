'use client'

import { useState, useEffect } from 'react'
import { useTreasuryWebSocket } from './useWebSocket'

interface TreasuryData {
  totalPortfolioValue: number
  totalCash: number
  totalInvestments: number
  portfolioVaR: number
  optimizationOpportunity: number
  entities: Array<{
    id: string
    name: string
    cashBalance: number
    investments: number
    currency: string
  }>
  riskMetrics: {
    var95: number
    var99: number
    expectedShortfall: number
    creditRisk: number
    marketRisk: number
    fxRisk: number
  }
  performance: {
    ytdReturn: number
    monthlyReturn: number
    sharpeRatio: number
    volatility: number
  }
}

export function useTreasuryData() {
  const [data, setData] = useState<TreasuryData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  const { isConnected, portfolioUpdates, marketData } = useTreasuryWebSocket()

  // Mock data for demo purposes
  const mockData: TreasuryData = {
    totalPortfolioValue: 500656000,
    totalCash: 300000000,
    totalInvestments: 200656000,
    portfolioVaR: 2450000,
    optimizationOpportunity: 1250000,
    entities: [
      {
        id: 'us-hq',
        name: 'US Headquarters',
        cashBalance: 150000000,
        investments: 100000000,
        currency: 'USD'
      },
      {
        id: 'eu-ltd',
        name: 'Europe Ltd.',
        cashBalance: 75000000,
        investments: 50000000,
        currency: 'EUR'
      },
      {
        id: 'apac-pte',
        name: 'Asia Pacific Pte.',
        cashBalance: 50000000,
        investments: 35000000,
        currency: 'USD'
      },
      {
        id: 'ca-corp',
        name: 'Canada Corp.',
        cashBalance: 25000000,
        investments: 15656000,
        currency: 'CAD'
      }
    ],
    riskMetrics: {
      var95: 2450000,
      var99: 3200000,
      expectedShortfall: 2800000,
      creditRisk: 850000,
      marketRisk: 1200000,
      fxRisk: 400000
    },
    performance: {
      ytdReturn: 3.2,
      monthlyReturn: 0.8,
      sharpeRatio: 1.45,
      volatility: 8.2
    }
  }

  useEffect(() => {
    // Simulate API call
    const fetchData = async () => {
      try {
        setLoading(true)
        
        // Simulate network delay
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // In a real app, this would be an API call
        // const response = await fetch('/api/treasury/portfolio')
        // const data = await response.json()
        
        setData(mockData)
        setError(null)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch treasury data')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  // Update data when WebSocket updates are received
  useEffect(() => {
    if (portfolioUpdates.length > 0 && data) {
      const latestUpdate = portfolioUpdates[0]
      setData(prevData => ({
        ...prevData!,
        ...latestUpdate
      }))
    }
  }, [portfolioUpdates, data])

  // Update market data
  useEffect(() => {
    if (marketData && data) {
      setData(prevData => ({
        ...prevData!,
        riskMetrics: {
          ...prevData!.riskMetrics,
          ...marketData.riskMetrics
        }
      }))
    }
  }, [marketData, data])

  const refreshData = async () => {
    setLoading(true)
    try {
      // Simulate refresh
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // Add some random variation to simulate real-time updates
      const updatedData = {
        ...mockData,
        totalPortfolioValue: mockData.totalPortfolioValue + (Math.random() - 0.5) * 1000000,
        portfolioVaR: mockData.portfolioVaR + (Math.random() - 0.5) * 100000,
        performance: {
          ...mockData.performance,
          monthlyReturn: mockData.performance.monthlyReturn + (Math.random() - 0.5) * 0.2
        }
      }
      
      setData(updatedData)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to refresh data')
    } finally {
      setLoading(false)
    }
  }

  return {
    data,
    loading,
    error,
    isConnected,
    refreshData
  }
}