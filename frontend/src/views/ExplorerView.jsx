import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Download, ChevronLeft, ChevronRight, Eye, MapPin } from 'lucide-react';

export function ExplorerView({ filters }) {
  const [reviewsData, setReviewsData] = useState({ reviews: [], total_filtered: 0, stores: [] });
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [sortBy, setSortBy] = useState('Newest First');
  const [selectedReview, setSelectedReview] = useState(null);
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    fetchReviews();
  }, [filters, page, sortBy]);

  const fetchReviews = async () => {
    setLoading(true);
    try {
      const data = await api.getReviews(filters, page, 20, sortBy);
      setReviewsData(data);
      if (data.reviews?.length > 0 && !selectedReview) {
        setSelectedReview(data.reviews[0]);
      }
    } catch (err) {
      console.error('Failed to fetch reviews:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadCSV = async () => {
    setDownloading(true);
    try {
      const url = api.getExportUrl(filters);
      const response = await fetch(url);
      if (!response.ok) throw new Error('Export failed');
      const blob = await response.blob();
      const blobUrl = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = blobUrl;
      link.download = 'mcdonalds_filtered_reviews.csv';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(blobUrl);
    } catch (err) {
      console.error('CSV download failed:', err);
      alert('Export failed. Make sure the backend server is running at http://localhost:8000');
    } finally {
      setDownloading(false);
    }
  };

  const totalPages = Math.ceil((reviewsData.total_filtered || 0) / 20);

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-extrabold text-[var(--text-primary)]">Review Dataset Explorer</h2>
          <p className="text-xs text-[var(--text-muted)]">Search, sort, filter, and inspect individual customer reviews.</p>
        </div>

        <div className="flex items-center gap-3">
          <select
            value={sortBy}
            onChange={(e) => { setSortBy(e.target.value); setPage(1); }}
            className="bg-[var(--bg)] border border-[var(--border)] text-[var(--text-primary)] text-xs rounded-xl px-3 py-2 font-bold focus:outline-none"
          >
            <option value="Newest First">Newest First</option>
            <option value="Oldest First">Oldest First</option>
            <option value="Highest Rating">Highest Rating</option>
            <option value="Lowest Rating">Lowest Rating</option>
          </select>

          <button
            onClick={handleDownloadCSV}
            disabled={downloading}
            className="flex items-center gap-2 btn-primary px-3.5 py-2 text-xs disabled:opacity-60 disabled:cursor-wait"
          >
            <Download className="w-4 h-4" />
            {downloading ? 'Downloading…' : 'Download CSV'}
          </button>
        </div>
      </div>

      {/* Main Content Layout */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        {/* Review Data Table */}
        <div className="md:col-span-8 card-2026 p-5 space-y-4">
          <div className="flex items-center justify-between text-xs font-bold text-[var(--text-muted)] pb-2 border-b border-[var(--border)]">
            <span>
              {loading ? 'Loading…' : `Displaying ${reviewsData.reviews?.length || 0} of ${reviewsData.total_filtered?.toLocaleString() || 0} reviews`}
            </span>
            <span>Page {page} of {totalPages || 1}</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[var(--bg)] text-[var(--text-muted)] uppercase tracking-wider font-extrabold border-b border-[var(--border)]">
                <tr>
                  <th className="p-3">Store</th>
                  <th className="p-3">Rating</th>
                  <th className="p-3">Sentiment</th>
                  <th className="p-3">Review Preview</th>
                  <th className="p-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--border)] text-[var(--text-primary)]">
                {loading ? (
                  <tr>
                    <td colSpan={5} className="p-6 text-center text-[var(--text-muted)]">Loading reviews…</td>
                  </tr>
                ) : reviewsData.reviews?.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="p-6 text-center text-[var(--text-muted)]">No reviews match your filters.</td>
                  </tr>
                ) : reviewsData.reviews?.map((row, i) => (
                  <tr key={i} className="hover:bg-[var(--bg)] transition-colors cursor-pointer" onClick={() => setSelectedReview(row)}>
                    <td className="p-3 font-bold truncate max-w-[120px]">{row.store_name || 'N/A'}</td>
                    <td className="p-3 font-extrabold text-[var(--accent)]">{row.rating_num}★</td>
                    <td className="p-3">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-extrabold ${
                        row.sentiment === 'Positive' ? 'bg-[var(--positive-bg)] text-[var(--positive)]' :
                        row.sentiment === 'Neutral' ? 'bg-[var(--neutral-bg)] text-[var(--neutral)]' :
                        'bg-[var(--negative-bg)] text-[var(--negative)]'
                      }`}>
                        {row.sentiment}
                      </span>
                    </td>
                    <td className="p-3 truncate max-w-[220px] text-[var(--text-secondary)]">"{row.review_clean}"</td>
                    <td className="p-3 text-right">
                      <button
                        onClick={(e) => { e.stopPropagation(); setSelectedReview(row); }}
                        className="p-1.5 rounded-lg bg-[var(--accent-bg)] text-[var(--accent)] hover:bg-[var(--accent)] hover:text-white transition-all"
                      >
                        <Eye className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination Controls */}
          <div className="flex items-center justify-between pt-3 border-t border-[var(--border)] text-xs">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="flex items-center gap-1 px-3 py-1.5 rounded-xl border border-[var(--border)] bg-[var(--bg)] font-bold text-[var(--text-primary)] disabled:opacity-40"
            >
              <ChevronLeft className="w-4 h-4" /> Previous
            </button>
            <span className="font-bold text-[var(--text-muted)]">Page {page} / {totalPages || 1}</span>
            <button
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages}
              className="flex items-center gap-1 px-3 py-1.5 rounded-xl border border-[var(--border)] bg-[var(--bg)] font-bold text-[var(--text-primary)] disabled:opacity-40"
            >
              Next <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Selected Review Inspector */}
        <div className="md:col-span-4 card-2026 p-5 space-y-4">
          <h3 className="text-xs font-extrabold uppercase tracking-wider text-[var(--text-primary)] pb-2 border-b border-[var(--border)]">
            Detailed Review Inspector
          </h3>

          {selectedReview ? (
            <div className="space-y-4 text-xs">
              <div className="p-3 rounded-xl bg-[var(--bg)] border border-[var(--border)] space-y-2">
                <div className="flex justify-between items-center font-bold">
                  <span className="text-[var(--text-muted)]">Reviewer ID:</span>
                  <span className="text-[var(--text-primary)]">{selectedReview.reviewer_id || 'N/A'}</span>
                </div>
                <div className="flex justify-between items-center font-bold">
                  <span className="text-[var(--text-muted)]">Rating:</span>
                  <span className="text-[var(--accent)] font-extrabold">{selectedReview.rating_num} / 5 Stars</span>
                </div>
                <div className="flex justify-between items-center font-bold">
                  <span className="text-[var(--text-muted)]">Sentiment:</span>
                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-extrabold ${
                    selectedReview.sentiment === 'Positive' ? 'bg-[var(--positive-bg)] text-[var(--positive)]' :
                    selectedReview.sentiment === 'Neutral' ? 'bg-[var(--neutral-bg)] text-[var(--neutral)]' :
                    'bg-[var(--negative-bg)] text-[var(--negative)]'
                  }`}>
                    {selectedReview.sentiment}
                  </span>
                </div>
                {selectedReview.label_source && (
                  <div className="flex justify-between items-center font-bold">
                    <span className="text-[var(--text-muted)]">Label Source:</span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-extrabold ${
                      selectedReview.label_source === 'human_annotated'
                        ? 'bg-purple-100 text-purple-700 dark:bg-purple-950 dark:text-purple-300'
                        : 'bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-300'
                    }`}>
                      {selectedReview.label_source === 'human_annotated' ? 'Human Pilot Gold' : 'Model Pseudo-Label'}
                    </span>
                  </div>
                )}
                {selectedReview.prediction_confidence !== undefined && (
                  <div className="flex justify-between items-center font-bold">
                    <span className="text-[var(--text-muted)]">Confidence:</span>
                    <span className="text-[var(--text-primary)]">
                      {(selectedReview.prediction_confidence * 100).toFixed(1)}%
                    </span>
                  </div>
                )}
                {selectedReview.derived_date && (
                  <div className="flex justify-between items-center font-bold">
                    <span className="text-[var(--text-muted)]">Date:</span>
                    <span className="text-[var(--text-secondary)]">{selectedReview.derived_date}</span>
                  </div>
                )}
              </div>

              <div>
                <label className="block text-[11px] font-bold text-[var(--text-muted)] uppercase tracking-wider mb-1">
                  Full Customer Review
                </label>
                <div className="p-3 rounded-xl bg-[var(--surface-elevated)] border border-[var(--border)] text-[var(--text-primary)] italic font-medium leading-relaxed">
                  "{selectedReview.review_clean}"
                </div>
              </div>

              {selectedReview.store_address && (
                <div className="flex items-start gap-2 p-2.5 rounded-xl bg-[var(--bg)] text-[var(--text-muted)] text-[11px]">
                  <MapPin className="w-4 h-4 text-[var(--accent)] shrink-0 mt-0.5" />
                  <span>{selectedReview.store_address}</span>
                </div>
              )}
            </div>
          ) : (
            <p className="text-xs text-[var(--text-muted)] text-center py-10">Select a review from the table to inspect details.</p>
          )}
        </div>
      </div>
    </div>
  );
}
