import React from 'react';
import { BookOpen, GraduationCap, Cpu, Layers, Database } from 'lucide-react';

export function ProjectInfoView() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-extrabold text-[var(--text-primary)]">Capstone II Project Details & Methodology</h2>
        <p className="text-xs text-[var(--text-muted)]">Academic overview, NLP pipeline architecture, and implementation details.</p>
      </div>

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

        <div className="space-y-3">
          <h4 className="text-xs font-extrabold uppercase tracking-wider text-[var(--text-primary)] flex items-center gap-1.5">
            <Layers className="w-4 h-4 text-[var(--accent)]" /> Machine Learning Pipeline Architecture
          </h4>
          <ol className="list-decimal pl-5 text-xs text-[var(--text-secondary)] space-y-2 font-medium">
            <li><b>Data Collection:</b> 22,366 raw McDonald's customer reviews collected across nationwide store locations.</li>
            <li><b>NLP Preprocessing:</b> Lowercasing, regex URL removal, non-alphabetic filtering, tokenization, and stop-word cleanup.</li>
            <li><b>TF-IDF Vectorization:</b> Feature extraction yielding 20,000 top n-gram terms.</li>
            <li><b>Supervised Classification:</b> Multi-class Logistic Regression with 80/20 train-test split.</li>
            <li><b>Baseline Evaluation:</b> Benchmarked against rule-based VADER lexicon sentiment analysis.</li>
          </ol>
        </div>
      </div>
    </div>
  );
}
