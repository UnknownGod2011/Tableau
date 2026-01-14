'use client'

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  PaperAirplaneIcon,
  SparklesIcon,
  ChartBarIcon,
  CurrencyDollarIcon,
  ShieldCheckIcon,
  ExclamationTriangleIcon,
  TrashIcon
} from '@heroicons/react/24/outline'

interface Message {
  id: string
  type: 'user' | 'assistant'
  content: string
  timestamp: Date
  suggestions?: string[]
  intent?: string
  confidence?: number
  isTyping?: boolean
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
  const [typingText, setTypingText] = useState('')
  const [typingMessageId, setTypingMessageId] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  // Only scroll when new messages are added, not during typing
  useEffect(() => {
    scrollToBottom()
  }, [messages.length])

  const typeMessage = async (fullText: string): Promise<void> => {
    const words = fullText.split(' ')
    let currentText = ''
    for (let i = 0; i < words.length; i++) {
      currentText += (i === 0 ? '' : ' ') + words[i]
      setTypingText(currentText)
      await new Promise(resolve => setTimeout(resolve, 15 + Math.random() * 20))
    }
    setTypingText('')
    setTypingMessageId(null)
  }

  const handleSendMessage = async (content: string) => {
    if (!content.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: content.trim(),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    await new Promise(resolve => setTimeout(resolve, 600 + Math.random() * 800))

    const aiResponse = generateAIResponse(content.trim())
    const assistantMessageId = (Date.now() + 1).toString()
    setTypingMessageId(assistantMessageId)
    
    setMessages(prev => [...prev, {
      id: assistantMessageId,
      type: 'assistant',
      content: '',
      timestamp: new Date(),
      isTyping: true
    }])
    
    setIsLoading(false)
    await typeMessage(aiResponse.content)
    
    setMessages(prev => prev.map(msg => 
      msg.id === assistantMessageId 
        ? { ...msg, content: aiResponse.content, suggestions: aiResponse.suggestions, intent: aiResponse.intent, confidence: aiResponse.confidence, isTyping: false }
        : msg
    ))
  }

  const generateAIResponse = (userInput: string): { content: string; suggestions?: string[]; intent?: string; confidence?: number } => {
    const input = userInput.toLowerCase()

    if (input.includes('cash') && (input.includes('optimization') || input.includes('optimize') || input.includes('opportunity'))) {
      return {
        content: `📊 Cash Optimization Analysis

Based on your current cash positions, I've identified significant opportunities:

💰 Potential Annual Yield Increase: $1.25M

Current State:
• Total Cash: $300M across 4 account types
• Weighted Average Yield: 2.1%
• Low-yield checking: $45M (0.5% APY)

Recommended Actions:

1️⃣ Move $15M from checking to money market
   Current: 0.5% → New: 2.5%
   Annual benefit: +$300,000

2️⃣ Reallocate $8M from savings to CDs
   Current: 1.5% → New: 3.5%
   Annual benefit: +$160,000

3️⃣ Deploy $12M to Treasury Bills
   Expected yield: 4.5%
   Annual benefit: +$540,000

Risk Assessment: Low - All recommendations maintain liquidity buffers.`,
        suggestions: ["Create implementation plan", "Show risk impact", "Compare with benchmarks", "Set up auto-sweeping"],
        intent: 'cash_optimization',
        confidence: 0.95
      }
    }

    if (input.includes('risk') || input.includes('var')) {
      return {
        content: `🛡️ Portfolio Risk Analysis

Value at Risk (VaR) - 95% Confidence:
• 1-Day VaR: $2.45M (0.49% of portfolio)
• 10-Day VaR: $7.75M (1.55% of portfolio)
• Expected Shortfall: $3.2M

Risk Decomposition:
• Credit Risk: 45% ($1.1M)
• Market Risk: 30% ($735K)
• FX Risk: 15% ($368K)
• Liquidity Risk: 10% ($245K)

Current Alerts:
🔴 HIGH - VaR approaching 80% of $3M limit (EU-LTD)
🟡 MEDIUM - EUR exposure increased 12% this week
🟢 LOW - Credit rating change on bond issuer

Stress Test Results:
• Interest Rate +200bp: -$8.5M
• Credit Spread +100bp: -$3.2M
• FX Volatility 2x: -$1.8M

Overall risk is within acceptable ranges. Consider reviewing EUR hedging.`,
        suggestions: ["Run stress scenarios", "Show FX hedging options", "Analyze credit concentration", "Set up alerts"],
        intent: 'risk_analysis',
        confidence: 0.92
      }
    }

    if (input.includes('investment') || input.includes('rebalance') || input.includes('portfolio')) {
      return {
        content: `📈 Investment Portfolio Analysis

Current Allocation: $200.7M

Asset Class     | Amount  | Allocation | Status
US Treasuries   | $50M    | 25%        | ✅
Money Market    | $75M    | 37%        | ✅
Corporate Bonds | $55M    | 27%        | ✅
Commercial Paper| $20.7M  | 10%        | ✅

Portfolio Metrics:
• Weighted Average Yield: 3.2%
• Average Duration: 2.3 years
• Average Credit Rating: AA-

Upcoming Maturities:
📅 30 days: $20.7M Commercial Paper
📅 6 months: $25M Corporate Bond
📅 18 months: $30M EUR Corporate Bond

Recommendations:
1️⃣ Reinvest maturing CP to Money Market (2.8% yield)
2️⃣ Consider ESG bonds for diversification
3️⃣ Extend duration slightly given yield curve`,
        suggestions: ["Show maturity ladder", "Find ESG options", "Analyze yield curve", "Compare alternatives"],
        intent: 'investment_analysis',
        confidence: 0.94
      }
    }

    if (input.includes('fx') || input.includes('currency') || input.includes('hedge')) {
      return {
        content: `🌍 Foreign Exchange Risk Analysis

Total FX Exposure: $120M

Currency | Exposure | Hedged | Unhedged | VaR
EUR      | $45M     | 75%    | 25%      | $280K
SGD      | $35M     | 40%    | 60%      | $180K
CAD      | $25M     | 60%    | 40%      | $95K
JPY      | $15M     | 50%    | 50%      | $120K

Risk Alerts:
🔴 SGD hedge ratio 40% (policy min: 60%)
🟡 EUR exposure +12% this month

Hedging Recommendations:
1️⃣ SGD forward contracts: $7M notional
2️⃣ Increase EUR hedge to 85%: +$4.5M
3️⃣ Consider JPY options for tail risk

Expected VaR Reduction: $280K (8% improvement)`,
        suggestions: ["Get hedging quotes", "Analyze costs", "Show correlations", "Set up FX alerts"],
        intent: 'fx_risk',
        confidence: 0.93
      }
    }

    if (input.includes('alert') || input.includes('urgent') || input.includes('warning')) {
      return {
        content: `🚨 Active Alerts

Critical (Action Required):
🔴 VaR Limit Warning - EU-LTD
   Current: $2.4M (80% of $3M limit)
   Action: Review EUR positions

🔴 SGD Hedge Below Policy
   Current: 40% | Required: 60%
   Action: Add forward contracts

Medium Priority:
🟡 EUR Exposure +12% this week
🟡 $20.7M CP matures in 30 days

Summary: 2 Critical | 2 Medium alerts`,
        suggestions: ["Fix VaR warning", "Set up SGD hedging", "Plan CP reinvestment", "View alert history"],
        intent: 'alerts',
        confidence: 0.94
      }
    }

    if (input.includes('hello') || input.includes('hi') || input.includes('hey')) {
      return {
        content: `👋 Hello! I'm your TreasuryIQ AI assistant.

I can help you with:
💰 Cash Management - Optimize yields
📊 Risk Analysis - VaR, stress testing
📈 Investments - Portfolio rebalancing
🌍 FX & Hedging - Currency exposure

Quick Stats:
• Total AUM: $500.7M
• Today's yield: 2.8%
• Active alerts: 4

What would you like to explore?`,
        suggestions: ["Show key metrics", "Any urgent alerts?", "Optimization opportunities", "Portfolio summary"],
        intent: 'greeting',
        confidence: 0.99
      }
    }

    return {
      content: `I can help you with treasury management:

💰 Cash Optimization - "What are my cash opportunities?"
📊 Risk Analysis - "Show me risk analysis"
📈 Investments - "How should I rebalance?"
🌍 FX Management - "What are my FX risks?"
🚨 Alerts - "Show me urgent alerts"

Quick Stats:
• Total AUM: $500.7M
• Today's yield: 2.8%
• Risk status: Moderate

What would you like to explore?`,
      suggestions: ["Cash optimization", "Risk metrics", "Investment portfolio", "FX exposure"],
      intent: 'general',
      confidence: 0.75
    }
  }

  const quickActions = [
    { icon: CurrencyDollarIcon, label: "Cash", query: "What's my cash optimization opportunity?" },
    { icon: ShieldCheckIcon, label: "Risk", query: "Show me the portfolio risk analysis" },
    { icon: ChartBarIcon, label: "Performance", query: "How is my portfolio performing?" },
    { icon: ExclamationTriangleIcon, label: "Alerts", query: "Show me urgent alerts" }
  ]

  const clearChat = () => {
    setMessages([{
      id: Date.now().toString(),
      type: 'assistant',
      content: "Chat cleared. How can I help you today?",
      timestamp: new Date(),
      suggestions: ["Cash optimization", "Risk analysis", "Investment portfolio", "FX exposure"]
    }])
  }

  return (
    <div className="flex flex-col h-[650px] bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-indigo-50">
        <div className="flex items-center">
          <SparklesIcon className="h-7 w-7 text-blue-600 mr-3" />
          <div>
            <h3 className="text-lg font-semibold text-gray-900">AI Treasury Assistant</h3>
            <p className="text-xs text-gray-500">Powered by TreasuryIQ</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <button onClick={clearChat} className="p-2 text-gray-400 hover:text-gray-600 rounded-lg" title="Clear">
            <TrashIcon className="h-5 w-5" />
          </button>
          <div className="flex items-center space-x-2 px-3 py-1 bg-green-100 rounded-full">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-sm text-green-700">Online</span>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
        <AnimatePresence>
          {messages.map((message) => (
            <motion.div key={message.id} className="flex flex-col" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
              <div className={`max-w-[85%] ${message.type === 'user' ? 'ml-auto' : 'mr-auto'}`}>
                <div className={`p-4 rounded-2xl ${message.type === 'user' ? 'bg-blue-600 text-white rounded-br-md' : 'bg-white text-gray-800 shadow-sm border border-gray-100 rounded-bl-md'}`}>
                  <div className="whitespace-pre-wrap text-sm leading-relaxed">
                    {message.isTyping && typingMessageId === message.id ? typingText : message.content}
                  </div>
                  {message.type === 'assistant' && !message.isTyping && message.confidence && (
                    <div className="flex items-center space-x-3 mt-3 pt-3 border-t border-gray-100 text-xs text-gray-400">
                      {message.intent && <span className="px-2 py-0.5 bg-blue-50 text-blue-600 rounded-full">{message.intent}</span>}
                      <span>Confidence: {(message.confidence * 100).toFixed(0)}%</span>
                    </div>
                  )}
                </div>
                <div className={`text-xs text-gray-400 mt-1 ${message.type === 'user' ? 'text-right' : 'text-left'}`}>
                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>
              {message.suggestions && !message.isTyping && (
                <div className="flex flex-wrap gap-2 mt-3 ml-2">
                  {message.suggestions.map((s, i) => (
                    <button key={i} onClick={() => handleSendMessage(s)} className="text-xs px-3 py-1.5 bg-white text-blue-600 border border-blue-200 rounded-full hover:bg-blue-50">{s}</button>
                  ))}
                </div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>
        {isLoading && (
          <div className="flex items-center space-x-2 p-4 bg-white rounded-2xl shadow-sm max-w-[85%]">
            <motion.div className="w-2 h-2 bg-blue-400 rounded-full" animate={{ y: [0, -8, 0] }} transition={{ duration: 0.6, repeat: Infinity }} />
            <motion.div className="w-2 h-2 bg-blue-400 rounded-full" animate={{ y: [0, -8, 0] }} transition={{ duration: 0.6, repeat: Infinity, delay: 0.15 }} />
            <motion.div className="w-2 h-2 bg-blue-400 rounded-full" animate={{ y: [0, -8, 0] }} transition={{ duration: 0.6, repeat: Infinity, delay: 0.3 }} />
            <span className="text-sm text-gray-500 ml-2">Analyzing...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Actions */}
      <div className="px-4 py-3 border-t border-gray-100 bg-white">
        <div className="flex space-x-2 overflow-x-auto">
          {quickActions.map((action, i) => (
            <button key={i} onClick={() => handleSendMessage(action.query)} disabled={isLoading} className="flex items-center space-x-2 px-4 py-2 bg-blue-50 text-blue-700 rounded-xl hover:bg-blue-100 whitespace-nowrap text-sm font-medium">
              <action.icon className="h-4 w-4" />
              <span>{action.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-200 bg-white">
        <div className="flex space-x-3">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage(inputValue)}
            placeholder="Ask about cash, risk, investments..."
            className="flex-1 px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none text-sm"
            disabled={isLoading}
          />
          <button onClick={() => handleSendMessage(inputValue)} disabled={isLoading || !inputValue.trim()} className="px-5 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-50">
            <PaperAirplaneIcon className="h-5 w-5" />
          </button>
        </div>
      </div>
    </div>
  )
}
