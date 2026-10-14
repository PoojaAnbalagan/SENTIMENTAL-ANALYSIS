import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { KpiCards } from '../components/KpiCards';
import { FilterBar } from '../components/FilterBar';

export function OverviewView({ analytics, metrics, filters, setFilters, stores }) {
  const sentimentData = analytics?.sentiment_share || [
    { name: 'Positive', count: 0, percentage: 0 },
    { name: 'Neutral', count: 0, percentage: 0 },
    { name: 'Negative', count: 0, percentage: 0 },
  ];

  const COLORS = {
    Positive: 'var(--positive)',
    Neutral: 'var(--neutral)',
    Negative: 'var(--negative)',
  };

  const avgRating = analytics?.average_rating !== undefined ? analytics.average_rating : 0.0;
  const bestAcc = ((metrics?.best_accuracy || 0.8569) * 100).toFixed(1);
  const gain = ((metrics?.accuracy_gain || 0.2398) * 100).toFixed(1);
  const bestModelName = metrics?.best_model_name || 'Logistic Regression (Balanced)';
  const totalReviews = (metrics?.total_corpus_count || 22124).toLocaleString();
  const filteredCount = analytics?.filtered_count || metrics?.total_corpus_count || 0;

  return (
    <div className="space-y-6">
      {/* Dynamic KPI Cards */}
      <KpiCards 
        metrics={metrics} 
        filteredCount={filteredCount} 
        analytics={analytics} 
      />

      {/* Dynamic Filter Controls */}
      {filters && setFilters && (
        <FilterBar 
          filters={filters} 
          setFilters={setFilters} 
          stores={stores} 
          matchingCount={filteredCount} 
        />
      )}

      {/* Main Charts & Overview Row */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        {/* Sentiment Donut Chart */}
        <div className="md:col-span-7 card-2026 p-5">
          <h3 className="text-sm font-bold text-[var(--text-primary)] mb-3">Sentiment Distribution Share</h3>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={sentimentData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={88}
                  paddingAngle={4}
                  dataKey="count"
                >
                  {sentimentData.map((entry) => (
                    <Cell key={entry.name} fill={COLORS[entry.name] || 'var(--accent)'} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'var(--surface-elevated)', 
                    borderColor: 'var(--border)',
                    borderRadius: '12px',
                    color: 'var(--text-primary)',
                    fontSize: '12px',
                    fontWeight: 'bold'
                  }} 
                />
                <Legend 
                  formatter={(value) => <span className="text-xs font-bold text-[var(--text-primary)]">{value}</span>}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Sentiment Health Gauge */}
          <div className="pt-3 border-t border-[var(--border)]">
            <div className="flex justify-between items-center text-xs font-bold mb-1.5">
              <span className="text-[var(--text-muted)] uppercase tracking-wider text-[10px]">Sentiment Spectrum Ratio</span>
              <span className="text-[var(--positive)] font-extrabold">
                {(sentimentData.find(s => s.name === 'Positive')?.percentage || 0)}% Positive Ratio
              </span>
            </div>
            <div className="w-full h-3 bg-black/10 rounded-full overflow-hidden flex">
              {sentimentData.map((s) => (
                <div 
                  key={s.name} 
                  style={{ width: `${s.percentage}%`, backgroundColor: COLORS[s.name] }}
                  title={`${s.name}: ${s.percentage}%`}
                  className="h-full transition-all"
                />
              ))}
            </div>
          </div>
        </div>

        {/* Key Project Insights */}
        <div className="md:col-span-5 card-2026 p-5 space-y-4">
          <h3 className="text-sm font-bold text-[var(--text-primary)] pb-2 border-b border-[var(--border)]">
            Key Project Insights
          </h3>

          <div className="space-y-3.5 text-xs">
            <div className="flex justify-between items-center pb-2 border-b border-[var(--border)]">
              <span className="font-semibold text-[var(--text-primary)]">Average Customer Rating</span>
              <span className="font-extrabold text-[var(--accent)] text-sm">{avgRating} / 5.0 Stars</span>
            </div>

            <div className="flex justify-between items-center pb-2 border-b border-[var(--border)]">
              <span className="font-semibold text-[var(--text-primary)]">Supervised vs Baseline Gain</span>
              <span className="font-extrabold text-[var(--positive)] text-sm">+{gain}% Accuracy</span>
            </div>

            <div className="flex justify-between items-center pb-2 border-b border-[var(--border)]">
              <span className="font-semibold text-[var(--text-primary)]">Champion Model</span>
              <span className="font-extrabold text-[var(--accent)] text-xs">{bestModelName}</span>
            </div>

            <div className="flex justify-between items-center pb-2 border-b border-[var(--border)]">
              <span className="font-semibold text-[var(--text-primary)]">Class Balance Strategy</span>
              <span className="font-extrabold text-[var(--positive)] text-xs">Stratified Split + Cost-Sensitive Loss</span>
            </div>

            <div className="flex justify-between items-center pb-2 border-b border-[var(--border)]">
              <span className="font-semibold text-[var(--text-primary)]">Primary Complaint Drivers</span>
              <span className="font-extrabold text-[var(--negative)] text-xs">Drive-thru delay, Cold food</span>
            </div>

            <div className="flex justify-between items-center">
              <span className="font-semibold text-[var(--text-primary)]">Evaluated Corpus Size</span>
              <span className="font-extrabold text-[var(--text-secondary)]">{totalReviews} Cleaned Reviews</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
