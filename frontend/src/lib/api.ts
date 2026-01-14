import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'

// API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const API_TIMEOUT = 30000 // 30 seconds

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for authentication
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // Add request timestamp
    config.headers['X-Request-Time'] = new Date().toISOString()
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    
    return Promise.reject(error)
  }
)

// API Response Types
export interface ApiResponse<T = any> {
  data: T
  message?: string
  status: 'success' | 'error'
  timestamp: string
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number
    limit: number
    total: number
    totalPages: number
  }
}

// Treasury API Endpoints
export const treasuryApi = {
  // Portfolio endpoints
  portfolio: {
    getOverview: (entityId?: string): Promise<ApiResponse> =>
      apiClient.get(`/api/v1/portfolio/overview${entityId ? `?entity_id=${entityId}` : ''}`),
    
    getPositions: (entityId?: string): Promise<ApiResponse> =>
      apiClient.get(`/api/v1/portfolio/positions${entityId ? `?entity_id=${entityId}` : ''}`),
    
    getCashFlow: (params: { startDate?: string; endDate?: string; entityId?: string }): Promise<ApiResponse> =>
      apiClient.get('/api/v1/portfolio/cash-flow', { params }),
    
    optimize: (data: { entityId: string; constraints: any }): Promise<ApiResponse> =>
      apiClient.post('/api/v1/portfolio/optimize', data),
  },

  // Risk endpoints
  risk: {
    calculateVaR: (data: { portfolioId: string; confidence: number; horizon: number }): Promise<ApiResponse> =>
      apiClient.post('/api/v1/risk/var', data),
    
    getMetrics: (entityId?: string): Promise<ApiResponse> =>
      apiClient.get(`/api/v1/risk/metrics${entityId ? `?entity_id=${entityId}` : ''}`),
    
    stressTest: (data: { scenarios: any[]; portfolioId: string }): Promise<ApiResponse> =>
      apiClient.post('/api/v1/risk/stress-test', data),
    
    getLimits: (): Promise<ApiResponse> =>
      apiClient.get('/api/v1/risk/limits'),
    
    updateLimits: (data: any): Promise<ApiResponse> =>
      apiClient.put('/api/v1/risk/limits', data),
  },

  // Market data endpoints
  marketData: {
    getRates: (currencies: string[]): Promise<ApiResponse> =>
      apiClient.get('/api/v1/market-data/rates', { params: { currencies: currencies.join(',') } }),
    
    getYieldCurve: (currency: string): Promise<ApiResponse> =>
      apiClient.get(`/api/v1/market-data/yield-curve/${currency}`),
    
    getHistoricalData: (params: { symbol: string; startDate: string; endDate: string }): Promise<ApiResponse> =>
      apiClient.get('/api/v1/market-data/historical', { params }),
  },

  // AI endpoints
  ai: {
    chat: (data: { message: string; context?: any }): Promise<ApiResponse> =>
      apiClient.post('/api/v1/ai/chat', data),
    
    getInsights: (entityId?: string): Promise<ApiResponse> =>
      apiClient.get(`/api/v1/ai/insights${entityId ? `?entity_id=${entityId}` : ''}`),
    
    optimize: (data: { type: 'cash' | 'portfolio'; parameters: any }): Promise<ApiResponse> =>
      apiClient.post('/api/v1/ai/optimize', data),
  },

  // Compliance endpoints
  compliance: {
    getReports: (): Promise<ApiResponse> =>
      apiClient.get('/api/v1/compliance/reports'),
    
    generateReport: (data: { type: string; parameters: any }): Promise<ApiResponse> =>
      apiClient.post('/api/v1/compliance/generate', data),
    
    getFrameworks: (): Promise<ApiResponse> =>
      apiClient.get('/api/v1/compliance/frameworks'),
    
    checkCompliance: (frameworkId: string): Promise<ApiResponse> =>
      apiClient.get(`/api/v1/compliance/check/${frameworkId}`),
  },

  // Audit endpoints
  audit: {
    getTrail: (params: { startDate?: string; endDate?: string; userId?: string; action?: string }): Promise<PaginatedResponse<any>> =>
      apiClient.get('/api/v1/audit/trail', { params }),
    
    exportTrail: (params: any): Promise<Blob> =>
      apiClient.get('/api/v1/audit/export', { params, responseType: 'blob' }),
  },

  // User management endpoints
  users: {
    getUsers: (params?: { page?: number; limit?: number; search?: string }): Promise<PaginatedResponse<any>> =>
      apiClient.get('/api/v1/users', { params }),
    
    createUser: (data: any): Promise<ApiResponse> =>
      apiClient.post('/api/v1/users', data),
    
    updateUser: (id: string, data: any): Promise<ApiResponse> =>
      apiClient.put(`/api/v1/users/${id}`, data),
    
    deleteUser: (id: string): Promise<ApiResponse> =>
      apiClient.delete(`/api/v1/users/${id}`),
    
    getRoles: (): Promise<ApiResponse> =>
      apiClient.get('/api/v1/users/roles'),
    
    createRole: (data: any): Promise<ApiResponse> =>
      apiClient.post('/api/v1/users/roles', data),
    
    updateRole: (id: string, data: any): Promise<ApiResponse> =>
      apiClient.put(`/api/v1/users/roles/${id}`, data),
  },

  // System endpoints
  system: {
    getHealth: (): Promise<ApiResponse> =>
      apiClient.get('/api/v1/system/health'),
    
    getMetrics: (): Promise<ApiResponse> =>
      apiClient.get('/api/v1/system/metrics'),
    
    getConfig: (): Promise<ApiResponse> =>
      apiClient.get('/api/v1/system/config'),
    
    updateConfig: (data: any): Promise<ApiResponse> =>
      apiClient.put('/api/v1/system/config', data),
  },

  // Export endpoints
  export: {
    generateReport: (data: { type: string; format: string; parameters: any }): Promise<ApiResponse> =>
      apiClient.post('/api/v1/export/generate', data),
    
    getJobs: (): Promise<ApiResponse> =>
      apiClient.get('/api/v1/export/jobs'),
    
    downloadFile: (jobId: string): Promise<Blob> =>
      apiClient.get(`/api/v1/export/download/${jobId}`, { responseType: 'blob' }),
  },

  // Tableau integration endpoints
  tableau: {
    getWorkbooks: (): Promise<ApiResponse> =>
      apiClient.get('/api/v1/tableau/workbooks'),
    
    getWorkbook: (workbookId: string): Promise<ApiResponse> =>
      apiClient.get(`/api/v1/tableau/workbooks/${workbookId}`),
    
    getViews: (): Promise<ApiResponse> =>
      apiClient.get('/api/v1/tableau/views'),
    
    getWorkbookViews: (workbookId: string): Promise<ApiResponse> =>
      apiClient.get(`/api/v1/tableau/workbooks/${workbookId}/views`),
    
    getDataSources: (): Promise<ApiResponse> =>
      apiClient.get('/api/v1/tableau/datasources'),
    
    refreshDataSource: (dataSourceId: string): Promise<ApiResponse> =>
      apiClient.post(`/api/v1/tableau/datasources/${dataSourceId}/refresh`),
    
    getJobStatus: (jobId: string): Promise<ApiResponse> =>
      apiClient.get(`/api/v1/tableau/jobs/${jobId}`),
    
    exportWorkbookPDF: (workbookId: string, options: any): Promise<Blob> =>
      apiClient.post(`/api/v1/tableau/workbooks/${workbookId}/export/pdf`, options, { responseType: 'blob' }),
    
    exportViewImage: (viewId: string, options: any): Promise<Blob> =>
      apiClient.post(`/api/v1/tableau/views/${viewId}/export/image`, options, { responseType: 'blob' }),
    
    exportViewCSV: (viewId: string, options: any): Promise<string> =>
      apiClient.post(`/api/v1/tableau/views/${viewId}/export/csv`, options, { responseType: 'text' }),
    
    getSiteInfo: (): Promise<ApiResponse> =>
      apiClient.get('/api/v1/tableau/site'),
    
    getProjects: (): Promise<ApiResponse> =>
      apiClient.get('/api/v1/tableau/projects'),
    
    authenticate: (): Promise<ApiResponse> =>
      apiClient.post('/api/v1/tableau/auth'),
    
    signOut: (): Promise<ApiResponse> =>
      apiClient.post('/api/v1/tableau/signout'),
  },
}

// Utility functions
export const handleApiError = (error: any): string => {
  if (error.response?.data?.message) {
    return error.response.data.message
  }
  
  if (error.message) {
    return error.message
  }
  
  return 'An unexpected error occurred'
}

export const downloadFile = (blob: Blob, filename: string) => {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

// Request queue for batch operations
class RequestQueue {
  private queue: Array<() => Promise<any>> = []
  private processing = false
  private maxConcurrent = 5

  add<T>(request: () => Promise<T>): Promise<T> {
    return new Promise((resolve, reject) => {
      this.queue.push(async () => {
        try {
          const result = await request()
          resolve(result)
        } catch (error) {
          reject(error)
        }
      })
      
      this.process()
    })
  }

  private async process() {
    if (this.processing || this.queue.length === 0) return
    
    this.processing = true
    
    while (this.queue.length > 0) {
      const batch = this.queue.splice(0, this.maxConcurrent)
      await Promise.allSettled(batch.map(request => request()))
    }
    
    this.processing = false
  }
}

export const requestQueue = new RequestQueue()

// Cache management
class ApiCache {
  private cache = new Map<string, { data: any; timestamp: number; ttl: number }>()

  set(key: string, data: any, ttl: number = 300000) { // 5 minutes default
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl
    })
  }

  get(key: string): any | null {
    const item = this.cache.get(key)
    
    if (!item) return null
    
    if (Date.now() - item.timestamp > item.ttl) {
      this.cache.delete(key)
      return null
    }
    
    return item.data
  }

  clear() {
    this.cache.clear()
  }

  delete(key: string) {
    this.cache.delete(key)
  }
}

export const apiCache = new ApiCache()

// Cached API wrapper
export const cachedApi = {
  get: async <T>(key: string, request: () => Promise<T>, ttl?: number): Promise<T> => {
    const cached = apiCache.get(key)
    if (cached) return cached
    
    const result = await request()
    apiCache.set(key, result, ttl)
    return result
  }
}

export default apiClient