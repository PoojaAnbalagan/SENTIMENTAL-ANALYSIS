"""Compute agreement and rating-proxy validation after blinded annotation.

Copy completed labels from the three blinded sheets into annotated_reviews.csv
before running.  This script never invents a final label and rejects incomplete
or invalid annotations.
"""
from pathlib import Path
from collections import Counter
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, cohen_kappa_score, confusion_matrix, f1_score

BASE = Path(__file__).parent.parent
ANNOTATED = BASE / "pilot" / "annotated_reviews.csv"
REPORTS_DIR = BASE / "reports"
IAA_CSV = REPORTS_DIR / "inter_annotator_agreement.csv"
DISAGREE_CSV = REPORTS_DIR / "disagreement_cases.csv"
SUMMARY_CSV = REPORTS_DIR / "agreement_summary.csv"
CLASSES = ["Positive", "Neutral", "Negative"]
ANN_COLS = ["annotator_1", "annotator_2", "annotator_3"]


def normalise(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.strip().str.capitalize()


def fleiss_kappa(labels: pd.DataFrame):
    matrix = np.column_stack([(labels == c).sum(axis=1).to_numpy() for c in CLASSES])
    raters = labels.shape[1]
    observed = float((matrix * (matrix - 1)).sum(axis=1).mean() / (raters * (raters - 1)))
    proportions = matrix.sum(axis=0) / (len(labels) * raters)
    expected = float((proportions ** 2).sum())
    return ((observed - expected) / (1 - expected) if expected < 1 else 1.0), observed, expected, proportions


def majority(row: pd.Series) -> str:
    label, count = Counter(row[ANN_COLS]).most_common(1)[0]
    return label if count >= 2 else ""


def main() -> None:
    REPORTS_DIR.mkdir(exist_ok=True)
    df = pd.read_csv(ANNOTATED, encoding="utf-8")
    required = {"review_id", "review", "rating", "rating_derived_label", *ANN_COLS, "final_sentiment"}
    if missing := required.difference(df.columns):
        raise ValueError(f"Missing columns: {sorted(missing)}")
    for column in ANN_COLS:
        df[column] = normalise(df[column])
    incomplete = df[ANN_COLS].eq("").any(axis=1)
    invalid = {c: sorted(set(df.loc[~df[c].isin(CLASSES), c]) - {""}) for c in ANN_COLS}
    invalid = {c: v for c, v in invalid.items() if v}
    if incomplete.any() or invalid:
        raise ValueError(f"Cannot analyse: {int(incomplete.sum())} incomplete rows; invalid labels={invalid}")

    df["majority_label"] = df.apply(majority, axis=1)
    df["full_agreement"] = df[ANN_COLS].nunique(axis=1).eq(1)
    df["requires_resolution"] = df["majority_label"].eq("")
    kappa, observed, expected, proportions = fleiss_kappa(df[ANN_COLS])
    final = normalise(df["final_sentiment"])
    fill_from_majority = final.eq("") & df["majority_label"].ne("")
    df.loc[fill_from_majority, "final_sentiment"] = df.loc[fill_from_majority, "majority_label"]
    df["final_sentiment"] = normalise(df["final_sentiment"])

    complete_final = df["final_sentiment"].isin(CLASSES).all()
    accuracy = rating_kappa = macro_f1 = np.nan
    if complete_final:
        accuracy = accuracy_score(df["final_sentiment"], df["rating_derived_label"])
        rating_kappa = cohen_kappa_score(df["final_sentiment"], df["rating_derived_label"], labels=CLASSES)
        macro_f1 = f1_score(df["final_sentiment"], df["rating_derived_label"], labels=CLASSES, average="macro", zero_division=0)
        matrix = confusion_matrix(df["final_sentiment"], df["rating_derived_label"], labels=CLASSES)
    else:
        matrix = None

    rows = [
        ("items", len(df)), ("full_agreement_rate", df["full_agreement"].mean()),
        ("mean_pairwise_observed_agreement", observed), ("expected_chance_agreement", expected),
        ("fleiss_kappa", kappa), ("all_three_different", int(df["requires_resolution"].sum())),
        ("rating_vs_final_accuracy", accuracy), ("rating_vs_final_cohen_kappa", rating_kappa),
        ("rating_vs_final_macro_f1", macro_f1),
    ]
    for label, proportion in zip(CLASSES, proportions):
        rows.extend([(f"annotation_proportion_{label}", proportion),
                     (f"full_consensus_{label}", int((df.loc[df.full_agreement, ANN_COLS].iloc[:, 0] == label).sum()))])
    pd.DataFrame(rows, columns=["metric", "value"]).to_csv(SUMMARY_CSV, index=False)
    df.to_csv(ANNOTATED, index=False, encoding="utf-8")
    df.to_csv(IAA_CSV, index=False, encoding="utf-8")
    disagreements = df.loc[~df.full_agreement].copy()
    # Preserve adjudication notes when the script is rerun after resolution.
    # The master file intentionally has no notes column, so carry existing
    # coordinator notes forward by review ID.
    if DISAGREE_CSV.exists():
        previous = pd.read_csv(DISAGREE_CSV, encoding="utf-8")
        if {"review_id", "resolution_notes"}.issubset(previous.columns):
            notes = previous.set_index("review_id")["resolution_notes"]
            disagreements["resolution_notes"] = disagreements["review_id"].map(notes).fillna("")
        else:
            disagreements["resolution_notes"] = ""
    else:
        disagreements["resolution_notes"] = ""
    disagreements.to_csv(DISAGREE_CSV, index=False, encoding="utf-8")

    print(f"Fleiss' kappa: {kappa:.4f}; mean pairwise observed agreement: {observed:.4f}.")
    print(f"Saved {IAA_CSV.name}, {DISAGREE_CSV.name}, and {SUMMARY_CSV.name}.")
    if matrix is None:
        print("Rating validation pending: resolve every final_sentiment first.")
    else:
        print(f"Rating vs final: accuracy={accuracy:.4f}, kappa={rating_kappa:.4f}, macro-F1={macro_f1:.4f}")
        print(pd.DataFrame(matrix, index=CLASSES, columns=CLASSES))


if __name__ == "__main__":
    main()
