# Data Architecture & Dataset Lineage

This directory houses the structured customer review corpora powering the McDonald's Customer Review Sentiment Analysis and Intelligence Platform.

---

## 📊 Dataset Catalog & Lifecycle

| Filename | Description | Records | Schema Highlights | Role in Pipeline |
| :--- | :--- | :--- | :--- | :--- |
| **`DATASET.csv`** | Raw initial dataset scraped from Google Maps across McDonald's outlets | 33,396 | `reviewer_id`, `store_name`, `category`, `store_address`, `latitude`, `longitude`, `rating_count`, `review_time`, `review`, `rating` | Raw Ingestion Source |
| **`cleaned_reviews.csv`** | Sanitized, deduplicated, and normalized customer review corpus | 22,476 | `reviewer_id`, `store_name`, `rating_num`, `review`, `review_clean`, `is_autotag`, `days_ago`, `derived_date` | Cleaned Master Dataset |
| **`final_pseudo_labeled_dataset.csv`** | Annotated master corpus with verified sentiment ground-truth labels | 22,448 | `reviewer_id`, `review`, `review_clean`, `rating_num`, `sentiment` (*Positive*, *Neutral*, *Negative*), `confidence`, `label_source` | Core Production Corpus (ML & REST API) |

---

## 🔄 10-Stage Data Cleaning & Preprocessing Flow

```
Raw Ingestion (DATASET.csv, 33,396 rows)
   │
   ▼
[1] CP1252/UTF-8 Mojibake Sanitization (Stripped 'ý', 'ï¿½')
   │
   ▼
[2] Star Rating Extraction (Parsed '1 star'...'5 stars' -> rating_num ∈ {1..5})
   │
   ▼
[3] Reviewer Rating Count Parsing (Numeric conversion)
   │
   ▼
[4] Relative Time Normalization ('3 months ago' -> days_ago & derived_date)
   │
   ▼
[5] Empty & Short Review Removal (<3 characters discarded)
   │
   ▼
[6] Google Autotag Isolation (Flagged is_autotag=True to prevent 100% label leakage)
   │
   ▼
[7] Exact Duplicate Elimination (10,741 duplicate reviews dropped)
   │
   ▼
[8] Cleaned Master Dataset (cleaned_reviews.csv, 22,476 rows)
   │
   ▼
[9] 3-Annotator Pilot & Pseudo-Labeling Pipeline (IAA Fleiss' κ = 0.6287)
   │
   ▼
[10] Final Labeled Master Corpus (final_pseudo_labeled_dataset.csv, 22,448 rows)
```

---

## 🛡️ Data Leakage Controls

1. **Autotag Isolation**: Generic Google star placeholder words (*'excellent'*, *'poor'*, *'good'*, *'average'*) were flagged and separated so classifiers cannot memorize 1-word shortcuts.
2. **Train/Test Isolation**: All TF-IDF vectorizers are fitted strictly on `X_train` (`fit_transform`) and applied to `X_test` via `.transform()`.
3. **Target Exclusions**: Metadata columns (star ratings, store addresses, timestamps) are strictly excluded from text feature matrices.
