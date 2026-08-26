import React, { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { BACKEND_URL } from '../services/api';

const METRIC_COLORS = ['#6366f1', '#22c55e', '#f59e0b', '#ef4444'];

export function ModelPerformanceView({ modelsData }) {
  const [selectedMetric, setSelectedMetric] = useState('accuracy');

  // Fallback data matching the actual model_results.csv + VADER from summary.json
  const models = modelsData?.models?.length
    ? modelsData.models
    : [
        { model: 'Logistic Regression',     accuracy: 0.7405, macro_precision: 0.6711, macro_recall: 0.6780, macro_f1: 0.6701 },
        { model: 'Linear SVM',              accuracy: 0.7456, macro_precision: 0.6434, macro_recall: 0.6423, macro_f1: 0.6426 },
        { model: 'Multinomial Naive Bayes', accuracy: 0.7664, macro_precision: 0.7535, macro_recall: 0.5982, macro_f1: 0.5576 },
        { model: 'VADER (Baseline)',         accuracy: 0.6434, macro_precision: 0.5752, macro_recall: 0.5628, macro_f1: 0.5627 },
      ];

  function toPercent(val) {
    const n = parseFloat(val);
    if (isNaN(n)) return 0;
    // Already a percentage (> 1) means it was stored that way
    return parseFloat((n <= 1 ? n * 100 : n).toFixed(2));
  }

  const chartData = models.map((m, i) => ({
    name: m.model,
    score: toPercent(m[selectedMetric]),
    color: METRIC_COLORS[i % METRIC_COLORS.length],
  }));

  const bestModel = [...models].sort((a, b) => toPercent(b[selectedMetric]) - toPercent(a[selectedMetric]))[0];

  const METRICS = [
    { key: 'accuracy',         label: 'Accuracy (%)' },
    { key: 'macro_precision',  label: 'Macro Precision (%)' },
    { key: 'macro_recall',     label: 'Macro Recall (%)' },
    { key: 'macro_f1',         label: 'Macro F1-Score (%)' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-2">
        <div>
          <h2 className="text-xl font-extrabold text-[var(--text-primary)]">Model Performance &amp; Evaluation Metrics</h2>
          <p className="text-xs text-[var(--text-muted)]">
            Comparative benchmarking of supervised ML algorithms trained with balanced class weights vs. unsupervised VADER baseline.
          </p>
        </div>
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-xl bg-[var(--positive-bg)] border border-[var(--positive-border)] text-[var(--positive)] text-[11px] font-bold self-start md:self-auto">
          <span>Cost-Sensitive Balanced Weights Enabled</span>
        </div>
      </div>

      {/* ── Benchmark Table ── */}
      <div className="card-2026 p-5 space-y-4">
        <h3 className="text-xs font-extrabold uppercase tracking-wider text-[var(--text-primary)] pb-2 border-b border-[var(--border)]">
          Comparative Benchmark Metrics Table
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[var(--bg)] text-[var(--text-muted)] uppercase tracking-wider font-extrabold border-b border-[var(--border)]">
              <tr>
                <th className="p-3">Algorithm / Model</th>
                <th className="p-3">Accuracy</th>
                <th className="p-3">Macro Precision</th>
                <th className="p-3">Macro Recall</th>
                <th className="p-3">Macro F1-Score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--border)] text-[var(--text-primary)] font-semibold">
              {models.map((m, i) => {
                const isBest = m.model === bestModel?.model;
                return (
                  <tr
                    key={i}
                    className={`transition-colors ${isBest ? 'bg-[var(--accent-bg)]' : 'hover:bg-[var(--bg)]'}`}
                  >
                    <td className="p-3 font-extrabold text-[var(--accent)] flex items-center gap-2">
                      {m.model}
                      {isBest && (
                        <span className="text-[9px] font-extrabold px-1.5 py-0.5 rounded bg-[var(--positive-bg)] text-[var(--positive)] uppercase">
                          Best
                        </span>
                      )}
                    </td>
                    <td className="p-3">{toPercent(m.accuracy).toFixed(2)}%</td>
                    <td className="p-3">{toPercent(m.macro_precision).toFixed(2)}%</td>
                    <td className="p-3">{toPercent(m.macro_recall).toFixed(2)}%</td>
                    <td className="p-3 font-bold text-[var(--positive)]">{toPercent(m.macro_f1).toFixed(2)}%</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* ── Bar Chart ── */}
      <div className="card-2026 p-5 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-extrabold uppercase tracking-wider text-[var(--text-primary)]">
            Benchmark Metric Comparison
          </h3>
          <select
            value={selectedMetric}
            onChange={(e) => setSelectedMetric(e.target.value)}
            className="bg-[var(--bg)] border border-[var(--border)] text-[var(--text-primary)] text-xs rounded-xl px-3 py-1.5 font-bold focus:outline-none"
          >
            {METRICS.map(m => (
              <option key={m.key} value={m.key}>{m.label}</option>
            ))}
          </select>
        </div>

        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 40 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis
                dataKey="name"
                stroke="var(--text-muted)"
                tick={{ fontSize: 10, fontWeight: 'bold', fill: 'var(--text-secondary)' }}
                angle={-15}
                textAnchor="end"
                interval={0}
              />
              <YAxis
                domain={[0, 100]}
                stroke="var(--text-muted)"
                tick={{ fontSize: 11, fill: 'var(--text-muted)' }}
                tickFormatter={(v) => `${v}%`}
              />
              <Tooltip
                formatter={(v) => [`${v.toFixed(2)}%`, METRICS.find(m => m.key === selectedMetric)?.label]}
                contentStyle={{
                  backgroundColor: 'var(--surface-elevated)',
                  borderColor: 'var(--border)',
                  borderRadius: '12px',
                  color: 'var(--text-primary)',
                  fontSize: '12px'
                }}
              />
              <Bar dataKey="score" radius={[6, 6, 0, 0]}>
                {chartData.map((entry, i) => (
                  <Cell key={i} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* ── Diagnostic Figures ── */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card-2026 p-4 space-y-2">
          <h4 className="text-xs font-extrabold text-[var(--text-primary)]">
            Logistic Regression — Confusion Matrix
          </h4>
          <div className="rounded-xl overflow-hidden bg-[var(--bg)] border border-[var(--border)] p-2">
            <img
              src={`${BACKEND_URL}/static/figures/07_confusion_matrix.png`}
              alt="LR Confusion Matrix"
              className="w-full h-auto max-h-72 object-contain"
              onError={(e) => { e.target.onerror = null; e.target.alt = 'Figure not available'; }}
            />
          </div>
        </div>

        <div className="card-2026 p-4 space-y-2">
          <h4 className="text-xs font-extrabold text-[var(--text-primary)]">
            Top Predictive Terms (Feature Importance)
          </h4>
          <div className="rounded-xl overflow-hidden bg-[var(--bg)] border border-[var(--border)] p-2">
            <img
              src={`${BACKEND_URL}/static/figures/09_top_predictive_words.png`}
              alt="Feature Importance"
              className="w-full h-auto max-h-72 object-contain"
              onError={(e) => { e.target.onerror = null; e.target.alt = 'Figure not available'; }}
            />
          </div>
        </div>

        <div className="card-2026 p-4 space-y-2">
          <h4 className="text-xs font-extrabold text-[var(--text-primary)]">
            Model Comparison Chart
          </h4>
          <div className="rounded-xl overflow-hidden bg-[var(--bg)] border border-[var(--border)] p-2">
            <img
              src={`${BACKEND_URL}/static/figures/08_model_comparison.png`}
              alt="Model Comparison"
              className="w-full h-auto max-h-72 object-contain"
              onError={(e) => { e.target.onerror = null; e.target.alt = 'Figure not available'; }}
            />
          </div>
        </div>

        <div className="card-2026 p-4 space-y-2">
          <h4 className="text-xs font-extrabold text-[var(--text-primary)]">
            VADER Confusion Matrix (Baseline)
          </h4>
          <div className="rounded-xl overflow-hidden bg-[var(--bg)] border border-[var(--border)] p-2">
            <img
              src={`${BACKEND_URL}/static/figures/11_vader_confusion_matrix.png`}
              alt="VADER Confusion Matrix"
              className="w-full h-auto max-h-72 object-contain"
              onError={(e) => { e.target.onerror = null; e.target.alt = 'Figure not available'; }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
