import React, { useState, useEffect } from 'react';
import { ThemeProvider } from './context/ThemeContext';
import { api } from './services/api';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { KpiCards } from './components/KpiCards';
import { FilterBar } from './components/FilterBar';

import { OverviewView } from './views/OverviewView';
import { PredictorView } from './views/PredictorView';
import { AnalyticsView } from './views/AnalyticsView';
import { ExplorerView } from './views/ExplorerView';
import { ModelPerformanceView } from './views/ModelPerformanceView';
import { ReportsView } from './views/ReportsView';
import { ProjectInfoView } from './views/ProjectInfoView';

export default function App() {
  const [currentTab, setTab] = useState('Overview');
  const [metrics, setMetrics] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [modelsData, setModelsData] = useState(null);
  const [stores, setStores] = useState([]);
  const [isApiOnline, setIsApiOnline] = useState(true);

  // Global Filter State
  const [filters, setFilters] = useState({
    dateRange: 'All Time',
    sentiments: ['Positive', 'Neutral', 'Negative'],
    ratings: [1, 2, 3, 4, 5],
    store: 'All Stores',
    search: ''
  });

  useEffect(() => {
    checkHealth();
    fetchInitialData();
    const timer = setInterval(() => {
      checkHealth();
    }, 5000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    fetchAnalyticsData();
  }, [filters]);

  const checkHealth = async () => {
    try {
      await api.getHealth();
      setIsApiOnline(true);
    } catch (e) {
      setIsApiOnline(false);
    }
  };

  const fetchInitialData = async () => {
    try {
      const [m, md] = await Promise.all([
        api.getMetrics(),
        api.getModels()
      ]);
      setMetrics(m);
      setModelsData(md);
      setIsApiOnline(true);
    } catch (e) {
      console.error('Failed to fetch metrics:', e);
      setIsApiOnline(false);
    }
  };

  const fetchAnalyticsData = async () => {
    try {
      const a = await api.getAnalytics(filters);
      setAnalytics(a);
      setIsApiOnline(true);
    } catch (e) {
      console.error('Failed to fetch analytics:', e);
      setIsApiOnline(false);
    }
  };

  return (
    <ThemeProvider>
      <div className="flex min-h-screen">
        {/* Sidebar */}
        <Sidebar currentTab={currentTab} setTab={setTab} />

        {/* Main Content Area */}
        <main className="flex-1 p-6 md:p-8 overflow-y-auto">
          {!isApiOnline && (
            <div className="mb-4 p-3 rounded-2xl bg-rose-50 border border-rose-200 text-rose-700 text-xs font-bold flex items-center justify-between animate-pulse">
              <span>⚠️ Backend API is offline. Ensure Python server (`python server.py`) is running on port 8000.</span>
              <button 
                onClick={checkHealth}
                className="px-3 py-1 bg-rose-600 text-white rounded-lg text-[11px] font-extrabold hover:bg-rose-700"
              >
                Retry Connection
              </button>
            </div>
          )}

          {/* Hero Header */}
          <Header 
            filteredCount={analytics?.filtered_count || metrics?.total_corpus_count || 22366} 
            totalCount={metrics?.total_corpus_count || 22366} 
            isApiOnline={isApiOnline}
          />

          {/* KPI & Sentiment Cards */}
          <KpiCards 
            metrics={metrics} 
            filteredCount={analytics?.filtered_count || 22366} 
            analytics={analytics} 
          />

          {/* Global Filter Bar */}
          <FilterBar 
            filters={filters} 
            setFilters={setFilters} 
            stores={stores} 
            matchingCount={analytics?.filtered_count || 0} 
          />

          {/* Dynamic Tab Views */}
          <div className="mt-6">
            {currentTab === 'Overview' && <OverviewView analytics={analytics} metrics={metrics} />}
            {currentTab === 'Live Predictor' && <PredictorView />}
            {currentTab === 'Sentiment Analytics' && <AnalyticsView analytics={analytics} />}
            {currentTab === 'Review Explorer' && <ExplorerView filters={filters} />}
            {currentTab === 'Model Performance' && <ModelPerformanceView modelsData={modelsData} />}
            {currentTab === 'Reports' && <ReportsView analytics={analytics} filters={filters} metrics={metrics} />}
            {currentTab === 'Project Information' && <ProjectInfoView />}
          </div>
        </main>
      </div>
    </ThemeProvider>
  );
}
