import React from 'react';
import { Filter, Calendar, Search, Store, X, RotateCcw } from 'lucide-react';

export function FilterBar({ filters, setFilters, stores = [], matchingCount = 0 }) {
  const dateOptions = ['All Time', 'Last 7 Days', 'Last 30 Days', 'Last 90 Days', 'Last 6 Months', 'Last 12 Months'];
  const sentiments = ['Positive', 'Neutral', 'Negative'];
  const ratings = [1, 2, 3, 4, 5];

  const toggleSentiment = (s) => {
    const active = filters.sentiments || [];
    const next = active.includes(s) ? active.filter(item => item !== s) : [...active, s];
    setFilters({ ...filters, sentiments: next });
  };

  const toggleRating = (r) => {
    const active = filters.ratings || [];
    const next = active.includes(r) ? active.filter(item => item !== r) : [...active, r];
    setFilters({ ...filters, ratings: next });
  };

  const resetFilters = () => {
    setFilters({
      dateRange: 'All Time',
      sentiments: ['Positive', 'Neutral', 'Negative'],
      ratings: [1, 2, 3, 4, 5],
      store: 'All Stores',
      search: ''
    });
  };

  // Build active filter chips list
  const activeChips = [];
  if (filters.dateRange !== 'All Time') activeChips.push({ label: `Date: ${filters.dateRange}`, type: 'date' });
  if (filters.sentiments?.length < 3) activeChips.push({ label: `Sentiments: ${filters.sentiments.join(', ')}`, type: 'sentiment' });
  if (filters.ratings?.length < 5) activeChips.push({ label: `Ratings: ${filters.ratings.join(', ')} Stars`, type: 'rating' });
  if (filters.store && filters.store !== 'All Stores') activeChips.push({ label: `Store: ${filters.store}`, type: 'store' });
  if (filters.search) activeChips.push({ label: `Search: "${filters.search}"`, type: 'search' });

  return (
    <div className="card-2026 p-4 mb-6 space-y-4">
      <div className="flex items-center justify-between border-b border-[var(--border)] pb-3">
        <div className="flex items-center gap-2 text-xs font-extrabold uppercase tracking-wider text-[var(--text-primary)]">
          <Filter className="w-4 h-4 text-[var(--accent)]" /> Global Analytics Filters
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs font-bold text-[var(--accent)] bg-[var(--accent-bg)] px-2.5 py-1 rounded-lg border border-[var(--border)]">
            {matchingCount.toLocaleString()} matching reviews
          </span>
          {activeChips.length > 0 && (
            <button
              onClick={resetFilters}
              className="flex items-center gap-1 text-xs font-bold text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5" /> Reset Filters
            </button>
          )}
        </div>
      </div>

      {/* Filter Options Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-xs">
        {/* Date Range Selector */}
        <div>
          <label className="block font-bold text-[var(--text-muted)] mb-1 flex items-center gap-1">
            <Calendar className="w-3.5 h-3.5" /> Date Range
          </label>
          <select
            value={filters.dateRange || 'All Time'}
            onChange={(e) => setFilters({ ...filters, dateRange: e.target.value })}
            className="w-full bg-[var(--bg)] border border-[var(--border)] text-[var(--text-primary)] rounded-xl px-3 py-2 font-medium focus:outline-none focus:border-[var(--accent)]"
          >
            {dateOptions.map(opt => <option key={opt} value={opt}>{opt}</option>)}
          </select>
        </div>

        {/* Sentiment Multiselect Chips */}
        <div>
          <label className="block font-bold text-[var(--text-muted)] mb-1">Sentiment Scope</label>
          <div className="flex flex-wrap gap-1">
            {sentiments.map(s => {
              const isSel = (filters.sentiments || []).includes(s);
              return (
                <button
                  key={s}
                  onClick={() => toggleSentiment(s)}
                  className={`px-2.5 py-1.5 rounded-lg font-bold text-[11px] border transition-all ${
                    isSel 
                      ? 'bg-[var(--accent-bg)] border-[var(--accent)] text-[var(--accent)] shadow-sm'
                      : 'bg-[var(--bg)] border-[var(--border)] text-[var(--text-muted)] hover:text-[var(--text-primary)]'
                  }`}
                >
                  {s}
                </button>
              );
            })}
          </div>
        </div>

        {/* Rating Multiselect Buttons */}
        <div>
          <label className="block font-bold text-[var(--text-muted)] mb-1">Star Ratings</label>
          <div className="flex gap-1">
            {ratings.map(r => {
              const isSel = (filters.ratings || []).includes(r);
              return (
                <button
                  key={r}
                  onClick={() => toggleRating(r)}
                  className={`w-7 h-7 rounded-lg font-bold text-xs flex items-center justify-center border transition-all ${
                    isSel 
                      ? 'bg-[var(--accent-bg)] border-[var(--accent)] text-[var(--accent)] shadow-sm'
                      : 'bg-[var(--bg)] border-[var(--border)] text-[var(--text-muted)]'
                  }`}
                >
                  {r}★
                </button>
              );
            })}
          </div>
        </div>

        {/* Search Keyword */}
        <div>
          <label className="block font-bold text-[var(--text-muted)] mb-1 flex items-center gap-1">
            <Search className="w-3.5 h-3.5" /> Search Keyword
          </label>
          <input
            type="text"
            placeholder="e.g. cold fries, fast service"
            value={filters.search || ''}
            onChange={(e) => setFilters({ ...filters, search: e.target.value })}
            className="w-full bg-[var(--bg)] border border-[var(--border)] text-[var(--text-primary)] rounded-xl px-3 py-1.5 font-medium focus:outline-none focus:border-[var(--accent)]"
          />
        </div>
      </div>

      {/* Removable Active Filter Chips */}
      {activeChips.length > 0 && (
        <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-[var(--border)]">
          <span className="text-[11px] font-bold text-[var(--text-muted)]">Active Filters:</span>
          {activeChips.map((chip, i) => (
            <span key={i} className="filter-chip">
              {chip.label}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
