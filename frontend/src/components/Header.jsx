import React from 'react';
import { Sparkles, Menu } from 'lucide-react';

const TAB_TITLES = {
  'Overview': 'AI-Powered Customer Sentiment Analytics Platform',
  'Live Predictor': 'Multi-Model Sentiment Inference & Head-to-Head Sandbox',
  'Batch Upload': 'Batch Review Processing & Dataset Intelligence',
  'Sentiment Analytics': 'Interactive Sentiment Analytics',
  'Review Explorer': 'Review Dataset Explorer',
  'Model Performance': 'Model Performance & Evaluation Metrics',
  'Reports': 'Executive Review Intelligence Report',
};

// Mobile-shortened titles for small screens
const TAB_TITLES_SHORT = {
  'Overview': 'Sentiment Analytics',
  'Live Predictor': 'Live Predictor',
  'Batch Upload': 'Batch Upload',
  'Sentiment Analytics': 'Analytics',
  'Review Explorer': 'Review Explorer',
  'Model Performance': 'Model Performance',
  'Reports': 'Reports',
};

export function Header({ isApiOnline = true, currentTab = 'Overview', onMenuToggle }) {
  const isOverview = currentTab === 'Overview';
  const title = TAB_TITLES[currentTab] || currentTab;
  const titleShort = TAB_TITLES_SHORT[currentTab] || currentTab;

  return (
    <header className="pb-4 mb-6 border-b border-[var(--border)]">
      {/* Top Row: Hamburger (mobile) + Mobile Title + API Status (Mobile Only) */}
      <div className="flex md:hidden items-center justify-between gap-3 mb-3">
        {/* Hamburger – mobile only */}
        <button
          onClick={onMenuToggle}
          className="p-2 rounded-xl border border-[var(--border)] bg-[var(--surface)] text-[var(--text-primary)] hover:bg-[var(--bg)] transition-all touch-manipulation shrink-0"
          aria-label="Open navigation menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Mobile title */}
        <div className="flex-1 min-w-0">
          <h1 className="text-base font-extrabold tracking-tight text-[var(--text-primary)] truncate">
            {titleShort}
          </h1>
        </div>

        {/* Status badge (mobile) */}
        <div className={`inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl border shadow-sm text-xs font-bold transition-all shrink-0 ${
          isApiOnline 
            ? 'border-[var(--positive-border)] bg-[var(--positive-bg)] text-[var(--positive)]' 
            : 'border-[var(--negative-border)] bg-[var(--negative-bg)] text-[var(--negative)]'
        }`}>
          <span className="relative flex h-2.5 w-2.5 shrink-0">
            {isApiOnline ? (
              <>
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
              </>
            ) : (
              <>
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-rose-500"></span>
              </>
            )}
          </span>
          <span className="text-[11px] font-extrabold hidden sm:inline">
            {isApiOnline ? 'API Online' : 'API Offline'}
          </span>
          <span className="text-[11px] font-extrabold sm:hidden">
            {isApiOnline ? '●' : '✕'}
          </span>
        </div>
      </div>

      {/* Full title row – desktop only */}
      <div key={currentTab} className="hidden md:flex md:items-center md:justify-between md:gap-4 animate-headerFadeIn">
        <div>
          {isOverview && (
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-extrabold uppercase tracking-wider mb-1.5 bg-[var(--accent-bg)] text-[var(--accent)] border border-[var(--border)]">
              <Sparkles className="w-3.5 h-3.5" /> Customer Review Intelligence
            </div>
          )}
          <h1 className="text-2xl font-extrabold tracking-tight text-[var(--text-primary)]">
            {title}
          </h1>
        </div>

        <div className="flex items-center gap-3">
          <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-xl border shadow-sm text-xs font-bold transition-all ${
            isApiOnline 
              ? 'border-[var(--positive-border)] bg-[var(--positive-bg)] text-[var(--positive)]' 
              : 'border-[var(--negative-border)] bg-[var(--negative-bg)] text-[var(--negative)]'
          }`}>
            <span className="relative flex h-2.5 w-2.5">
              {isApiOnline ? (
                <>
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
                </>
              ) : (
                <>
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-rose-500"></span>
                </>
              )}
            </span>
            <span className="text-[11px] font-extrabold">
              {isApiOnline ? 'API Online' : 'API Offline (Backend Down)'}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}
