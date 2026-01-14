'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  DocumentArrowDownIcon,
  DocumentTextIcon,
  TableCellsIcon,
  ChartBarIcon,
  CalendarIcon,
  Cog6ToothIcon,
  XMarkIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline'

interface ExportFormat {
  id: string
  name: string
  description: string
  icon: React.ComponentType<{ className?: string }>
  formats: string[]
  size?: string
}

interface ExportJob {
  id: string
  name: string
  format: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  createdAt: string
  downloadUrl?: string
  error?: string
}

export default function ExportCenter() {
  const [isOpen, setIsOpen] = useState(false)
  const [selectedExport, setSelectedExport] = useState<string>('')
  const [exportJobs, setExportJobs] = useState<ExportJob[]>([])
  const [exportConfig, setExportConfig] = useState({
    dateRange: '1M',
    entities: ['all'],
    includeCharts: true,
    includeRawData: false,
    format: 'pdf'
  })

  const exportOptions: ExportFormat[] = [
    {
      id: 'portfolio-report',
      name: 'Portfolio Report',
      description: 'Comprehensive portfolio analysis with charts and metrics',
      icon: ChartBarIcon,
      formats: ['pdf', 'xlsx', 'pptx'],
      size: '~2-5 MB'
    },
    {
      id: 'risk-analysis',
      name: 'Risk Analysis Report',
      description: 'VaR calculations, stress tests, and risk metrics',
      icon: DocumentTextIcon,
      formats: ['pdf', 'xlsx'],
      size: '~1-3 MB'
    },
    {
      id: 'cash-positions',
      name: 'Cash Positions',
      description: 'Detailed cash allocation and optimization data',
      icon: TableCellsIcon,
      formats: ['xlsx', 'csv'],
      size: '~500 KB'
    },
    {
      id: 'regulatory-report',
      name: 'Regulatory Report',
      description: 'Compliance-ready reports for regulatory submissions',
      icon: DocumentArrowDownIcon,
      formats: ['pdf', 'xml'],
      size: '~1-2 MB'
    }
  ]

  const handleExport = async (exportType: string) => {
    const newJob: ExportJob = {
      id: `job_${Date.now()}`,
      name: exportOptions.find(opt => opt.id === exportType)?.name || 'Export',
      format: exportConfig.format,
      status: 'pending',
      progress: 0,
      createdAt: new Date().toISOString()
    }

    setExportJobs(prev => [newJob, ...prev])
    
    // Simulate export process
    simulateExportProcess(newJob.id)
    setIsOpen(false)
  }

  const simulateExportProcess = async (jobId: string) => {
    // Update to processing
    setExportJobs(prev => prev.map(job => 
      job.id === jobId ? { ...job, status: 'processing' as const } : job
    ))

    // Simulate progress
    for (let progress = 0; progress <= 100; progress += 10) {
      await new Promise(resolve => setTimeout(resolve, 200))
      setExportJobs(prev => prev.map(job => 
        job.id === jobId ? { ...job, progress } : job
      ))
    }

    // Complete the job
    setExportJobs(prev => prev.map(job => 
      job.id === jobId ? { 
        ...job, 
        status: 'completed' as const, 
        downloadUrl: `/api/exports/${jobId}/download`
      } : job
    ))
  }

  const downloadFile = (job: ExportJob) => {
    // In a real app, this would trigger the actual download
    console.log('Downloading:', job.downloadUrl)
    
    // Simulate download
    const link = document.createElement('a')
    link.href = job.downloadUrl || '#'
    link.download = `${job.name.toLowerCase().replace(/\s+/g, '-')}.${job.format}`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const getStatusColor = (status: ExportJob['status']) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-50'
      case 'processing':
        return 'text-blue-600 bg-blue-50'
      case 'failed':
        return 'text-red-600 bg-red-50'
      default:
        return 'text-yellow-600 bg-yellow-50'
    }
  }

  return (
    <>
      {/* Export Button */}
      <button
        onClick={() => setIsOpen(true)}
        className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
      >
        <DocumentArrowDownIcon className="h-4 w-4 mr-2" />
        Export Data
      </button>

      {/* Export Modal */}
      <AnimatePresence>
        {isOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black bg-opacity-50 z-50"
              onClick={() => setIsOpen(false)}
            />
            
            {/* Modal */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="fixed inset-0 z-50 overflow-y-auto"
            >
              <div className="flex min-h-full items-center justify-center p-4">
                <div className="bg-white rounded-xl shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
                  {/* Header */}
                  <div className="px-6 py-4 border-b border-gray-200">
                    <div className="flex items-center justify-between">
                      <h3 className="text-lg font-semibold text-gray-900">
                        Export Treasury Data
                      </h3>
                      <button
                        onClick={() => setIsOpen(false)}
                        className="text-gray-400 hover:text-gray-600"
                      >
                        <XMarkIcon className="h-6 w-6" />
                      </button>
                    </div>
                  </div>

                  <div className="flex h-[600px]">
                    {/* Export Options */}
                    <div className="w-1/2 p-6 border-r border-gray-200">
                      <h4 className="text-sm font-medium text-gray-900 mb-4">
                        Select Report Type
                      </h4>
                      <div className="space-y-3">
                        {exportOptions.map((option) => {
                          const Icon = option.icon
                          return (
                            <motion.button
                              key={option.id}
                              onClick={() => setSelectedExport(option.id)}
                              whileHover={{ scale: 1.02 }}
                              whileTap={{ scale: 0.98 }}
                              className={`w-full p-4 text-left rounded-lg border-2 transition-all ${
                                selectedExport === option.id
                                  ? 'border-blue-500 bg-blue-50'
                                  : 'border-gray-200 hover:border-gray-300'
                              }`}
                            >
                              <div className="flex items-start space-x-3">
                                <Icon className="h-6 w-6 text-blue-600 mt-1" />
                                <div className="flex-1">
                                  <h5 className="font-medium text-gray-900">
                                    {option.name}
                                  </h5>
                                  <p className="text-sm text-gray-600 mt-1">
                                    {option.description}
                                  </p>
                                  <div className="flex items-center justify-between mt-2">
                                    <div className="flex space-x-1">
                                      {option.formats.map(format => (
                                        <span
                                          key={format}
                                          className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800"
                                        >
                                          {format.toUpperCase()}
                                        </span>
                                      ))}
                                    </div>
                                    {option.size && (
                                      <span className="text-xs text-gray-500">
                                        {option.size}
                                      </span>
                                    )}
                                  </div>
                                </div>
                              </div>
                            </motion.button>
                          )
                        })}
                      </div>
                    </div>

                    {/* Configuration */}
                    <div className="w-1/2 p-6">
                      <h4 className="text-sm font-medium text-gray-900 mb-4">
                        Export Configuration
                      </h4>
                      
                      {selectedExport && (
                        <div className="space-y-4">
                          {/* Date Range */}
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Date Range
                            </label>
                            <select
                              value={exportConfig.dateRange}
                              onChange={(e) => setExportConfig(prev => ({ ...prev, dateRange: e.target.value }))}
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                              <option value="1W">Last Week</option>
                              <option value="1M">Last Month</option>
                              <option value="3M">Last 3 Months</option>
                              <option value="6M">Last 6 Months</option>
                              <option value="1Y">Last Year</option>
                              <option value="custom">Custom Range</option>
                            </select>
                          </div>

                          {/* Entities */}
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Entities
                            </label>
                            <select
                              multiple
                              value={exportConfig.entities}
                              onChange={(e) => setExportConfig(prev => ({ 
                                ...prev, 
                                entities: Array.from(e.target.selectedOptions, option => option.value)
                              }))}
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                              <option value="all">All Entities</option>
                              <option value="us-hq">US Headquarters</option>
                              <option value="eu-ltd">Europe Ltd.</option>
                              <option value="apac-pte">Asia Pacific Pte.</option>
                              <option value="ca-corp">Canada Corp.</option>
                            </select>
                          </div>

                          {/* Format */}
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Format
                            </label>
                            <select
                              value={exportConfig.format}
                              onChange={(e) => setExportConfig(prev => ({ ...prev, format: e.target.value }))}
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                              {exportOptions.find(opt => opt.id === selectedExport)?.formats.map(format => (
                                <option key={format} value={format}>
                                  {format.toUpperCase()}
                                </option>
                              ))}
                            </select>
                          </div>

                          {/* Options */}
                          <div className="space-y-2">
                            <label className="flex items-center">
                              <input
                                type="checkbox"
                                checked={exportConfig.includeCharts}
                                onChange={(e) => setExportConfig(prev => ({ ...prev, includeCharts: e.target.checked }))}
                                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                              />
                              <span className="ml-2 text-sm text-gray-700">Include Charts</span>
                            </label>
                            <label className="flex items-center">
                              <input
                                type="checkbox"
                                checked={exportConfig.includeRawData}
                                onChange={(e) => setExportConfig(prev => ({ ...prev, includeRawData: e.target.checked }))}
                                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                              />
                              <span className="ml-2 text-sm text-gray-700">Include Raw Data</span>
                            </label>
                          </div>

                          {/* Export Button */}
                          <button
                            onClick={() => handleExport(selectedExport)}
                            disabled={!selectedExport}
                            className="w-full mt-6 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                          >
                            Generate Export
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Export Jobs Status */}
      {exportJobs.length > 0 && (
        <div className="fixed bottom-4 right-4 w-80 bg-white rounded-lg shadow-lg border border-gray-200 z-40">
          <div className="p-4 border-b border-gray-200">
            <h4 className="font-medium text-gray-900">Export Jobs</h4>
          </div>
          <div className="max-h-64 overflow-y-auto">
            {exportJobs.slice(0, 5).map((job) => (
              <div key={job.id} className="p-3 border-b border-gray-100 last:border-b-0">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="text-sm font-medium text-gray-900">
                      {job.name}
                    </div>
                    <div className="text-xs text-gray-500">
                      {new Date(job.createdAt).toLocaleString()}
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${getStatusColor(job.status)}`}>
                      {job.status}
                    </span>
                    {job.status === 'completed' && (
                      <button
                        onClick={() => downloadFile(job)}
                        className="text-blue-600 hover:text-blue-800"
                      >
                        <DocumentArrowDownIcon className="h-4 w-4" />
                      </button>
                    )}
                  </div>
                </div>
                {job.status === 'processing' && (
                  <div className="mt-2">
                    <div className="w-full bg-gray-200 rounded-full h-1">
                      <div
                        className="bg-blue-600 h-1 rounded-full transition-all duration-300"
                        style={{ width: `${job.progress}%` }}
                      />
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </>
  )
}