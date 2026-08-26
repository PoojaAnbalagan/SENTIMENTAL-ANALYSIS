"""
build_final_dataset.py
======================
Run AFTER:
  (a) The 1,000-review pilot has been fully annotated and final_sentiment is
      filled in annotated_reviews.csv for every row, AND
  (b) You have decided to use the validated rating-based strategy for the
      remaining ~21,000 reviews (Strategy A), or you have manually annotated
      all reviews (Strategy B).

What this script does
---------------------
1.  Loads cleaned_reviews.csv (22,477 rows).
2.  Applies the validated sentiment label:
      • For the 1,000 pilot rows  → uses the human-resolved final_sentiment.
      • For the remaining rows    → uses the rating-derived label
        (1-2 → Negative | 3 → Neutral | 4-5 → Positive),
        PROVIDED you confirmed this mapping is sufficiently reliable in compute_iaa.py.
3.  Excludes auto-tag rows from the supervised learning set (flagged separately).
4.  Performs quality-control checks.
5.  Reports the final class distribution and imbalance status.
6.  Saves final_labeled_dataset.csv.

Usage
-----
    python build_final_dataset.py

Output
------
    ../labeling/final_labeled_dataset.csv
"""

import pathlib
import json
import pandas as pd
import numpy as np

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE         = pathlib.Path(__file__).parent.parent
DATA_DIR     = BASE.parent / "data"
CLEANED_CSV  = DATA_DIR / "cleaned_reviews.csv"
ANNOTATED    = BASE / "pilot" / "annotated_reviews.csv"
FINAL_CSV    = BASE / "archive" / "rating_proxy_dataset.csv"
DECISION_JSON = BASE / "decisions" / "labeling_decision.json"

CLASSES = {"Positive", "Neutral", "Negative"}

# ── Load ──────────────────────────────────────────────────────────────────────
print("Loading datasets...")
df      = pd.read_csv(CLEANED_CSV, encoding="utf-8", low_memory=False)
pilot   = pd.read_csv(ANNOTATED,   encoding="utf-8")

print(f"  Cleaned dataset  : {len(df):,} rows")
print(f"  Pilot sample     : {len(pilot):,} rows")

# The remaining reviews must not be rating-labelled merely because this script
# exists.  A researcher records an explicit decision only after inspecting the
# pilot's agreement and rating-validation results.
if not DECISION_JSON.exists():
    raise RuntimeError(
        "Missing labeling_decision.json. Do not create the full dataset until "
        "the human pilot is complete and the final strategy has been approved."
    )
with DECISION_JSON.open(encoding="utf-8") as f:
    decision = json.load(f)
if decision.get("strategy") not in {"validated_rating_based", "rating_proxy_with_limitations"} or decision.get("approved") is not True:
    raise RuntimeError(
        "This builder requires an explicitly approved rating-based strategy. "
        "For manual or another strategy, create labels with its documented procedure."
    )
if decision.get("strategy") == "rating_proxy_with_limitations" and decision.get("acknowledged_limitations") is not True:
    raise RuntimeError(
        "The rating-proxy strategy requires acknowledged_limitations=true in labeling_decision.json."
    )

# ── Validate pilot completeness ───────────────────────────────────────────────
pilot_filled  = pilot["final_sentiment"].astype(str).str.strip().isin(CLASSES)
n_filled      = pilot_filled.sum()
n_missing     = (~pilot_filled).sum()

print(f"\n  Pilot rows with final_sentiment filled  : {n_filled}")
print(f"  Pilot rows still MISSING final_sentiment: {n_missing}")

if n_missing > 0:
    raise RuntimeError("Every pilot review needs a valid final_sentiment before the full dataset can be built.")

pilot_valid = pilot[pilot_filled].copy()

# ── Build sentiment column for the full dataset ───────────────────────────────
# Strategy A: rating-based for non-pilot rows, human label for pilot rows
def rating_to_sentiment(r):
    if r <= 2:
        return "Negative"
    elif r == 3:
        return "Neutral"
    else:
        return "Positive"

df["sentiment_final"]   = df["rating_num"].apply(rating_to_sentiment)
df["label_source"]      = "rating_derived"

# Overwrite pilot rows with the human-resolved label
pilot_ids = pilot_valid.set_index("review_id")["final_sentiment"]
pilot_mask = df["reviewer_id"].isin(pilot_ids.index)
df.loc[pilot_mask, "sentiment_final"] = df.loc[pilot_mask, "reviewer_id"].map(pilot_ids)
df.loc[pilot_mask, "label_source"]    = "human_annotated"

print(f"\n  Label source breakdown:")
print(df["label_source"].value_counts().to_string())

# ── Quality-Control Checks ────────────────────────────────────────────────────
print("\n=== QUALITY-CONTROL REPORT ===")

# QC-1: Missing labels
n_missing_label = df["sentiment_final"].isna().sum()
print(f"\n  QC-1  Missing sentiment labels  : {n_missing_label}")

# QC-2: Invalid labels
invalid_mask = ~df["sentiment_final"].isin(CLASSES)
n_invalid = invalid_mask.sum()
print(f"  QC-2  Invalid sentiment labels  : {n_invalid}")
if n_invalid > 0:
    print("         Invalid values found:", df.loc[invalid_mask, "sentiment_final"].unique())

# QC-3: Duplicate reviews with conflicting labels
dup_mask = df.duplicated(subset=["review_clean"], keep=False)
dups = df[dup_mask]
conflict_dups = dups.groupby("review_clean")["sentiment_final"].nunique()
n_conflicted = (conflict_dups > 1).sum()
print(f"  QC-3  Duplicate reviews with conflicting labels: {n_conflicted}")

# QC-4: Rating-sentiment consistency (for rating-derived rows only)
rd = df[df["label_source"] == "rating_derived"].copy()
inconsistent = (
    ((rd["rating_num"] <= 2) & (rd["sentiment_final"] != "Negative")) |
    ((rd["rating_num"] == 3) & (rd["sentiment_final"] != "Neutral"))  |
    ((rd["rating_num"] >= 4) & (rd["sentiment_final"] != "Positive"))
)
print(f"  QC-4  Rating/label inconsistencies (rating-derived rows): {inconsistent.sum()}")

# QC-5: Auto-tag rows
n_autotag = df["is_autotag"].sum()
print(f"  QC-5  Auto-tag rows (excluded from ML set): {n_autotag}")

# QC-6: Very short reviews (≤ 5 chars) — flagged but NOT removed
n_short = (df["review_clean"].str.len() <= 5).sum()
print(f"  QC-6  Very short reviews (<= 5 chars): {n_short}")

# QC-7: Empty reviews
n_empty = (df["review_clean"].str.strip() == "").sum()
print(f"  QC-7  Empty reviews                 : {n_empty}")

# ── Class distribution ────────────────────────────────────────────────────────
print("\n=== CLASS DISTRIBUTION (full dataset, inc. auto-tag) ===")
dist = df["sentiment_final"].value_counts()
total = len(df)
for label in ["Positive", "Neutral", "Negative"]:
    count = dist.get(label, 0)
    pct   = count / total * 100
    print(f"  {label:10s}: {count:6,}  ({pct:.1f}%)")

# ML set = free-text only (exclude auto-tags)
print("\n=== CLASS DISTRIBUTION (ML set - free-text only, is_autotag=False) ===")
df_ml = df[~df["is_autotag"]].copy()
dist_ml = df_ml["sentiment_final"].value_counts()
total_ml = len(df_ml)
counts = {}
for label in ["Positive", "Neutral", "Negative"]:
    count = dist_ml.get(label, 0)
    pct   = count / total_ml * 100
    counts[label] = count
    print(f"  {label:10s}: {count:6,}  ({pct:.1f}%)")

# Imbalance assessment
max_cls = max(counts.values())
min_cls = min(counts.values())
ratio   = max_cls / min_cls if min_cls > 0 else float("inf")
print(f"\n  Majority / Minority ratio: {ratio:.2f}")
if ratio < 1.5:
    imbalance = "Balanced — no special handling needed."
elif ratio < 4.0:
    imbalance = "Moderately imbalanced — use stratified splits and class weights."
else:
    imbalance = "Highly imbalanced — consider class weights + stratified splits."
print(f"  Imbalance status: {imbalance}")

print("\n  Recommendation:")
print("  - Always use stratified train/val/test splits.")
print("  - Pass class_weight='balanced' to scikit-learn classifiers.")
print("  - For transformers, use weighted cross-entropy loss.")
print("  - Do NOT apply SMOTE or similar oversampling to raw text data.")

# ── Save ──────────────────────────────────────────────────────────────────────
out_cols = [
    "reviewer_id",
    "review_clean",
    "rating_num",
    "sentiment_final",
    "label_source",
    "is_autotag",
    "store_name",
    "store_address",
    "review_time",
    "days_ago",
]
# Keep only columns that exist
out_cols = [c for c in out_cols if c in df.columns]

df[out_cols].rename(columns={
    "reviewer_id":    "review_id",
    "review_clean":   "review",
    "rating_num":     "rating",
    "sentiment_final":"sentiment",
}).to_csv(FINAL_CSV, index=False, encoding="utf-8")

print(f"\nSaved -> {FINAL_CSV}  ({len(df):,} rows)")
print("\nDone. You are now ready for the preprocessing / feature engineering stage.")
