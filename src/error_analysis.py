"""
error_analysis.py
=================
Systematic error analysis and misclassification taxonomy for the untouched test set.
Categorizes misclassifications into linguistic and structural failure modes.
"""

import re
import pandas as pd
import numpy as np

def categorize_error_sample(text: str, true_label: str, pred_label: str) -> str:
    """
    Heuristically tags failure modes based on explicit textual cues.
    """
    t_lower = str(text).lower()
    word_count = len(t_lower.split())
    
    # Check length first
    if word_count <= 3:
        return "Very Short Text (< 4 words)"
    if word_count >= 60:
        return "Very Long / Narrative Review (> 60 words)"

    # Check contrastive / mixed markers
    contrast_markers = [" but ", " however ", " though ", " although ", " yet ", " while "]
    if any(m in t_lower for m in contrast_markers):
        return "Mixed Sentiment / Contrastive Clause"

    # Check negation markers
    negation_markers = [" not ", " no ", " never ", "n't", " neither ", " nor ", " without "]
    if any(m in t_lower for m in negation_markers):
        return "Negation Interaction"

    # Check sarcasm cues
    sarcasm_markers = ["great,", "wonderful,", "thanks for nothing", "amazing wait", "love waiting"]
    if any(m in t_lower for m in sarcasm_markers) and true_label == "Negative":
        return "Sarcasm / Ironic Sentiment"

    # Neutral class confusion
    if true_label == "Neutral" or pred_label == "Neutral":
        return "Neutral Ambiguity / Borderline Polarity"

    # Spelling / noisy text
    if re.search(r"(.)\1{3,}", t_lower) or re.search(r"\b(gud|servce|burgur|terrible|mcd)\b", t_lower):
        return "Spelling / Lexical Noise"

    return "Domain Nuance / Uncategorized"


def perform_test_error_analysis(
    test_df: pd.DataFrame,
    y_pred: np.ndarray,
    y_proba: np.ndarray = None,
    model_name: str = "Linear SVM",
    raw_col: str = "review"
) -> pd.DataFrame:
    """
    Extracts all misclassified examples from the test set and tags their failure categories.
    """
    df_res = test_df.copy()
    df_res["true_sentiment"] = df_res["sentiment"]
    df_res["predicted_sentiment"] = y_pred
    df_res["is_error"] = df_res["true_sentiment"] != df_res["predicted_sentiment"]

    if y_proba is not None and y_proba.shape[1] == 3:
        df_res["prediction_confidence"] = np.max(y_proba, axis=1).round(4)
    else:
        df_res["prediction_confidence"] = np.nan

    errors_df = df_res[df_res["is_error"]].copy()
    
    error_cats = []
    for _, row in errors_df.iterrows():
        cat = categorize_error_sample(row[raw_col], row["true_sentiment"], row["predicted_sentiment"])
        error_cats.append(cat)
        
    errors_df["error_category"] = error_cats
    
    cols_to_keep = [
        raw_col, "true_sentiment", "predicted_sentiment",
        "error_category", "prediction_confidence"
    ]
    if "rating_num" in errors_df.columns:
        cols_to_keep.insert(1, "rating_num")
    if "rating" in errors_df.columns and "rating_num" not in errors_df.columns:
        cols_to_keep.insert(1, "rating")

    cols_to_keep = [c for c in cols_to_keep if c in errors_df.columns]
    errors_df = errors_df[cols_to_keep].copy()
    
    print(f"\n[ErrorAnalysis] {model_name} produced {len(errors_df):,} test errors out of {len(test_df):,} samples ({len(errors_df)/len(test_df)*100:.2f}% Error Rate).")
    print("Top Error Categories:")
    print(errors_df["error_category"].value_counts().to_string())
    
    return errors_df
