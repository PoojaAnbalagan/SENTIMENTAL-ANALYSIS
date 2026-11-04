import React, { useState, useEffect } from 'react';
import { ThemeProvider } from './context/ThemeContext';
import { api } from './services/api';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { 
  LayoutDashboard, Zap, BarChart3, Database, Cpu, FileText, UploadCloud
} from 'lucide-react';

import { OverviewView } from './views/OverviewView';
import { PredictorView } from './views/PredictorView';
import { BatchUploadView } from './views/BatchUploadView';
import { AnalyticsView } from './views/AnalyticsView';
import { ExplorerView } from './views/ExplorerView';
import { ModelPerformanceView } from './views/ModelPerformanceView';
import { ReportsView } from './views/ReportsView';

const BOTTOM_NAV = [
  { id: 'Overview', icon: LayoutDashboard },
  { id: 'Live Predictor', icon: Zap },
  { id: 'Sentiment Analytics', icon: BarChart3 },
  { id: 'Review Explorer', icon: Database },
  { id: 'Reports', icon: FileText },
];

export default function App() {
  const [currentTab, setTab] = useState('Overview');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
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
    }, 8000);
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
      const [m, md, r] = await Promise.all([
        api.getMetrics(),
        api.getModels(),
        api.getReviews(filters, 1, 1)
      ]);
      setMetrics(m);
      setModelsData(md);
      if (r?.stores) {
        setStores(r.stores);
      }
      setIsApiOnline(true);
    } catch (e) {
      console.error('Failed to fetch initial data:', e);
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
        {/* Sidebar (desktop + mobile drawer) */}
        <Sidebar 
          currentTab={currentTab} 
          setTab={setTab} 
          mobileMenuOpen={mobileMenuOpen}
          setMobileMenuOpen={setMobileMenuOpen}
        />

        {/* Main Content Area */}
        <main className="flex-1 min-w-0 p-4 md:p-6 lg:p-8 overflow-y-auto pb-20 md:pb-8">
          {!isApiOnline && (
            <div className="mb-4 p-3 rounded-2xl bg-rose-50 border border-rose-200 text-rose-700 text-xs font-bold flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 animate-pulse">
              <span>⚠️ Backend API is offline. Ensure Python server (`python server.py`) is running on port 8000.</span>
              <button 
                onClick={checkHealth}
                className="px-3 py-1 bg-rose-600 text-white rounded-lg text-[11px] font-extrabold hover:bg-rose-700 shrink-0 touch-manipulation"
              >
                Retry Connection
              </button>
            </div>
          )}

          {/* Hero Header */}
          <Header 
            filteredCount={analytics?.filtered_count || metrics?.total_corpus_count || 22124} 
            totalCount={metrics?.total_corpus_count || 22124} 
            isApiOnline={isApiOnline}
            currentTab={currentTab}
            onMenuToggle={() => setMobileMenuOpen(prev => !prev)}
          />

          {/* Dynamic Tab Views */}
          <div key={currentTab} className="mt-2 animate-tabFadeIn">
            {currentTab === 'Overview' && (
              <OverviewView 
                analytics={analytics} 
                metrics={metrics} 
                filters={filters} 
                setFilters={setFilters} 
                stores={stores} 
              />
            )}
            {currentTab === 'Live Predictor' && <PredictorView />}
            {currentTab === 'Batch Upload' && <BatchUploadView />}
            {currentTab === 'Sentiment Analytics' && (
              <AnalyticsView 
                analytics={analytics} 
                filters={filters} 
                setFilters={setFilters} 
                stores={stores} 
              />
            )}
            {currentTab === 'Review Explorer' && (
              <ExplorerView 
                filters={filters} 
                setFilters={setFilters} 
                stores={stores} 
              />
            )}
            {currentTab === 'Model Performance' && <ModelPerformanceView modelsData={modelsData} />}
            {currentTab === 'Reports' && (
              <ReportsView 
                analytics={analytics} 
                filters={filters} 
                metrics={metrics} 
                setFilters={setFilters} 
                stores={stores} 
              />
            )}
          </div>
        </main>

        {/* ── Mobile Bottom Navigation Bar ── */}
        <nav className="fixed bottom-0 left-0 right-0 z-30 md:hidden bg-[var(--surface)] border-t border-[var(--border)] flex items-center justify-around px-2 py-2 shadow-lg" style={{ paddingBottom: 'max(0.5rem, env(safe-area-inset-bottom))' }}>
          {BOTTOM_NAV.map(({ id, icon: Icon }) => {
            const isActive = currentTab === id;
            return (
              <button
                key={id}
                onClick={() => setTab(id)}
                className={`flex flex-col items-center gap-0.5 px-2 py-1.5 rounded-xl transition-all touch-manipulation ${
                  isActive
                    ? 'text-[var(--accent)] bg-[var(--accent-bg)]'
                    : 'text-[var(--text-muted)]'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span className="text-[9px] font-bold leading-none truncate max-w-[52px]">{id.split(' ')[0]}</span>
              </button>
            );
          })}
          {/* "More" opens the full sidebar drawer */}
          <button
            onClick={() => setMobileMenuOpen(true)}
            className="flex flex-col items-center gap-0.5 px-2 py-1.5 rounded-xl text-[var(--text-muted)] touch-manipulation"
          >
            <UploadCloud className="w-5 h-5" />
            <span className="text-[9px] font-bold leading-none">More</span>
          </button>
        </nav>
      </div>
    </ThemeProvider>
  );
}
