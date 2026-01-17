'use client'

import { useEffect, useRef, useState } from 'react'
import { 
  ArrowPathIcon, 
  ArrowsPointingOutIcon,
  FunnelIcon,
  ShareIcon,
  CloudArrowDownIcon,
  DocumentArrowDownIcon,
  PhotoIcon
} from '@heroicons/react/24/outline'
import tableauService, { TableauWorkbook, TableauView } from '@/lib/tableau'
import { useTreasuryStore } from '@/store/treasuryStore'

declare global {
  interface Window {
    tableau: any
  }
}

export default function TableauDashboard() {
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
  const { addAlert } = useTreasuryStore()
  
  const [filters, setFilters] = useState({
    entity: 'All',
    timeRange: '1Y',
    currency: 'USD'
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
      const workbooksData = await tableauService.getWorkbooks()
      const viewsData = await tableauService.getViews()
      
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

  const initializeViz = () => {
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
  }

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
        height: '600px',
        onFirstInteractive: () => {
          console.log('Tableau viz loaded successfully')
          addAlert({
            type: 'success',
            title: 'Dashboard Loaded',
            message: `${selectedView.name} is ready for interaction`
          })
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
      
      // Show fallback content
      if (vizRef.current) {
        vizRef.current.innerHTML = `
          <div class="flex items-center justify-center h-96 bg-gradient-to-br from-blue-50 to-indigo-100 rounded-lg border-2 border-dashed border-blue-300">
            <div class="text-center">
              <div class="w-16 h-16 bg-blue-600 rounded-lg flex items-center justify-center mx-auto mb-4">
                <svg class="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z"/>
                </svg>
              </div>
              <h3 class="text-lg font-medium text-gray-900 mb-2">${selectedView.name}</h3>
              <p class="text-gray-600 mb-4">Tableau Dashboard</p>
              <div class="text-sm text-red-600">
                ⚠️ Unable to load interactive dashboard
              </div>
              <div class="mt-4 text-xs text-gray-500">
                Check Tableau Server connection and permissions
              </div>
            </div>
          </div>
        `
      }
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

  const applyFilters = async () => {
    if (!viz) return
    
    try {
      const workbook = viz.getWorkbook()
      const activeSheet = workbook.getActiveSheet()
      
      // Apply filters based on current filter state
      if (filters.entity !== 'All') {
        await activeSheet.applyFilterAsync('Entity', filters.entity, 'REPLACE')
      }
      
      if (filters.timeRange) {
        await activeSheet.applyFilterAsync('Time Range', filters.timeRange, 'REPLACE')
      }
      
      if (filters.currency !== 'USD') {
        await activeSheet.applyFilterAsync('Currency', filters.currency, 'REPLACE')
      }

      addAlert({
        type: 'success',
        title: 'Filters Applied',
        message: 'Dashboard filters have been updated'
      })
      
    } catch (err: any) {
      console.error('Failed to apply filters:', err)
      addAlert({
        type: 'error',
        title: 'Filter Error',
        message: 'Failed to apply filters to the dashboard'
      })
    }
  }

  const exportData = async (format: 'PDF' | 'PNG' | 'CSV') => {
    if (!selectedView || !selectedWorkbook) return
    
    setExporting(true)
    try {
      let blob: Blob | string
      let filename: string
      let mimeType: string

      switch (format) {
        case 'PDF':
          blob = await tableauService.exportWorkbookPDF(selectedWorkbook.id, {
            pageType: 'A4',
            pageOrientation: 'Landscape'
          })
          filename = `${selectedWorkbook.name}_${new Date().toISOString().split('T')[0]}.pdf`
          mimeType = 'application/pdf'
          break
          
        case 'PNG':
          blob = await tableauService.exportViewImage(selectedView.id, {
            resolution: 'high'
          })
          filename = `${selectedView.name}_${new Date().toISOString().split('T')[0]}.png`
          mimeType = 'image/png'
          break
          
        case 'CSV':
          blob = await tableauService.exportViewCSV(selectedView.id)
          filename = `${selectedView.name}_${new Date().toISOString().split('T')[0]}.csv`
          mimeType = 'text/csv'
          break
          
        default:
          throw new Error('Unsupported export format')
      }

      // Download the file
      if (blob instanceof Blob) {
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = filename
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        URL.revokeObjectURL(url)
      } else {
        // Handle CSV string data
        const csvBlob = new Blob([blob], { type: mimeType })
        const url = URL.createObjectURL(csvBlob)
        const link = document.createElement('a')
        link.href = url
        link.download = filename
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        URL.revokeObjectURL(url)
      }

      addAlert({
        type: 'success',
        title: 'Export Complete',
        message: `Dashboard exported as ${format} successfully`
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
  }, [])

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Tableau Dashboards</h2>
          <p className="text-gray-600 mt-1">
            Interactive business intelligence and analytics
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={loadTableauData}
            disabled={loading}
            className="btn-secondary"
          >
            <ArrowPathIcon className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Reconnect
          </button>
        </div>
      </div>

      {/* Workbook and View Selector */}
      {workbooks.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Workbook
              </label>
              <select
                value={selectedWorkbook?.id || ''}
                onChange={(e) => {
                  const workbook = workbooks.find(w => w.id === e.target.value)
                  if (workbook) handleWorkbookChange(workbook)
                }}
                className="w-full border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              >
                {workbooks.map((workbook) => (
                  <option key={workbook.id} value={workbook.id}>
                    {workbook.name}
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select View
              </label>
              <select
                value={selectedView?.id || ''}
                onChange={(e) => {
                  const view = views.find(v => v.id === e.target.value)
                  if (view) handleViewChange(view)
                }}
                className="w-full border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
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
            <div className="mt-4 p-3 bg-gray-50 rounded-lg">
              <h4 className="font-medium text-gray-900">{selectedWorkbook.name}</h4>
              <p className="text-sm text-gray-600 mt-1">
                {selectedWorkbook.description || 'No description available'}
              </p>
              <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                <span>Project: {selectedWorkbook.project.name}</span>
                <span>Owner: {selectedWorkbook.owner.name}</span>
                <span>Updated: {new Date(selectedWorkbook.updatedAt).toLocaleDateString()}</span>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Controls */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            {/* Filters */}
            <div className="flex items-center space-x-2">
              <FunnelIcon className="h-5 w-5 text-gray-400" />
              <select
                value={filters.entity}
                onChange={(e) => setFilters({ ...filters, entity: e.target.value })}
                className="text-sm border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="All">All Entities</option>
                <option value="US">US Headquarters</option>
                <option value="EU">Europe Ltd.</option>
                <option value="APAC">Asia Pacific</option>
                <option value="CA">Canada Corp.</option>
                <option value="JP">Japan KK</option>
              </select>
              
              <select
                value={filters.timeRange}
                onChange={(e) => setFilters({ ...filters, timeRange: e.target.value })}
                className="text-sm border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="1M">1 Month</option>
                <option value="3M">3 Months</option>
                <option value="6M">6 Months</option>
                <option value="1Y">1 Year</option>
                <option value="2Y">2 Years</option>
              </select>
              
              <select
                value={filters.currency}
                onChange={(e) => setFilters({ ...filters, currency: e.target.value })}
                className="text-sm border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="USD">USD</option>
                <option value="EUR">EUR</option>
                <option value="GBP">GBP</option>
                <option value="JPY">JPY</option>
              </select>
              
              <button
                onClick={applyFilters}
                disabled={!viz}
                className="px-3 py-1 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                Apply
              </button>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            {/* Refresh */}
            <button
              onClick={refreshData}
              disabled={refreshing || !selectedView}
              className="p-2 text-gray-400 hover:text-gray-600 transition-colors disabled:opacity-50"
              title="Refresh Data"
            >
              <ArrowPathIcon className={`h-5 w-5 ${refreshing ? 'animate-spin' : ''}`} />
            </button>

            {/* Fullscreen */}
            <button
              onClick={() => {
                if (viz) {
                  viz.getWorkbook().getActiveSheet().changeSizeAsync({
                    behavior: 'AUTOMATIC'
                  })
                }
              }}
              disabled={!viz}
              className="p-2 text-gray-400 hover:text-gray-600 transition-colors disabled:opacity-50"
              title="Fullscreen"
            >
              <ArrowsPointingOutIcon className="h-5 w-5" />
            </button>

            {/* Export Dropdown */}
            <div className="relative">
              <div className="flex items-center space-x-1">
                <button
                  onClick={() => exportData('PDF')}
                  disabled={exporting || !selectedView}
                  className="p-2 text-gray-400 hover:text-gray-600 transition-colors disabled:opacity-50"
                  title="Export as PDF"
                >
                  <DocumentArrowDownIcon className="h-5 w-5" />
                </button>
                <button
                  onClick={() => exportData('PNG')}
                  disabled={exporting || !selectedView}
                  className="p-2 text-gray-400 hover:text-gray-600 transition-colors disabled:opacity-50"
                  title="Export as Image"
                >
                  <PhotoIcon className="h-5 w-5" />
                </button>
                <button
                  onClick={() => exportData('CSV')}
                  disabled={exporting || !selectedView}
                  className="p-2 text-gray-400 hover:text-gray-600 transition-colors disabled:opacity-50"
                  title="Export Data as CSV"
                >
                  <CloudArrowDownIcon className="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tableau Visualization */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        {loading && (
          <div className="flex items-center justify-center h-96">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <span className="text-lg text-gray-600">
                {workbooks.length === 0 ? 'Connecting to Tableau Server...' : 'Loading dashboard...'}
              </span>
            </div>
          </div>
        )}
        
        {error && (
          <div className="flex items-center justify-center h-96">
            <div className="text-center">
              <div className="text-red-500 mb-2 text-4xl">⚠️</div>
              <h3 className="text-lg font-medium text-red-800 mb-2">Connection Error</h3>
              <p className="text-red-600 mb-4">{error}</p>
              <button
                onClick={loadTableauData}
                className="btn-primary"
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
              <div className="text-gray-400 mb-2 text-4xl">📊</div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Dashboards Found</h3>
              <p className="text-gray-600 mb-4">
                No Tableau workbooks are available in your site
              </p>
              <button
                onClick={loadTableauData}
                className="btn-primary"
              >
                Refresh
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Dashboard Info */}
      <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-blue-800">
              Tableau Integration Features
            </h3>
            <div className="mt-2 text-sm text-blue-700">
              <ul className="list-disc list-inside space-y-1">
                <li>Real-time data refresh from Tableau Server/Cloud</li>
                <li>Interactive filtering and drill-down capabilities</li>
                <li>Export to PDF, PNG, and CSV formats</li>
                <li>Mobile-responsive dashboard viewing</li>
                <li>Role-based access control and data security</li>
                <li>Automatic authentication with Personal Access Token</li>
                <li>Support for multiple workbooks and views</li>
                <li>Advanced visualization and analytics</li>
              </ul>
            </div>
            {selectedView && (
              <div className="mt-3 p-2 bg-blue-100 rounded text-xs">
                <strong>Current View:</strong> {selectedView.name}<br/>
                <strong>Workbook:</strong> {selectedView.workbook.name}<br/>
                <strong>Total Views:</strong> {selectedView.usage?.totalViewCount || 0}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}