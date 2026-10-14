"""
run_evaluation_pipeline.py
==========================
Master Orchestrator for the Research-Grade Sentiment Analysis Evaluation Pipeline.
Implements all 26 phases of the research evaluation framework:
- Ingestion & Deduplication Audit
- Strict 70% Train / 15% Val / 15% Untouched Test Stratified Split
- Zero-Leakage Feature Extraction
- Classical ML, VADER, and DistilBERT Benchmarking
- Comprehensive Metrics (Accuracy, Macro/Weighted/Per-class Precision, Recall, F1, Support)
- Raw & Normalized Confusion Matrices and Error Pairs
- 5-Fold Stratified Cross-Validation
- Probability Calibration, Log Loss, Brier Score, ROC-AUC, PR-AUC
- Robustness Challenge Suite
- Diagnostic Error Analysis
- Systematic Ablation Studies
- Global & Local Explainability
- Computational Efficiency Profiling
- Centralized Results Export & Backend Synchronization
"""

import os
import sys
import json
import joblib
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Suppress runtime warnings for clean terminal logging
warnings.filterwarnings("ignore")

from src.data_loader import load_and_audit_dataset, create_stratified_splits, CLASSES, LABEL_MAP, REV_LABEL_MAP, SEED
from src.feature_engineering import clean_text_for_classical, build_tfidf_pipeline
from src.models import get_classical_models, VaderSentimentBaseline, DistilBERTPipeline, TRANSFORMERS_AVAILABLE
from src.evaluation_metrics import compute_comprehensive_metrics, export_confusion_matrix_plot
from src.cross_validation import run_stratified_kfold_cv
from src.robustness_testing import run_robustness_benchmark
from src.error_analysis import perform_test_error_analysis
from src.ablation_studies import run_ablation_study
from src.explainability import extract_global_feature_importance, get_sample_token_contributions
from src.efficiency import measure_efficiency_metrics

def main():
    print("=" * 80)
    print("  RESEARCH-GRADE MACHINE LEARNING EVALUATION PIPELINE")
    print("  Dataset: McDonald's Customer Review Sentiment Analysis")
    print("=" * 80)

    # 1. Directories Setup
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    RESULTS_DIR = os.path.join(BASE_DIR, "results")
    MODELS_DIR = os.path.join(BASE_DIR, "models")
    FIG_DIR = os.path.join(BASE_DIR, "Figures")
    CM_DIR = os.path.join(RESULTS_DIR, "confusion_matrices")

    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(MODELS_DIR, exist_ok=True)
    os.makedirs(FIG_DIR, exist_ok=True)
    os.makedirs(CM_DIR, exist_ok=True)

    # 2. Ingestion & Deduplication Audit (Phases 1 & 3)
    df, audit_info = load_and_audit_dataset()
    print("\n[Phase 1 & 3] Dataset Ingestion & Deduplication Audit:")
    print(f"  Total Valid Reviews: {audit_info['valid_rows']:,}")
    print(f"  Exact Duplicates Removed: {audit_info['exact_duplicates']:,}")
    print(f"  Conflicting Labels: {audit_info['conflicting_label_duplicates']:,}")
    print("  Class Distribution:")
    for cname, count in audit_info['sentiment_distribution'].items():
        pct = audit_info['sentiment_proportions'][cname] * 100
        print(f"    - {cname:10s}: {count:6,} ({pct:.2f}%)")

    # 3. Stratified 70/15/15 Split (Phase 2)
    train_df, val_df, test_df, split_stats = create_stratified_splits(df, seed=SEED)
    raw_col = "review" if "review" in df.columns else "review_clean"

    # Save split info
    with open(os.path.join(RESULTS_DIR, "split_summary.json"), "w", encoding="utf-8") as f:
        json.dump(split_stats, f, indent=2)

    # 4. Feature Extraction strictly on Training Data (Phases 3 & 5)
    print("\n[Phase 3 & 5] Building TF-IDF Feature Pipeline (N-grams: 1-2, Sublinear TF)...")
    vectorizer, X_train, X_val, X_test = build_tfidf_pipeline(
        train_df[raw_col],
        val_texts=val_df[raw_col],
        test_texts=test_df[raw_col],
        ngram_range=(1, 2),
        min_df=3,
        max_df=0.95,
        sublinear_tf=True,
        max_features=25000
    )
    print(f"  Training TF-IDF Matrix Shape  : {X_train.shape}")
    print(f"  Validation TF-IDF Matrix Shape: {X_val.shape}")
    print(f"  Untouched Test Matrix Shape   : {X_test.shape}")
    print(f"  Fitted Vocabulary Term Count  : {len(vectorizer.get_feature_names_out()):,}")

    # 5. Train Classical Models on Training Split & Benchmark on Validation Split (Phases 4, 5, 6)
    print("\n[Phases 4, 5, 6] Training Classical Supervised Classifiers...")
    classical_models = get_classical_models(seed=SEED)
    trained_models = {}
    val_predictions = {}
    test_predictions = {}
    test_probabilities = {}

    for name, clf in classical_models.items():
        print(f"  -> Fitting {name} on training partition...")
        clf.fit(X_train, train_df["sentiment"])
        trained_models[name] = clf
        
        # Validation predictions
        val_preds = clf.predict(X_val)
        val_predictions[name] = val_preds
        
        # Test predictions (for final evaluation)
        test_preds = clf.predict(X_test)
        test_predictions[name] = test_preds

        # Test probabilities
        if hasattr(clf, "predict_proba"):
            test_probabilities[name] = clf.predict_proba(X_test)
        elif hasattr(clf, "decision_function"):
            decision = clf.decision_function(X_test)
            if decision.ndim == 1:
                prob_pos = 1.0 / (1.0 + np.exp(-decision))
                test_probabilities[name] = np.column_stack([1.0 - prob_pos, prob_pos])
            else:
                exp_scores = np.exp(decision - np.max(decision, axis=1, keepdims=True))
                test_probabilities[name] = exp_scores / np.sum(exp_scores, axis=1, keepdims=True)
        else:
            test_probabilities[name] = None

    # 6. VADER Baseline Evaluation (Phase 4)
    print("\n[Phase 4] Evaluating VADER Rule-Based Baseline...")
    vader_model = VaderSentimentBaseline()
    trained_models["VADER (Baseline)"] = vader_model
    vader_test_preds = vader_model.predict(test_df[raw_col])
    test_predictions["VADER (Baseline)"] = vader_test_preds
    test_probabilities["VADER (Baseline)"] = vader_model.predict_proba(test_df[raw_col])

    # 7. Fine-Tuned DistilBERT Evaluation (Phase 7)
    distilbert_saved_dir = os.path.join(MODELS_DIR, "distilbert_sentiment")
    if os.path.exists(distilbert_saved_dir) and TRANSFORMERS_AVAILABLE:
        print(f"\n[Phase 7] Loading existing fine-tuned DistilBERT from {distilbert_saved_dir}...")
        try:
            distilbert_pipeline = DistilBERTPipeline(model_path=distilbert_saved_dir)
            trained_models["DistilBERT (Transformer)"] = distilbert_pipeline
            print("  -> Evaluating DistilBERT on untouched test set...")
            d_preds = distilbert_pipeline.predict(test_df[raw_col].tolist())
            d_probas = distilbert_pipeline.predict_proba(test_df[raw_col].tolist())
            test_predictions["DistilBERT (Transformer)"] = d_preds
            test_probabilities["DistilBERT (Transformer)"] = d_probas
            print("  -> DistilBERT test evaluation complete.")
        except Exception as e:
            print(f"Warning: Failed to load DistilBERT model: {e}")
    else:
        print("\n[Phase 7] Note: DistilBERT checkpoint directory not found or PyTorch/Transformers not installed. Skipping deep transformer inference.")

    # 8. Comprehensive Metrics on Untouched Test Set (Phases 8, 9, 10, 12, 13)
    print("\n[Phases 8-13] Calculating Comprehensive Evaluation Metrics on Untouched Final Test Set...")
    all_metrics_list = []
    per_class_records = []
    y_test_true = test_df["sentiment"].values

    for name in test_predictions.keys():
        y_pred = test_predictions[name]
        y_prob = test_probabilities.get(name)
        
        metrics = compute_comprehensive_metrics(
            y_test_true,
            y_pred,
            y_proba=y_prob,
            model_name=name
        )
        all_metrics_list.append(metrics)

        # Per-class breakdown
        for cname, pstats in metrics["per_class"].items():
            per_class_records.append({
                "model": name,
                "sentiment_class": cname,
                "precision": pstats["precision"],
                "recall": pstats["recall"],
                "f1": pstats["f1"],
                "support": pstats["support"]
            })

        # Save confusion matrix CSV and PNG
        cm_raw = metrics["confusion_matrix"]
        cm_norm = metrics["normalized_confusion_matrix"]
        
        safe_name = name.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("-", "_")
        pd.DataFrame(cm_raw, index=CLASSES, columns=CLASSES).to_csv(
            os.path.join(CM_DIR, f"{safe_name}_confusion_matrix_raw.csv")
        )
        pd.DataFrame(cm_norm, index=CLASSES, columns=CLASSES).to_csv(
            os.path.join(CM_DIR, f"{safe_name}_confusion_matrix_normalized.csv")
        )
        export_confusion_matrix_plot(
            cm_raw,
            model_name=name,
            output_path=os.path.join(CM_DIR, f"{safe_name}_confusion_matrix.png"),
            normalized=False
        )

    # 9. Master Results DataFrames
    df_metrics = pd.DataFrame([
        {
            "model": m["model"],
            "accuracy": m["accuracy"],
            "macro_precision": m["macro_precision"],
            "macro_recall": m["macro_recall"],
            "macro_f1": m["macro_f1"],
            "weighted_f1": m["weighted_f1"],
            "negative_f1": m["per_class"]["Negative"]["f1"],
            "neutral_f1": m["per_class"]["Neutral"]["f1"],
            "positive_f1": m["per_class"]["Positive"]["f1"],
            "log_loss": m.get("log_loss", np.nan),
            "brier_score": m.get("brier_score", np.nan),
            "macro_roc_auc": m.get("macro_roc_auc", np.nan),
            "macro_pr_auc": m.get("macro_pr_auc", np.nan)
        } for m in all_metrics_list
    ])

    df_per_class = pd.DataFrame(per_class_records)

    # Save to results/
    df_metrics.to_csv(os.path.join(RESULTS_DIR, "classification_metrics.csv"), index=False)
    df_per_class.to_csv(os.path.join(RESULTS_DIR, "per_class_metrics.csv"), index=False)

    print("\n" + "=" * 80)
    print("FINAL UNTOUCHED TEST SET PERFORMANCE BENCHMARK")
    print("=" * 80)
    print(df_metrics[["model", "accuracy", "macro_precision", "macro_recall", "macro_f1", "weighted_f1", "neutral_f1"]].to_string(index=False))

    # 10. 5-Fold Stratified Cross-Validation on Development Set (Phase 11)
    dev_df = pd.concat([train_df, val_df], ignore_index=True)
    df_cv = run_stratified_kfold_cv(dev_df, n_splits=5, seed=SEED)
    df_cv.to_csv(os.path.join(RESULTS_DIR, "cross_validation_results.csv"), index=False)

    print("\n" + "=" * 80)
    print("5-FOLD STRATIFIED CROSS-VALIDATION SUMMARY (Development Partition)")
    print("=" * 80)
    print(df_cv[["model", "accuracy_mean", "accuracy_std", "macro_f1_mean", "macro_f1_std", "cv_macro_f1_display", "neutral_f1_mean"]].to_string(index=False))

    # 11. Master Model Comparison Table (Phase 20)
    df_comparison = df_metrics.merge(
        df_cv[["model", "macro_f1_mean", "macro_f1_std", "cv_macro_f1_display"]],
        on="model",
        how="left"
    )
    df_comparison.to_csv(os.path.join(RESULTS_DIR, "model_comparison.csv"), index=False)

    # 12. Systematic Ablation Studies (Phase 17)
    df_ablation = run_ablation_study(train_df, val_df, seed=SEED)
    df_ablation.to_csv(os.path.join(RESULTS_DIR, "ablation_results.csv"), index=False)

    # 13. Robustness Testing Suite (Phase 14)
    print("\n[Phase 14] Executing Robustness & Behavioral Stress-Testing Suite...")
    df_robustness = run_robustness_benchmark(
        trained_models,
        vectorizer=vectorizer,
        preprocess_fn=clean_text_for_classical
    )
    df_robustness.to_csv(os.path.join(RESULTS_DIR, "robustness_results.csv"), index=False)
    print(f"  Saved {len(df_robustness)} challenge case results -> results/robustness_results.csv")

    # 14. Error Analysis on Test Misclassifications (Phase 15)
    best_model_name = df_metrics.sort_values("macro_f1", ascending=False).iloc[0]["model"]
    print(f"\n[Phase 15] Performing Diagnostic Error Analysis for Champion Model: {best_model_name}...")
    df_errors = perform_test_error_analysis(
        test_df,
        y_pred=test_predictions[best_model_name],
        y_proba=test_probabilities.get(best_model_name),
        model_name=best_model_name,
        raw_col=raw_col
    )
    df_errors.to_csv(os.path.join(RESULTS_DIR, "error_analysis.csv"), index=False)

    # 15. Global Explainability & Feature Importance (Phase 18)
    print("\n[Phase 18] Extracting Global Feature Importance Terms...")
    champion_clf = trained_models.get("Linear SVM", trained_models["Logistic Regression"])
    df_features = extract_global_feature_importance(champion_clf, vectorizer, top_k=25)
    df_features.to_csv(os.path.join(RESULTS_DIR, "feature_importance.csv"), index=False)

    # 16. Computational Efficiency Benchmarking (Phase 21)
    print("\n[Phase 21] Benchmarking Computational Efficiency & Latency...")
    sample_texts = test_df[raw_col].head(1000).tolist()
    efficiency_records = []

    for name, clf in classical_models.items():
        eff = measure_efficiency_metrics(
            name,
            fit_fn=lambda: clf.fit(X_train, train_df["sentiment"]),
            predict_fn=lambda txts: clf.predict(vectorizer.transform([clean_text_for_classical(t) for t in txts])),
            sample_texts=sample_texts,
            model_obj=clf,
            save_path=os.path.join(MODELS_DIR, f"{name.lower().replace(' ', '_')}_model.pkl")
        )
        efficiency_records.append(eff)

    if "DistilBERT (Transformer)" in trained_models:
        d_pipe = trained_models["DistilBERT (Transformer)"]
        eff_d = measure_efficiency_metrics(
            "DistilBERT (Transformer)",
            fit_fn=lambda: d_pipe,
            predict_fn=lambda txts: d_pipe.predict(txts),
            sample_texts=sample_texts[:200],  # Subsample for latency estimation
            model_obj=d_pipe.model,
            save_path=distilbert_saved_dir
        )
        efficiency_records.append(eff_d)

    df_efficiency = pd.DataFrame(efficiency_records)
    df_efficiency.to_csv(os.path.join(RESULTS_DIR, "efficiency_benchmark.csv"), index=False)
    print(df_efficiency.to_string(index=False))

    # 17. Save Champion Models & Assets for Backend (Phase 19 & Compatibility)
    print("\n[Phase 19] Exporting Champion Model Assets & Synchronizing FastAPI Backend...")
    joblib.dump(vectorizer, os.path.join(MODELS_DIR, "tfidf_vectorizer.pkl"))
    joblib.dump(trained_models["Logistic Regression"], os.path.join(MODELS_DIR, "logistic_regression_model.pkl"))
    joblib.dump(trained_models["Linear SVM"], os.path.join(MODELS_DIR, "linear_svm_model.pkl"))
    joblib.dump(trained_models.get(best_model_name, trained_models["Linear SVM"]), os.path.join(MODELS_DIR, "best_sentiment_model.pkl"))

    # Backend compatibility files
    backend_res_df = df_metrics[["model", "accuracy", "macro_precision", "macro_recall", "macro_f1"]].copy()
    backend_res_df.to_csv(os.path.join(RESULTS_DIR, "model_results.csv"), index=False)

    best_row = df_metrics[df_metrics["model"] == best_model_name].iloc[0]
    vader_row = df_metrics[df_metrics["model"] == "VADER (Baseline)"].iloc[0]

    summary_json = {
        "best_supervised_model": best_model_name,
        "best_supervised_accuracy": float(best_row["accuracy"]),
        "best_supervised_macro_precision": float(best_row["macro_precision"]),
        "best_supervised_macro_recall": float(best_row["macro_recall"]),
        "best_supervised_macro_f1": float(best_row["macro_f1"]),
        "vader_accuracy": float(vader_row["accuracy"]),
        "vader_macro_precision": float(vader_row["macro_precision"]),
        "vader_macro_recall": float(vader_row["macro_recall"]),
        "vader_macro_f1": float(vader_row["macro_f1"]),
        "n_total": int(len(df)),
        "n_train": int(len(train_df)),
        "n_val": int(len(val_df)),
        "n_test": int(len(test_df)),
        "tfidf_features": int(len(vectorizer.get_feature_names_out())),
        "class_imbalance_handling": "70/15/15 Stratified Split + Class-Weighted Loss (balanced)",
        "train_size": 0.70,
        "val_size": 0.15,
        "test_size": 0.15,
        "random_state": SEED
    }

    with open(os.path.join(RESULTS_DIR, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary_json, f, indent=2)

    # 18. Generate Core Visualizations in Figures/
    print("\nGenerating Diagnostic Visualizations in Figures/...")

    def safe_savefig(fig, filepath):
        try:
            norm_path = os.path.abspath(os.path.normpath(filepath))
            os.makedirs(os.path.dirname(norm_path), exist_ok=True)
            fig.savefig(norm_path, dpi=300, bbox_inches="tight")
        except Exception as e:
            print(f"Warning: Could not save figure to {filepath} ({e}). Attempting fallback...")
            try:
                fig.savefig(norm_path, dpi=150)
            except Exception as e2:
                print(f"Warning: Failed to export figure {filepath}: {e2}")
        finally:
            plt.close(fig)

    # Model Comparison Bar Chart
    fig, ax = plt.subplots(figsize=(11, 5), dpi=300)
    plot_df = df_metrics.set_index("model")[["accuracy", "macro_precision", "macro_recall", "macro_f1"]]
    plot_df.plot(kind="bar", colormap="viridis", width=0.8, ax=ax)
    ax.set_title("Benchmarking Supervised & Transformer Models vs VADER Baseline (Untouched Test Set)", fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel("Model Architecture", fontweight="bold")
    ax.set_ylabel("Score (0.0 to 1.0)", fontweight="bold")
    ax.set_ylim(0, 1.05)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=15, ha="right")
    ax.legend(title="Evaluation Metric", bbox_to_anchor=(1.02, 1), loc="upper left")
    fig.tight_layout()
    safe_savefig(fig, os.path.join(FIG_DIR, "08_model_comparison.png"))

    # Dual Confusion Matrix Figure
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), dpi=300)
    cm_lr = compute_comprehensive_metrics(y_test_true, test_predictions["Logistic Regression"])["confusion_matrix"]
    sns.heatmap(cm_lr, annot=True, fmt="d", cmap="Blues", xticklabels=CLASSES, yticklabels=CLASSES, ax=axes[0])
    axes[0].set_title("Logistic Regression (TF-IDF)", fontweight="bold")
    axes[0].set_xlabel("Predicted Sentiment")
    axes[0].set_ylabel("Actual Sentiment")

    second_name = "Linear SVM" if "Linear SVM" in test_predictions else list(test_predictions.keys())[0]
    cm_second = compute_comprehensive_metrics(y_test_true, test_predictions[second_name])["confusion_matrix"]
    sns.heatmap(cm_second, annot=True, fmt="d", cmap="Greens", xticklabels=CLASSES, yticklabels=CLASSES, ax=axes[1])
    axes[1].set_title(f"{second_name}", fontweight="bold")
    axes[1].set_xlabel("Predicted Sentiment")
    axes[1].set_ylabel("Actual Sentiment")

    fig.tight_layout()
    safe_savefig(fig, os.path.join(FIG_DIR, "07_confusion_matrix.png"))

    # Top Predictive Words Bar Chart
    if not df_features.empty:
        fig, axes = plt.subplots(1, 3, figsize=(16, 5), dpi=300)
        colors = {"Negative": "#e74c3c", "Neutral": "#f39c12", "Positive": "#27ae60"}
        for ax, cname in zip(axes, CLASSES):
            sub = df_features[df_features["sentiment_class"] == cname].head(10)
            sns.barplot(
                x="positive_coefficient",
                y="top_positive_term",
                data=sub,
                ax=ax,
                color=colors.get(cname, "steelblue")
            )
            ax.set_title(f"Top Terms: {cname}", fontweight="bold")
            ax.set_xlabel("Coefficient Weight")
            ax.set_ylabel("Feature N-gram")
        fig.tight_layout()
        safe_savefig(fig, os.path.join(FIG_DIR, "09_top_predictive_words.png"))

    print("\n" + "=" * 80)
    print("RESEARCH PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
    print("All results, tables, and diagnostic figures saved in 'results/' and 'Figures/'.")
    print("=" * 80)

if __name__ == "__main__":
    main()
