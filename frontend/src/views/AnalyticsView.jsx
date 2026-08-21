import React, { useState } from 'react';
import { 
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend,
  BarChart, Bar, XAxis, YAxis, CartesianGrid
} from 'recharts';
import { Image as ImageIcon, BarChart3 } from 'lucide-react';
import { BACKEND_URL } from '../services/api';

export function AnalyticsView({ analytics }) {
  const [activeTab, setActiveTab] = useState('interactive');

  const sentimentData = analytics?.sentiment_share || [
    { name: 'Positive', count: 0, percentage: 0 },
    { name: 'Neutral', count: 0, percentage: 0 },
    { name: 'Negative', count: 0, percentage: 0 },
  ];

  const ratingData = analytics?.rating_breakdown || [];
  const topStores = analytics?.top_stores || [];

  const figFiles = [
    { name: '01_sentiment_rating_dist.png', title: 'Sentiment Rating Distribution' },
    { name: '02_length_by_sentiment.png', title: 'Review Length Distribution' },
    { name: '03_autotag_share.png', title: 'Auto-Tag Share Analysis' },
    { name: '04_sentiment_over_time.png', title: 'Sentiment Over Time Trends' },
    { name: '05_wordclouds.png', title: 'Sentiment Word Clouds' },
    { name: '06_top_bigrams.png', title: 'Top N-Gram Bigrams' }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-extrabold text-[var(--text-primary)]">Interactive Sentiment Analytics</h2>
        <p className="text-xs text-[var(--text-muted)]">Deep-dive analytics on review sentiment distributions, star ratings, and store volume.</p>
      </div>

      {/* View Switcher Tabs */}
      <div className="flex border-b border-[var(--border)]">
        <button
          onClick={() => setActiveTab('interactive')}
          className={`flex items-center gap-2 px-4 py-2.5 text-xs font-bold border-b-2 transition-all ${
            activeTab === 'interactive'
              ? 'border-[var(--accent)] text-[var(--accent)] font-extrabold'
              : 'border-transparent text-[var(--text-muted)] hover:text-[var(--text-primary)]'
          }`}
        >
          <BarChart3 className="w-4 h-4" /> Interactive Visualizations
        </button>
        <button
          onClick={() => setActiveTab('figures')}
          className={`flex items-center gap-2 px-4 py-2.5 text-xs font-bold border-b-2 transition-all ${
            activeTab === 'figures'
              ? 'border-[var(--accent)] text-[var(--accent)] font-extrabold'
              : 'border-transparent text-[var(--text-muted)] hover:text-[var(--text-primary)]'
          }`}
        >
          <ImageIcon className="w-4 h-4" /> Diagnostic Figures Gallery
        </button>
      </div>

      {activeTab === 'interactive' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Chart 1: Sentiment Donut */}
          <div className="card-2026 p-5">
            <h3 className="text-xs font-extrabold uppercase tracking-wider text-[var(--text-primary)] mb-3">
              Sentiment Share Breakdown
            </h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={sentimentData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={90}
                    paddingAngle={4}
                    dataKey="count"
                  >
                    <Cell fill="var(--positive)" />
                    <Cell fill="var(--neutral)" />
                    <Cell fill="var(--negative)" />
                  </Pie>
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'var(--surface-elevated)', 
                      borderColor: 'var(--border)',
                      borderRadius: '12px',
                      color: 'var(--text-primary)',
                      fontSize: '12px'
                    }} 
                  />
                  <Legend formatter={(val) => <span className="text-xs font-bold text-[var(--text-primary)]">{val}</span>} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Chart 2: Rating Breakdown */}
          <div className="card-2026 p-5">
            <h3 className="text-xs font-extrabold uppercase tracking-wider text-[var(--text-primary)] mb-3">
              Sentiment Breakdown by Star Rating
            </h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={ratingData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                  <XAxis dataKey="rating" stroke="var(--text-muted)" tick={{ fontSize: 11, fontWeight: 'bold' }} />
                  <YAxis stroke="var(--text-muted)" tick={{ fontSize: 11, fontWeight: 'bold' }} />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'var(--surface-elevated)', 
                      borderColor: 'var(--border)',
                      borderRadius: '12px',
                      color: 'var(--text-primary)',
                      fontSize: '12px'
                    }} 
                  />
                  <Bar dataKey="Positive" fill="var(--positive)" stackId="a" radius={[0, 0, 0, 0]} />
                  <Bar dataKey="Neutral" fill="var(--neutral)" stackId="a" radius={[0, 0, 0, 0]} />
                  <Bar dataKey="Negative" fill="var(--negative)" stackId="a" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Chart 3: Top Stores Volume */}
          <div className="md:col-span-2 card-2026 p-5">
            <div className="flex justify-between items-center mb-3">
              <h3 className="text-xs font-extrabold uppercase tracking-wider text-[var(--text-primary)]">
                Top Store Locations by Review Volume
              </h3>
              <span className="text-[11px] font-semibold text-[var(--text-muted)]">
                Hover bar to view full store address
              </span>
            </div>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={topStores} layout="vertical" margin={{ left: 10, right: 30, top: 10, bottom: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" horizontal={false} />
                  <XAxis type="number" stroke="var(--text-muted)" tick={{ fontSize: 11, fontWeight: '600' }} />
                  <YAxis 
                    dataKey="store" 
                    type="category" 
                    stroke="var(--text-muted)" 
                    tick={{ fontSize: 11, fontWeight: '700', fill: 'var(--text-secondary)' }} 
                    width={210} 
                    tickFormatter={(val) => {
                      if (!val) return '';
                      const parts = val.split(',');
                      if (parts.length >= 2) return `${parts[0].trim()}, ${parts[1].trim()}`;
                      return val.length > 26 ? val.substring(0, 24) + '…' : val;
                    }}
                  />
                  <Tooltip 
                    formatter={(val) => [`${val.toLocaleString()} Reviews`, 'Review Count']}
                    labelFormatter={(label) => `📍 ${label}`}
                    contentStyle={{ 
                      backgroundColor: 'var(--surface)', 
                      borderColor: 'var(--border)',
                      borderRadius: '12px',
                      color: 'var(--text-primary)',
                      fontSize: '12px',
                      fontWeight: 'bold',
                      boxShadow: 'var(--shadow)',
                      maxWidth: '340px'
                    }} 
                  />
                  <Bar dataKey="count" fill="var(--accent)" radius={[0, 6, 6, 0]} barSize={20} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {figFiles.map((fig, i) => (
            <div key={i} className="card-2026 p-4 space-y-2">
              <h4 className="text-xs font-extrabold text-[var(--text-primary)]">{fig.title}</h4>
              <div className="rounded-xl overflow-hidden bg-[var(--bg)] border border-[var(--border)] p-2">
                <img 
                  src={`${BACKEND_URL}/static/figures/${fig.name}`} 
                  alt={fig.title} 
                  className="w-full h-auto object-contain max-h-72"
                  onError={(e) => { e.target.onerror = null; e.target.src = 'https://via.placeholder.com/500x300?text=Diagnostic+Figure'; }}
                />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
