'use client'

import { useEffect, useRef, useState, useCallback } from 'react'
import { 
  ArrowPathIcon, 
  ArrowsPointingOutIcon,
  FunnelIcon,
  ShareIcon,
  CloudArrowDownIcon,
  DocumentArrowDownIcon,
  PhotoIcon,
  ChartBarIcon,
  BellIcon,
  EyeIcon,
  CogIcon,
  SparklesIcon,
  RocketLaunchIcon,
  LightBulbIcon
} from '@heroicons/react/24/outline'
import tableauService, { 
  TableauWorkbook, 
  TableauView, 
  TableauInsights, 
  TableauUsageMetrics,
  TreasuryDashboardConfig 
} from '@/lib/tableau'
import { useTreasuryStore } from '@/store/treasuryStore'

declare global {
  interface Window {
    tableau: any
  }
}

interface DashboardFilter {
  entity: string[]
  currency: string[]
  dateRange: { start: string; end: string }
  riskLevel: string[]
  accountType: string[]
}

export default function EnhancedTableauDashboard() {
  const vizRef = useRef<HTMLDivElement>(null)
  const [viz, setViz] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [workbooks, setWorkbooks] = useState<TableauWorkbook[]>([])
  const [views, setViews] = useState<TableauView[]>([])
  const [selectedWorkbook, setSelectedWorkbook] = useState<TableauWorkbook | null>(null)
  const [selectedView, setSelectedView] = useState<TableauView | null>(null)
  const [refreshing, setRefreshing] = useState(false)
  const [exporting, setExporting] = useState(false)
  const [insights, setInsights] = useState<TableauInsights | null>(null)
  const [usageMetrics, setUsageMetrics] = useState<TableauUsageMetrics | null>(null)
  const [showInsights, setShowInsights] = useState(false)
  const [showMetrics, setShowMetrics] = useState(false)
  const [creatingDashboard, setCreatingDashboard] = useState(false)
  const [streamingData, setStreamingData] = useState(false)
  const { addAlert } = useTreasuryStore()
  
  const [filters, setFilters] = useState<DashboardFilter>({
    entity: [],
    currency: ['USD'],
    dateRange: { 
      start: new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      end: new Date().toISOString().split('T')[0]
    },
    riskLevel: [],
    accountType: []
  })

  // Load Tableau data on component mount
  useEffect(() => {
    loadTableauData()
  }, [])

  // Load workbooks and views from Tableau Server
  const loadTableauData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Authenticate and load workbooks
      await tableauService.authenticate()
      const [workbooksData, viewsData] = await Promise.all([
        tableauService.getWorkbooks(),
        tableauService.getViews()
      ])
      
      setWorkbooks(workbooksData)
      setViews(viewsData)
      
      // Select first workbook and view by default
      if (workbooksData.length > 0) {
        setSelectedWorkbook(workbooksData[0])
        const workbookViews = viewsData.filter(view => view.workbook.id === workbooksData[0].id)
        if (workbookViews.length > 0) {
          setSelectedView(workbookViews[0])
        }
      }

      addAlert({
        type: 'success',
        title: 'Tableau Connected',
        message: `Successfully loaded ${workbooksData.length} workbooks and ${viewsData.length} views`
      })

    } catch (err: any) {
      console.error('Error loading Tableau data:', err)
      setError(err.message || 'Failed to connect to Tableau Server')
      addAlert({
        type: 'error',
        title: 'Tableau Connection Failed',
        message: err.message || 'Failed to connect to Tableau Server'
      })
    } finally {
      setLoading(false)
    }
  }

  // Initialize Tableau visualization
  useEffect(() => {
    if (selectedView && !loading) {
      initializeViz()
    }
  }, [selectedView, loading])

  const initializeViz = useCallback(() => {
    if (!vizRef.current || !selectedView) return

    try {
      // Dispose existing viz
      if (viz) {
        viz.dispose()
        setViz(null)
      }

      // Load Tableau JavaScript API if not already loaded
      if (!window.tableau) {
        const script = document.createElement('script')
        script.src = 'https://public.tableau.com/javascripts/api/tableau-2.min.js'
        script.onload = () => createViz()
        script.onerror = () => {
          setError('Failed to load Tableau JavaScript API')
        }
        document.head.appendChild(script)
      } else {
        createViz()
      }

    } catch (err: any) {
      console.error('Error initializing viz:', err)
      setError('Failed to initialize Tableau visualization')
    }
  }, [selectedView, viz])

  const createViz = () => {
    if (!vizRef.current || !selectedView || !window.tableau) return

    try {
      const embedConfig = tableauService.getEmbedConfig()
      const embedUrl = tableauService.generateEmbedUrl(selectedView.id, {
        showTabs: true,
        showToolbar: true,
        showShareOptions: false
      })

      const options = {
        hideTabs: false,
        hideToolbar: false,
        width: '100%',
        height: '700px',
        onFirstInteractive: () => {
          console.log('Tableau viz loaded successfully')
          addAlert({
            type: 'success',
            title: 'Dashboard Loaded',
            message: `${selectedView.name} is ready for interaction`
          })
          
          // Load insights and metrics after viz is ready
          loadInsightsAndMetrics()
        }
      }

      // Clear container
      vizRef.current.innerHTML = ''
      
      // Create new viz
      const newViz = new window.tableau.Viz(vizRef.current, embedUrl, options)
      setViz(newViz)

    } catch (err: any) {
      console.error('Error creating viz:', err)
      setError('Failed to create Tableau visualization')
      
      // Show enhanced fallback content
      showFallbackDashboard()
    }
  }

  const showFallbackDashboard = () => {
    if (!vizRef.current || !selectedView) return
    
    vizRef.current.innerHTML = `
      <div class="flex items-center justify-center h-96 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 rounded-lg border-2 border-dashed border-blue-300">
        <div class="text-center max-w-md">
          <div class="w-20 h-20 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center mx-auto mb-6 shadow-lg">
            <svg class="w-10 h-10 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z"/>
            </svg>
          </div>
          <h3 class="text-xl font-bold text-gray-900 mb-3">${selectedView.name}</h3>
          <p class="text-gray-600 mb-4">Advanced Treasury Analytics Dashboard</p>
          <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
            <div class="flex items-center">
              <svg class="w-5 h-5 text-yellow-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
              </svg>
              <span class="text-sm font-medium text-yellow-800">Interactive dashboard temporarily unavailable</span>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4 text-sm">
            <div class="bg-white rounded-lg p-3 shadow-sm">
              <div class="font-semibold text-blue-600">Cash Position</div>
              <div class="text-gray-600">$2.4B Total</div>
            </div>
            <div class="bg-white rounded-lg p-3 shadow-sm">
              <div class="font-semibold text-green-600">FX Exposure</div>
              <div class="text-gray-600">€180M EUR</div>
            </div>
            <div class="bg-white rounded-lg p-3 shadow-sm">
              <div class="font-semibold text-purple-600">Risk Score</div>
              <div class="text-gray-600">Medium (7.2)</div>
            </div>
            <div class="bg-white rounded-lg p-3 shadow-sm">
              <div class="font-semibold text-orange-600">Liquidity</div>
              <div class="text-gray-600">98.5% Ratio</div>
            </div>
          </div>
          <div class="mt-4 text-xs text-gray-500">
            Check Tableau Server connection and permissions
          </div>
        </div>
      </div>
    `
  }

  const loadInsightsAndMetrics = async () => {
    if (!selectedWorkbook) return
    
    try {
      const [insightsData, metricsData] = await Promise.all([
        tableauService.getTreasuryInsights(selectedWorkbook.id),
        tableauService.getDashboardUsageMetrics(selectedWorkbook.id, 30)
      ])
      
      setInsights(insightsData)
      setUsageMetrics(metricsData)
    } catch (error) {
      console.error('Failed to load insights and metrics:', error)
    }
  }

  const refreshData = async () => {
    if (!selectedView) return
    
    setRefreshing(true)
    try {
      // Refresh the current visualization
      if (viz) {
        await viz.refreshDataAsync()
        addAlert({
          type: 'success',
          title: 'Data Refreshed',
          message: 'Dashboard data has been updated successfully'
        })
      } else {
        // Reload the entire dashboard
        await loadTableauData()
      }
      
      // Reload insights and metrics
      await loadInsightsAndMetrics()
    } catch (err: any) {
      console.error('Error refreshing data:', err)
      addAlert({
        type: 'error',
        title: 'Refresh Failed',
        message: err.message || 'Failed to refresh dashboard data'
      })
    } finally {
      setRefreshing(false)
    }
  }

  const applyAdvancedFilters = async () => {
    if (!selectedView) return
    
    try {
      await tableauService.applyAdvancedFilters(selectedView.id, filters)
      
      addAlert({
        type: 'success',
        title: 'Advanced Filters Applied',
        message: 'Dashboard filters have been updated with treasury-specific criteria'
      })
      
    } catch (err: any) {
      console.error('Failed to apply advanced filters:', err)
      addAlert({
        type: 'error',
        title: 'Filter Error',
        message: 'Failed to apply advanced filters to the dashboard'
      })
    }
  }

  const exportData = async (format: 'PDF' | 'PNG' | 'CSV') => {
    if (!selectedView || !selectedWorkbook) return
    
    setExporting(true)
    try {
      let blob: Blob
      let filename: string
      let mimeType: string

      switch (format) {
        case 'PDF':
          blob = await tableauService.exportWorkbookPDF(selectedWorkbook.id, {
            pageType: 'A4',
            pageOrientation: 'Landscape'
          })
          filename = `TreasuryIQ_${selectedWorkbook.name}_${new Date().toISOString().split('T')[0]}.pdf`
          mimeType = 'application/pdf'
          break
          
        case 'PNG':
          blob = await tableauService.exportViewImage(selectedView.id, {
            resolution: 'high'
          })
          filename = `TreasuryIQ_${selectedView.name}_${new Date().toISOString().split('T')[0]}.png`
          mimeType = 'image/png'
          break
          
        case 'CSV':
          blob = await tableauService.exportViewCSV(selectedView.id)
          filename = `TreasuryIQ_${selectedView.name}_${new Date().toISOString().split('T')[0]}.csv`
          mimeType = 'text/csv'
          break
          
        default:
          throw new Error('Unsupported export format')
      }

      // Download the file
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)

      addAlert({
        type: 'success',
        title: 'Export Complete',
        message: `Treasury dashboard exported as ${format} successfully`
      })

    } catch (err: any) {
      console.error('Export failed:', err)
      addAlert({
        type: 'error',
        title: 'Export Failed',
        message: err.message || `Failed to export dashboard as ${format}`
      })
    } finally {
      setExporting(false)
    }
  }

  const createTreasuryDashboard = async () => {
    setCreatingDashboard(true)
    try {
      const config: TreasuryDashboardConfig = {
        name: `TreasuryIQ Dashboard ${new Date().toLocaleDateString()}`,
        project_id: 'default',
        data_sources: ['treasury_data', 'market_data', 'risk_data'],
        views: [
          { name: 'Cash Position Overview', type: 'cash_position' },
          { name: 'FX Risk Analysis', type: 'fx_risk' },
          { name: 'Liquidity Forecast', type: 'liquidity' },
          { name: 'Compliance Dashboard', type: 'compliance' }
        ],
        filters: filters,
        refresh_schedule: 'hourly'
      }

      const result = await tableauService.createTreasuryDashboard(config)
      
      addAlert({
        type: 'success',
        title: 'Dashboard Created',
        message: `New treasury dashboard "${result.workbook_name}" created successfully`
      })

      // Reload workbooks to include the new one
      await loadTableauData()
      
    } catch (err: any) {
      console.error('Failed to create treasury dashboard:', err)
      addAlert({
        type: 'error',
        title: 'Creation Failed',
        message: err.message || 'Failed to create treasury dashboard'
      })
    } finally {
      setCreatingDashboard(false)
    }
  }

  const startDataStreaming = async () => {
    if (!selectedView) return
    
    setStreamingData(true)
    try {
      // Simulate real-time data streaming
      const dataStream = async function* () {
        for (let i = 0; i < 10; i++) {
          yield {
            cash_positions: [
              {
                date: new Date().toISOString(),
                entity: 'US Headquarters',
                currency: 'USD',
                balance: Math.random() * 1000000000,
                account_type: 'Operating'
              }
            ],
            fx_rates: [
              {
                date: new Date().toISOString(),
                base_currency: 'USD',
                target_currency: 'EUR',
                rate: 0.85 + Math.random() * 0.1
              }
            ]
          }
          await new Promise(resolve => setTimeout(resolve, 2000))
        }
      }

      // Start streaming (this would use a real data source ID in production)
      await tableauService.streamTreasuryData('demo_datasource', dataStream())
      
      addAlert({
        type: 'success',
        title: 'Data Streaming Complete',
        message: 'Real-time treasury data has been streamed to Tableau'
      })
      
    } catch (err: any) {
      console.error('Data streaming failed:', err)
      addAlert({
        type: 'error',
        title: 'Streaming Failed',
        message: err.message || 'Failed to stream treasury data'
      })
    } finally {
      setStreamingData(false)
    }
  }

  const handleWorkbookChange = (workbook: TableauWorkbook) => {
    setSelectedWorkbook(workbook)
    
    // Find views for this workbook
    const workbookViews = views.filter(view => view.workbook.id === workbook.id)
    if (workbookViews.length > 0) {
      setSelectedView(workbookViews[0])
    } else {
      setSelectedView(null)
    }
  }

  const handleViewChange = (view: TableauView) => {
    setSelectedView(view)
  }

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (viz) {
        viz.dispose()
      }
    }
  }, [viz])

  return (
    <div className="space-y-6">
      {/* Enhanced Header */}
      <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 rounded-xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold mb-2">TreasuryIQ Analytics Hub</h2>
            <p className="text-blue-100 text-lg">
              Advanced Tableau integration with AI-powered insights and real-time streaming
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={createTreasuryDashboard}
              disabled={creatingDashboard}
              className="bg-white/20 hover:bg-white/30 text-white px-4 py-2 rounded-lg transition-colors flex items-center space-x-2"
            >
              <RocketLaunchIcon className={`h-5 w-5 ${creatingDashboard ? 'animate-pulse' : ''}`} />
              <span>{creatingDashboard ? 'Creating...' : 'Create Dashboard'}</span>
            </button>
            <button
              onClick={loadTableauData}
              disabled={loading}
              className="bg-white/20 hover:bg-white/30 text-white px-4 py-2 rounded-lg transition-colors flex items-center space-x-2"
            >
              <ArrowPathIcon className={`h-5 w-5 ${loading ? 'animate-spin' : ''}`} />
              <span>Reconnect</span>
            </button>
          </div>
        </div>
      </div>

      {/* Workbook and View Selector */}
      {workbooks.length > 0 && (
        <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                Select Workbook
              </label>
              <select
                value={selectedWorkbook?.id || ''}
                onChange={(e) => {
                  const workbook = workbooks.find(w => w.id === e.target.value)
                  if (workbook) handleWorkbookChange(workbook)
                }}
                className="w-full border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
              >
                {workbooks.map((workbook) => (
                  <option key={workbook.id} value={workbook.id}>
                    {workbook.name}
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                Select View
              </label>
              <select
                value={selectedView?.id || ''}
                onChange={(e) => {
                  const view = views.find(v => v.id === e.target.value)
                  if (view) handleViewChange(view)
                }}
                className="w-full border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                disabled={!selectedWorkbook}
              >
                {views
                  .filter(view => !selectedWorkbook || view.workbook.id === selectedWorkbook.id)
                  .map((view) => (
                    <option key={view.id} value={view.id}>
                      {view.name}
                    </option>
                  ))}
              </select>
            </div>
          </div>
          
          {selectedWorkbook && (
            <div className="mt-6 p-4 bg-gradient-to-r from-gray-50 to-blue-50 rounded-lg border border-gray-200">
              <h4 className="font-semibold text-gray-900 text-lg">{selectedWorkbook.name}</h4>
              <p className="text-sm text-gray-600 mt-1">
                {selectedWorkbook.description || 'Advanced treasury analytics and reporting dashboard'}
              </p>
              <div className="flex items-center space-x-6 mt-3 text-xs text-gray-500">
                <span className="flex items-center">
                  <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                  Project: {selectedWorkbook.project.name}
                </span>
                <span className="flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  Owner: {selectedWorkbook.owner.name}
                </span>
                <span className="flex items-center">
                  <span className="w-2 h-2 bg-purple-500 rounded-full mr-2"></span>
                  Updated: {new Date(selectedWorkbook.updatedAt).toLocaleDateString()}
                </span>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Advanced Controls */}
      <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Advanced Controls</h3>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowInsights(!showInsights)}
              className={`p-2 rounded-lg transition-colors ${showInsights ? 'bg-blue-100 text-blue-600' : 'text-gray-400 hover:text-gray-600'}`}
              title="AI Insights"
            >
              <SparklesIcon className="h-5 w-5" />
            </button>
            <button
              onClick={() => setShowMetrics(!showMetrics)}
              className={`p-2 rounded-lg transition-colors ${showMetrics ? 'bg-green-100 text-green-600' : 'text-gray-400 hover:text-gray-600'}`}
              title="Usage Metrics"
            >
              <ChartBarIcon className="h-5 w-5" />
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Filters */}
          <div className="lg:col-span-2">
            <div className="flex items-center space-x-4 mb-4">
              <FunnelIcon className="h-5 w-5 text-gray-400" />
              <span className="font-medium text-gray-700">Treasury Filters</span>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Entity</label>
                <select
                  multiple
                  value={filters.entity}
                  onChange={(e) => setFilters({ 
                    ...filters, 
                    entity: Array.from(e.target.selectedOptions, option => option.value)
                  })}
                  className="w-full text-xs border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  size={3}
                >
                  <option value="US">US Headquarters</option>
                  <option value="EU">Europe Ltd.</option>
                  <option value="APAC">Asia Pacific</option>
                  <option value="CA">Canada Corp.</option>
                  <option value="JP">Japan KK</option>
                </select>
              </div>
              
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Currency</label>
                <select
                  multiple
                  value={filters.currency}
                  onChange={(e) => setFilters({ 
                    ...filters, 
                    currency: Array.from(e.target.selectedOptions, option => option.value)
                  })}
                  className="w-full text-xs border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  size={3}
                >
                  <option value="USD">USD</option>
                  <option value="EUR">EUR</option>
                  <option value="GBP">GBP</option>
                  <option value="JPY">JPY</option>
                  <option value="CAD">CAD</option>
                </select>
              </div>
              
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Risk Level</label>
                <select
                  multiple
                  value={filters.riskLevel}
                  onChange={(e) => setFilters({ 
                    ...filters, 
                    riskLevel: Array.from(e.target.selectedOptions, option => option.value)
                  })}
                  className="w-full text-xs border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  size={3}
                >
                  <option value="Low">Low</option>
                  <option value="Medium">Medium</option>
                  <option value="High">High</option>
                  <option value="Critical">Critical</option>
                </select>
              </div>
              
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Account Type</label>
                <select
                  multiple
                  value={filters.accountType}
                  onChange={(e) => setFilters({ 
                    ...filters, 
                    accountType: Array.from(e.target.selectedOptions, option => option.value)
                  })}
                  className="w-full text-xs border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  size={3}
                >
                  <option value="Operating">Operating</option>
                  <option value="Investment">Investment</option>
                  <option value="Savings">Savings</option>
                  <option value="Credit">Credit Line</option>
                </select>
              </div>
            </div>
            
            <div className="mt-4 flex items-center space-x-3">
              <button
                onClick={applyAdvancedFilters}
                disabled={!selectedView}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 text-sm font-medium"
              >
                Apply Advanced Filters
              </button>
              
              <button
                onClick={startDataStreaming}
                disabled={streamingData || !selectedView}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50 text-sm font-medium flex items-center space-x-2"
              >
                <ArrowPathIcon className={`h-4 w-4 ${streamingData ? 'animate-spin' : ''}`} />
                <span>{streamingData ? 'Streaming...' : 'Stream Data'}</span>
              </button>
            </div>
          </div>

          {/* Actions */}
          <div>
            <div className="flex items-center space-x-4 mb-4">
              <CogIcon className="h-5 w-5 text-gray-400" />
              <span className="font-medium text-gray-700">Actions</span>
            </div>
            
            <div className="space-y-3">
              <button
                onClick={refreshData}
                disabled={refreshing || !selectedView}
                className="w-full flex items-center justify-center space-x-2 p-3 text-gray-600 hover:text-gray-800 hover:bg-gray-50 rounded-lg transition-colors disabled:opacity-50"
              >
                <ArrowPathIcon className={`h-5 w-5 ${refreshing ? 'animate-spin' : ''}`} />
                <span>Refresh Data</span>
              </button>

              <div className="grid grid-cols-3 gap-2">
                <button
                  onClick={() => exportData('PDF')}
                  disabled={exporting || !selectedView}
                  className="flex flex-col items-center justify-center p-3 text-gray-600 hover:text-gray-800 hover:bg-gray-50 rounded-lg transition-colors disabled:opacity-50"
                  title="Export as PDF"
                >
                  <DocumentArrowDownIcon className="h-5 w-5 mb-1" />
                  <span className="text-xs">PDF</span>
                </button>
                <button
                  onClick={() => exportData('PNG')}
                  disabled={exporting || !selectedView}
                  className="flex flex-col items-center justify-center p-3 text-gray-600 hover:text-gray-800 hover:bg-gray-50 rounded-lg transition-colors disabled:opacity-50"
                  title="Export as Image"
                >
                  <PhotoIcon className="h-5 w-5 mb-1" />
                  <span className="text-xs">PNG</span>
                </button>
                <button
                  onClick={() => exportData('CSV')}
                  disabled={exporting || !selectedView}
                  className="flex flex-col items-center justify-center p-3 text-gray-600 hover:text-gray-800 hover:bg-gray-50 rounded-lg transition-colors disabled:opacity-50"
                  title="Export Data as CSV"
                >
                  <CloudArrowDownIcon className="h-5 w-5 mb-1" />
                  <span className="text-xs">CSV</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* AI Insights Panel */}
      {showInsights && insights && (
        <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl border border-purple-200 p-6">
          <div className="flex items-center space-x-3 mb-4">
            <SparklesIcon className="h-6 w-6 text-purple-600" />
            <h3 className="text-lg font-semibold text-gray-900">AI-Powered Treasury Insights</h3>
            <span className="px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded-full">
              {Math.round(insights.confidence * 100)}% Confidence
            </span>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                <LightBulbIcon className="h-4 w-4 text-yellow-500 mr-2" />
                Key Findings
              </h4>
              <ul className="space-y-2">
                {insights.key_findings.map((finding, index) => (
                  <li key={index} className="text-sm text-gray-700 flex items-start">
                    <span className="w-2 h-2 bg-blue-500 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                    {finding}
                  </li>
                ))}
              </ul>
            </div>
            
            <div>
              <h4 className="font-medium text-gray-900 mb-2 flex items-center">
                <BellIcon className="h-4 w-4 text-red-500 mr-2" />
                Risk Alerts
              </h4>
              <div className="space-y-2">
                {insights.risk_alerts.map((alert, index) => (
                  <div key={index} className={`p-3 rounded-lg border ${
                    alert.severity === 'High' ? 'bg-red-50 border-red-200' :
                    alert.severity === 'Medium' ? 'bg-yellow-50 border-yellow-200' :
                    'bg-green-50 border-green-200'
                  }`}>
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-sm">{alert.type}</span>
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        alert.severity === 'High' ? 'bg-red-100 text-red-700' :
                        alert.severity === 'Medium' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-green-100 text-green-700'
                      }`}>
                        {alert.severity}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mt-1">{alert.description}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
          
          <div className="mt-4 p-4 bg-white rounded-lg">
            <h4 className="font-medium text-gray-900 mb-2">Summary</h4>
            <p className="text-sm text-gray-700">{insights.summary}</p>
          </div>
        </div>
      )}

      {/* Usage Metrics Panel */}
      {showMetrics && usageMetrics && (
        <div className="bg-gradient-to-r from-green-50 to-teal-50 rounded-xl border border-green-200 p-6">
          <div className="flex items-center space-x-3 mb-4">
            <ChartBarIcon className="h-6 w-6 text-green-600" />
            <h3 className="text-lg font-semibold text-gray-900">Dashboard Usage Analytics</h3>
            <span className={`px-2 py-1 text-xs rounded-full ${
              usageMetrics.engagement_level === 'High' ? 'bg-green-100 text-green-700' :
              usageMetrics.engagement_level === 'Medium' ? 'bg-yellow-100 text-yellow-700' :
              'bg-red-100 text-red-700'
            }`}>
              {usageMetrics.engagement_level} Engagement
            </span>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-blue-600">{usageMetrics.total_views}</div>
              <div className="text-sm text-gray-600">Total Views</div>
            </div>
            <div className="bg-white rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-green-600">{usageMetrics.unique_users}</div>
              <div className="text-sm text-gray-600">Unique Users</div>
            </div>
            <div className="bg-white rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-purple-600">{usageMetrics.avg_daily_views.toFixed(1)}</div>
              <div className="text-sm text-gray-600">Avg Daily Views</div>
            </div>
            <div className="bg-white rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-orange-600">{usageMetrics.popularity_score}%</div>
              <div className="text-sm text-gray-600">Popularity Score</div>
            </div>
          </div>
        </div>
      )}

      {/* Tableau Visualization */}
      <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
        {loading && (
          <div className="flex items-center justify-center h-96">
            <div className="text-center">
              <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-6"></div>
              <span className="text-xl text-gray-600 font-medium">
                {workbooks.length === 0 ? 'Connecting to Tableau Server...' : 'Loading advanced dashboard...'}
              </span>
              <p className="text-sm text-gray-500 mt-2">
                Initializing AI-powered analytics and real-time data streaming
              </p>
            </div>
          </div>
        )}
        
        {error && (
          <div className="flex items-center justify-center h-96">
            <div className="text-center max-w-md">
              <div className="text-red-500 mb-4 text-6xl">⚠️</div>
              <h3 className="text-xl font-semibold text-red-800 mb-3">Connection Error</h3>
              <p className="text-red-600 mb-6">{error}</p>
              <button
                onClick={loadTableauData}
                className="bg-red-600 hover:bg-red-700 text-white px-6 py-3 rounded-lg transition-colors font-medium"
              >
                Retry Connection
              </button>
            </div>
          </div>
        )}
        
        {!loading && !error && selectedView && (
          <div ref={vizRef} className="tableau-viz min-h-96" />
        )}
        
        {!loading && !error && workbooks.length === 0 && (
          <div className="flex items-center justify-center h-96">
            <div className="text-center">
              <div className="text-gray-400 mb-4 text-6xl">📊</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">No Dashboards Found</h3>
              <p className="text-gray-600 mb-6">
                No Tableau workbooks are available in your site. Create your first treasury dashboard!
              </p>
              <button
                onClick={createTreasuryDashboard}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition-colors font-medium mr-3"
              >
                Create Treasury Dashboard
              </button>
              <button
                onClick={loadTableauData}
                className="bg-gray-600 hover:bg-gray-700 text-white px-6 py-3 rounded-lg transition-colors font-medium"
              >
                Refresh
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Enhanced Feature Info */}
      <div className="bg-gradient-to-r from-indigo-50 via-blue-50 to-cyan-50 rounded-xl p-6 border border-indigo-200">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <RocketLaunchIcon className="h-8 w-8 text-indigo-600" />
          </div>
          <div className="ml-4">
            <h3 className="text-lg font-semibold text-indigo-900 mb-3">
              TreasuryIQ Advanced Tableau Integration
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-indigo-800">
              <div>
                <h4 className="font-medium mb-2">🚀 Advanced Features</h4>
                <ul className="space-y-1">
                  <li>• AI-powered treasury insights and recommendations</li>
                  <li>• Real-time data streaming and live updates</li>
                  <li>• Advanced filtering with treasury-specific criteria</li>
                  <li>• Automated dashboard creation and deployment</li>
                  <li>• Usage analytics and engagement tracking</li>
                </ul>
              </div>
              <div>
                <h4 className="font-medium mb-2">💡 Smart Analytics</h4>
                <ul className="space-y-1">
                  <li>• Risk alert monitoring and notifications</li>
                  <li>• Predictive cash flow analysis</li>
                  <li>• FX exposure optimization recommendations</li>
                  <li>• Compliance dashboard automation</li>
                  <li>• Multi-format export with branding</li>
                </ul>
              </div>
            </div>
            {selectedView && (
              <div className="mt-4 p-3 bg-white/60 rounded-lg text-xs">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <strong>Current View:</strong><br/>
                    {selectedView.name}
                  </div>
                  <div>
                    <strong>Workbook:</strong><br/>
                    {selectedView.workbook.name}
                  </div>
                  <div>
                    <strong>Total Views:</strong><br/>
                    {selectedView.usage?.totalViewCount || 0}
                  </div>
                  <div>
                    <strong>Status:</strong><br/>
                    <span className="text-green-600 font-medium">● Active</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}