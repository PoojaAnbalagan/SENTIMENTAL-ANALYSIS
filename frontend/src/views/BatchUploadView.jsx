import React, { useState, useRef } from 'react';
import { api } from '../services/api';
import { 
  UploadCloud, FileSpreadsheet, Download, RefreshCw, CheckCircle, 
  AlertCircle, Sparkles, TrendingUp, Target, Database, Eye, FileText,
  Clock, ThumbsDown, ThumbsUp, Layers, ChevronLeft, ChevronRight,
  BrainCircuit
} from 'lucide-react';
import { 
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend,
  BarChart, Bar, XAxis, YAxis, CartesianGrid
} from 'recharts';

export function BatchUploadView() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isSampleFile, setIsSampleFile] = useState(false);
  const [modelType, setModelType] = useState('logistic_regression');
  const [loading, setLoading] = useState(false);
  const [batchResult, setBatchResult] = useState(null);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [sentimentFilter, setSentimentFilter] = useState('All');
  const [page, setPage] = useState(1);
  const fileInputRef = useRef(null);

  const handleFileDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      validateAndSetFile(file);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const validateAndSetFile = (file) => {
    const validExts = ['.csv', '.xlsx', '.xls', '.json'];
    const hasValidExt = validExts.some(ext => file.name.toLowerCase().endsWith(ext));
    if (!hasValidExt) {
      setError('Please upload a valid .csv, .xlsx, or .json file.');
      return;
    }
    setSelectedFile(file);
    setIsSampleFile(false);
    setError('');
    setBatchResult(null);
  };

  const handleProcessBatch = async () => {
    if (!selectedFile) {
      setError('Please select a file to process.');
      return;
    }
    if (isSampleFile || selectedFile?.isSample) {
      return handleLoadSampleBatch();
    }
    setLoading(true);
    setError('');
    try {
      const data = await api.batchPredict(selectedFile, modelType);
      setBatchResult(data);
      setPage(1);
    } catch (err) {
      const detail = err.response?.data?.detail || err.message || 'Failed to process batch. Ensure backend is running.';
      setError(detail);
    } finally {
      setLoading(false);
    }
  };

  const handleLoadSampleBatch = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await api.getSampleBatch(modelType);
      setBatchResult(data);
      setSelectedFile({ name: data.file_name || 'mcdonalds_sample_unlabelled_reviews.csv', size: 14250, isSample: true });
      setIsSampleFile(true);
      setPage(1);
    } catch (err) {
      const detail = err.response?.data?.detail || err.message || 'Failed to load sample batch';
      setError(`Failed to load sample: ${detail}`);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadAnnotatedCSV = () => {
    if (!batchResult?.annotated_csv_data) return;
    const blob = new Blob([batchResult.annotated_csv_data], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `annotated_${batchResult.file_name || 'sentiment_batch.csv'}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  // Filter preview records
  const filteredRecords = (batchResult?.preview_records || []).filter(row => {
    const txt = String(row[batchResult.detected_text_column] || row.review || row.text || row.review_clean || '').toLowerCase();
    const matchSearch = !searchTerm || txt.includes(searchTerm.toLowerCase());
    const matchSent = sentimentFilter === 'All' || row.predicted_sentiment === sentimentFilter;
    return matchSearch && matchSent;
  });

  const pageSize = 10;
  const totalPages = Math.ceil(filteredRecords.length / pageSize) || 1;
  const pagedRecords = filteredRecords.slice((page - 1) * pageSize, page * pageSize);

  const COLORS = {
    Positive: 'var(--positive)',
    Neutral: 'var(--neutral)',
    Negative: 'var(--negative)'
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">

        {/* Classifier Selection */}
        <div className="flex items-center gap-2 self-start md:self-auto">
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[var(--surface)] border border-[var(--border)] text-xs font-bold text-[var(--text-primary)]">
            <Layers className="w-4 h-4 text-[var(--accent)]" />
            <span className="text-[var(--text-muted)]">Model:</span>
            <select
              value={modelType}
              onChange={(e) => setModelType(e.target.value)}
              className="bg-transparent font-extrabold focus:outline-none cursor-pointer text-xs text-[var(--accent)]"
            >
              <option value="distilbert">DistilBERT (Transformer - Neural)</option>
              <option value="linear_svm">Linear SVM (Support Vector Classifier)</option>
              <option value="logistic_regression">Logistic Regression (Linear Classifier)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Upload Drag & Drop Box */}
      <div className="card-2026 p-6 space-y-4">
        <div
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleFileDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all duration-300 flex flex-col items-center justify-center space-y-3 ${
            selectedFile
              ? 'border-[var(--positive-border)] bg-[var(--positive-bg)]'
              : 'border-[var(--border)] hover:border-[var(--accent)] bg-[var(--bg)]'
          }`}
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".csv, .xlsx, .xls, .json"
            className="hidden"
          />

          <div className={`w-14 h-14 rounded-2xl flex items-center justify-center transition-all ${
            selectedFile
              ? 'bg-[var(--positive)] text-white shadow-md'
              : 'bg-[var(--accent-bg)] text-[var(--accent)] shadow-sm'
          }`}>
            {selectedFile ? <FileSpreadsheet className="w-7 h-7" /> : <UploadCloud className="w-7 h-7" />}
          </div>

          <div>
            <h4 className="text-sm font-extrabold text-[var(--text-primary)]">
              {selectedFile ? selectedFile.name : 'Drag and drop review file here, or click to browse'}
            </h4>
            <p className="text-xs text-[var(--text-muted)] font-medium mt-1">
              Supports .CSV, .XLSX (Excel), and .JSON files containing customer feedback text.
            </p>
          </div>

          {selectedFile && (
            <span className="text-[11px] font-bold px-3 py-1 rounded-full bg-white/70 text-[var(--positive)] border border-[var(--positive-border)]">
              Ready to process ({(selectedFile.size / 1024).toFixed(1)} KB)
            </span>
          )}
        </div>

        {error && (
          <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs font-bold flex items-center gap-2 animate-slideUpFade">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2">
          <div className="flex items-center gap-2 w-full sm:w-auto">
            <button
              onClick={handleProcessBatch}
              disabled={loading || !selectedFile}
              className="flex-1 sm:flex-initial flex items-center justify-center gap-2 btn-primary px-5 py-2.5 text-xs disabled:opacity-50"
            >
              {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
              {loading ? 'Analyzing Batch...' : 'Run Batch Sentiment Analysis'}
            </button>

            {selectedFile && (
              <button
                onClick={() => { setSelectedFile(null); setIsSampleFile(false); setBatchResult(null); }}
                className="btn-secondary px-3.5 py-2.5 text-xs"
              >
                Clear
              </button>
            )}
          </div>

          <button
            onClick={handleLoadSampleBatch}
            disabled={loading}
            className="w-full sm:w-auto flex items-center justify-center gap-2 text-xs font-bold px-4 py-2.5 rounded-xl border border-[var(--border)] bg-[var(--surface-elevated)] text-[var(--accent)] hover:bg-[var(--accent-bg)] transition-colors disabled:opacity-50"
          >
            <Database className="w-3.5 h-3.5" />
            Quick Test: Load Sample Batch (60 Reviews)
          </button>
        </div>
      </div>

      {/* ── BATCH ANALYTICS DASHBOARD ── */}
      {batchResult && (
        <div className="space-y-6 animate-fadeInScale">
          {/* Active Model & Dataset Banner */}
          <div className="p-4 rounded-2xl bg-[var(--surface-elevated)] border border-[var(--border)] flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-[var(--accent-bg)] text-[var(--accent)] border border-[var(--border)] shrink-0">
                <BrainCircuit className="w-5 h-5" />
              </div>
              <div>
                <span className="text-[10px] uppercase font-extrabold tracking-wider text-[var(--text-muted)]">
                  Evaluated Classifier
                </span>
                <div className="text-sm font-extrabold text-[var(--text-primary)] flex items-center gap-2">
                  <span>{batchResult.model_used}</span>
                  <span className="text-[10px] px-2 py-0.5 rounded-md bg-[var(--positive-bg)] text-[var(--positive)] border border-[var(--positive-border)] font-bold">
                    Active
                  </span>
                </div>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2 text-[11px] font-bold text-[var(--text-muted)]">
              <span className="px-2.5 py-1 rounded-lg bg-[var(--bg)] border border-[var(--border)]">
                File: <b className="text-[var(--text-primary)]">{batchResult.file_name}</b>
              </span>
              <span className="px-2.5 py-1 rounded-lg bg-[var(--bg)] border border-[var(--border)]">
                Detected Column: <b className="text-[var(--accent)]">{batchResult.detected_text_column}</b>
              </span>
            </div>
          </div>

          {/* Executive KPI Summary Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="kpi-card-2026 border-l-4 border-l-purple-600">
              <div className="text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)]">Total Reviews Processed</div>
              <div className="text-2xl font-extrabold text-[var(--text-primary)] my-1">
                {batchResult.total_processed.toLocaleString()}
              </div>
              <div className="text-xs text-[var(--text-secondary)] font-medium">Text Column: <b>{batchResult.detected_text_column}</b></div>
            </div>

            <div className="kpi-card-2026 border-l-4 border-l-teal-500">
              <div className="text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)]">Dominant Sentiment</div>
              <div className="text-2xl font-extrabold text-[var(--accent)] my-1">
                {batchResult.dominant_sentiment}
              </div>
              <div className="text-xs text-[var(--text-secondary)] font-medium">Majority Class in Batch</div>
            </div>

            <div className="kpi-card-2026 border-l-4 border-l-emerald-500">
              <div className="text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)]">Average Confidence</div>
              <div className="text-2xl font-extrabold text-[var(--positive)] my-1">
                {batchResult.average_confidence}%
              </div>
              <div className="text-xs text-[var(--text-secondary)] font-medium">Mean Classifier Probability</div>
            </div>

            <div className="kpi-card-2026 border-l-4 border-l-indigo-500">
              <div className="text-[11px] font-bold uppercase tracking-wider text-[var(--text-muted)]">Batch Inference Latency</div>
              <div className="text-2xl font-extrabold text-[var(--text-primary)] my-1">
                {batchResult.processing_time_ms} ms
              </div>
              <div className="text-xs text-[var(--text-secondary)] font-medium">{batchResult.model_used}</div>
            </div>
          </div>

          {/* Visual Charts Grid */}
          <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
            {/* Chart 1: Sentiment Donut */}
            <div className="md:col-span-5 card-2026 p-5">
              <h3 className="text-xs font-extrabold uppercase tracking-wider text-[var(--text-primary)] mb-3">
                Batch Sentiment Breakdown
              </h3>
              <div className="h-60">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={batchResult.sentiment_share}
                      cx="50%"
                      cy="50%"
                      innerRadius={55}
                      outerRadius={85}
                      paddingAngle={4}
                      dataKey="count"
                    >
                      {batchResult.sentiment_share?.map((entry) => (
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
                    <Legend formatter={(val) => <span className="text-xs font-bold text-[var(--text-primary)]">{val}</span>} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Chart 2: Top Negative Complaint Drivers */}
            <div className="md:col-span-7 card-2026 p-5">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-xs font-extrabold uppercase tracking-wider text-[var(--negative)] flex items-center gap-1.5">
                  <ThumbsDown className="w-3.5 h-3.5" /> Top Negative Complaint Drivers
                </h3>
                <span className="text-[11px] font-semibold text-[var(--text-muted)]">Extracted from Negative Reviews</span>
              </div>
              <div className="h-60">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={batchResult.top_complaint_drivers} layout="vertical" margin={{ left: 20, right: 30, top: 10, bottom: 10 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" horizontal={false} />
                    <XAxis type="number" stroke="var(--text-muted)" tick={{ fontSize: 11, fontWeight: '600' }} />
                    <YAxis dataKey="word" type="category" stroke="var(--text-muted)" tick={{ fontSize: 11, fontWeight: '700', fill: 'var(--text-secondary)' }} width={80} />
                    <Tooltip 
                      formatter={(val) => [`${val} occurrences`, 'Frequency']}
                      contentStyle={{ 
                        backgroundColor: 'var(--surface)', 
                        borderColor: 'var(--border)',
                        borderRadius: '12px',
                        color: 'var(--text-primary)',
                        fontSize: '12px',
                        fontWeight: 'bold'
                      }} 
                    />
                    <Bar dataKey="count" fill="var(--negative)" radius={[0, 6, 6, 0]} barSize={16} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Annotated Dataset Preview Table */}
          <div className="card-2026 p-5 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[var(--border)]">
              <div>
                <h3 className="text-sm font-extrabold text-[var(--text-primary)]">
                  Annotated Batch Dataset Preview
                </h3>
                <p className="text-xs text-[var(--text-muted)]">
                  Showing {filteredRecords.length} records matching search filters.
                </p>
              </div>

              <button
                onClick={handleDownloadAnnotatedCSV}
                className="flex items-center gap-2 btn-primary px-4 py-2 text-xs font-bold self-start sm:self-auto"
              >
                <Download className="w-4 h-4" /> Download Full Annotated Dataset (.CSV)
              </button>
            </div>

            {/* Filter & Search Bar */}
            <div className="flex flex-col sm:flex-row items-center gap-3">
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => { setSearchTerm(e.target.value); setPage(1); }}
                placeholder="Filter reviews by keyword..."
                className="flex-1 w-full bg-[var(--bg)] border border-[var(--border)] text-[var(--text-primary)] text-xs rounded-xl px-3 py-2 font-medium focus:outline-none focus:border-[var(--accent)]"
              />

              <div className="flex items-center gap-1.5 w-full sm:w-auto">
                {['All', 'Positive', 'Neutral', 'Negative'].map((s) => (
                  <button
                    key={s}
                    onClick={() => { setSentimentFilter(s); setPage(1); }}
                    className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                      sentimentFilter === s
                        ? 'bg-[var(--accent)] text-white'
                        : 'bg-[var(--bg)] text-[var(--text-muted)] hover:text-[var(--text-primary)] border border-[var(--border)]'
                    }`}
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>

            {/* Table */}
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-[var(--bg)] text-[var(--text-muted)] uppercase tracking-wider font-extrabold border-b border-[var(--border)]">
                  <tr>
                    <th className="p-3">#</th>
                    <th className="p-3">Customer Review Text</th>
                    <th className="p-3">Predicted Sentiment</th>
                    <th className="p-3">Confidence</th>
                    <th className="p-3 text-right">Probability Distribution</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[var(--border)] text-[var(--text-primary)]">
                  {pagedRecords.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="p-6 text-center text-[var(--text-muted)] font-semibold">
                        No reviews match your keyword search.
                      </td>
                    </tr>
                  ) : (
                    pagedRecords.map((row, i) => {
                      const text = row[batchResult.detected_text_column] || row.review || row.text || row.review_clean || '';
                      const isPos = row.predicted_sentiment === 'Positive';
                      const isNeu = row.predicted_sentiment === 'Neutral';
                      const badgeBg = isPos ? 'bg-[var(--positive-bg)] text-[var(--positive)] border-[var(--positive-border)]' :
                                      isNeu ? 'bg-[var(--neutral-bg)] text-[var(--neutral)] border-[var(--neutral-border)]' :
                                      'bg-[var(--negative-bg)] text-[var(--negative)] border-[var(--negative-border)]';

                      return (
                        <tr key={i} className="hover:bg-[var(--bg)] transition-colors">
                          <td className="p-3 text-[var(--text-muted)] font-bold">{(page - 1) * pageSize + i + 1}</td>
                          <td className="p-3 font-medium max-w-md truncate" title={text}>
                            "{text}"
                          </td>
                          <td className="p-3">
                            <span className={`px-2.5 py-1 rounded-xl text-[11px] font-extrabold border ${badgeBg}`}>
                              {row.predicted_sentiment}
                            </span>
                          </td>
                          <td className="p-3 font-extrabold text-[var(--text-primary)]">
                            {row.confidence_percentage}%
                          </td>
                          <td className="p-3 text-right">
                            <div className="inline-flex items-center gap-1.5 text-[10px] font-bold">
                              <span className="text-[var(--positive)]">+{((row.prob_positive || 0)*100).toFixed(0)}%</span>
                              <span className="text-[var(--neutral)]">~{((row.prob_neutral || 0)*100).toFixed(0)}%</span>
                              <span className="text-[var(--negative)]">-{((row.prob_negative || 0)*100).toFixed(0)}%</span>
                            </div>
                          </td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="flex items-center justify-between pt-3 border-t border-[var(--border)] text-xs">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="flex items-center gap-1 px-3 py-1.5 rounded-xl border border-[var(--border)] bg-[var(--bg)] font-bold text-[var(--text-primary)] disabled:opacity-40"
              >
                <ChevronLeft className="w-4 h-4" /> Previous
              </button>
              <span className="font-bold text-[var(--text-muted)]">
                Page {page} of {totalPages}
              </span>
              <button
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page >= totalPages}
                className="flex items-center gap-1 px-3 py-1.5 rounded-xl border border-[var(--border)] bg-[var(--bg)] font-bold text-[var(--text-primary)] disabled:opacity-40"
              >
                Next <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
