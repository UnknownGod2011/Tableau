/**
 * Treasury Dashboard Page
 * Comprehensive Tableau integration showcasing all features
 */

import React, { useState, useEffect } from 'react';
import TableauDashboard from '../components/TableauDashboard';
import Dock from '../components/Dock';
import '../components/Dock.css';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface DashboardConfig {
  id: string;
  name: string;
  url: string;
  description: string;
  category: string;
}

type TabType = 'overview' | 'analytics' | 'risk' | 'ai';

const TreasuryDashboardPage: React.FC = () => {
  const [dashboards, setDashboards] = useState<DashboardConfig[]>([]);
  const [selectedDashboard, setSelectedDashboard] = useState<DashboardConfig | null>(null);
  const [filters, setFilters] = useState<Record<string, string>>({});
  const [parameters, setParameters] = useState<Record<string, string>>({});
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<TabType>('overview');

  // Treasury-specific filter options
  const [currencies, setCurrencies] = useState(['USD', 'EUR', 'GBP', 'JPY', 'CNY']);
  const [regions, setRegions] = useState(['North America', 'Europe', 'Asia Pacific', 'Latin America']);
  const [entities, setEntities] = useState(['HQ', 'Subsidiary A', 'Subsidiary B', 'Subsidiary C']);

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

  useEffect(() => {
    initializeTableau();
  }, []);

  const initializeTableau = async () => {
    try {
      // Authenticate with Tableau
      const authResponse = await axios.post(`${API_URL}/api/v1/tableau/auth`);
      
      if (authResponse.data.status === 'success') {
        setIsAuthenticated(true);
        await loadDashboards();
      }
    } catch (error) {
      console.error('Failed to authenticate with Tableau:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadDashboards = async () => {
    try {
      // Get all workbooks
      const workbooksResponse = await axios.get(`${API_URL}/api/v1/tableau/workbooks`);
      
      if (workbooksResponse.data.status === 'success') {
        const workbooks = workbooksResponse.data.data;
        
        // Map to dashboard configs
        const dashboardConfigs: DashboardConfig[] = workbooks.map((wb: any) => ({
          id: wb.id,
          name: wb.name,
          url: wb.webPageUrl,
          description: wb.description || 'Treasury analytics dashboard',
          category: wb.project?.name || 'General'
        }));
        
        setDashboards(dashboardConfigs);
        
        // Select first dashboard by default
        if (dashboardConfigs.length > 0) {
          setSelectedDashboard(dashboardConfigs[0]);
        }
      }
    } catch (error) {
      console.error('Failed to load dashboards:', error);
    }
  };

  const handleFilterChange = (filterName: string, value: string) => {
    setFilters(prev => ({
      ...prev,
      [filterName]: value
    }));
  };

  const handleParameterChange = (paramName: string, value: string) => {
    setParameters(prev => ({
      ...prev,
      [paramName]: value
    }));
  };

  const refreshDashboardData = async () => {
    if (!selectedDashboard) return;

    try {
      // Get data sources for the workbook
      const datasourcesResponse = await axios.get(`${API_URL}/api/v1/tableau/datasources`);
      
      if (datasourcesResponse.data.status === 'success') {
        const datasources = datasourcesResponse.data.data;
        
        // Refresh each data source
        for (const ds of datasources) {
          await axios.post(`${API_URL}/api/v1/tableau/datasources/${ds.id}/refresh`);
        }
        
        alert('Dashboard data refresh initiated');
      }
    } catch (error) {
      console.error('Failed to refresh data:', error);
      alert('Failed to refresh dashboard data');
    }
  };

  const exportDashboard = async (format: 'pdf' | 'image' | 'csv') => {
    if (!selectedDashboard) return;

    try {
      let endpoint = '';
      let filename = '';
      
      switch (format) {
        case 'pdf':
          endpoint = `/api/v1/tableau/workbooks/${selectedDashboard.id}/export/pdf`;
          filename = `${selectedDashboard.name}.pdf`;
          break;
        case 'image':
          // Get first view of workbook
          const viewsResponse = await axios.get(
            `${API_URL}/api/v1/tableau/workbooks/${selectedDashboard.id}/views`
          );
          const viewId = viewsResponse.data.data[0]?.id;
          if (!viewId) throw new Error('No views found');
          
          endpoint = `/api/v1/tableau/views/${viewId}/export/image`;
          filename = `${selectedDashboard.name}.png`;
          break;
        case 'csv':
          const csvViewsResponse = await axios.get(
            `${API_URL}/api/v1/tableau/workbooks/${selectedDashboard.id}/views`
          );
          const csvViewId = csvViewsResponse.data.data[0]?.id;
          if (!csvViewId) throw new Error('No views found');
          
          endpoint = `/api/v1/tableau/views/${csvViewId}/export/csv`;
          filename = `${selectedDashboard.name}.csv`;
          break;
      }

      const response = await axios.post(`${API_URL}${endpoint}`, {}, {
        responseType: 'blob'
      });

      // Download file
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error(`Failed to export as ${format}:`, error);
      alert(`Failed to export dashboard as ${format}`);
    }
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return (
          <div className="space-y-6">
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
            {selectedDashboard && (
              <TableauDashboard
                url={selectedDashboard.url}
                width="100%"
                height="600px"
                filters={filters}
                parameters={parameters}
                toolbar="top"
                hideTabs={false}
                hideToolbar={false}
                onLoad={() => console.log('Dashboard loaded')}
                onFilterChange={(f) => console.log('Filter changed:', f)}
                onParameterChange={(p) => console.log('Parameter changed:', p)}
              />
            )}
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
            {selectedDashboard && (
              <TableauDashboard
                url={selectedDashboard.url}
                width="100%"
                height="500px"
                filters={filters}
                parameters={parameters}
              />
            )}
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
            {selectedDashboard && (
              <TableauDashboard
                url={selectedDashboard.url}
                width="100%"
                height="600px"
                filters={filters}
                parameters={parameters}
              />
            )}
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
            {selectedDashboard && (
              <TableauDashboard
                url={selectedDashboard.url}
                width="100%"
                height="500px"
                filters={filters}
                parameters={parameters}
              />
            )}
          </div>
        );
      
      default:
        return null;
    }
  };

  const createAlert = async () => {
    if (!selectedDashboard) return;

    try {
      const alertConfig = {
        name: `Treasury Alert - ${selectedDashboard.name}`,
        workbook_id: selectedDashboard.id,
        subject: 'Treasury Dashboard Alert',
        message: 'Important treasury metrics update',
        schedule: {
          frequency: 'Daily',
          time: '09:00'
        },
        conditions: {
          metric: 'cash_balance',
          operator: 'less_than',
          threshold: 1000000
        }
      };

      const response = await axios.post(
        `${API_URL}/api/v1/tableau/subscriptions/create-treasury-alert`,
        alertConfig
      );

      if (response.data.status === 'success') {
        alert('Treasury alert created successfully');
      }
    } catch (error) {
      console.error('Failed to create alert:', error);
      alert('Failed to create treasury alert');
    }
  };

  const getUsageMetrics = async () => {
    if (!selectedDashboard) return;

    try {
      const response = await axios.get(
        `${API_URL}/api/v1/tableau/metrics/dashboard-usage/${selectedDashboard.id}?days=30`
      );

      if (response.data.status === 'success') {
        console.log('Usage metrics:', response.data.data);
        alert(`Dashboard Usage:\nViews: ${response.data.data.metrics?.views || 'N/A'}\nUsers: ${response.data.data.metrics?.users || 'N/A'}`);
      }
    } catch (error) {
      console.error('Failed to get usage metrics:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading Treasury Dashboards...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-red-600">Authentication Failed</h2>
          <p className="mt-2 text-gray-600">Unable to connect to Tableau Server</p>
          <button
            onClick={initializeTableau}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-32">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-3xl font-bold text-gray-900">Treasury Analytics Dashboard</h1>
          <p className="mt-1 text-sm text-gray-600">
            Comprehensive Tableau integration with all features
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-12 gap-6">
          {/* Sidebar - Dashboard Selection */}
          <div className="col-span-3">
            <div className="bg-white rounded-lg shadow p-4">
              <h2 className="text-lg font-semibold mb-4">Dashboards</h2>
              <div className="space-y-2">
                {dashboards.map(dashboard => (
                  <button
                    key={dashboard.id}
                    onClick={() => setSelectedDashboard(dashboard)}
                    className={`w-full text-left px-3 py-2 rounded transition-colors ${
                      selectedDashboard?.id === dashboard.id
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 hover:bg-gray-200 text-gray-800'
                    }`}
                  >
                    <div className="font-medium">{dashboard.name}</div>
                    <div className="text-xs opacity-75">{dashboard.category}</div>
                  </button>
                ))}
              </div>

              {/* Filters */}
              <div className="mt-6">
                <h3 className="text-sm font-semibold mb-3">Filters</h3>
                
                <div className="space-y-3">
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">
                      Currency
                    </label>
                    <select
                      onChange={(e) => handleFilterChange('Currency', e.target.value)}
                      className="w-full px-2 py-1 text-sm border rounded"
                    >
                      <option value="">All</option>
                      {currencies.map(curr => (
                        <option key={curr} value={curr}>{curr}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">
                      Region
                    </label>
                    <select
                      onChange={(e) => handleFilterChange('Region', e.target.value)}
                      className="w-full px-2 py-1 text-sm border rounded"
                    >
                      <option value="">All</option>
                      {regions.map(region => (
                        <option key={region} value={region}>{region}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">
                      Entity
                    </label>
                    <select
                      onChange={(e) => handleFilterChange('Entity', e.target.value)}
                      className="w-full px-2 py-1 text-sm border rounded"
                    >
                      <option value="">All</option>
                      {entities.map(entity => (
                        <option key={entity} value={entity}>{entity}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="mt-6 space-y-2">
                <button
                  onClick={refreshDashboardData}
                  className="w-full px-3 py-2 text-sm bg-green-600 text-white rounded hover:bg-green-700"
                >
                  Refresh Data
                </button>
                <button
                  onClick={createAlert}
                  className="w-full px-3 py-2 text-sm bg-yellow-600 text-white rounded hover:bg-yellow-700"
                >
                  Create Alert
                </button>
                <button
                  onClick={getUsageMetrics}
                  className="w-full px-3 py-2 text-sm bg-purple-600 text-white rounded hover:bg-purple-700"
                >
                  Usage Metrics
                </button>
              </div>

              {/* Export Options */}
              <div className="mt-6">
                <h3 className="text-sm font-semibold mb-2">Export</h3>
                <div className="space-y-2">
                  <button
                    onClick={() => exportDashboard('pdf')}
                    className="w-full px-3 py-1 text-sm bg-gray-600 text-white rounded hover:bg-gray-700"
                  >
                    Export PDF
                  </button>
                  <button
                    onClick={() => exportDashboard('image')}
                    className="w-full px-3 py-1 text-sm bg-gray-600 text-white rounded hover:bg-gray-700"
                  >
                    Export Image
                  </button>
                  <button
                    onClick={() => exportDashboard('csv')}
                    className="w-full px-3 py-1 text-sm bg-gray-600 text-white rounded hover:bg-gray-700"
                  >
                    Export CSV
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Main Content - Tab-based content */}
          <div className="col-span-9">
            <div className="bg-white rounded-lg shadow p-6">
              {renderTabContent()}
            </div>
          </div>
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
};

export default TreasuryDashboardPage;
