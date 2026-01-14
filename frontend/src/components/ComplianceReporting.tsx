'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  DocumentCheckIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ArrowDownTrayIcon,
  CalendarIcon,
  ChartBarIcon,
  ShieldCheckIcon
} from '@heroicons/react/24/outline'
import { formatDate, formatDateTime } from '@/lib/utils'

interface ComplianceReport {
  id: string
  name: string
  type: 'regulatory' | 'internal' | 'audit'
  frequency: 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'annual'
  status: 'compliant' | 'warning' | 'non_compliant' | 'pending'
  lastGenerated: string
  nextDue: string
  description: string
  requirements: string[]
  metrics: {
    name: string
    value: number
    threshold: number
    status: 'pass' | 'warning' | 'fail'
    unit: string
  }[]
  documents: {
    name: string
    url: string
    generatedAt: string
    size: string
  }[]
}

interface ComplianceFramework {
  id: string
  name: string
  description: string
  reports: string[]
  compliance: number
  lastAssessment: string
}

export default function ComplianceReporting() {
  const [reports, setReports] = useState<ComplianceReport[]>([])
  const [frameworks, setFrameworks] = useState<ComplianceFramework[]>([])
  const [selectedReport, setSelectedReport] = useState<ComplianceReport | null>(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'overview' | 'reports' | 'frameworks'>('overview')

  useEffect(() => {
    // Mock compliance data
    const mockReports: ComplianceReport[] = [
      {
        id: 'sox_404',
        name: 'SOX 404 Internal Controls',
        type: 'regulatory',
        frequency: 'quarterly',
        status: 'compliant',
        lastGenerated: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
        nextDue: new Date(Date.now() + 85 * 24 * 60 * 60 * 1000).toISOString(),
        description: 'Sarbanes-Oxley Section 404 internal control assessment',
        requirements: [
          'Document key financial processes',
          'Test control effectiveness',
          'Management assessment',
          'External auditor attestation'
        ],
        metrics: [
          { name: 'Control Deficiencies', value: 0, threshold: 0, status: 'pass', unit: 'count' },
          { name: 'Material Weaknesses', value: 0, threshold: 0, status: 'pass', unit: 'count' },
          { name: 'Process Coverage', value: 98.5, threshold: 95, status: 'pass', unit: '%' }
        ],
        documents: [
          { name: 'Q4_2024_SOX_Report.pdf', url: '/reports/sox_q4_2024.pdf', generatedAt: new Date().toISOString(), size: '2.3 MB' }
        ]
      },
      {
        id: 'basel_iii',
        name: 'Basel III Capital Requirements',
        type: 'regulatory',
        frequency: 'monthly',
        status: 'warning',
        lastGenerated: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
        nextDue: new Date(Date.now() + 28 * 24 * 60 * 60 * 1000).toISOString(),
        description: 'Basel III capital adequacy and liquidity requirements',
        requirements: [
          'Common Equity Tier 1 ratio ≥ 4.5%',
          'Tier 1 capital ratio ≥ 6%',
          'Total capital ratio ≥ 8%',
          'Liquidity Coverage Ratio ≥ 100%'
        ],
        metrics: [
          { name: 'CET1 Ratio', value: 12.8, threshold: 4.5, status: 'pass', unit: '%' },
          { name: 'Tier 1 Ratio', value: 14.2, threshold: 6, status: 'pass', unit: '%' },
          { name: 'LCR', value: 98.5, threshold: 100, status: 'warning', unit: '%' }
        ],
        documents: [
          { name: 'Basel_III_Dec_2024.xlsx', url: '/reports/basel_dec_2024.xlsx', generatedAt: new Date().toISOString(), size: '1.8 MB' }
        ]
      },
      {
        id: 'ifrs_9',
        name: 'IFRS 9 Expected Credit Loss',
        type: 'regulatory',
        frequency: 'quarterly',
        status: 'compliant',
        lastGenerated: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString(),
        nextDue: new Date(Date.now() + 76 * 24 * 60 * 60 * 1000).toISOString(),
        description: 'IFRS 9 expected credit loss calculation and reporting',
        requirements: [
          'Stage 1: 12-month ECL',
          'Stage 2: Lifetime ECL',
          'Stage 3: Credit-impaired assets',
          'Forward-looking information'
        ],
        metrics: [
          { name: 'ECL Coverage Ratio', value: 1.2, threshold: 1.0, status: 'pass', unit: '%' },
          { name: 'Stage 2 Assets', value: 3.8, threshold: 5.0, status: 'pass', unit: '%' },
          { name: 'Model Accuracy', value: 94.2, threshold: 90, status: 'pass', unit: '%' }
        ],
        documents: [
          { name: 'IFRS9_Q4_2024.pdf', url: '/reports/ifrs9_q4_2024.pdf', generatedAt: new Date().toISOString(), size: '3.1 MB' }
        ]
      },
      {
        id: 'aml_kyc',
        name: 'AML/KYC Compliance',
        type: 'regulatory',
        frequency: 'monthly',
        status: 'compliant',
        lastGenerated: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
        nextDue: new Date(Date.now() + 29 * 24 * 60 * 60 * 1000).toISOString(),
        description: 'Anti-Money Laundering and Know Your Customer compliance',
        requirements: [
          'Customer due diligence',
          'Transaction monitoring',
          'Suspicious activity reporting',
          'Record keeping'
        ],
        metrics: [
          { name: 'KYC Completion', value: 99.8, threshold: 95, status: 'pass', unit: '%' },
          { name: 'SAR Filings', value: 12, threshold: 50, status: 'pass', unit: 'count' },
          { name: 'Alert Resolution Time', value: 2.3, threshold: 5, status: 'pass', unit: 'days' }
        ],
        documents: [
          { name: 'AML_Report_Dec_2024.pdf', url: '/reports/aml_dec_2024.pdf', generatedAt: new Date().toISOString(), size: '1.5 MB' }
        ]
      }
    ]

    const mockFrameworks: ComplianceFramework[] = [
      {
        id: 'sox',
        name: 'Sarbanes-Oxley Act',
        description: 'US federal law for corporate financial reporting and governance',
        reports: ['sox_404'],
        compliance: 100,
        lastAssessment: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString()
      },
      {
        id: 'basel',
        name: 'Basel III',
        description: 'International regulatory framework for banks',
        reports: ['basel_iii'],
        compliance: 95,
        lastAssessment: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString()
      },
      {
        id: 'ifrs',
        name: 'IFRS Standards',
        description: 'International Financial Reporting Standards',
        reports: ['ifrs_9'],
        compliance: 100,
        lastAssessment: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString()
      },
      {
        id: 'aml',
        name: 'AML/BSA',
        description: 'Anti-Money Laundering and Bank Secrecy Act',
        reports: ['aml_kyc'],
        compliance: 98,
        lastAssessment: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString()
      }
    ]

    setReports(mockReports)
    setFrameworks(mockFrameworks)
    setLoading(false)
  }, [])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'compliant':
      case 'pass':
        return 'text-green-600 bg-green-50 border-green-200'
      case 'warning':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200'
      case 'non_compliant':
      case 'fail':
        return 'text-red-600 bg-red-50 border-red-200'
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'compliant':
      case 'pass':
        return <CheckCircleIcon className="h-4 w-4" />
      case 'warning':
        return <ExclamationTriangleIcon className="h-4 w-4" />
      case 'non_compliant':
      case 'fail':
        return <ExclamationTriangleIcon className="h-4 w-4" />
      default:
        return <ClockIcon className="h-4 w-4" />
    }
  }

  const generateReport = (reportId: string) => {
    // Simulate report generation
    console.log('Generating report:', reportId)
    // In a real app, this would trigger the backend to generate the report
  }

  const downloadDocument = (document: any) => {
    // Simulate document download
    console.log('Downloading:', document.name)
    // In a real app, this would download the actual file
  }

  const renderOverview = () => (
    <div className="space-y-6">
      {/* Compliance Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center">
            <CheckCircleIcon className="h-8 w-8 text-green-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-green-800">Compliant</p>
              <p className="text-2xl font-bold text-green-900">
                {reports.filter(r => r.status === 'compliant').length}
              </p>
            </div>
          </div>
        </div>
        
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-center">
            <ExclamationTriangleIcon className="h-8 w-8 text-yellow-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-yellow-800">Warnings</p>
              <p className="text-2xl font-bold text-yellow-900">
                {reports.filter(r => r.status === 'warning').length}
              </p>
            </div>
          </div>
        </div>
        
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <ExclamationTriangleIcon className="h-8 w-8 text-red-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-red-800">Non-Compliant</p>
              <p className="text-2xl font-bold text-red-900">
                {reports.filter(r => r.status === 'non_compliant').length}
              </p>
            </div>
          </div>
        </div>
        
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center">
            <DocumentCheckIcon className="h-8 w-8 text-blue-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-blue-800">Total Reports</p>
              <p className="text-2xl font-bold text-blue-900">{reports.length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Upcoming Deadlines */}
      <div className="bg-white border border-gray-200 rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h4 className="text-lg font-medium text-gray-900">Upcoming Deadlines</h4>
        </div>
        <div className="divide-y divide-gray-200">
          {reports
            .sort((a, b) => new Date(a.nextDue).getTime() - new Date(b.nextDue).getTime())
            .slice(0, 5)
            .map((report) => (
              <div key={report.id} className="px-6 py-4 flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <CalendarIcon className="h-5 w-5 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">{report.name}</p>
                    <p className="text-xs text-gray-500">{report.frequency} • {report.type}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-900">{formatDate(report.nextDue)}</p>
                  <p className="text-xs text-gray-500">
                    {Math.ceil((new Date(report.nextDue).getTime() - Date.now()) / (1000 * 60 * 60 * 24))} days
                  </p>
                </div>
              </div>
            ))}
        </div>
      </div>
    </div>
  )

  const renderReports = () => (
    <div className="space-y-4">
      {reports.map((report) => (
        <motion.div
          key={report.id}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow cursor-pointer"
          onClick={() => setSelectedReport(report)}
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center space-x-3">
                <h4 className="text-lg font-medium text-gray-900">{report.name}</h4>
                <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(report.status)}`}>
                  {getStatusIcon(report.status)}
                  <span className="ml-1 capitalize">{report.status.replace('_', ' ')}</span>
                </span>
              </div>
              <p className="text-sm text-gray-600 mt-1">{report.description}</p>
              
              <div className="flex items-center space-x-6 mt-3 text-sm text-gray-500">
                <span>Frequency: {report.frequency}</span>
                <span>Last: {formatDate(report.lastGenerated)}</span>
                <span>Next: {formatDate(report.nextDue)}</span>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  generateReport(report.id)
                }}
                className="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
              >
                Generate
              </button>
              {report.documents.length > 0 && (
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    downloadDocument(report.documents[0])
                  }}
                  className="px-3 py-1 text-xs border border-gray-300 text-gray-700 rounded hover:bg-gray-50 transition-colors"
                >
                  <ArrowDownTrayIcon className="h-3 w-3 inline mr-1" />
                  Download
                </button>
              )}
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  )

  const renderFrameworks = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {frameworks.map((framework) => (
        <motion.div
          key={framework.id}
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-white border border-gray-200 rounded-lg p-6"
        >
          <div className="flex items-start justify-between mb-4">
            <div>
              <h4 className="text-lg font-medium text-gray-900">{framework.name}</h4>
              <p className="text-sm text-gray-600 mt-1">{framework.description}</p>
            </div>
            <div className="text-right">
              <div className={`text-2xl font-bold ${framework.compliance >= 95 ? 'text-green-600' : framework.compliance >= 90 ? 'text-yellow-600' : 'text-red-600'}`}>
                {framework.compliance}%
              </div>
              <div className="text-xs text-gray-500">Compliance</div>
            </div>
          </div>
          
          <div className="mb-4">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all duration-300 ${
                  framework.compliance >= 95 ? 'bg-green-500' : 
                  framework.compliance >= 90 ? 'bg-yellow-500' : 'bg-red-500'
                }`}
                style={{ width: `${framework.compliance}%` }}
              />
            </div>
          </div>
          
          <div className="text-sm text-gray-600">
            <p>Reports: {framework.reports.length}</p>
            <p>Last Assessment: {formatDate(framework.lastAssessment)}</p>
          </div>
        </motion.div>
      ))}
    </div>
  )

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Compliance Reporting</h2>
          <p className="text-gray-600 mt-1">Regulatory compliance and risk management</p>
        </div>
        <div className="flex items-center space-x-3">
          <button className="btn-secondary">
            <ShieldCheckIcon className="h-4 w-4 mr-2" />
            Compliance Dashboard
          </button>
          <button className="btn-primary">
            <DocumentCheckIcon className="h-4 w-4 mr-2" />
            Generate Report
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'overview', name: 'Overview', icon: ChartBarIcon },
            { id: 'reports', name: 'Reports', icon: DocumentCheckIcon },
            { id: 'frameworks', name: 'Frameworks', icon: ShieldCheckIcon }
          ].map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="h-4 w-4 mr-2" />
                {tab.name}
              </button>
            )
          })}
        </nav>
      </div>

      {/* Content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.2 }}
        >
          {activeTab === 'overview' && renderOverview()}
          {activeTab === 'reports' && renderReports()}
          {activeTab === 'frameworks' && renderFrameworks()}
        </motion.div>
      </AnimatePresence>

      {/* Report Detail Modal */}
      <AnimatePresence>
        {selectedReport && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
            onClick={() => setSelectedReport(null)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-white rounded-xl shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="px-6 py-4 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-gray-900">{selectedReport.name}</h3>
                  <button
                    onClick={() => setSelectedReport(null)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    ×
                  </button>
                </div>
              </div>
              
              <div className="p-6 space-y-6">
                {/* Metrics */}
                <div>
                  <h4 className="text-sm font-medium text-gray-900 mb-3">Compliance Metrics</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {selectedReport.metrics.map((metric, index) => (
                      <div key={index} className="bg-gray-50 rounded-lg p-4">
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium text-gray-900">{metric.name}</span>
                          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(metric.status)}`}>
                            {getStatusIcon(metric.status)}
                          </span>
                        </div>
                        <div className="mt-2">
                          <span className="text-2xl font-bold text-gray-900">{metric.value}</span>
                          <span className="text-sm text-gray-500 ml-1">{metric.unit}</span>
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          Threshold: {metric.threshold}{metric.unit}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Requirements */}
                <div>
                  <h4 className="text-sm font-medium text-gray-900 mb-3">Requirements</h4>
                  <ul className="space-y-2">
                    {selectedReport.requirements.map((req, index) => (
                      <li key={index} className="flex items-center text-sm text-gray-600">
                        <CheckCircleIcon className="h-4 w-4 text-green-500 mr-2" />
                        {req}
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Documents */}
                <div>
                  <h4 className="text-sm font-medium text-gray-900 mb-3">Generated Documents</h4>
                  <div className="space-y-2">
                    {selectedReport.documents.map((doc, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center">
                          <DocumentCheckIcon className="h-5 w-5 text-gray-400 mr-3" />
                          <div>
                            <p className="text-sm font-medium text-gray-900">{doc.name}</p>
                            <p className="text-xs text-gray-500">
                              {formatDateTime(doc.generatedAt)} • {doc.size}
                            </p>
                          </div>
                        </div>
                        <button
                          onClick={() => downloadDocument(doc)}
                          className="text-blue-600 hover:text-blue-800"
                        >
                          <ArrowDownTrayIcon className="h-4 w-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}