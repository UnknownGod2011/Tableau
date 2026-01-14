'use client'

import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  MagnifyingGlassIcon,
  SparklesIcon,
  ClockIcon,
  TrendingUpIcon,
  CurrencyDollarIcon,
  ShieldCheckIcon,
  ChartBarIcon,
  XMarkIcon
} from '@heroicons/react/24/outline'

interface SearchResult {
  id: string
  type: 'entity' | 'metric' | 'report' | 'action' | 'insight'
  title: string
  description: string
  value?: string
  icon: React.ComponentType<{ className?: string }>
  category: string
  relevance: number
  onClick: () => void
}

interface SearchSuggestion {
  id: string
  text: string
  type: 'recent' | 'trending' | 'ai'
  icon: React.ComponentType<{ className?: string }>
}

export default function SmartSearch() {
  const [query, setQuery] = useState('')
  const [isOpen, setIsOpen] = useState(false)
  const [results, setResults] = useState<SearchResult[]>([])
  const [suggestions, setSuggestions] = useState<SearchSuggestion[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [selectedIndex, setSelectedIndex] = useState(-1)
  
  const inputRef = useRef<HTMLInputElement>(null)
  const resultsRef = useRef<HTMLDivElement>(null)

  // Mock data for search results
  const mockResults: SearchResult[] = [
    {
      id: '1',
      type: 'entity',
      title: 'US Headquarters',
      description: 'Primary entity with $200M portfolio',
      value: '$200,000,000',
      icon: CurrencyDollarIcon,
      category: 'Entities',
      relevance: 0.95,
      onClick: () => console.log('Navigate to US HQ')
    },
    {
      id: '2',
      type: 'metric',
      title: 'Portfolio VaR',
      description: 'Current 1-day Value at Risk',
      value: '$2.45M',
      icon: ShieldCheckIcon,
      category: 'Risk Metrics',
      relevance: 0.88,
      onClick: () => console.log('Show VaR details')
    },
    {
      id: '3',
      type: 'action',
      title: 'Cash Optimization',
      description: 'Optimize cash allocation for better yields',
      icon: TrendingUpIcon,
      category: 'Actions',
      relevance: 0.82,
      onClick: () => console.log('Start cash optimization')
    },
    {
      id: '4',
      type: 'report',
      title: 'Monthly Risk Report',
      description: 'Comprehensive risk analysis for December 2024',
      icon: ChartBarIcon,
      category: 'Reports',
      relevance: 0.75,
      onClick: () => console.log('Open risk report')
    },
    {
      id: '5',
      type: 'insight',
      title: 'FX Hedging Opportunity',
      description: 'AI detected potential EUR hedging improvement',
      icon: SparklesIcon,
      category: 'AI Insights',
      relevance: 0.70,
      onClick: () => console.log('Show FX insight')
    }
  ]

  const mockSuggestions: SearchSuggestion[] = [
    {
      id: '1',
      text: 'Show me cash optimization opportunities',
      type: 'ai',
      icon: SparklesIcon
    },
    {
      id: '2',
      text: 'Portfolio VaR analysis',
      type: 'recent',
      icon: ClockIcon
    },
    {
      id: '3',
      text: 'FX exposure by entity',
      type: 'trending',
      icon: TrendingUpIcon
    },
    {
      id: '4',
      text: 'Investment maturity schedule',
      type: 'recent',
      icon: ClockIcon
    },
    {
      id: '5',
      text: 'Risk limit breaches',
      type: 'ai',
      icon: SparklesIcon
    }
  ]

  useEffect(() => {
    setSuggestions(mockSuggestions)
  }, [])

  useEffect(() => {
    if (query.length > 0) {
      setIsLoading(true)
      
      // Simulate API search with debouncing
      const timeoutId = setTimeout(() => {
        const filtered = mockResults.filter(result =>
          result.title.toLowerCase().includes(query.toLowerCase()) ||
          result.description.toLowerCase().includes(query.toLowerCase()) ||
          result.category.toLowerCase().includes(query.toLowerCase())
        ).sort((a, b) => b.relevance - a.relevance)
        
        setResults(filtered)
        setIsLoading(false)
      }, 300)

      return () => clearTimeout(timeoutId)
    } else {
      setResults([])
      setIsLoading(false)
    }
  }, [query])

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isOpen) return

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault()
        setSelectedIndex(prev => 
          prev < (query ? results.length - 1 : suggestions.length - 1) ? prev + 1 : prev
        )
        break
      case 'ArrowUp':
        e.preventDefault()
        setSelectedIndex(prev => prev > 0 ? prev - 1 : prev)
        break
      case 'Enter':
        e.preventDefault()
        if (selectedIndex >= 0) {
          if (query && results[selectedIndex]) {
            results[selectedIndex].onClick()
          } else if (!query && suggestions[selectedIndex]) {
            setQuery(suggestions[selectedIndex].text)
          }
          setIsOpen(false)
        }
        break
      case 'Escape':
        setIsOpen(false)
        inputRef.current?.blur()
        break
    }
  }

  const handleSuggestionClick = (suggestion: SearchSuggestion) => {
    setQuery(suggestion.text)
    setIsOpen(false)
    inputRef.current?.focus()
  }

  const clearSearch = () => {
    setQuery('')
    setResults([])
    setSelectedIndex(-1)
    inputRef.current?.focus()
  }

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'Entities':
        return 'text-blue-600 bg-blue-50'
      case 'Risk Metrics':
        return 'text-red-600 bg-red-50'
      case 'Actions':
        return 'text-green-600 bg-green-50'
      case 'Reports':
        return 'text-purple-600 bg-purple-50'
      case 'AI Insights':
        return 'text-yellow-600 bg-yellow-50'
      default:
        return 'text-gray-600 bg-gray-50'
    }
  }

  return (
    <div className="relative w-full max-w-lg">
      {/* Search Input */}
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
        </div>
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => setIsOpen(true)}
          onKeyDown={handleKeyDown}
          placeholder="Search treasury data, ask AI, or find insights..."
          className="block w-full pl-10 pr-10 py-3 border border-gray-300 rounded-lg bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
        />
        {query && (
          <button
            onClick={clearSearch}
            className="absolute inset-y-0 right-0 pr-3 flex items-center"
          >
            <XMarkIcon className="h-5 w-5 text-gray-400 hover:text-gray-600" />
          </button>
        )}
      </div>

      {/* Search Results/Suggestions Dropdown */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
            ref={resultsRef}
            className="absolute z-50 w-full mt-2 bg-white rounded-lg shadow-xl border border-gray-200 max-h-96 overflow-hidden"
          >
            {query ? (
              // Search Results
              <div>
                {isLoading ? (
                  <div className="px-4 py-8 text-center">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="text-sm text-gray-500 mt-2">Searching...</p>
                  </div>
                ) : results.length > 0 ? (
                  <div className="py-2">
                    <div className="px-4 py-2 text-xs font-medium text-gray-500 uppercase tracking-wider border-b border-gray-100">
                      Search Results ({results.length})
                    </div>
                    {results.map((result, index) => {
                      const Icon = result.icon
                      return (
                        <motion.button
                          key={result.id}
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.05 }}
                          onClick={result.onClick}
                          className={`w-full px-4 py-3 text-left hover:bg-gray-50 focus:bg-gray-50 focus:outline-none transition-colors ${
                            selectedIndex === index ? 'bg-blue-50' : ''
                          }`}
                        >
                          <div className="flex items-center space-x-3">
                            <div className="flex-shrink-0">
                              <Icon className="h-5 w-5 text-gray-400" />
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center justify-between">
                                <p className="text-sm font-medium text-gray-900 truncate">
                                  {result.title}
                                </p>
                                {result.value && (
                                  <span className="text-sm font-semibold text-gray-700">
                                    {result.value}
                                  </span>
                                )}
                              </div>
                              <p className="text-sm text-gray-500 truncate">
                                {result.description}
                              </p>
                              <div className="flex items-center justify-between mt-1">
                                <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${getCategoryColor(result.category)}`}>
                                  {result.category}
                                </span>
                                <span className="text-xs text-gray-400">
                                  {Math.round(result.relevance * 100)}% match
                                </span>
                              </div>
                            </div>
                          </div>
                        </motion.button>
                      )
                    })}
                  </div>
                ) : (
                  <div className="px-4 py-8 text-center">
                    <MagnifyingGlassIcon className="h-8 w-8 text-gray-300 mx-auto mb-2" />
                    <p className="text-sm text-gray-500">No results found</p>
                    <p className="text-xs text-gray-400 mt-1">
                      Try searching for entities, metrics, or ask the AI
                    </p>
                  </div>
                )}
              </div>
            ) : (
              // Suggestions
              <div className="py-2">
                <div className="px-4 py-2 text-xs font-medium text-gray-500 uppercase tracking-wider border-b border-gray-100">
                  Suggestions
                </div>
                {suggestions.map((suggestion, index) => {
                  const Icon = suggestion.icon
                  return (
                    <motion.button
                      key={suggestion.id}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.05 }}
                      onClick={() => handleSuggestionClick(suggestion)}
                      className={`w-full px-4 py-3 text-left hover:bg-gray-50 focus:bg-gray-50 focus:outline-none transition-colors ${
                        selectedIndex === index ? 'bg-blue-50' : ''
                      }`}
                    >
                      <div className="flex items-center space-x-3">
                        <div className="flex-shrink-0">
                          <Icon className={`h-4 w-4 ${
                            suggestion.type === 'ai' ? 'text-yellow-500' :
                            suggestion.type === 'trending' ? 'text-green-500' :
                            'text-gray-400'
                          }`} />
                        </div>
                        <div className="flex-1">
                          <p className="text-sm text-gray-900">{suggestion.text}</p>
                        </div>
                        <div className="flex-shrink-0">
                          <span className={`text-xs px-2 py-1 rounded-full ${
                            suggestion.type === 'ai' ? 'bg-yellow-100 text-yellow-700' :
                            suggestion.type === 'trending' ? 'bg-green-100 text-green-700' :
                            'bg-gray-100 text-gray-600'
                          }`}>
                            {suggestion.type === 'ai' ? 'AI' : 
                             suggestion.type === 'trending' ? 'Trending' : 'Recent'}
                          </span>
                        </div>
                      </div>
                    </motion.button>
                  )
                })}
                
                {/* Quick Actions */}
                <div className="border-t border-gray-100 mt-2 pt-2">
                  <div className="px-4 py-2 text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Quick Actions
                  </div>
                  <button
                    onClick={() => {
                      setQuery('Show me cash optimization opportunities')
                      setIsOpen(false)
                    }}
                    className="w-full px-4 py-2 text-left hover:bg-gray-50 focus:bg-gray-50 focus:outline-none transition-colors"
                  >
                    <div className="flex items-center space-x-3">
                      <SparklesIcon className="h-4 w-4 text-blue-500" />
                      <span className="text-sm text-gray-900">Ask AI for insights</span>
                    </div>
                  </button>
                </div>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  )
}