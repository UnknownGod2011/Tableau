'use client';

import { useState } from 'react';
import Dock from '../../components/Dock';
import '../../components/Dock.css';

type TabType = 'overview' | 'analytics' | 'risk' | 'ai';

export default function TreasuryDashboardPage() {
  const [activeTab, setActiveTab] = useState<TabType>('overview');

  // Dock items configuration
  const dockItems = [
    {
      icon: (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
          <polyline points="9 22 9 12 15 12 15 22" />
        </svg>
      ),
      label: 'Treasury Overview',
      onClick: () => setActiveTab('overview'),
      className: activeTab === 'overview' ? 'active' : ''
    },
    {
      icon: (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <line x1="12" y1="20" x2="12" y2="10" />
          <line x1="18" y1="20" x2="18" y2="4" />
          <line x1="6" y1="20" x2="6" y2="16" />
        </svg>
      ),
      label: 'Advanced Analytics',
      onClick: () => setActiveTab('analytics'),
      className: activeTab === 'analytics' ? 'active' : ''
    },
    {
      icon: (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
          <line x1="12" y1="9" x2="12" y2="13" />
          <line x1="12" y1="17" x2="12.01" y2="17" />
        </svg>
      ),
      label: 'Risk Dashboard',
      onClick: () => setActiveTab('risk'),
      className: activeTab === 'risk' ? 'active' : ''
    },
    {
      icon: (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="10" />
          <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
          <line x1="12" y1="17" x2="12.01" y2="17" />
        </svg>
      ),
      label: 'AI Analytics',
      onClick: () => setActiveTab('ai'),
      className: activeTab === 'ai' ? 'active' : ''
    }
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900">Treasury Overview</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg p-6 text-white">
                <h3 className="text-sm font-medium opacity-90">Total Cash Position</h3>
                <p className="text-3xl font-bold mt-2">$500M</p>
                <p className="text-sm mt-1 opacity-75">+2.5% from last month</p>
              </div>
              <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg p-6 text-white">
                <h3 className="text-sm font-medium opacity-90">Available Liquidity</h3>
                <p className="text-3xl font-bold mt-2">$350M</p>
                <p className="text-sm mt-1 opacity-75">70% of total</p>
              </div>
              <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg p-6 text-white">
                <h3 className="text-sm font-medium opacity-90">FX Exposure</h3>
                <p className="text-3xl font-bold mt-2">$125M</p>
                <p className="text-sm mt-1 opacity-75">5 currencies</p>
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4">Global Cash Position</h3>
              <div className="h-64 flex items-center justify-center bg-gray-50 rounded">
                <p className="text-gray-500">Tableau Dashboard will load here</p>
              </div>
            </div>
          </div>
        );
      
      case 'analytics':
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900">Advanced Analytics</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold mb-4">Cash Flow Trends</h3>
                <div className="h-64 flex items-center justify-center bg-gray-50 rounded">
                  <p className="text-gray-500">Tableau Analytics View</p>
                </div>
              </div>
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold mb-4">Predictive Forecasting</h3>
                <div className="h-64 flex items-center justify-center bg-gray-50 rounded">
                  <p className="text-gray-500">AI-Powered Predictions</p>
                </div>
              </div>
            </div>
          </div>
        );
      
      case 'risk':
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900">Risk Dashboard</h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <h3 className="text-sm font-medium text-red-800">High Risk</h3>
                <p className="text-2xl font-bold text-red-600 mt-2">3</p>
              </div>
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <h3 className="text-sm font-medium text-yellow-800">Medium Risk</h3>
                <p className="text-2xl font-bold text-yellow-600 mt-2">7</p>
              </div>
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <h3 className="text-sm font-medium text-green-800">Low Risk</h3>
                <p className="text-2xl font-bold text-green-600 mt-2">15</p>
              </div>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="text-sm font-medium text-blue-800">VaR (95%)</h3>
                <p className="text-2xl font-bold text-blue-600 mt-2">$2.5M</p>
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4">Risk Exposure Analysis</h3>
              <div className="h-64 flex items-center justify-center bg-gray-50 rounded">
                <p className="text-gray-500">Risk visualization will load here</p>
              </div>
            </div>
          </div>
        );
      
      case 'ai':
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900">AI Analytics</h2>
            <div className="bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg p-6 text-white">
              <h3 className="text-lg font-semibold mb-2">AI-Powered Insights</h3>
              <p className="text-sm opacity-90">
                Machine learning models analyzing your treasury data in real-time
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold mb-4">Anomaly Detection</h3>
                <div className="space-y-2">
                  <div className="flex items-center justify-between p-3 bg-yellow-50 rounded">
                    <span className="text-sm">Unusual transaction pattern detected</span>
                    <span className="text-xs text-yellow-600 font-medium">2h ago</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-green-50 rounded">
                    <span className="text-sm">Cash flow optimization opportunity</span>
                    <span className="text-xs text-green-600 font-medium">5h ago</span>
                  </div>
                </div>
              </div>
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold mb-4">Recommendations</h3>
                <div className="space-y-2">
                  <div className="p-3 bg-blue-50 rounded">
                    <p className="text-sm font-medium text-blue-900">Optimize EUR holdings</p>
                    <p className="text-xs text-blue-600 mt-1">Potential savings: $50K</p>
                  </div>
                  <div className="p-3 bg-purple-50 rounded">
                    <p className="text-sm font-medium text-purple-900">Hedge FX exposure</p>
                    <p className="text-xs text-purple-600 mt-1">Risk reduction: 15%</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        );
      
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 pb-32">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-3xl font-bold text-gray-900">Treasury Analytics Dashboard</h1>
          <p className="mt-1 text-sm text-gray-600">
            Comprehensive Tableau integration with floating dock navigation
          </p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow p-6">
          {renderTabContent()}
        </div>
      </div>

      {/* Floating Dock at Bottom */}
      <Dock
        items={dockItems}
        panelHeight={68}
        baseItemSize={50}
        magnification={70}
        distance={200}
      />
    </div>
  );
}
