# Sentiment Labeling Methodology

## Dataset inspection (completed)

| Item | Result |
|---|---|
| Dataset size | 22,476 cleaned records |
| Review-text column | `review_clean` |
| Rating column | `rating_num` (integer 1–5) |
| Existing sentiment column | `sentiment` |
| Current label status | Existing labels exactly follow 1–2 = Negative, 3 = Neutral, 4–5 = Positive; they are rating-derived proxies, not validated text ground truth. |
| Missing values | `latitude` and `longitude`: 650 each; no missing review, rating, or existing proxy label values. |
| Exact duplicate review texts | 342 (none duplicate on the review-plus-rating combination) |
| Empty reviews | 0 |
| Auto-generated tags flagged | 28 |

Rating distribution: 1 star 7,192 (32.0%); 2 stars 2,271 (10.1%); 3 stars 3,194 (14.2%); 4 stars 3,635 (16.2%); 5 stars 6,184 (27.5%).

**Applicable case: D.** The data contain reviews and ratings but no independently validated sentiment labels. The pre-existing `sentiment` column must be treated as a rating-derived label, not as a reliable human label.

## Label schema and procedure

Use exactly three labels: `Positive`, `Neutral`, and `Negative`. Their definitions and edge-case rules are in `annotation_guidelines.md`. Labels reflect the review's overall expressed sentiment, rather than individual words or the star rating. Annotators must label text only: ratings are withheld during independent annotation.

A reproducible 1,000-review pilot was drawn from free-text records with seed 42, proportionally stratified by rating. Three independent annotators each label the same pilot in their own blinded sheet. Fleiss' Kappa, chance-corrected agreement, is calculated only after all three annotations are complete. Percentage agreement must be reported alongside, never used as the sole reliability claim.

For a two-to-one split, the majority label is entered as the provisional final label. For an all-different split, annotators discuss the case using the guideline and document the decision and rationale in `disagreement_cases.csv`. Original annotations are never overwritten.

The rating mapping (1–2 Negative, 3 Neutral, 4–5 Positive) is evaluated against the fully resolved human pilot with accuracy, Cohen's Kappa, macro-F1, and a three-class confusion matrix. Only if the team considers the results substantively adequate and records an explicit approval may it label remaining reviews. A suggested minimum decision rule is accuracy at least 0.80 **and** Fleiss' Kappa at least 0.60, but the final decision must discuss class-specific errors, particularly the Neutral class, rather than relying on thresholds alone.

## Pilot and final-labeling results

Three annotators completed the 1,000-review pilot. Fleiss' Kappa was **0.6287** (substantial agreement), with mean pairwise observed agreement of **0.7697**. There were 664 full-agreement cases, 317 two-of-three majority cases, and 19 all-different cases adjudicated to a final label.

The rating mapping compared with the resolved human pilot produced accuracy **0.7890**, Cohen's Kappa **0.6543**, and macro-F1 **0.6936**. It fell below the pre-specified 0.80 accuracy criterion and was particularly weak for human-Neutral reviews (51 of 135 correctly mapped), so it is retained only as a documented baseline.

The selected alternative is **hybrid pseudo-labeling**. A TF-IDF (unigrams and bigrams) Logistic Regression model was selected using a 700/150 human train/validation split and evaluated once on an untouched 150-review gold test set. Gold-test accuracy was **0.7067** and macro-F1 was **0.5986**. The chosen model was refit on the 850 human train-plus-validation records and predicted the 21,448 remaining free-text reviews. The output is `data/final_pseudo_labeled_dataset.csv`: 1,000 `human_annotated` records and 21,448 `model_pseudo_label` records. A total of 9,549 predictions were below the predeclared 0.60 confidence threshold and are flagged `needs_human_review=True`.

Predicted labels are not human ground truth. Report the gold-test metrics and the pseudo-label limitation, retain the `gold_test` split for independent evaluation, and never use rating as an ML input feature.

## Leakage controls

The human pilot was split before model selection into train, validation, and an untouched `gold_test` set. Do not use the gold test set to tune models or alter labels. Do not use sentiment labels or ratings as model input features. Do not report an evaluation against model-generated pseudo-labels as independent model performance.

## Final QC

Before modeling, verify no missing or invalid labels; inspect duplicate review texts with conflicting labels; count empty/very short and ambiguous reviews; confirm the label source for every record; and report class counts and percentages. Use `needs_human_review` to identify the 9,549 lower-confidence pseudo-labels. Use stratified splits and class-weighted learning for the class imbalance. Do not apply SMOTE directly to raw text.

## Action plan

1. Give each annotator only their corresponding `annotator_N_sheet.csv` and the guidelines.
2. Collect the sheets; validate that IDs are unchanged, then copy each label column into `annotated_reviews.csv`.
3. Run `python labeling/compute_iaa.py`; resolve every listed disagreement and rerun it.
4. Review `agreement_summary.csv`, the confusion matrix, and mismatches. Decide and document whether rating-derived labels are defensible.
5. If approved, create `labeling_decision.json` with the documented approval and run `python labeling/build_final_dataset.py`. If not approved, follow a separately documented manual-labeling or adjudication plan; do not use the rating proxy by default.
6. Run final QC, report the class distribution, then split data for modeling using stratification.

## Deliverables and columns

| File | Required columns / purpose |
|---|---|
| `annotation_guidelines.md` (and PDF export) | Rules, definitions, examples, and ambiguity handling. |
| `annotation_sample_1000.csv` | `review_id, review, rating, rating_derived_label`; coordinator reference only. |
| `annotator_1_sheet.csv` through `annotator_3_sheet.csv` | `review_id, review, annotator_N`; blinded independent labeling. |
| `annotated_reviews.csv` | Reference columns plus the three annotator columns and `final_sentiment`. |
| `inter_annotator_agreement.csv` | Annotated master plus `majority_label`, `full_agreement`, and `requires_resolution`. |
| `agreement_summary.csv` | Fleiss' Kappa, agreement metrics, and rating-validation metrics. |
| `disagreement_cases.csv` | Disputed items plus `resolution_notes`. |
| `final_labeled_dataset.csv` | `review_id, review, rating, sentiment, label_source, is_autotag` and contextual source fields. |
