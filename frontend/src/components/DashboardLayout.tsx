'use client'

import { ReactNode } from 'react'
import { motion } from 'framer-motion'
import { 
  Bars3Icon,
  UserCircleIcon,
  Cog6ToothIcon,
  ArrowRightOnRectangleIcon
} from '@heroicons/react/24/outline'
import NotificationCenter from './NotificationCenter'
import SmartSearch from './SmartSearch'
import SettingsPanel from './SettingsPanel'

interface DashboardLayoutProps {
  children: ReactNode
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      {/* Top Navigation */}
      <nav className="bg-white/80 backdrop-blur-md shadow-sm border-b border-gray-200/50 sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            {/* Left side */}
            <div className="flex items-center space-x-8">
              <div className="flex-shrink-0 flex items-center">
                <motion.div 
                  whileHover={{ scale: 1.05 }}
                  className="h-10 w-10 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg"
                >
                  <span className="text-white font-bold text-lg">T</span>
                </motion.div>
                <div className="ml-3">
                  <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                    TreasuryIQ
                  </span>
                  <div className="text-xs text-gray-500 -mt-1">Corporate AI Treasury</div>
                </div>
              </div>

              {/* Search */}
              <div className="hidden md:block">
                <SmartSearch />
              </div>
            </div>

            {/* Center - Status Indicators */}
            <div className="hidden lg:flex items-center space-x-6">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm text-gray-600">Live Data</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <span className="text-sm text-gray-600">AI Online</span>
              </div>
              <div className="text-sm text-gray-500">
                Last sync: {new Date().toLocaleTimeString()}
              </div>
            </div>

            {/* Right side */}
            <div className="flex items-center space-x-4">
              {/* Mobile search button */}
              <button className="md:hidden p-2 text-gray-400 hover:text-gray-600 rounded-lg">
                <Bars3Icon className="h-6 w-6" />
              </button>

              {/* Notifications */}
              <NotificationCenter />

              {/* Settings */}
              <SettingsPanel />

              {/* User menu */}
              <div className="flex items-center space-x-3 pl-4 border-l border-gray-200">
                <div className="text-right hidden sm:block">
                  <div className="text-sm font-medium text-gray-900">Sarah Chen</div>
                  <div className="text-xs text-gray-500">Treasury Manager</div>
                </div>
                <div className="relative">
                  <motion.div
                    whileHover={{ scale: 1.05 }}
                    className="h-10 w-10 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-white font-medium shadow-lg cursor-pointer"
                  >
                    SC
                  </motion.div>
                  <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-500 border-2 border-white rounded-full"></div>
                </div>
                
                {/* Logout button */}
                <motion.button 
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="p-2 text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-lg transition-colors"
                  title="Sign out"
                >
                  <ArrowRightOnRectangleIcon className="h-5 w-5" />
                </motion.button>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main content */}
      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          {children}
        </motion.div>
      </main>

      {/* Enhanced Footer */}
      <footer className="bg-white/80 backdrop-blur-md border-t border-gray-200/50 mt-16">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Company Info */}
            <div>
              <div className="flex items-center space-x-2 mb-2">
                <div className="h-6 w-6 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-xs">T</span>
                </div>
                <span className="font-semibold text-gray-900">TreasuryIQ</span>
              </div>
              <p className="text-sm text-gray-600">
                AI-powered corporate treasury management platform
              </p>
              <p className="text-xs text-gray-500 mt-1">
                © 2024 TreasuryIQ. All rights reserved.
              </p>
            </div>

            {/* System Status */}
            <div>
              <h4 className="font-medium text-gray-900 mb-2">System Status</h4>
              <div className="space-y-1 text-sm">
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Data Refresh</span>
                  <div className="flex items-center space-x-1">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span className="text-green-600 text-xs">60s</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">API Status</span>
                  <div className="flex items-center space-x-1">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span className="text-green-600 text-xs">99.9%</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">AI Services</span>
                  <div className="flex items-center space-x-1">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span className="text-green-600 text-xs">Online</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Security & Compliance */}
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Security & Compliance</h4>
              <div className="flex flex-wrap gap-2">
                <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-green-100 text-green-800">
                  SOC 2 Type II
                </span>
                <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800">
                  ISO 27001
                </span>
                <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-purple-100 text-purple-800">
                  GDPR Compliant
                </span>
                <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-800">
                  256-bit SSL
                </span>
              </div>
              <p className="text-xs text-gray-500 mt-2">
                Enterprise-grade security with end-to-end encryption
              </p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}