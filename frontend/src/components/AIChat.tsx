'use client'

import { useState, useRef, useEffect } from 'react'
import { 
  PaperAirplaneIcon,
  SparklesIcon,
  ChartBarIcon,
  CurrencyDollarIcon,
  ShieldCheckIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'

interface Message {
  id: string
  type: 'user' | 'assistant'
  content: string
  timestamp: Date
  suggestions?: string[]
  intent?: string
  confidence?: number
  visualizations?: any[]
  error?: string
}

interface ChatResponse {
  response: string
  session_id: string
  turn_id: string
  intent?: string
  entities?: any
  confidence: number
  processing_time_ms: number
  data_visualizations?: any[]
  suggested_actions?: string[]
  error?: string
}

export default function AIChat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'assistant',
      content: "Hello! I'm your TreasuryIQ AI assistant. I can help you with cash optimization, risk analysis, investment recommendations, and answer questions about your treasury portfolio. What would you like to know?",
      timestamp: new Date(),
      suggestions: [
        "What's my current cash optimization opportunity?",
        "Show me the portfolio risk analysis",
        "How should I rebalance my investments?",
        "What are the FX exposure risks?"
      ]
    }
  ])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState<string>('')
  const [connectionStatus, setConnectionStatus] = useState<'online' | 'offline' | 'connecting'>('connecting')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  // Initialize session and check connection
  useEffect(() => {
    initializeSession()
  }, [])

  const initializeSession = async () => {
    try {
      // Generate a session ID
      const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      setSessionId(newSessionId)
      
      // Test connection to AI service
      const response = await fetch('/api/v1/ai/health')
      if (response.ok) {
        setConnectionStatus('online')
      } else {
        setConnectionStatus('offline')
      }
    } catch (error) {
      console.error('Failed to initialize AI session:', error)
      setConnectionStatus('offline')
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async (content: string) => {
    if (!content.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: content.trim(),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    try {
      // Call the real AI API
      const response = await fetch('/api/v1/ai/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: content.trim(),
          session_id: sessionId,
          entity_scope: ['demo_entity'], // In production, get from user context
          dashboard_context: {
            current_page: 'chat',
            timestamp: new Date().toISOString()
          }
        })
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
      }

      const aiResponse: ChatResponse = await response.json()
      
      const assistantMessage: Message = {
        id: aiResponse.turn_id || (Date.now() + 1).toString(),
        type: 'assistant',
        content: aiResponse.response,
        timestamp: new Date(),
        suggestions: aiResponse.suggested_actions,
        intent: aiResponse.intent,
        confidence: aiResponse.confidence,
        visualizations: aiResponse.data_visualizations,
        error: aiResponse.error
      }

      setMessages(prev => [...prev, assistantMessage])
      
      // Update session ID if provided
      if (aiResponse.session_id && aiResponse.session_id !== sessionId) {
        setSessionId(aiResponse.session_id)
      }

    } catch (error) {
      console.error('AI API error:', error)
      
      // Fallback to mock response if API fails
      const fallbackResponse = generateAIResponse(content.trim())
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: connectionStatus === 'offline' 
          ? `🔌 **Offline Mode**: ${fallbackResponse.content}\n\n*Note: Using cached responses. Some features may be limited.*`
          : "I apologize, but I'm having trouble processing your request right now. Please try again in a moment.",
        timestamp: new Date(),
        suggestions: fallbackResponse.suggestions,
        error: connectionStatus === 'offline' ? undefined : 'API connection failed'
      }
      
      setMessages(prev => [...prev, assistantMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const generateAIResponse = (userInput: string): { content: string; suggestions?: string[] } => {
    const input = userInput.toLowerCase()

    if (input.includes('cash') && input.includes('optimization')) {
      return {
        content: "Based on your current cash positions, I've identified a significant optimization opportunity:\n\n💰 **$1.25M Annual Yield Increase Available**\n\n**Key Recommendations:**\n• Move $15M from checking (0.5% APY) to money market (2.5% APY)\n• Reallocate $8M from savings to 6-month CDs (3.5% APY)\n• Consider Treasury bills for $12M excess liquidity\n\n**Expected Impact:**\n• Additional annual income: $1,250,000\n• Improved weighted average yield: 2.1% → 2.8%\n• Maintained liquidity requirements\n\nWould you like me to create a detailed implementation plan?",
        suggestions: [
          "Create implementation plan for cash optimization",
          "Show me the risk impact of these changes",
          "What are the liquidity implications?",
          "Compare with peer benchmarks"
        ]
      }
    }

    if (input.includes('risk') || input.includes('var')) {
      return {
        content: "Here's your current portfolio risk analysis:\n\n🛡️ **Risk Metrics Summary**\n\n**Value at Risk (95% confidence):**\n• 1-day VaR: $2.45M (0.49% of portfolio)\n• 10-day VaR: $7.75M (1.55% of portfolio)\n• Expected Shortfall: $3.2M\n\n**Risk Breakdown:**\n• Cash positions: $0.3M (12%)\n• Fixed income: $1.8M (73%)\n• FX exposure: $0.35M (15%)\n\n**Key Risks:**\n⚠️ EUR exposure increased 12% this month\n⚠️ Credit concentration in financial sector\n✅ Interest rate duration well-managed\n\nYour risk levels are within acceptable ranges, but consider additional EUR hedging.",
        suggestions: [
          "Show FX hedging recommendations",
          "Analyze credit concentration risk",
          "Run stress test scenarios",
          "Compare risk vs. peer portfolios"
        ]
      }
    }

    if (input.includes('investment') || input.includes('rebalance')) {
      return {
        content: "Investment portfolio rebalancing analysis:\n\n📊 **Current Allocation vs. Target**\n\n**Fixed Income: $200.7M (40.1%)**\n• Target: 35-45% ✅\n• Quality: High (avg. rating: AA-)\n• Duration: 2.3 years\n\n**Recommendations:**\n1. **Reduce Treasury concentration** - Currently 37% in Treasuries\n2. **Add corporate bonds** - Target 15% allocation (currently 12%)\n3. **Consider international bonds** - Diversify currency exposure\n\n**Maturity Schedule:**\n• $20.7M maturing in 30 days (Commercial Paper)\n• $25M maturing in 18 months (Corporate Bond)\n\n**Action Items:**\n• Reinvest maturing CP in money market or short-term Treasuries\n• Consider ESG-compliant corporate bonds for diversification",
        suggestions: [
          "Show detailed maturity schedule",
          "Find ESG investment options",
          "Analyze yield curve positioning",
          "Compare investment alternatives"
        ]
      }
    }

    if (input.includes('fx') || input.includes('currency') || input.includes('hedge')) {
      return {
        content: "Foreign Exchange Risk Analysis:\n\n🌍 **FX Exposure Summary**\n\n**Total Exposure: $115M**\n• EUR: $45M (39%) - 75% hedged\n• JPY: $15M (13%) - 50% hedged\n• CAD: $25M (22%) - 60% hedged\n• SGD: $35M (26%) - 40% hedged\n\n**Risk Alerts:**\n🔴 **EUR exposure** increased 12% this month\n🟡 **SGD hedging** below target (40% vs 60% target)\n🟢 **CAD exposure** well-hedged\n\n**Hedging Recommendations:**\n1. Increase EUR hedging to 85% (+$4.5M notional)\n2. Add SGD forward contracts (+$7M notional)\n3. Consider JPY options for tail risk protection\n\n**Expected VaR Reduction:** $280K (8% improvement)",
        suggestions: [
          "Get specific hedging quotes",
          "Analyze hedging costs vs. benefits",
          "Show currency correlation matrix",
          "Set up automated hedging alerts"
        ]
      }
    }

    if (input.includes('performance') || input.includes('benchmark')) {
      return {
        content: "Portfolio Performance vs. Benchmarks:\n\n📈 **YTD Performance**\n\n**Total Return: +3.2%**\n• Cash yield: +2.1% (vs. Fed Funds 5.25%)\n• Investment return: +4.8%\n• FX impact: -0.3%\n\n**Peer Comparison:**\n• Industry median: +2.8% ✅ Outperforming\n• Top quartile: +3.8% (Target)\n• Your ranking: 32nd percentile\n\n**Key Drivers:**\n✅ Strong money market allocation\n✅ Well-timed Treasury purchases\n⚠️ FX headwinds from EUR weakness\n\n**Improvement Opportunities:**\n• Optimize cash drag (low-yield checking accounts)\n• Consider longer-duration positioning\n• Enhanced FX hedging strategy",
        suggestions: [
          "Show detailed performance attribution",
          "Compare with specific peer group",
          "Analyze risk-adjusted returns",
          "Get improvement recommendations"
        ]
      }
    }

    // Default response
    return {
      content: "I understand you're asking about treasury management. I can help you with:\n\n• **Cash Optimization** - Maximize yields while maintaining liquidity\n• **Risk Analysis** - VaR calculations, stress testing, and risk monitoring\n• **Investment Strategy** - Portfolio allocation and rebalancing\n• **FX Risk Management** - Currency exposure analysis and hedging\n• **Performance Analytics** - Benchmarking and attribution analysis\n• **Regulatory Compliance** - Audit trails and reporting\n\nWhat specific area would you like to explore?",
      suggestions: [
        "Analyze my cash optimization opportunities",
        "Show me current risk metrics",
        "Review investment portfolio allocation",
        "Check FX exposure and hedging status"
      ]
    }
  }

  const quickActions = [
    {
      icon: CurrencyDollarIcon,
      label: "Cash Optimization",
      query: "What's my current cash optimization opportunity?"
    },
    {
      icon: ShieldCheckIcon,
      label: "Risk Analysis",
      query: "Show me the portfolio risk analysis"
    },
    {
      icon: ChartBarIcon,
      label: "Performance Review",
      query: "How is my portfolio performing vs benchmarks?"
    }
  ]

  return (
    <div className="flex flex-col h-[600px] bg-white rounded-lg shadow-sm border border-gray-200">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div className="flex items-center">
          <SparklesIcon className="h-6 w-6 text-blue-600 mr-2" />
          <h3 className="text-lg font-medium text-gray-900">AI Treasury Assistant</h3>
        </div>
        <div className="flex items-center space-x-2">
          <div className={`w-2 h-2 rounded-full ${
            connectionStatus === 'online' ? 'bg-green-500' : 
            connectionStatus === 'connecting' ? 'bg-yellow-500' : 'bg-red-500'
          }`}></div>
          <span className={`text-sm ${
            connectionStatus === 'online' ? 'text-green-600' : 
            connectionStatus === 'connecting' ? 'text-yellow-600' : 'text-red-600'
          }`}>
            {connectionStatus === 'online' ? 'Online' : 
             connectionStatus === 'connecting' ? 'Connecting...' : 'Offline'}
          </span>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div key={message.id} className="flex flex-col">
            <div className={`chat-message ${message.type}`}>
              <div className="flex items-start justify-between">
                <div className="whitespace-pre-wrap flex-1">{message.content}</div>
                {message.error && (
                  <ExclamationTriangleIcon className="h-5 w-5 text-red-500 ml-2 flex-shrink-0" />
                )}
              </div>
              
              {/* Show confidence and intent for assistant messages */}
              {message.type === 'assistant' && (message.confidence || message.intent) && (
                <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                  {message.intent && (
                    <span>Intent: {message.intent}</span>
                  )}
                  {message.confidence && (
                    <span>Confidence: {(message.confidence * 100).toFixed(0)}%</span>
                  )}
                </div>
              )}
              
              {/* Show visualizations if available */}
              {message.visualizations && message.visualizations.length > 0 && (
                <div className="mt-3 p-3 bg-blue-50 rounded-lg">
                  <div className="text-sm font-medium text-blue-800 mb-2">📊 Available Visualizations:</div>
                  {message.visualizations.map((viz, index) => (
                    <div key={index} className="text-sm text-blue-700">
                      • {viz.type.replace('_', ' ').replace(/\b\w/g, (l: string) => l.toUpperCase())}
                    </div>
                  ))}
                </div>
              )}
            </div>
            
            {message.suggestions && (
              <div className="flex flex-wrap gap-2 mt-2 ml-4">
                {message.suggestions.map((suggestion, index) => (
                  <button
                    key={index}
                    onClick={() => handleSendMessage(suggestion)}
                    className="text-xs px-3 py-1 bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200 transition-colors"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}
        
        {isLoading && (
          <div className="chat-message assistant">
            <div className="flex items-center space-x-2">
              <div className="animate-pulse flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
              <span className="text-sm text-gray-500">AI is thinking...</span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Actions */}
      <div className="px-4 py-2 border-t border-gray-100">
        <div className="flex space-x-2 overflow-x-auto">
          {quickActions.map((action, index) => {
            const Icon = action.icon
            return (
              <button
                key={index}
                onClick={() => handleSendMessage(action.query)}
                className="flex items-center space-x-2 px-3 py-2 bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 transition-colors whitespace-nowrap text-sm"
              >
                <Icon className="h-4 w-4" />
                <span>{action.label}</span>
              </button>
            )
          })}
        </div>
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-200">
        <div className="flex space-x-2">
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                handleSendMessage(inputValue)
              }
            }}
            placeholder="Ask about cash optimization, risk analysis, investments..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            disabled={isLoading}
          />
          <button
            onClick={() => handleSendMessage(inputValue)}
            disabled={isLoading || !inputValue.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <PaperAirplaneIcon className="h-5 w-5" />
          </button>
        </div>
      </div>
    </div>
  )
}