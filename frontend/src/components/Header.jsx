import React from 'react';
import { Sparkles, Database } from 'lucide-react';

export function Header({ filteredCount = 22366, totalCount = 22366, isApiOnline = true }) {
  return (
    <header className="flex flex-col md:flex-row md:items-center justify-between pb-4 mb-6 border-b border-[var(--border)] gap-4">
      <div>
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-extrabold uppercase tracking-wider mb-1.5 bg-[var(--accent-bg)] text-[var(--accent)] border border-[var(--border)]">
          <Sparkles className="w-3.5 h-3.5" /> Customer Review Intelligence
        </div>
        <h1 className="text-2xl font-extrabold tracking-tight text-[var(--text-primary)]">
          AI-Powered Customer Sentiment Analytics Platform
        </h1>
      </div>

      <div className="flex items-center gap-3 self-start md:self-auto">
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

        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-xl border border-[var(--border)] bg-[var(--surface)] shadow-sm text-xs font-extrabold text-[var(--text-primary)]">
          <Database className="w-4 h-4 text-[var(--accent)]" />
          <span>{filteredCount.toLocaleString()}</span> / <span>{totalCount.toLocaleString()}</span> Reviews Analyzed
        </div>
      </div>
    </header>
  );
}
