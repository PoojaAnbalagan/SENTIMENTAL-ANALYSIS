import React from 'react';
import { Database, Target, TrendingUp, Award, CheckCircle, MinusCircle, AlertCircle } from 'lucide-react';

export function KpiCards({ metrics, filteredCount, analytics }) {
  const bestAcc = (metrics?.best_accuracy || 0.7405) * 100;
  const bestF1 = (metrics?.best_f1 || 0.6701) * 100;
  const gain = (metrics?.accuracy_gain || 0.0971) * 100;

  const sentimentShares = analytics?.sentiment_share || [
    { name: 'Positive', count: 0, percentage: 0 },
    { name: 'Neutral', count: 0, percentage: 0 },
    { name: 'Negative', count: 0, percentage: 0 },
  ];

  const posData = sentimentShares.find(s => s.name === 'Positive') || { count: 0, percentage: 0 };
  const neuData = sentimentShares.find(s => s.name === 'Neutral') || { count: 0, percentage: 0 };
  const negData = sentimentShares.find(s => s.name === 'Negative') || { count: 0, percentage: 0 };

  return (
    <div className="space-y-4 mb-6">
      {/* KPI Cards Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Card 1 - Filtered Dataset */}
        <div className="kpi-card-2026 border-l-4 border-l-purple-600">
          <div className="w-10 h-10 rounded-xl bg-purple-600/10 text-purple-600 dark:text-purple-400 flex items-center justify-center mb-3">
            <Database className="w-5 h-5" />
          </div>
          <div className="text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)]">Filtered Dataset</div>
          <div className="text-2xl font-extrabold text-[var(--text-primary)] my-1">{filteredCount.toLocaleString()}</div>
          <div className="text-xs text-[var(--text-secondary)] font-medium">Reviews in active scope</div>
        </div>

        {/* Card 2 - Supervised Accuracy */}
        <div className="kpi-card-2026 border-l-4 border-l-teal-500">
          <div className="w-10 h-10 rounded-xl bg-teal-500/10 text-teal-600 dark:text-teal-400 flex items-center justify-center mb-3">
            <Target className="w-5 h-5" />
          </div>
          <div className="text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)]">Supervised Accuracy</div>
          <div className="text-2xl font-extrabold text-[var(--text-primary)] my-1">{bestAcc.toFixed(1)}%</div>
          <div className="text-xs text-[var(--text-secondary)] font-medium">Logistic Regression Classifier</div>
        </div>

        {/* Card 3 - Macro F1-Score */}
        <div className="kpi-card-2026 border-l-4 border-l-emerald-500">
          <div className="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 flex items-center justify-center mb-3">
            <TrendingUp className="w-5 h-5" />
          </div>
          <div className="text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)]">Macro F1-Score</div>
          <div className="text-2xl font-extrabold text-[var(--text-primary)] my-1">{bestF1.toFixed(1)}%</div>
          <div className="text-xs text-[var(--text-secondary)] font-medium">Balanced Multi-Class Metric</div>
        </div>

        {/* Card 4 - Gain vs VADER */}
        <div className="kpi-card-2026 border-l-4 border-l-indigo-500">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 flex items-center justify-center mb-3">
            <Award className="w-5 h-5" />
          </div>
          <div className="text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)]">Gain vs VADER</div>
          <div className="text-2xl font-extrabold text-[var(--text-primary)] my-1">+{gain.toFixed(1)}%</div>
          <div className="text-xs text-[var(--text-secondary)] font-medium">Outperforms Baseline</div>
        </div>
      </div>

      {/* Sentiment Breakdown Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Positive Card */}
        <div className="p-4 rounded-2xl bg-[var(--positive-bg)] border border-[var(--positive-border)]">
          <div className="flex items-center justify-between mb-1">
            <span className="font-bold text-xs flex items-center gap-1.5 text-[var(--positive)]">
              <CheckCircle className="w-4 h-4" /> Positive Sentiment
            </span>
            <span className="font-extrabold text-sm text-[var(--positive)]">{posData.percentage}%</span>
          </div>
          <div className="text-xl font-extrabold text-[var(--text-primary)]">
            {posData.count.toLocaleString()} <span className="text-xs font-semibold text-[var(--text-muted)]">reviews</span>
          </div>
          <div className="w-full h-1.5 bg-black/10 rounded-full overflow-hidden mt-2">
            <div className="h-full bg-[var(--positive)] rounded-full transition-all" style={{ width: `${posData.percentage}%` }} />
          </div>
        </div>

        {/* Neutral Card */}
        <div className="p-4 rounded-2xl bg-[var(--neutral-bg)] border border-[var(--neutral-border)]">
          <div className="flex items-center justify-between mb-1">
            <span className="font-bold text-xs flex items-center gap-1.5 text-[var(--neutral)]">
              <MinusCircle className="w-4 h-4" /> Neutral Sentiment
            </span>
            <span className="font-extrabold text-sm text-[var(--neutral)]">{neuData.percentage}%</span>
          </div>
          <div className="text-xl font-extrabold text-[var(--text-primary)]">
            {neuData.count.toLocaleString()} <span className="text-xs font-semibold text-[var(--text-muted)]">reviews</span>
          </div>
          <div className="w-full h-1.5 bg-black/10 rounded-full overflow-hidden mt-2">
            <div className="h-full bg-[var(--neutral)] rounded-full transition-all" style={{ width: `${neuData.percentage}%` }} />
          </div>
        </div>

        {/* Negative Card */}
        <div className="p-4 rounded-2xl bg-[var(--negative-bg)] border border-[var(--negative-border)]">
          <div className="flex items-center justify-between mb-1">
            <span className="font-bold text-xs flex items-center gap-1.5 text-[var(--negative)]">
              <AlertCircle className="w-4 h-4" /> Negative Sentiment
            </span>
            <span className="font-extrabold text-sm text-[var(--negative)]">{negData.percentage}%</span>
          </div>
          <div className="text-xl font-extrabold text-[var(--text-primary)]">
            {negData.count.toLocaleString()} <span className="text-xs font-semibold text-[var(--text-muted)]">reviews</span>
          </div>
          <div className="w-full h-1.5 bg-black/10 rounded-full overflow-hidden mt-2">
            <div className="h-full bg-[var(--negative)] rounded-full transition-all" style={{ width: `${negData.percentage}%` }} />
          </div>
        </div>
      </div>
    </div>
  );
}
