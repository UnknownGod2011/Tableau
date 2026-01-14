'use client'

import { useEffect, useRef, useState, useCallback } from 'react'
import { io, Socket } from 'socket.io-client'

interface WebSocketConfig {
  url: string
  options?: any
  autoConnect?: boolean
}

interface WebSocketMessage {
  type: string
  data: any
  timestamp: string
}

export function useWebSocket({ url, options = {}, autoConnect = true }: WebSocketConfig) {
  const [socket, setSocket] = useState<Socket | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)
  const [connectionError, setConnectionError] = useState<string | null>(null)
  const reconnectAttempts = useRef(0)
  const maxReconnectAttempts = 5

  const connect = useCallback(() => {
    if (socket?.connected) return

    const newSocket = io(url, {
      transports: ['websocket'],
      timeout: 20000,
      ...options
    })

    newSocket.on('connect', () => {
      console.log('WebSocket connected')
      setIsConnected(true)
      setConnectionError(null)
      reconnectAttempts.current = 0
    })

    newSocket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason)
      setIsConnected(false)
      
      // Auto-reconnect logic
      if (reason === 'io server disconnect') {
        // Server initiated disconnect, don't reconnect
        return
      }
      
      if (reconnectAttempts.current < maxReconnectAttempts) {
        setTimeout(() => {
          reconnectAttempts.current++
          connect()
        }, Math.pow(2, reconnectAttempts.current) * 1000) // Exponential backoff
      }
    })

    newSocket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error)
      setConnectionError(error.message)
      setIsConnected(false)
    })

    // Handle incoming messages
    newSocket.onAny((eventName, data) => {
      setLastMessage({
        type: eventName,
        data,
        timestamp: new Date().toISOString()
      })
    })

    setSocket(newSocket)
  }, [url, options])

  const disconnect = useCallback(() => {
    if (socket) {
      socket.disconnect()
      setSocket(null)
      setIsConnected(false)
    }
  }, [socket])

  const emit = useCallback((event: string, data: any) => {
    if (socket?.connected) {
      socket.emit(event, data)
    } else {
      console.warn('Socket not connected, cannot emit event:', event)
    }
  }, [socket])

  const subscribe = useCallback((event: string, callback: (data: any) => void) => {
    if (socket) {
      socket.on(event, callback)
      return () => socket.off(event, callback)
    }
    return () => {}
  }, [socket])

  useEffect(() => {
    if (autoConnect) {
      connect()
    }

    return () => {
      disconnect()
    }
  }, [connect, disconnect, autoConnect])

  return {
    socket,
    isConnected,
    lastMessage,
    connectionError,
    connect,
    disconnect,
    emit,
    subscribe
  }
}

// Specialized hook for treasury data updates
export function useTreasuryWebSocket() {
  const { isConnected, lastMessage, emit, subscribe } = useWebSocket({
    url: process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000',
    options: {
      auth: {
        // Add authentication if needed
      }
    }
  })

  const [portfolioUpdates, setPortfolioUpdates] = useState<any[]>([])
  const [riskAlerts, setRiskAlerts] = useState<any[]>([])
  const [marketData, setMarketData] = useState<any>(null)

  useEffect(() => {
    const unsubscribePortfolio = subscribe('portfolio_update', (data) => {
      setPortfolioUpdates(prev => [data, ...prev.slice(0, 99)]) // Keep last 100 updates
    })

    const unsubscribeRisk = subscribe('risk_alert', (data) => {
      setRiskAlerts(prev => [data, ...prev.slice(0, 49)]) // Keep last 50 alerts
    })

    const unsubscribeMarket = subscribe('market_data', (data) => {
      setMarketData(data)
    })

    return () => {
      unsubscribePortfolio()
      unsubscribeRisk()
      unsubscribeMarket()
    }
  }, [subscribe])

  const requestPortfolioUpdate = useCallback((entityId?: string) => {
    emit('request_portfolio_update', { entityId })
  }, [emit])

  const requestRiskCalculation = useCallback((params: any) => {
    emit('request_risk_calculation', params)
  }, [emit])

  return {
    isConnected,
    lastMessage,
    portfolioUpdates,
    riskAlerts,
    marketData,
    requestPortfolioUpdate,
    requestRiskCalculation
  }
}