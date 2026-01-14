'use client';

/**
 * Tableau Dashboard Embed Component
 * Implements Tableau JavaScript API for interactive embedded dashboards
 */

import React, { useEffect, useRef, useState } from 'react';

// Tableau JavaScript API types
declare global {
  interface Window {
    tableau: any;
  }
}

interface TableauDashboardProps {
  url: string;
  width?: string;
  height?: string;
  filters?: Record<string, string | string[]>;
  parameters?: Record<string, string>;
  onLoad?: () => void;
  onFilterChange?: (filters: any) => void;
  onParameterChange?: (parameters: any) => void;
  toolbar?: 'yes' | 'no' | 'top' | 'bottom';
  hideTabs?: boolean;
  hideToolbar?: boolean;
}

export const TableauDashboard: React.FC<TableauDashboardProps> = ({
  url,
  width = '100%',
  height = '800px',
  filters = {},
  parameters = {},
  onLoad,
  onFilterChange,
  onParameterChange,
  toolbar = 'top',
  hideTabs = false,
  hideToolbar = false,
}) => {
  const vizRef = useRef<HTMLDivElement>(null);
  const [viz, setViz] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Load Tableau JavaScript API
    const script = document.createElement('script');
    script.src = 'https://prod-useast-b.online.tableau.com/javascripts/api/tableau-2.9.1.min.js';
    script.async = true;
    script.onload = initializeViz;
    script.onerror = () => setError('Failed to load Tableau JavaScript API');
    document.body.appendChild(script);

    return () => {
      if (viz) {
        viz.dispose();
      }
      if (document.body.contains(script)) {
        document.body.removeChild(script);
      }
    };
  }, []);

  useEffect(() => {
    if (viz && Object.keys(filters).length > 0) {
      applyFilters();
    }
  }, [filters, viz]);

  useEffect(() => {
    if (viz && Object.keys(parameters).length > 0) {
      applyParameters();
    }
  }, [parameters, viz]);

  const initializeViz = () => {
    if (!vizRef.current || !window.tableau) return;

    try {
      const options = {
        width,
        height,
        hideTabs,
        hideToolbar,
        toolbar,
        onFirstInteractive: () => {
          setIsLoading(false);
          if (onLoad) onLoad();
          
          // Apply initial filters and parameters
          if (Object.keys(filters).length > 0) applyFilters();
          if (Object.keys(parameters).length > 0) applyParameters();
          
          // Set up event listeners
          setupEventListeners();
        },
      };

      const newViz = new window.tableau.Viz(vizRef.current, url, options);
      setViz(newViz);
    } catch (err) {
      setError(`Failed to initialize Tableau viz: ${err}`);
      setIsLoading(false);
    }
  };

  const applyFilters = async () => {
    if (!viz) return;

    try {
      const workbook = viz.getWorkbook();
      const activeSheet = workbook.getActiveSheet();

      for (const [fieldName, value] of Object.entries(filters)) {
        if (Array.isArray(value)) {
          await activeSheet.applyFilterAsync(
            fieldName,
            value,
            window.tableau.FilterUpdateType.REPLACE
          );
        } else {
          await activeSheet.applyFilterAsync(
            fieldName,
            [value],
            window.tableau.FilterUpdateType.REPLACE
          );
        }
      }
    } catch (err) {
      console.error('Error applying filters:', err);
    }
  };

  const applyParameters = async () => {
    if (!viz) return;

    try {
      const workbook = viz.getWorkbook();

      for (const [name, value] of Object.entries(parameters)) {
        await workbook.changeParameterValueAsync(name, value);
      }
    } catch (err) {
      console.error('Error applying parameters:', err);
    }
  };

  const setupEventListeners = () => {
    if (!viz) return;

    // Listen for filter changes
    viz.addEventListener(
      window.tableau.TableauEventName.FILTER_CHANGE,
      (event: any) => {
        if (onFilterChange) {
          const filterInfo = event.getFilterAsync();
          onFilterChange(filterInfo);
        }
      }
    );

    // Listen for parameter changes
    viz.addEventListener(
      window.tableau.TableauEventName.PARAMETER_VALUE_CHANGE,
      (event: any) => {
        if (onParameterChange) {
          const parameterInfo = event.getParameterAsync();
          onParameterChange(parameterInfo);
        }
      }
    );
  };

  const exportToPDF = async () => {
    if (!viz) return;

    try {
      viz.showExportPDFDialog();
    } catch (err) {
      console.error('Error exporting to PDF:', err);
    }
  };

  const exportToImage = async () => {
    if (!viz) return;

    try {
      viz.showExportImageDialog();
    } catch (err) {
      console.error('Error exporting to image:', err);
    }
  };

  const exportToCSV = async () => {
    if (!viz) return;

    try {
      viz.showExportCrossTabDialog();
    } catch (err) {
      console.error('Error exporting to CSV:', err);
    }
  };

  const refreshData = async () => {
    if (!viz) return;

    try {
      await viz.refreshDataAsync();
    } catch (err) {
      console.error('Error refreshing data:', err);
    }
  };

  const revertAll = async () => {
    if (!viz) return;

    try {
      await viz.revertAllAsync();
    } catch (err) {
      console.error('Error reverting:', err);
    }
  };

  if (error) {
    return (
      <div className="flex items-center justify-center h-full bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="text-center">
          <svg
            className="mx-auto h-12 w-12 text-red-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-red-800">Error Loading Dashboard</h3>
          <p className="mt-1 text-sm text-red-600">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative w-full">
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-white bg-opacity-75 z-10">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-sm text-gray-600">Loading Tableau Dashboard...</p>
          </div>
        </div>
      )}

      {!hideToolbar && (
        <div className="flex gap-2 mb-4 p-2 bg-gray-50 rounded-lg">
          <button
            onClick={refreshData}
            className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
            disabled={!viz}
          >
            Refresh Data
          </button>
          <button
            onClick={exportToPDF}
            className="px-3 py-1 text-sm bg-gray-600 text-white rounded hover:bg-gray-700"
            disabled={!viz}
          >
            Export PDF
          </button>
          <button
            onClick={exportToImage}
            className="px-3 py-1 text-sm bg-gray-600 text-white rounded hover:bg-gray-700"
            disabled={!viz}
          >
            Export Image
          </button>
          <button
            onClick={exportToCSV}
            className="px-3 py-1 text-sm bg-gray-600 text-white rounded hover:bg-gray-700"
            disabled={!viz}
          >
            Export CSV
          </button>
          <button
            onClick={revertAll}
            className="px-3 py-1 text-sm bg-gray-600 text-white rounded hover:bg-gray-700"
            disabled={!viz}
          >
            Reset
          </button>
        </div>
      )}

      <div ref={vizRef} className="tableau-viz" style={{ width, height }} />
    </div>
  );
};

export default TableauDashboard;
