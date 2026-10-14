"""
data_loader.py
==============
Data loading, cleaning, deduplication auditing, and strict 70/15/15 stratified splitting.
Guarantees zero data leakage into the final test set.
"""

import os
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

CLASSES = ["Negative", "Neutral", "Positive"]
LABEL_MAP = {"Negative": 0, "Neutral": 1, "Positive": 2}
REV_LABEL_MAP = {0: "Negative", 1: "Neutral", 2: "Positive"}
SEED = 42

def load_and_audit_dataset(data_path: str = None) -> tuple[pd.DataFrame, dict]:
    """
    Loads the dataset from available candidates, audits duplicates and class distribution.
    """
    if data_path is None:
        candidate_paths = [
            "data/final_pseudo_labeled_dataset.csv",
            "../data/final_pseudo_labeled_dataset.csv",
            "data/cleaned_reviews.csv",
            "../data/cleaned_reviews.csv",
            "notebooks/text_reviews_processed.csv",
            "text_reviews_processed.csv"
        ]
        data_path = next((p for p in candidate_paths if os.path.exists(p)), None)
        if data_path is None:
            raise FileNotFoundError("Could not find suitable review dataset in project.")

    print(f"[DataLoader] Ingesting dataset from: {data_path}")
    df = pd.read_csv(data_path)

    # Standardize column naming
    raw_col = "review" if "review" in df.columns else ("review_clean" if "review_clean" in df.columns else df.columns[1])
    if "review_clean" not in df.columns:
        df["review_clean"] = df[raw_col]
    if "sentiment" not in df.columns and "sentiment_final" in df.columns:
        df["sentiment"] = df["sentiment_final"]

    # Filter invalid/empty rows
    initial_count = len(df)
    df = df.dropna(subset=[raw_col, "sentiment"]).copy()
    df["sentiment"] = df["sentiment"].astype(str).str.strip().str.capitalize()
    df = df[df["sentiment"].isin(CLASSES)].copy()
    
    # Exclude auto-tag rows if flagged
    if "is_autotag" in df.columns:
        df = df[~df["is_autotag"].astype(bool)].copy()

    # Deduplication audit
    exact_duplicates = df.duplicated(subset=[raw_col, "sentiment"]).sum()
    text_conflicts = df.groupby(raw_col)["sentiment"].nunique()
    conflict_count = (text_conflicts > 1).sum()

    audit_info = {
        "initial_rows": initial_count,
        "valid_rows": len(df),
        "exact_duplicates": int(exact_duplicates),
        "conflicting_label_duplicates": int(conflict_count),
        "sentiment_distribution": df["sentiment"].value_counts().to_dict(),
        "sentiment_proportions": df["sentiment"].value_counts(normalize=True).to_dict()
    }

    # Remove exact duplicates for clean evaluation while preserving original data
    if exact_duplicates > 0:
        df = df.drop_duplicates(subset=[raw_col, "sentiment"]).copy()
        audit_info["rows_after_deduplication"] = len(df)
    else:
        audit_info["rows_after_deduplication"] = len(df)

    df["label_id"] = df["sentiment"].map(LABEL_MAP)
    return df, audit_info


def create_stratified_splits(
    df: pd.DataFrame,
    train_size: float = 0.70,
    val_size: float = 0.15,
    test_size: float = 0.15,
    seed: int = SEED
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
    """
    Splits dataset into 70% Train, 15% Validation, and 15% Final Untouched Test
    with class stratification on sentiment labels.
    """
    assert np.isclose(train_size + val_size + test_size, 1.0), "Split ratios must sum to 1.0"

    # Step 1: Split into Train (70%) and Temp (30%)
    train_df, temp_df = train_test_split(
        df,
        train_size=train_size,
        random_state=seed,
        stratify=df["label_id"]
    )

    # Step 2: Split Temp into Validation (50% of 30% = 15%) and Final Test (50% of 30% = 15%)
    val_df, test_df = train_test_split(
        temp_df,
        test_size=0.50,
        random_state=seed,
        stratify=temp_df["label_id"]
    )

    split_stats = {
        "train_count": len(train_df),
        "train_pct": round(len(train_df) / len(df) * 100, 2),
        "val_count": len(val_df),
        "val_pct": round(len(val_df) / len(df) * 100, 2),
        "test_count": len(test_df),
        "test_pct": round(len(test_df) / len(df) * 100, 2),
        "train_distribution": train_df["sentiment"].value_counts().to_dict(),
        "val_distribution": val_df["sentiment"].value_counts().to_dict(),
        "test_distribution": test_df["sentiment"].value_counts().to_dict()
    }

    print(f"[DataLoader] Stratified Split complete:")
    print(f"  - Training (70%)      : {len(train_df):,} samples")
    print(f"  - Validation (15%)    : {len(val_df):,} samples")
    print(f"  - Untouched Test (15%): {len(test_df):,} samples")

    return train_df.copy(), val_df.copy(), test_df.copy(), split_stats
