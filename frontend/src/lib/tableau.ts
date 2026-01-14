import { API_BASE_URL } from './api'

export interface TableauWorkbook {
  id: string
  name: string
  description?: string
  webPageUrl: string
  contentUrl: string
  showTabs: boolean
  size: number
  createdAt: string
  updatedAt: string
  project: {
    id: string
    name: string
  }
  owner: {
    id: string
    name: string
  }
  tags?: Array<{
    label: string
  }>
  viewCount?: number
  userCount?: number
}

export interface TableauView {
  id: string
  name: string
  contentUrl: string
  viewUrlName: string
  workbook: {
    id: string
    name: string
  }
  owner: {
    id: string
    name: string
  }
  project: {
    id: string
    name: string
  }
  tags?: Array<{
    label: string
  }>
  usage?: {
    totalViewCount: number
  }
  createdAt: string
  updatedAt: string
}

export interface TableauDataSource {
  id: string
  name: string
  contentUrl: string
  type: string
  createdAt: string
  updatedAt: string
  project: {
    id: string
    name: string
  }
  owner: {
    id: string
    name: string
  }
  isCertified: boolean
  useRemoteQueryAgent: boolean
}

export interface TableauEmbedConfig {
  server: string
  site: string
  ticket?: string
  token?: string
}

export interface TableauInsights {
  summary: string
  key_findings: string[]
  recommendations: string[]
  risk_alerts: Array<{
    type: string
    severity: string
    description: string
  }>
  confidence: number
  data_quality_score: number
}

export interface TableauUsageMetrics {
  total_views: number
  unique_users: number
  avg_daily_views: number
  last_accessed: string
  popularity_score: number
  engagement_level: string
}

export interface TreasuryDashboardConfig {
  name: string
  project_id: string
  data_sources: string[]
  views: Array<{
    name: string
    type: 'cash_position' | 'fx_risk' | 'liquidity' | 'compliance'
  }>
  filters: Record<string, any>
  refresh_schedule: string
}

class TableauService {
  private baseUrl: string
  private isAuthenticated: boolean = false
  private authToken: string | null = null

  constructor() {
    this.baseUrl = `${API_BASE_URL}/tableau`
  }

  async authenticate(): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/auth`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        throw new Error(`Authentication failed: ${response.statusText}`)
      }

      const result = await response.json()
      this.isAuthenticated = true
      
      console.log('Tableau authentication successful:', result.data)
    } catch (error) {
      console.error('Tableau authentication failed:', error)
      this.isAuthenticated = false
      throw error
    }
  }

  async signOut(): Promise<void> {
    try {
      await fetch(`${this.baseUrl}/signout`, {
        method: 'POST',
      })
      this.isAuthenticated = false
      this.authToken = null
    } catch (error) {
      console.error('Tableau sign out failed:', error)
    }
  }

  async getWorkbooks(): Promise<TableauWorkbook[]> {
    const response = await fetch(`${this.baseUrl}/workbooks`)
    
    if (!response.ok) {
      throw new Error(`Failed to fetch workbooks: ${response.statusText}`)
    }

    const result = await response.json()
    return result.data || []
  }

  async getWorkbook(workbookId: string): Promise<TableauWorkbook> {
    const response = await fetch(`${this.baseUrl}/workbooks/${workbookId}`)
    
    if (!response.ok) {
      throw new Error(`Failed to fetch workbook: ${response.statusText}`)
    }

    const result = await response.json()
    return result.data
  }

  async getViews(): Promise<TableauView[]> {
    const response = await fetch(`${this.baseUrl}/views`)
    
    if (!response.ok) {
      throw new Error(`Failed to fetch views: ${response.statusText}`)
    }

    const result = await response.json()
    return result.data || []
  }

  async getWorkbookViews(workbookId: string): Promise<TableauView[]> {
    const response = await fetch(`${this.baseUrl}/workbooks/${workbookId}/views`)
    
    if (!response.ok) {
      throw new Error(`Failed to fetch workbook views: ${response.statusText}`)
    }

    const result = await response.json()
    return result.data || []
  }

  async getDataSources(): Promise<TableauDataSource[]> {
    const response = await fetch(`${this.baseUrl}/datasources`)
    
    if (!response.ok) {
      throw new Error(`Failed to fetch data sources: ${response.statusText}`)
    }

    const result = await response.json()
    return result.data || []
  }

  async refreshDataSource(dataSourceId: string): Promise<{ job_id: string; status: string }> {
    const response = await fetch(`${this.baseUrl}/datasources/${dataSourceId}/refresh`, {
      method: 'POST',
    })
    
    if (!response.ok) {
      throw new Error(`Failed to refresh data source: ${response.statusText}`)
    }

    const result = await response.json()
    return result.data
  }

  async getJobStatus(jobId: string): Promise<any> {
    const response = await fetch(`${this.baseUrl}/jobs/${jobId}`)
    
    if (!response.ok) {
      throw new Error(`Failed to fetch job status: ${response.statusText}`)
    }

    const result = await response.json()
    return result.data
  }

  async exportWorkbookPDF(workbookId: string, options?: {
    pageType?: string
    pageOrientation?: string
    maxAge?: number
  }): Promise<Blob> {
    const response = await fetch(`${this.baseUrl}/workbooks/${workbookId}/export/pdf`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(options || {}),
    })
    
    if (!response.ok) {
      throw new Error(`Failed to export workbook as PDF: ${response.statusText}`)
    }

    return response.blob()
  }

  async exportViewImage(viewId: string, options?: {
    resolution?: string
    maxAge?: number
  }): Promise<Blob> {
    const response = await fetch(`${this.baseUrl}/views/${viewId}/export/image`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(options || {}),
    })
    
    if (!response.ok) {
      throw new Error(`Failed to export view as image: ${response.statusText}`)
    }

    return response.blob()
  }

  async exportViewCSV(viewId: string, options?: {
    maxAge?: number
  }): Promise<Blob> {
    const response = await fetch(`${this.baseUrl}/views/${viewId}/export/csv`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(options || {}),
    })
    
    if (!response.ok) {
      throw new Error(`Failed to export view as CSV: ${response.statusText}`)
    }

    return response.blob()
  }

  // Advanced Treasury-specific features

  async publishTreasuryData(dataSourceId: string, data: any): Promise<void> {
    const response = await fetch(`${this.baseUrl}/datasources/${dataSourceId}/publish-data`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
    
    if (!response.ok) {
      throw new Error(`Failed to publish treasury data: ${response.statusText}`)
    }
  }

  async createTreasuryDashboard(config: TreasuryDashboardConfig): Promise<{ workbook_id: string; workbook_name: string }> {
    const response = await fetch(`${this.baseUrl}/workbooks/create-treasury-dashboard`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(config),
    })
    
    if (!response.ok) {
      throw new Error(`Failed to create treasury dashboard: ${response.statusText}`)
    }

    const result = await response.json()
    return result.data
  }

  async applyTreasuryFilters(viewId: string, filters: Record<string, any>): Promise<void> {
    const response = await fetch(`${this.baseUrl}/views/${viewId}/apply-treasury-filters`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(filters),
    })
    
    if (!response.ok) {
      throw new Error(`Failed to apply treasury filters: ${response.statusText}`)
    }
  }

  async getTreasuryInsights(workbookId: string): Promise<TableauInsights> {
    const response = await fetch(`${this.baseUrl}/analytics/treasury-insights/${workbookId}`)
    
    if (!response.ok) {
      throw new Error(`Failed to get treasury insights: ${response.statusText}`)
    }

    const result = await response.json()
    return result.data.insights
  }

  async createTreasuryAlert(config: {
    subject: string
    view_id: string
    user_id: string
    conditions: Record<string, any>
  }): Promise<{ subscription_id: string }> {
    const response = await fetch(`${this.baseUrl}/subscriptions/create-treasury-alert`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(config),
    })
    
    if (!response.ok) {
      throw new Error(`Failed to create treasury alert: ${response.statusText}`)
    }

    const result = await response.json()
    return result.data
  }

  async getDashboardUsageMetrics(workbookId: string, days: number = 30): Promise<TableauUsageMetrics> {
    const response = await fetch(`${this.baseUrl}/metrics/dashboard-usage/${workbookId}?days=${days}`)
    
    if (!response.ok) {
      throw new Error(`Failed to get dashboard usage metrics: ${response.statusText}`)
    }

    const result = await response.json()
    return result.data.metrics
  }

  async getSiteInfo(): Promise<any> {
    const response = await fetch(`${this.baseUrl}/site`)
    
    if (!response.ok) {
      throw new Error(`Failed to fetch site info: ${response.statusText}`)
    }

    const result = await response.json()
    return result.data
  }

  async getProjects(): Promise<any[]> {
    const response = await fetch(`${this.baseUrl}/projects`)
    
    if (!response.ok) {
      throw new Error(`Failed to fetch projects: ${response.statusText}`)
    }

    const result = await response.json()
    return result.data || []
  }

  async checkHealth(): Promise<any> {
    const response = await fetch(`${this.baseUrl}/health`)
    
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.statusText}`)
    }

    return response.json()
  }

  // Embedding utilities
  getEmbedConfig(): TableauEmbedConfig {
    return {
      server: process.env.NEXT_PUBLIC_TABLEAU_SERVER || 'https://prod-useast-b.online.tableau.com',
      site: process.env.NEXT_PUBLIC_TABLEAU_SITE || '',
    }
  }

  generateEmbedUrl(viewId: string, options?: {
    showTabs?: boolean
    showToolbar?: boolean
    showShareOptions?: boolean
    width?: string
    height?: string
  }): string {
    const config = this.getEmbedConfig()
    const baseUrl = `${config.server}/views/${viewId}`
    
    const params = new URLSearchParams()
    
    if (options?.showTabs === false) params.append(':tabs', 'no')
    if (options?.showToolbar === false) params.append(':toolbar', 'no')
    if (options?.showShareOptions === false) params.append(':share', 'no')
    
    const queryString = params.toString()
    return queryString ? `${baseUrl}?${queryString}` : baseUrl
  }

  // Real-time data streaming
  async streamTreasuryData(dataSourceId: string, dataStream: AsyncIterable<any>): Promise<void> {
    for await (const data of dataStream) {
      try {
        await this.publishTreasuryData(dataSourceId, data)
        console.log('Treasury data streamed successfully:', data)
      } catch (error) {
        console.error('Failed to stream treasury data:', error)
        // Continue streaming despite errors
      }
    }
  }

  // Batch operations
  async batchRefreshDataSources(dataSourceIds: string[]): Promise<Array<{ id: string; job_id: string; status: string }>> {
    const results = await Promise.allSettled(
      dataSourceIds.map(async (id) => {
        const result = await this.refreshDataSource(id)
        return { id, ...result }
      })
    )

    return results
      .filter((result): result is PromiseFulfilledResult<{ id: string; job_id: string; status: string }> => 
        result.status === 'fulfilled'
      )
      .map(result => result.value)
  }

  // Advanced filtering
  async applyAdvancedFilters(viewId: string, filters: {
    entity?: string[]
    currency?: string[]
    dateRange?: { start: string; end: string }
    riskLevel?: string[]
    accountType?: string[]
  }): Promise<void> {
    const formattedFilters: Record<string, any> = {}

    if (filters.entity) formattedFilters['Entity'] = filters.entity
    if (filters.currency) formattedFilters['Currency'] = filters.currency
    if (filters.dateRange) {
      formattedFilters['Date'] = `${filters.dateRange.start} to ${filters.dateRange.end}`
    }
    if (filters.riskLevel) formattedFilters['Risk Level'] = filters.riskLevel
    if (filters.accountType) formattedFilters['Account Type'] = filters.accountType

    await this.applyTreasuryFilters(viewId, formattedFilters)
  }
}

const tableauService = new TableauService()
export default tableauService