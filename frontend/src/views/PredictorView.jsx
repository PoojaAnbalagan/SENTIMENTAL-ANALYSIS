import React, { useState, useMemo } from 'react';
import { api } from '../services/api';
import { RefreshCw, Sparkles, Send, Copy, Check } from 'lucide-react';

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
  let sentimentType = 'Neutral';

  if (!text.trim()) {
    label = 'Ready to Analyze';
  } else if (score >= 2) {
    label = 'Strongly Positive Tone';
    colorClass = 'text-[var(--positive)] bg-[var(--positive-bg)] border-[var(--positive-border)]';
    sentimentType = 'Positive';
  } else if (score === 1) {
    label = 'Slightly Positive Tone';
    colorClass = 'text-[var(--positive)] bg-[var(--positive-bg)] border-[var(--positive-border)]';
    sentimentType = 'Positive';
  } else if (score === -1) {
    label = 'Slightly Negative Tone';
    colorClass = 'text-[var(--negative)] bg-[var(--negative-bg)] border-[var(--negative-border)]';
    sentimentType = 'Negative';
  } else if (score <= -2) {
    label = 'Strongly Negative Tone';
    colorClass = 'text-[var(--negative)] bg-[var(--negative-bg)] border-[var(--negative-border)]';
    sentimentType = 'Negative';
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
    'Neutral Review (Standard Visit)': 'It was an average visit. The food was okay and the service was standard for fast food. Neither good nor bad.'
  };

  const [preset, setPreset] = useState('Custom Review Text');
  const [reviewText, setReviewText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);

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
      const data = await api.predictSentiment(reviewText);
      setResult(data);
    } catch (err) {
      setError('Failed to analyze sentiment. Ensure backend API server is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    if (!result) return;
    const textToCopy = `Review: "${reviewText}"\nPredicted Sentiment: ${result.predicted_sentiment} (${result.confidence_percentage}% Confidence)`;
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const wordCount = reviewText.trim() ? reviewText.trim().split(/\s+/).length : 0;
  const charCount = reviewText.length;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-extrabold text-[var(--text-primary)]">Live Review Sentiment Analyzer</h2>
        <p className="text-xs text-[var(--text-muted)]">Perform real-time NLP sentiment evaluation on custom customer review text.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        {/* Left Input Panel */}
        <div className="md:col-span-6 card-2026 p-5 space-y-4">
          <div>
            <label className="block text-xs font-bold text-[var(--text-muted)] mb-1">Select Preset Example</label>
            <select
              value={preset}
              onChange={(e) => handlePresetChange(e.target.value)}
              className="w-full bg-[var(--bg)] border border-[var(--border)] text-[var(--text-primary)] text-xs rounded-xl px-3 py-2 font-medium focus:outline-none focus:border-[var(--accent)]"
            >
              {Object.keys(samplePresets).map(k => <option key={k} value={k}>{k}</option>)}
            </select>
          </div>

          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="block text-xs font-bold text-[var(--text-muted)]">Review Text Input</label>
              <LiveToneEmoji text={reviewText} />
            </div>
            <textarea
              rows={6}
              value={reviewText}
              onChange={(e) => { setReviewText(e.target.value); setResult(null); }}
              placeholder="Type or paste a customer review here..."
              className="w-full bg-[var(--bg)] border border-[var(--border)] text-[var(--text-primary)] text-xs rounded-xl p-3 font-medium focus:outline-none focus:border-[var(--accent)] resize-none"
            />
            <div className="flex justify-between text-[11px] text-[var(--text-muted)] mt-1 font-semibold">
              <span>Word count: <b>{wordCount}</b></span>
              <span>Character count: <b>{charCount}</b></span>
            </div>
          </div>

          {error && <div className="text-xs text-rose-500 font-bold bg-rose-50 p-2.5 rounded-xl border border-rose-200">{error}</div>}

          <div className="flex gap-3 pt-2">
            <button
              onClick={handleAnalyze}
              disabled={loading}
              className="flex-1 flex items-center justify-center gap-2 btn-primary py-2.5 px-4 text-xs disabled:opacity-50"
            >
              {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
              Analyze Sentiment
            </button>
            <button
              onClick={() => { setReviewText(''); setResult(null); }}
              className="btn-secondary px-4 py-2.5 text-xs"
            >
              Clear
            </button>
          </div>
        </div>

        {/* Right Output Panel */}
        <div className="md:col-span-6 card-2026 p-5 space-y-5">
          <div className="flex items-center justify-between pb-2 border-b border-[var(--border)]">
            <h3 className="text-sm font-bold text-[var(--text-primary)]">
              AI Prediction & Explainability Results
            </h3>
            {result && (
              <button
                onClick={handleCopy}
                className="flex items-center gap-1.5 text-[11px] font-bold text-[var(--accent)] hover:text-[var(--accent-hover)] transition-colors"
                title="Copy Prediction Summary"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-[var(--positive)]" /> : <Copy className="w-3.5 h-3.5" />}
                {copied ? 'Copied!' : 'Copy Summary'}
              </button>
            )}
          </div>

          {result ? (
            <div className="space-y-5 animate-fadeIn">
              {/* Prediction Badge featuring Vector SVG Expression Emoji instead of checkmark */}
              <div className={`p-4 rounded-2xl border text-center ${
                result.predicted_sentiment === 'Positive' ? 'bg-[var(--positive-bg)] border-[var(--positive-border)]' :
                result.predicted_sentiment === 'Neutral' ? 'bg-[var(--neutral-bg)] border-[var(--neutral-border)]' :
                'bg-[var(--negative-bg)] border-[var(--negative-border)]'
              }`}>
                <div className="inline-flex p-2.5 rounded-full mb-2 bg-white/30 shadow-sm">
                  <SentimentFaceEmoji sentiment={result.predicted_sentiment} size={36} />
                </div>
                <div className="text-2xl font-extrabold text-[var(--text-primary)]">{result.predicted_sentiment} Sentiment</div>
                <div className="text-xs font-semibold text-[var(--text-muted)] mt-0.5">Confidence Score: {result.confidence_percentage}%</div>
              </div>

              {/* Probabilities Progress Bars */}
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
                        <div className="h-full rounded-full transition-all" style={{ width: `${pct}%`, backgroundColor: color }} />
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Key Token Contributions */}
              {result.contributions && result.contributions.length > 0 && (
                <div className="space-y-2 pt-2 border-t border-[var(--border)]">
                  <div className="flex items-center justify-between">
                    <h4 className="text-xs font-bold text-[var(--text-muted)] uppercase tracking-wider">
                      Key Influential Terms for {result.predicted_sentiment}
                    </h4>
                    <span className="text-[10px] text-[var(--text-muted)] font-semibold">
                      Model Feature Weight
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {result.contributions.map((c, i) => {
                      const badgeClass =
                        result.predicted_sentiment === 'Positive'
                          ? 'bg-[var(--positive-bg)] border-[var(--positive-border)] text-[var(--positive)]'
                          : result.predicted_sentiment === 'Neutral'
                          ? 'bg-[var(--neutral-bg)] border-[var(--neutral-border)] text-[var(--neutral)]'
                          : 'bg-[var(--negative-bg)] border-[var(--negative-border)] text-[var(--negative)]';

                      return (
                        <span
                          key={i}
                          className={`text-xs font-bold px-2.5 py-1 rounded-lg border ${badgeClass}`}
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
            <div className="h-64 flex flex-col items-center justify-center text-center p-6 text-[var(--text-muted)]">
              <Sparkles className="w-8 h-8 mb-2 opacity-50 text-[var(--accent)]" />
              <p className="text-xs font-bold">Enter text on the left or select a preset review to run live AI analysis.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

