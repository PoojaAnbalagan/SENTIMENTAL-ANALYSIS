import React from 'react';
import { BookOpen, GraduationCap, Cpu, Layers, Database, Scale, CheckCircle2, ShieldAlert } from 'lucide-react';

export function ProjectInfoView() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-extrabold text-[var(--text-primary)]">Capstone II Project Details & Methodology</h2>
        <p className="text-xs text-[var(--text-muted)]">Academic overview, NLP pipeline architecture, class balancing strategy, and implementation details.</p>
      </div>

      {/* Academic Header */}
      <div className="card-2026 p-6 space-y-5">
        <div>
          <h3 className="text-base font-extrabold text-[var(--accent)] flex items-center gap-2">
            <GraduationCap className="w-5 h-5" /> Sabaragamuwa University of Sri Lanka (SUSL)
          </h3>
          <p className="text-xs font-semibold text-[var(--text-muted)] mt-0.5">
            Department of Data Science • Capstone II Project (DS3206)
          </p>
        </div>

        <hr className="border-[var(--border)]" />

        {/* Pipeline Architecture */}
        <div className="space-y-3">
          <h4 className="text-xs font-extrabold uppercase tracking-wider text-[var(--text-primary)] flex items-center gap-1.5">
            <Layers className="w-4 h-4 text-[var(--accent)]" /> 1. NLP &amp; Labeling Pipeline Architecture
          </h4>
          <ol className="list-decimal pl-5 text-xs text-[var(--text-secondary)] space-y-2 font-medium">
            <li>
              <b>Data Ingestion &amp; Cleaning:</b> 22,476 McDonald's customer reviews parsed, deduplicated, and audited for auto-generated Google Maps non-text rating tags.
            </li>
            <li>
              <b>Human Pilot &amp; Pseudo-Labeling:</b> 1,000-review pilot annotated by 3 independent annotators with Inter-Annotator Agreement (IAA) resolution. A transparent TF-IDF Logistic Regression classifier trained solely on human ground-truth was used to pseudo-label remaining free-text reviews (retaining confidence scores and gold holdouts).
            </li>
            <li>
              <b>Sentiment-Aware Preprocessing:</b> Lowercasing, URL removal, contraction expansion (e.g., <i>can't &rarr; can not</i>), non-alphabetic filtering, and crucial <b>negation preservation</b> (<i>not, never, neither, nor, without</i>) to maintain polarity.
            </li>
            <li>
              <b>TF-IDF Vectorization:</b> Feature extraction with sublinear term-frequency scaling and $N$-gram range (1&ndash;3) capturing 20,000 predictive lexical tokens.
            </li>
            <li>
              <b>Model Training &amp; Baseline Benchmarking:</b> Multi-class Logistic Regression, Linear SVM, and Multinomial Naive Bayes benchmarked against the rule-based VADER lexicon baseline.
            </li>
          </ol>
        </div>

        <hr className="border-[var(--border)]" />

        {/* Class Imbalance Strategy */}
        <div className="space-y-3">
          <h4 className="text-xs font-extrabold uppercase tracking-wider text-[var(--text-primary)] flex items-center gap-1.5">
            <Scale className="w-4 h-4 text-[var(--positive)]" /> 2. Class Imbalance Mitigation Strategy
          </h4>
          <p className="text-xs text-[var(--text-secondary)]">
            Review corpora exhibit a natural imbalance where Negative (~42%) and Positive (~44%) reviews heavily outnumber Neutral reviews (~14%). To prevent majority-class bias without distorting discrete text features with synthetic sampling (such as SMOTE):
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-1">
            <div className="p-3.5 rounded-xl bg-[var(--bg)] border border-[var(--border)] space-y-1.5">
              <div className="flex items-center gap-1.5 font-bold text-xs text-[var(--accent)]">
                <CheckCircle2 className="w-3.5 h-3.5" /> Stratified Sampling
              </div>
              <p className="text-[11px] text-[var(--text-muted)] font-medium">
                <code>stratify=y</code> guarantees training and test partitions maintain identical class ratios, preventing minority class starvation.
              </p>
            </div>

            <div className="p-3.5 rounded-xl bg-[var(--bg)] border border-[var(--border)] space-y-1.5">
              <div className="flex items-center gap-1.5 font-bold text-xs text-[var(--positive)]">
                <Scale className="w-3.5 h-3.5" /> Cost-Sensitive Loss
              </div>
              <p className="text-[11px] text-[var(--text-muted)] font-medium">
                <code>class_weight='balanced'</code> penalizes minority class errors inversely proportional to class frequency: <i>w<sub>j</sub> = N / (K &times; n<sub>j</sub>)</i>.
              </p>
            </div>

            <div className="p-3.5 rounded-xl bg-[var(--bg)] border border-[var(--border)] space-y-1.5">
              <div className="flex items-center gap-1.5 font-bold text-xs text-[var(--warning, #f59e0b)]">
                <BookOpen className="w-3.5 h-3.5" /> Macro-F1 Selection
              </div>
              <p className="text-[11px] text-[var(--text-muted)] font-medium">
                Models are evaluated and selected using <b>Macro-F1</b> (unweighted class average) ensuring equal evaluation priority for all sentiment classes.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

