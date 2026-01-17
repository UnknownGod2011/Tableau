import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface Alert {
  id: string
  type: 'info' | 'warning' | 'error' | 'success'
  title: string
  message: string
  timestamp: string
  read: boolean
}

interface TreasuryStore {
  // Theme
  theme: 'light' | 'dark'
  setTheme: (theme: 'light' | 'dark') => void
  
  // Alerts
  alerts: Alert[]
  addAlert: (alert: Omit<Alert, 'id' | 'timestamp' | 'read'>) => void
  markAlertAsRead: (id: string) => void
  removeAlert: (id: string) => void
  clearAllAlerts: () => void
  
  // Dashboard state
  activeEntity: string | null
  setActiveEntity: (entityId: string | null) => void
  
  // Filters
  dateRange: string
  setDateRange: (range: string) => void
  
  // Settings
  autoRefresh: boolean
  setAutoRefresh: (enabled: boolean) => void
  
  refreshInterval: number
  setRefreshInterval: (interval: number) => void
  
  // UI state
  sidebarCollapsed: boolean
  setSidebarCollapsed: (collapsed: boolean) => void
  
  // Cache
  lastDataUpdate: string | null
  setLastDataUpdate: (timestamp: string) => void
}

export const useTreasuryStore = create<TreasuryStore>()(
  persist(
    (set, get) => ({
      // Theme
      theme: 'light',
      setTheme: (theme) => set({ theme }),
      
      // Alerts
      alerts: [],
      addAlert: (alert) => {
        const newAlert: Alert = {
          ...alert,
          id: `alert_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          timestamp: new Date().toISOString(),
          read: false
        }
        set((state) => ({
          alerts: [newAlert, ...state.alerts.slice(0, 99)] // Keep last 100 alerts
        }))
      },
      markAlertAsRead: (id) => {
        set((state) => ({
          alerts: state.alerts.map(alert =>
            alert.id === id ? { ...alert, read: true } : alert
          )
        }))
      },
      removeAlert: (id) => {
        set((state) => ({
          alerts: state.alerts.filter(alert => alert.id !== id)
        }))
      },
      clearAllAlerts: () => set({ alerts: [] }),
      
      // Dashboard state
      activeEntity: null,
      setActiveEntity: (entityId) => set({ activeEntity: entityId }),
      
      // Filters
      dateRange: '1M',
      setDateRange: (range) => set({ dateRange: range }),
      
      // Settings
      autoRefresh: true,
      setAutoRefresh: (enabled) => set({ autoRefresh: enabled }),
      
      refreshInterval: 60000, // 1 minute
      setRefreshInterval: (interval) => set({ refreshInterval: interval }),
      
      // UI state
      sidebarCollapsed: false,
      setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),
      
      // Cache
      lastDataUpdate: null,
      setLastDataUpdate: (timestamp) => set({ lastDataUpdate: timestamp })
    }),
    {
      name: 'treasury-store',
      partialize: (state) => ({
        theme: state.theme,
        activeEntity: state.activeEntity,
        dateRange: state.dateRange,
        autoRefresh: state.autoRefresh,
        refreshInterval: state.refreshInterval,
        sidebarCollapsed: state.sidebarCollapsed
      })
    }
  )
)

// Selectors
export const useAlerts = () => useTreasuryStore((state) => state.alerts)
export const useUnreadAlertsCount = () => 
  useTreasuryStore((state) => state.alerts.filter(alert => !alert.read).length)
export const useTheme = () => useTreasuryStore((state) => state.theme)
export const useActiveEntity = () => useTreasuryStore((state) => state.activeEntity)
export const useDateRange = () => useTreasuryStore((state) => state.dateRange)
export const useAutoRefresh = () => useTreasuryStore((state) => state.autoRefresh)
export const useRefreshInterval = () => useTreasuryStore((state) => state.refreshInterval)