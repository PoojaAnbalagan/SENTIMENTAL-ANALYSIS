import React, { useState, useMemo, useEffect } from 'react';
import { api } from '../services/api';
import { 
  RefreshCw, Sparkles, Send, Copy, Check, Zap, Cpu, Gauge, 
  Layers, CheckCircle2, Award, Clock, ArrowRight, BarChart2,
  BrainCircuit, ShieldCheck, Binary, Activity
} from 'lucide-react';

const POSITIVE_KEYWORDS = [
  'great', 'amazing', 'good', 'fast', 'fresh', 'excellent', 'love', 'friendly', 
  'delicious', 'quick', 'perfect', 'awesome', 'nice', 'best', 'clean', 'helpful', 
  'happy', 'smooth', 'top', 'enjoyed', 'tasty', 'wonderful', 'super', 'polite'
];

const NEGATIVE_KEYWORDS = [
  'slow', 'cold', 'bad', 'terrible', 'horrible', 'worst', 'soggy', 'rude', 
  'late', 'dirty', 'wrong', 'missing', 'waste', 'poor', 'gross', 'waiting', 
  'delay', 'refund', 'mistake', 'disappointed', 'raw', 'disgusting', 'awful'
];

const MODEL_OPTIONS = [
  { id: 'all', label: 'Head-to-Head Sandbox', shortLabel: 'Head-to-Head (All 5)', icon: Zap, badge: '5 Models', desc: 'Run all 5 algorithms side-by-side with latency & consensus tracking' },
  { id: 'logistic_regression', label: 'Logistic Regression', shortLabel: 'Logistic Reg.', icon: Layers, badge: 'Champion', desc: 'Balanced L2 regularized linear classifier' },
  { id: 'linear_svm', label: 'Linear SVM', shortLabel: 'Linear SVM', icon: ShieldCheck, badge: 'Max Margin', desc: 'Support Vector Classifier (LinearSVC)' },
  { id: 'distilbert', label: 'DistilBERT (Transformer)', shortLabel: 'DistilBERT', icon: BrainCircuit, badge: 'Neural', desc: 'Deep contextual neural network' },
  { id: 'naive_bayes', label: 'Multinomial Naive Bayes', shortLabel: 'Naive Bayes', icon: Binary, badge: 'Bayesian', desc: 'Fast probabilistic bag-of-words classifier' },
  { id: 'vader', label: 'VADER (Lexicon Baseline)', shortLabel: 'VADER', icon: Activity, badge: 'Rule-Based', desc: 'Unsupervised rule-based sentiment lexicon' },
];

function SentimentFaceEmoji({ sentiment, size = 32, className = '' }) {
  let faceColor = 'var(--text-muted)';
  let mouthPath = 'M 13 24 L 27 24'; // Straight
  let eyebrows = null;

  if (sentiment === 'Positive' || sentiment === 'Strongly Positive') {
    faceColor = 'var(--positive)';
    mouthPath = 'M 11 20 Q 20 30 29 20';
    eyebrows = (
      <>
        <path d="M 11 12 Q 15 10 18 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" fill="none" />
        <path d="M 22 12 Q 25 10 29 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" fill="none" />
      </>
    );
  } else if (sentiment === 'Neutral') {
    faceColor = 'var(--neutral)';
    mouthPath = 'M 13 24 L 27 24';
  } else if (sentiment === 'Negative' || sentiment === 'Strongly Negative') {
    faceColor = 'var(--negative)';
    mouthPath = 'M 11 27 Q 20 17 29 27';
    eyebrows = (
      <>
        <path d="M 11 11 Q 15 14 18 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" fill="none" />
        <path d="M 22 13 Q 25 14 29 11" stroke="currentColor" strokeWidth="2" strokeLinecap="round" fill="none" />
      </>
    );
  }

  return (
    <svg width={size} height={size} viewBox="0 0 40 40" className={`transition-all duration-300 ${className}`}>
      <circle cx="20" cy="20" r="18" fill="none" stroke={faceColor} strokeWidth="2.8" />
      {eyebrows}
      <circle cx="14" cy="16" r="2.5" fill={faceColor} />
      <circle cx="26" cy="16" r="2.5" fill={faceColor} />
      <path d={mouthPath} stroke={faceColor} strokeWidth="3" strokeLinecap="round" fill="none" className="transition-all duration-300" />
    </svg>
  );
}

function LiveToneEmoji({ text }) {
  const score = useMemo(() => {
    if (!text || !text.trim()) return 0;
    const tokens = text.toLowerCase().split(/\W+/);
    let s = 0;
    tokens.forEach(t => {
      if (POSITIVE_KEYWORDS.includes(t)) s += 1;
      if (NEGATIVE_KEYWORDS.includes(t)) s -= 1;
    });
    return s;
  }, [text]);

  let label = 'Neutral / Awaiting Input';
  let colorClass = 'text-[var(--text-muted)] bg-[var(--surface-elevated)] border-[var(--border)]';

  if (!text.trim()) {
    label = 'Ready to Analyze';
  } else if (score >= 2) {
    label = 'Strongly Positive Tone';
    colorClass = 'text-[var(--positive)] bg-[var(--positive-bg)] border-[var(--positive-border)]';
  } else if (score === 1) {
    label = 'Slightly Positive Tone';
    colorClass = 'text-[var(--positive)] bg-[var(--positive-bg)] border-[var(--positive-border)]';
  } else if (score === -1) {
    label = 'Slightly Negative Tone';
    colorClass = 'text-[var(--negative)] bg-[var(--negative-bg)] border-[var(--negative-border)]';
  } else if (score <= -2) {
    label = 'Strongly Negative Tone';
    colorClass = 'text-[var(--negative)] bg-[var(--negative-bg)] border-[var(--negative-border)]';
  }

  return (
    <div className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-xl border text-[11px] font-bold transition-all duration-300 ${colorClass}`}>
      <span className="w-2 h-2 rounded-full bg-current opacity-80 animate-pulse"></span>
      <span>{label}</span>
    </div>
  );
}

export function PredictorView() {
  const samplePresets = {
    'Custom Review Text': '',
    'Negative Review (Slow & Cold)': 'The drive-thru was extremely slow, took over 25 minutes! The fries were cold, soggy, and un-salted. Terrible customer service.',
    'Positive Review (Fast & Fresh)': 'Amazing experience! The staff was super friendly, order was accurate, and the burger was fresh and delicious. Quick service!',
    'Neutral Review (Standard Visit)': 'It was an average visit. The food was okay and the service was standard for fast food. Neither good nor bad.',
    'Mixed Ambiguous Review': 'The staff was friendly and the place was clean, but the wait was way too long and they forgot my barbecue sauce.'
  };

  const [selectedModel, setSelectedModel] = useState('all');
  const [preset, setPreset] = useState('Custom Review Text');
  const [reviewText, setReviewText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);

  // Smooth automatic re-inference when switching models if text is present
  const handleModelChange = async (modelId) => {
    setSelectedModel(modelId);
    if (reviewText.trim() && result) {
      setLoading(true);
      setError('');
      try {
        const data = await api.predictSentiment(reviewText, modelId);
        setResult(data);
      } catch (err) {
        const detail = err.response?.data?.detail || err.message || 'Error running model inference';
        setError(detail);
      } finally {
        setLoading(false);
      }
    }
  };

  const handlePresetChange = (key) => {
    setPreset(key);
    setReviewText(samplePresets[key]);
    setResult(null);
  };

  const handleAnalyze = async () => {
    if (!reviewText.trim()) {
      setError('Please enter a review text to analyze.');
      return;
    }
    setError('');
    setLoading(true);
    try {
      const data = await api.predictSentiment(reviewText, selectedModel);
      setResult(data);
    } catch (err) {
      const detail = err.response?.data?.detail || err.message || 'Ensure backend server is running on http://localhost:8000';
      setError(`Failed to analyze sentiment: ${detail}`);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    if (!result) return;
    let textToCopy = '';
    if (result.mode === 'head_to_head') {
      textToCopy = `Review: "${reviewText}"\nConsensus Sentiment: ${result.consensus_sentiment} (${result.agreement_percentage}% Model Agreement)\nFastest Model: ${result.fastest_model}\n` +
        result.models.map(m => `• ${m.model_name}: ${m.predicted_sentiment} (${m.confidence_percentage}%, ${m.latency_ms}ms)`).join('\n');
    } else {
      textToCopy = `Review: "${reviewText}"\nModel: ${result.model_name}\nPredicted Sentiment: ${result.predicted_sentiment} (${result.confidence_percentage}% Confidence, ${result.latency_ms}ms)`;
    }
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const wordCount = reviewText.trim() ? reviewText.trim().split(/\s+/).length : 0;
  const charCount = reviewText.length;

  return (
    <div className="space-y-6">

      {/* Smooth Model Switcher Pill Bar */}
      <div className="card-2026 p-2">
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
          {MODEL_OPTIONS.map((m) => {
            const Icon = m.icon;
            const isSelected = selectedModel === m.id;
            return (
              <button
                key={m.id}
                onClick={() => handleModelChange(m.id)}
                className={`flex items-center justify-center gap-1.5 px-3 py-2 rounded-xl text-xs font-bold transition-all duration-300 ${
                  isSelected
                    ? 'bg-[var(--accent)] text-white shadow-md shadow-purple-500/20 scale-[1.02]'
                    : 'text-[var(--text-secondary)] hover:bg-[var(--surface-elevated)] hover:text-[var(--text-primary)] border border-transparent'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 shrink-0 ${isSelected ? 'text-white' : 'text-[var(--accent)]'}`} />
                <span className="truncate">{m.shortLabel}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Main Two-Column Layout */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        {/* Left Input Panel */}
        <div className="md:col-span-5 card-2026 p-5 space-y-4">
          <div>
            <label className="block text-xs font-bold text-[var(--text-muted)] mb-1">Select Preset Example</label>
            <select
              value={preset}
              onChange={(e) => handlePresetChange(e.target.value)}
              className="w-full bg-[var(--bg)] border border-[var(--border)] text-[var(--text-primary)] text-xs rounded-xl px-3 py-2 font-medium focus:outline-none focus:border-[var(--accent)] transition-colors"
            >
              {Object.keys(samplePresets).map(k => <option key={k} value={k}>{k}</option>)}
            </select>
          </div>

          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="block text-xs font-bold text-[var(--text-muted)]">Customer Review Text</label>
              <LiveToneEmoji text={reviewText} />
            </div>
            <textarea
              rows={6}
              value={reviewText}
              onChange={(e) => { setReviewText(e.target.value); setResult(null); }}
              placeholder="Type or paste a customer review here to test multi-model inference..."
              className="w-full bg-[var(--bg)] border border-[var(--border)] text-[var(--text-primary)] text-xs rounded-xl p-3 font-medium focus:outline-none focus:border-[var(--accent)] resize-none transition-colors"
            />
            <div className="flex justify-between text-[11px] text-[var(--text-muted)] mt-1 font-semibold">
              <span>Word count: <b>{wordCount}</b></span>
              <span>Character count: <b>{charCount}</b></span>
            </div>
          </div>

          {error && (
            <div className="text-xs text-rose-500 font-bold bg-rose-50 p-2.5 rounded-xl border border-rose-200 animate-slideUpFade">
              {error}
            </div>
          )}

          <div className="flex gap-3 pt-2">
            <button
              onClick={handleAnalyze}
              disabled={loading}
              className="flex-1 flex items-center justify-center gap-2 btn-primary py-2.5 px-4 text-xs disabled:opacity-50"
            >
              {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
              {selectedModel === 'all' ? 'Run Head-to-Head Comparison' : 'Analyze with Selected Model'}
            </button>
            <button
              onClick={() => { setReviewText(''); setResult(null); }}
              className="btn-secondary px-4 py-2.5 text-xs"
            >
              Clear
            </button>
          </div>
        </div>

        {/* Right Output Panel with Smooth Transitions */}
        <div className="md:col-span-7 card-2026 p-5 space-y-5">
          <div className="flex items-center justify-between pb-2 border-b border-[var(--border)]">
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-[var(--text-primary)]">
                {result?.mode === 'head_to_head' ? 'Head-to-Head Model Sandbox Results' : 'AI Prediction & Explainability'}
              </h3>
              {result && (
                <span className="text-[10px] font-extrabold px-2 py-0.5 rounded-full bg-[var(--accent-bg)] text-[var(--accent)] border border-[var(--border)] animate-fadeInScale">
                  {result.mode === 'head_to_head' ? '5 Models Benchmarked' : result.model_name}
                </span>
              )}
            </div>
            {result && (
              <button
                onClick={handleCopy}
                className="flex items-center gap-1.5 text-[11px] font-bold text-[var(--accent)] hover:text-[var(--accent-hover)] transition-colors"
                title="Copy Results"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-[var(--positive)]" /> : <Copy className="w-3.5 h-3.5" />}
                {copied ? 'Copied!' : 'Copy Summary'}
              </button>
            )}
          </div>

          {loading ? (
            /* Smooth Loading State */
            <div className="h-72 flex flex-col items-center justify-center text-center p-6 space-y-3 animate-fadeInScale">
              <div className="w-12 h-12 rounded-2xl bg-[var(--accent-bg)] text-[var(--accent)] flex items-center justify-center animate-pulseGlow">
                <Cpu className="w-6 h-6 animate-pulse" />
              </div>
              <div>
                <p className="text-xs font-extrabold text-[var(--text-primary)]">
                  {selectedModel === 'all' ? 'Running 5 Models Concurrently...' : `Evaluating with ${MODEL_OPTIONS.find(m => m.id === selectedModel)?.label}...`}
                </p>
                <p className="text-[11px] text-[var(--text-muted)] font-semibold mt-0.5">Profiling latency &amp; confidence spectrum</p>
              </div>
            </div>
          ) : result ? (
            <div className="space-y-5 animate-fadeInScale">
              {/* ── MODE 1: HEAD-TO-HEAD MULTI-MODEL SANDBOX ── */}
              {result.mode === 'head_to_head' ? (
                <div className="space-y-4">
                  {/* Consensus Summary Banner */}
                  <div className={`p-4 rounded-2xl border flex flex-col sm:flex-row items-center justify-between gap-4 transition-all duration-500 animate-slideUpFade ${
                    result.consensus_sentiment === 'Positive' ? 'bg-[var(--positive-bg)] border-[var(--positive-border)]' :
                    result.consensus_sentiment === 'Neutral' ? 'bg-[var(--neutral-bg)] border-[var(--neutral-border)]' :
                    'bg-[var(--negative-bg)] border-[var(--negative-border)]'
                  }`}>
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-full bg-white/40 shadow-sm shrink-0">
                        <SentimentFaceEmoji sentiment={result.consensus_sentiment} size={32} />
                      </div>
                      <div>
                        <span className="text-[10px] uppercase tracking-wider font-extrabold text-[var(--text-muted)]">
                          Consensus Prediction
                        </span>
                        <div className="text-lg font-extrabold text-[var(--text-primary)]">
                          {result.consensus_sentiment} Sentiment
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-2.5 text-xs font-bold">
                      <div className="px-3 py-1.5 rounded-xl bg-white/60 dark:bg-black/20 border border-[var(--border)]">
                        <span className="text-[var(--text-muted)]">Agreement:</span>{' '}
                        <b className="text-[var(--text-primary)]">{result.agreement_percentage}%</b> ({result.agreement_count}/{result.total_models})
                      </div>
                      <div className="px-3 py-1.5 rounded-xl bg-white/60 dark:bg-black/20 border border-[var(--border)] flex items-center gap-1.5 text-[var(--accent)]">
                        <Zap className="w-3.5 h-3.5" />
                        <span>Fastest: <b>{result.fastest_model}</b></span>
                      </div>
                    </div>
                  </div>

                  {/* 5 Models Side-by-Side Cards with Staggered Entrance */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {result.models?.map((m, idx) => {
                      const isPos = m.predicted_sentiment === 'Positive';
                      const isNeu = m.predicted_sentiment === 'Neutral';
                      const badgeBg = isPos ? 'bg-[var(--positive-bg)] border-[var(--positive-border)] text-[var(--positive)]' :
                                      isNeu ? 'bg-[var(--neutral-bg)] border-[var(--neutral-border)] text-[var(--neutral)]' :
                                      'bg-[var(--negative-bg)] border-[var(--negative-border)] text-[var(--negative)]';

                      return (
                        <div 
                          key={idx} 
                          style={{ animationDelay: `${idx * 60}ms` }}
                          className="p-3.5 rounded-2xl bg-[var(--surface-elevated)] border border-[var(--border)] space-y-2.5 transition-all duration-300 hover:scale-[1.02] hover:shadow-md animate-slideUpFade"
                        >
                          <div className="flex items-start justify-between gap-2">
                            <div>
                              <div className="font-extrabold text-xs text-[var(--text-primary)] flex items-center gap-1.5">
                                {m.model_name}
                                {m.is_fastest && (
                                  <span className="text-[9px] px-1.5 py-0.5 rounded bg-[var(--accent-bg)] text-[var(--accent)] border border-[var(--border)] font-extrabold flex items-center gap-0.5">
                                    <Zap className="w-2.5 h-2.5" /> Fast
                                  </span>
                                )}
                              </div>
                              <span className="text-[10px] text-[var(--text-muted)] font-medium">
                                {m.architecture}
                              </span>
                            </div>
                            <span className="text-[11px] font-extrabold text-[var(--accent)] shrink-0 flex items-center gap-1">
                              <Clock className="w-3 h-3 text-[var(--text-muted)]" />
                              {m.latency_ms} ms
                            </span>
                          </div>

                          <div className="flex items-center justify-between pt-1">
                            <span className={`text-xs font-extrabold px-2.5 py-1 rounded-xl border flex items-center gap-1.5 ${badgeBg}`}>
                              <SentimentFaceEmoji sentiment={m.predicted_sentiment} size={16} />
                              {m.predicted_sentiment}
                            </span>
                            <span className="text-xs font-extrabold text-[var(--text-primary)]">
                              {m.confidence_percentage}% <span className="text-[10px] text-[var(--text-muted)] font-normal">conf</span>
                            </span>
                          </div>

                          {/* Smooth Mini Probabilities Distribution */}
                          <div className="w-full h-1.5 bg-black/10 rounded-full overflow-hidden flex">
                            <div style={{ width: `${(m.probabilities?.Positive || 0) * 100}%` }} className="h-full bg-[var(--positive)] transition-all duration-700" title={`Positive: ${((m.probabilities?.Positive || 0)*100).toFixed(1)}%`} />
                            <div style={{ width: `${(m.probabilities?.Neutral || 0) * 100}%` }} className="h-full bg-[var(--neutral)] transition-all duration-700" title={`Neutral: ${((m.probabilities?.Neutral || 0)*100).toFixed(1)}%`} />
                            <div style={{ width: `${(m.probabilities?.Negative || 0) * 100}%` }} className="h-full bg-[var(--negative)] transition-all duration-700" title={`Negative: ${((m.probabilities?.Negative || 0)*100).toFixed(1)}%`} />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ) : (
                /* ── MODE 2: SINGLE MODEL INFERENCE VIEW ── */
                <div className="space-y-4 animate-slideUpFade">
                  <div className={`p-4 rounded-2xl border text-center transition-all duration-500 ${
                    result.predicted_sentiment === 'Positive' ? 'bg-[var(--positive-bg)] border-[var(--positive-border)]' :
                    result.predicted_sentiment === 'Neutral' ? 'bg-[var(--neutral-bg)] border-[var(--neutral-border)]' :
                    'bg-[var(--negative-bg)] border-[var(--negative-border)]'
                  }`}>
                    <div className="inline-flex p-2.5 rounded-full mb-2 bg-white/30 shadow-sm">
                      <SentimentFaceEmoji sentiment={result.predicted_sentiment} size={36} />
                    </div>
                    <div className="text-2xl font-extrabold text-[var(--text-primary)]">{result.predicted_sentiment} Sentiment</div>
                    <div className="text-xs font-semibold text-[var(--text-muted)] mt-1 flex items-center justify-center gap-3">
                      <span>Confidence Score: <b>{result.confidence_percentage}%</b></span>
                      <span>•</span>
                      <span className="flex items-center gap-1 text-[var(--accent)] font-bold">
                        <Clock className="w-3.5 h-3.5" /> Latency: <b>{result.latency_ms} ms</b>
                      </span>
                    </div>
                  </div>

                  {/* Probabilities Breakdown */}
                  <div className="space-y-3">
                    <h4 className="text-xs font-bold text-[var(--text-muted)] uppercase tracking-wider">Confidence Breakdown</h4>
                    {Object.entries(result.probabilities || {}).map(([cat, prob]) => {
                      const pct = (prob * 100).toFixed(1);
                      const color = cat === 'Positive' ? 'var(--positive)' : cat === 'Neutral' ? 'var(--neutral)' : 'var(--negative)';
                      return (
                        <div key={cat} className="space-y-1 text-xs">
                          <div className="flex justify-between font-bold text-[var(--text-primary)]">
                            <span>{cat}</span>
                            <span>{pct}%</span>
                          </div>
                          <div className="w-full h-2 bg-black/10 rounded-full overflow-hidden">
                            <div className="h-full rounded-full transition-all duration-700 ease-out" style={{ width: `${pct}%`, backgroundColor: color }} />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Key Token Contributions (Explainability) */}
              {result.contributions && result.contributions.length > 0 && (
                <div className="space-y-2 pt-3 border-t border-[var(--border)] animate-slideUpFade">
                  <div className="flex items-center justify-between">
                    <h4 className="text-xs font-bold text-[var(--text-muted)] uppercase tracking-wider">
                      Key Influential Terms (Feature Weights)
                    </h4>
                    <span className="text-[10px] text-[var(--text-muted)] font-semibold">
                      Linear Model Attribution
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {result.contributions.map((c, i) => {
                      const badgeClass =
                        (result.consensus_sentiment || result.predicted_sentiment) === 'Positive'
                          ? 'bg-[var(--positive-bg)] border-[var(--positive-border)] text-[var(--positive)]'
                          : (result.consensus_sentiment || result.predicted_sentiment) === 'Neutral'
                          ? 'bg-[var(--neutral-bg)] border-[var(--neutral-border)] text-[var(--neutral)]'
                          : 'bg-[var(--negative-bg)] border-[var(--negative-border)] text-[var(--negative)]';

                      return (
                        <span
                          key={i}
                          className={`text-xs font-bold px-2.5 py-1 rounded-lg border transition-all duration-300 hover:scale-105 ${badgeClass}`}
                        >
                          {c.word} ({c.score > 0 ? '+' : ''}{c.score.toFixed(2)})
                        </span>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="h-64 flex flex-col items-center justify-center text-center p-6 text-[var(--text-muted)] animate-fadeInScale">
              <Sparkles className="w-8 h-8 mb-2 opacity-50 text-[var(--accent)]" />
              <p className="text-xs font-bold">Enter text on the left or select a preset review to run multi-model inference.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
