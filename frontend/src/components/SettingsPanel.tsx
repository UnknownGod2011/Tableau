'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Cog6ToothIcon,
  XMarkIcon,
  BellIcon,
  ShieldCheckIcon,
  EyeIcon,
  UserIcon,
  GlobeAltIcon,
  ChartBarIcon,
  CurrencyDollarIcon,
  ClockIcon,
  CheckIcon
} from '@heroicons/react/24/outline'
import { useTreasuryStore } from '@/store/treasuryStore'

interface SettingsSection {
  id: string
  name: string
  icon: React.ComponentType<{ className?: string }>
  description: string
}

export default function SettingsPanel() {
  const [isOpen, setIsOpen] = useState(false)
  const [activeSection, setActiveSection] = useState('general')
  const [settings, setSettings] = useState({
    general: {
      theme: 'light',
      language: 'en',
      timezone: 'UTC',
      currency: 'USD',
      dateFormat: 'MM/DD/YYYY',
      numberFormat: 'US'
    },
    notifications: {
      emailAlerts: true,
      pushNotifications: true,
      riskAlerts: true,
      portfolioUpdates: true,
      marketNews: false,
      weeklyReports: true,
      alertThresholds: {
        varLimit: 3000000,
        cashThreshold: 5000000,
        fxExposure: 10000000
      }
    },
    dashboard: {
      defaultView: 'overview',
      autoRefresh: true,
      refreshInterval: 60,
      showAnimations: true,
      compactMode: false,
      chartType: 'interactive',
      defaultTimeRange: '1M'
    },
    security: {
      twoFactorAuth: false,
      sessionTimeout: 30,
      ipWhitelist: '',
      auditLogging: true,
      dataEncryption: true,
      apiAccess: false
    },
    integrations: {
      tableauEnabled: true,
      tableauServer: '',
      tableauSite: '',
      aiAssistant: true,
      webSocketUpdates: true,
      exportFormats: ['pdf', 'xlsx', 'csv']
    }
  })

  const { theme, setTheme } = useTreasuryStore()

  const sections: SettingsSection[] = [
    {
      id: 'general',
      name: 'General',
      icon: Cog6ToothIcon,
      description: 'Basic application preferences'
    },
    {
      id: 'notifications',
      name: 'Notifications',
      icon: BellIcon,
      description: 'Alert and notification settings'
    },
    {
      id: 'dashboard',
      name: 'Dashboard',
      icon: ChartBarIcon,
      description: 'Dashboard layout and behavior'
    },
    {
      id: 'security',
      name: 'Security',
      icon: ShieldCheckIcon,
      description: 'Security and privacy settings'
    },
    {
      id: 'integrations',
      name: 'Integrations',
      icon: GlobeAltIcon,
      description: 'Third-party integrations'
    }
  ]

  const updateSetting = (section: string, key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [section]: {
        ...prev[section as keyof typeof prev],
        [key]: value
      }
    }))
  }

  const updateNestedSetting = (section: string, parentKey: string, key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [section]: {
        ...prev[section as keyof typeof prev],
        [parentKey]: {
          ...(prev[section as keyof typeof prev] as any)[parentKey],
          [key]: value
        }
      }
    }))
  }

  const saveSettings = async () => {
    // In a real app, this would save to the backend
    console.log('Saving settings:', settings)
    
    // Update theme in store
    if (settings.general.theme !== theme) {
      setTheme(settings.general.theme as 'light' | 'dark')
    }
    
    // Show success message
    // You could use a toast notification here
    alert('Settings saved successfully!')
  }

  const renderGeneralSettings = () => (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Theme
        </label>
        <select
          value={settings.general.theme}
          onChange={(e) => updateSetting('general', 'theme', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="light">Light</option>
          <option value="dark">Dark</option>
          <option value="auto">Auto (System)</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Language
        </label>
        <select
          value={settings.general.language}
          onChange={(e) => updateSetting('general', 'language', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="en">English</option>
          <option value="es">Spanish</option>
          <option value="fr">French</option>
          <option value="de">German</option>
          <option value="zh">Chinese</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Default Currency
        </label>
        <select
          value={settings.general.currency}
          onChange={(e) => updateSetting('general', 'currency', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="USD">USD - US Dollar</option>
          <option value="EUR">EUR - Euro</option>
          <option value="GBP">GBP - British Pound</option>
          <option value="JPY">JPY - Japanese Yen</option>
          <option value="CAD">CAD - Canadian Dollar</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Timezone
        </label>
        <select
          value={settings.general.timezone}
          onChange={(e) => updateSetting('general', 'timezone', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="UTC">UTC</option>
          <option value="America/New_York">Eastern Time</option>
          <option value="America/Chicago">Central Time</option>
          <option value="America/Denver">Mountain Time</option>
          <option value="America/Los_Angeles">Pacific Time</option>
          <option value="Europe/London">London</option>
          <option value="Europe/Paris">Paris</option>
          <option value="Asia/Tokyo">Tokyo</option>
        </select>
      </div>
    </div>
  )

  const renderNotificationSettings = () => (
    <div className="space-y-6">
      <div className="space-y-4">
        <h4 className="text-sm font-medium text-gray-900">Alert Types</h4>
        
        {[
          { key: 'emailAlerts', label: 'Email Alerts', description: 'Receive alerts via email' },
          { key: 'pushNotifications', label: 'Push Notifications', description: 'Browser push notifications' },
          { key: 'riskAlerts', label: 'Risk Alerts', description: 'VaR and risk limit notifications' },
          { key: 'portfolioUpdates', label: 'Portfolio Updates', description: 'Portfolio value changes' },
          { key: 'marketNews', label: 'Market News', description: 'Relevant market updates' },
          { key: 'weeklyReports', label: 'Weekly Reports', description: 'Automated weekly summaries' }
        ].map(({ key, label, description }) => (
          <label key={key} className="flex items-center justify-between">
            <div>
              <div className="text-sm font-medium text-gray-900">{label}</div>
              <div className="text-xs text-gray-500">{description}</div>
            </div>
            <input
              type="checkbox"
              checked={settings.notifications[key as keyof typeof settings.notifications] as boolean}
              onChange={(e) => updateSetting('notifications', key, e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
          </label>
        ))}
      </div>

      <div className="space-y-4">
        <h4 className="text-sm font-medium text-gray-900">Alert Thresholds</h4>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            VaR Limit ($)
          </label>
          <input
            type="number"
            value={settings.notifications.alertThresholds.varLimit}
            onChange={(e) => updateNestedSetting('notifications', 'alertThresholds', 'varLimit', parseInt(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Cash Threshold ($)
          </label>
          <input
            type="number"
            value={settings.notifications.alertThresholds.cashThreshold}
            onChange={(e) => updateNestedSetting('notifications', 'alertThresholds', 'cashThreshold', parseInt(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>
    </div>
  )

  const renderDashboardSettings = () => (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Default View
        </label>
        <select
          value={settings.dashboard.defaultView}
          onChange={(e) => updateSetting('dashboard', 'defaultView', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="overview">Treasury Overview</option>
          <option value="risk">Risk Management</option>
          <option value="analytics">Advanced Analytics</option>
          <option value="chat">AI Assistant</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Auto Refresh Interval (seconds)
        </label>
        <select
          value={settings.dashboard.refreshInterval}
          onChange={(e) => updateSetting('dashboard', 'refreshInterval', parseInt(e.target.value))}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value={30}>30 seconds</option>
          <option value={60}>1 minute</option>
          <option value={300}>5 minutes</option>
          <option value={600}>10 minutes</option>
          <option value={0}>Disabled</option>
        </select>
      </div>

      <div className="space-y-4">
        {[
          { key: 'autoRefresh', label: 'Auto Refresh', description: 'Automatically refresh data' },
          { key: 'showAnimations', label: 'Animations', description: 'Enable UI animations' },
          { key: 'compactMode', label: 'Compact Mode', description: 'Reduce spacing and padding' }
        ].map(({ key, label, description }) => (
          <label key={key} className="flex items-center justify-between">
            <div>
              <div className="text-sm font-medium text-gray-900">{label}</div>
              <div className="text-xs text-gray-500">{description}</div>
            </div>
            <input
              type="checkbox"
              checked={settings.dashboard[key as keyof typeof settings.dashboard] as boolean}
              onChange={(e) => updateSetting('dashboard', key, e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
          </label>
        ))}
      </div>
    </div>
  )

  const renderSecuritySettings = () => (
    <div className="space-y-6">
      <div className="space-y-4">
        {[
          { key: 'twoFactorAuth', label: 'Two-Factor Authentication', description: 'Require 2FA for login' },
          { key: 'auditLogging', label: 'Audit Logging', description: 'Log all user actions' },
          { key: 'dataEncryption', label: 'Data Encryption', description: 'Encrypt sensitive data' },
          { key: 'apiAccess', label: 'API Access', description: 'Enable API access tokens' }
        ].map(({ key, label, description }) => (
          <label key={key} className="flex items-center justify-between">
            <div>
              <div className="text-sm font-medium text-gray-900">{label}</div>
              <div className="text-xs text-gray-500">{description}</div>
            </div>
            <input
              type="checkbox"
              checked={settings.security[key as keyof typeof settings.security] as boolean}
              onChange={(e) => updateSetting('security', key, e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
          </label>
        ))}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Session Timeout (minutes)
        </label>
        <select
          value={settings.security.sessionTimeout}
          onChange={(e) => updateSetting('security', 'sessionTimeout', parseInt(e.target.value))}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value={15}>15 minutes</option>
          <option value={30}>30 minutes</option>
          <option value={60}>1 hour</option>
          <option value={240}>4 hours</option>
          <option value={480}>8 hours</option>
        </select>
      </div>
    </div>
  )

  const renderIntegrationsSettings = () => (
    <div className="space-y-6">
      <div className="space-y-4">
        {[
          { key: 'tableauEnabled', label: 'Tableau Integration', description: 'Enable Tableau dashboards' },
          { key: 'aiAssistant', label: 'AI Assistant', description: 'Enable AI chat functionality' },
          { key: 'webSocketUpdates', label: 'Real-time Updates', description: 'WebSocket live data updates' }
        ].map(({ key, label, description }) => (
          <label key={key} className="flex items-center justify-between">
            <div>
              <div className="text-sm font-medium text-gray-900">{label}</div>
              <div className="text-xs text-gray-500">{description}</div>
            </div>
            <input
              type="checkbox"
              checked={settings.integrations[key as keyof typeof settings.integrations] as boolean}
              onChange={(e) => updateSetting('integrations', key, e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
          </label>
        ))}
      </div>

      {settings.integrations.tableauEnabled && (
        <div className="space-y-4 p-4 bg-gray-50 rounded-lg">
          <h4 className="text-sm font-medium text-gray-900">Tableau Configuration</h4>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tableau Server URL
            </label>
            <input
              type="url"
              value={settings.integrations.tableauServer}
              onChange={(e) => updateSetting('integrations', 'tableauServer', e.target.value)}
              placeholder="https://your-tableau-server.com"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Site ID
            </label>
            <input
              type="text"
              value={settings.integrations.tableauSite}
              onChange={(e) => updateSetting('integrations', 'tableauSite', e.target.value)}
              placeholder="your-site-id"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      )}
    </div>
  )

  const renderContent = () => {
    switch (activeSection) {
      case 'general':
        return renderGeneralSettings()
      case 'notifications':
        return renderNotificationSettings()
      case 'dashboard':
        return renderDashboardSettings()
      case 'security':
        return renderSecuritySettings()
      case 'integrations':
        return renderIntegrationsSettings()
      default:
        return null
    }
  }

  return (
    <>
      {/* Settings Button */}
      <button
        onClick={() => setIsOpen(true)}
        className="p-2 text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-lg transition-colors"
      >
        <Cog6ToothIcon className="h-6 w-6" />
      </button>

      {/* Settings Modal */}
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
              initial={{ opacity: 0, scale: 0.95, x: '100%' }}
              animate={{ opacity: 1, scale: 1, x: 0 }}
              exit={{ opacity: 0, scale: 0.95, x: '100%' }}
              transition={{ type: 'spring', damping: 25, stiffness: 300 }}
              className="fixed right-0 top-0 h-full w-96 bg-white shadow-xl z-50 overflow-hidden"
            >
              {/* Header */}
              <div className="px-6 py-4 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-gray-900">
                    Settings
                  </h3>
                  <button
                    onClick={() => setIsOpen(false)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <XMarkIcon className="h-6 w-6" />
                  </button>
                </div>
              </div>

              <div className="flex h-full">
                {/* Sidebar */}
                <div className="w-32 bg-gray-50 border-r border-gray-200">
                  <nav className="p-2 space-y-1">
                    {sections.map((section) => {
                      const Icon = section.icon
                      return (
                        <button
                          key={section.id}
                          onClick={() => setActiveSection(section.id)}
                          className={`w-full p-2 text-left rounded-lg transition-colors ${
                            activeSection === section.id
                              ? 'bg-blue-100 text-blue-700'
                              : 'text-gray-600 hover:bg-gray-100'
                          }`}
                        >
                          <Icon className="h-5 w-5 mx-auto mb-1" />
                          <div className="text-xs text-center">{section.name}</div>
                        </button>
                      )
                    })}
                  </nav>
                </div>

                {/* Content */}
                <div className="flex-1 flex flex-col">
                  <div className="flex-1 p-6 overflow-y-auto">
                    <div className="mb-4">
                      <h4 className="text-lg font-medium text-gray-900">
                        {sections.find(s => s.id === activeSection)?.name}
                      </h4>
                      <p className="text-sm text-gray-600">
                        {sections.find(s => s.id === activeSection)?.description}
                      </p>
                    </div>
                    {renderContent()}
                  </div>

                  {/* Footer */}
                  <div className="px-6 py-4 border-t border-gray-200">
                    <button
                      onClick={saveSettings}
                      className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      Save Settings
                    </button>
                  </div>
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  )
}