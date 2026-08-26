"""Create a transparent hybrid sentiment dataset from the human-labeled pilot.

The script uses only final human pilot labels as model targets; it never uses
star ratings or the old rating-derived ``sentiment`` column as input features.
It holds out a gold test set before model selection, evaluates once on that
test set, and labels only non-pilot free-text reviews with the chosen model.
"""
from pathlib import Path
import json
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split

BASE = Path(__file__).parent.parent
CLEANED = BASE.parent / "data" / "cleaned_reviews.csv"
PILOT = BASE / "pilot" / "annotated_reviews.csv"
REPORTS_DIR = BASE / "reports"
OUT_DATA = BASE.parent / "data" / "final_pseudo_labeled_dataset.csv"
OUT_REPORT = REPORTS_DIR / "pseudo_labeling_report.json"
OUT_HOLDOUT = REPORTS_DIR / "pseudo_labeling_holdout_predictions.csv"
OUT_MODEL = BASE.parent / "models" / "human_pilot_tfidf_logistic_model.pkl"
SEED = 42
CLASSES = ["Positive", "Neutral", "Negative"]
CONFIDENCE_REVIEW_THRESHOLD = 0.60


def metrics(y_true, y_pred):
    return {
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "macro_f1": round(float(f1_score(y_true, y_pred, labels=CLASSES, average="macro", zero_division=0)), 4),
    }


def main():
    REPORTS_DIR.mkdir(exist_ok=True)
    pilot = pd.read_csv(PILOT, encoding="utf-8")
    pilot["final_sentiment"] = pilot["final_sentiment"].fillna("").astype(str).str.strip().str.capitalize()
    human = pilot.loc[pilot["final_sentiment"].isin(CLASSES), ["review_id", "review", "rating", "final_sentiment"]].copy()
    if len(human) != len(pilot):
        raise ValueError("All pilot rows must have a valid final_sentiment before pseudo-labeling.")
    if human["review_id"].duplicated().any():
        raise ValueError("Pilot review_id values must be unique.")

    # 70/15/15 stratified split: validation selects hyperparameters; the test
    # set remains untouched until the one final evaluation below.
    train, temporary = train_test_split(human, test_size=0.30, random_state=SEED,
                                        stratify=human["final_sentiment"])
    validation, test = train_test_split(temporary, test_size=0.50, random_state=SEED,
                                        stratify=temporary["final_sentiment"])
    vectorizer = TfidfVectorizer(lowercase=True, stop_words="english", ngram_range=(1, 2),
                                 min_df=2, max_df=0.95, sublinear_tf=True, max_features=50000)
    x_train = vectorizer.fit_transform(train["review"])
    x_validation = vectorizer.transform(validation["review"])

    candidates = [
        {"C": 0.5, "class_weight": None},
        {"C": 1.0, "class_weight": None},
        {"C": 1.0, "class_weight": "balanced"},
        {"C": 2.0, "class_weight": "balanced"},
    ]
    candidate_results = []
    selected = None
    for parameters in candidates:
        classifier = LogisticRegression(max_iter=3000, random_state=SEED, multi_class="auto", **parameters)
        classifier.fit(x_train, train["final_sentiment"])
        result = {**parameters, **metrics(validation["final_sentiment"], classifier.predict(x_validation))}
        candidate_results.append(result)
        if selected is None or (result["macro_f1"], result["accuracy"]) > (selected[0]["macro_f1"], selected[0]["accuracy"]):
            selected = (result, parameters)

    # Evaluate the selected model exactly once against the untouched human test set.
    x_test = vectorizer.transform(test["review"])
    test_model = LogisticRegression(max_iter=3000, random_state=SEED, multi_class="auto", **selected[1])
    test_model.fit(x_train, train["final_sentiment"])
    test_predictions = test_model.predict(x_test)
    test_metrics = metrics(test["final_sentiment"], test_predictions)
    test_report = classification_report(test["final_sentiment"], test_predictions, labels=CLASSES,
                                        output_dict=True, zero_division=0)
    holdout = test[["review_id", "review", "rating", "final_sentiment"]].copy()
    holdout["predicted_sentiment"] = test_predictions
    holdout.to_csv(OUT_HOLDOUT, index=False, encoding="utf-8")

    # Refit only on the human train + validation records, preserving the gold
    # test labels for independent future evaluation.
    development = pd.concat([train, validation], ignore_index=True)
    final_vectorizer = TfidfVectorizer(lowercase=True, stop_words="english", ngram_range=(1, 2),
                                       min_df=2, max_df=0.95, sublinear_tf=True, max_features=50000)
    x_development = final_vectorizer.fit_transform(development["review"])
    final_model = LogisticRegression(max_iter=3000, random_state=SEED, multi_class="auto", **selected[1])
    final_model.fit(x_development, development["final_sentiment"])
    OUT_MODEL.parent.mkdir(exist_ok=True)
    joblib.dump({"vectorizer": final_vectorizer, "classifier": final_model, "classes": CLASSES}, OUT_MODEL)

    data = pd.read_csv(CLEANED, encoding="utf-8", low_memory=False)
    free_text = data.loc[~data["is_autotag"].astype(bool)].copy()
    pilot_ids = set(human["review_id"])
    remaining = free_text.loc[~free_text["reviewer_id"].isin(pilot_ids)].copy()
    probabilities = final_model.predict_proba(final_vectorizer.transform(remaining["review_clean"]))
    remaining["sentiment"] = final_model.classes_[probabilities.argmax(axis=1)]
    remaining["prediction_confidence"] = probabilities.max(axis=1)
    remaining["label_source"] = "model_pseudo_label"
    remaining["needs_human_review"] = remaining["prediction_confidence"] < CONFIDENCE_REVIEW_THRESHOLD
    remaining["split_role"] = "unlabeled_pool"

    human_output = free_text.loc[free_text["reviewer_id"].isin(pilot_ids)].copy()
    human_labels = human.set_index("review_id")["final_sentiment"]
    human_output["sentiment"] = human_output["reviewer_id"].map(human_labels)
    human_output["prediction_confidence"] = 1.0
    human_output["label_source"] = "human_annotated"
    human_output["needs_human_review"] = False
    roles = {row.review_id: "train" for row in train.itertuples()}
    roles.update({row.review_id: "validation" for row in validation.itertuples()})
    roles.update({row.review_id: "gold_test" for row in test.itertuples()})
    human_output["split_role"] = human_output["reviewer_id"].map(roles)

    output = pd.concat([human_output, remaining], ignore_index=True)
    output = output[["reviewer_id", "review_clean", "rating_num", "sentiment", "label_source",
                     "prediction_confidence", "needs_human_review", "split_role", "is_autotag",
                     "store_name", "store_address", "review_time", "days_ago"]].rename(columns={
                         "reviewer_id": "review_id", "review_clean": "review", "rating_num": "rating"
                     })
    output.to_csv(OUT_DATA, index=False, encoding="utf-8")

    report = {
        "method": "TF-IDF (1-2 grams) + Logistic Regression; trained only on resolved human pilot labels",
        "random_seed": SEED,
        "split_counts": {"train": len(train), "validation": len(validation), "gold_test": len(test)},
        "selected_parameters": selected[1], "validation_candidates": candidate_results,
        "gold_test_metrics": test_metrics, "gold_test_classification_report": test_report,
        "pseudo_labeling": {"human_annotated": len(human_output), "model_pseudo_label": len(remaining),
                              "confidence_review_threshold": CONFIDENCE_REVIEW_THRESHOLD,
                              "low_confidence_predictions": int(remaining["needs_human_review"].sum())},
        "limitation": "Predicted labels are pseudo-labels, not human ground truth. The gold_test split was excluded from training and must be retained for independent evaluation. Rating was not used as a predictive input feature."
    }
    OUT_REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("Selected validation configuration:", selected[0])
    print("Gold-test metrics:", test_metrics)
    print(f"Saved {OUT_DATA.name}: {len(output)} free-text rows; {int(remaining['needs_human_review'].sum())} low-confidence pseudo-labels.")
    print("Saved:", OUT_REPORT.name, OUT_HOLDOUT.name, OUT_MODEL)


if __name__ == "__main__":
    main()
