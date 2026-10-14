"""
evaluation_metrics.py
=====================
Comprehensive evaluation framework for 3-class sentiment classification:
- Accuracy, Macro/Weighted/Per-Class Precision, Recall, F1, Support
- Raw & Normalized Confusion Matrices and Top Confusion Pairs
- Multi-class Log Loss & Multi-class Brier Score
- One-vs-Rest Macro ROC-AUC & PR-AUC
- Publication-quality Confusion Matrix PNG & CSV export
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    log_loss,
    brier_score_loss,
    roc_auc_score,
    average_precision_score
)
from sklearn.preprocessing import label_binarize

CLASSES = ["Negative", "Neutral", "Positive"]
LABEL_MAP = {"Negative": 0, "Neutral": 1, "Positive": 2}
REV_LABEL_MAP = {0: "Negative", 1: "Neutral", 2: "Positive"}

def compute_comprehensive_metrics(
    y_true: np.ndarray | list,
    y_pred: np.ndarray | list,
    y_proba: np.ndarray = None,
    model_name: str = "Model"
) -> dict:
    """
    Computes all standard, macro, weighted, and per-class metrics.
    """
    y_true = np.array([str(y).capitalize() for y in y_true])
    y_pred = np.array([str(y).capitalize() for y in y_pred])

    acc = accuracy_score(y_true, y_pred)

    # Macro averages
    macro_p, macro_r, macro_f1, _ = precision_recall_fscore_support(
        y_true, y_pred, labels=CLASSES, average="macro", zero_division=0
    )

    # Weighted averages
    weight_p, weight_r, weight_f1, _ = precision_recall_fscore_support(
        y_true, y_pred, labels=CLASSES, average="weighted", zero_division=0
    )

    # Per-class metrics
    class_p, class_r, class_f1, class_supp = precision_recall_fscore_support(
        y_true, y_pred, labels=CLASSES, average=None, zero_division=0
    )

    per_class_dict = {}
    for idx, cname in enumerate(CLASSES):
        per_class_dict[cname] = {
            "precision": round(float(class_p[idx]), 4),
            "recall": round(float(class_r[idx]), 4),
            "f1": round(float(class_f1[idx]), 4),
            "support": int(class_supp[idx])
        }

    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred, labels=CLASSES)
    cm_norm = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis]
    cm_norm = np.nan_to_num(cm_norm)

    # Identify most common confusion pairs (off-diagonal)
    confusion_pairs = []
    for i, true_c in enumerate(CLASSES):
        for j, pred_c in enumerate(CLASSES):
            if i != j:
                confusion_pairs.append({
                    "true_class": true_c,
                    "pred_class": pred_c,
                    "count": int(cm[i, j]),
                    "error_rate_in_class": round(float(cm_norm[i, j] * 100), 2)
                })
    confusion_pairs.sort(key=lambda x: x["count"], reverse=True)

    # Probability metrics if provided
    prob_metrics = {}
    if y_proba is not None and y_proba.shape[1] == 3:
        try:
            # One-hot true matrix
            y_true_bin = label_binarize([LABEL_MAP[c] for c in y_true], classes=[0, 1, 2])
            prob_metrics["log_loss"] = round(float(log_loss(y_true_bin, y_proba)), 4)

            # Multi-class Brier score (mean squared difference over classes)
            brier_sum = 0.0
            for k in range(3):
                brier_sum += brier_score_loss(y_true_bin[:, k], y_proba[:, k])
            prob_metrics["brier_score"] = round(float(brier_sum / 3.0), 4)

            # Macro ROC-AUC (One-vs-Rest)
            prob_metrics["macro_roc_auc"] = round(float(roc_auc_score(y_true_bin, y_proba, average="macro", multi_class="ovr")), 4)

            # Macro PR-AUC (Average Precision)
            prob_metrics["macro_pr_auc"] = round(float(average_precision_score(y_true_bin, y_proba, average="macro")), 4)
        except Exception as e:
            print(f"Warning: Failed probability metric calculation for {model_name}: {e}")

    results = {
        "model": model_name,
        "accuracy": round(float(acc), 4),
        "macro_precision": round(float(macro_p), 4),
        "macro_recall": round(float(macro_r), 4),
        "macro_f1": round(float(macro_f1), 4),
        "weighted_precision": round(float(weight_p), 4),
        "weighted_recall": round(float(weight_r), 4),
        "weighted_f1": round(float(weight_f1), 4),
        "per_class": per_class_dict,
        "confusion_matrix": cm.tolist(),
        "normalized_confusion_matrix": cm_norm.round(4).tolist(),
        "top_confusion_pairs": confusion_pairs[:4],
        **prob_metrics
    }
    return results


def export_confusion_matrix_plot(
    cm: np.ndarray | list,
    model_name: str,
    output_path: str,
    normalized: bool = False
):
    """
    Renders and exports high-resolution confusion matrix heatmap.
    """
    cm = np.array(cm)
    norm_path = os.path.abspath(os.path.normpath(output_path))
    os.makedirs(os.path.dirname(norm_path), exist_ok=True)
    
    fig, ax = plt.subplots(figsize=(6, 5), dpi=300)
    fmt = ".2%" if normalized else "d"
    cmap = "Blues" if not normalized else "Greens"
    
    sns.heatmap(
        cm,
        annot=True,
        fmt=fmt,
        cmap=cmap,
        xticklabels=CLASSES,
        yticklabels=CLASSES,
        cbar=True,
        linewidths=0.5,
        linecolor="gray",
        ax=ax
    )
    title_suffix = " (Normalized)" if normalized else " (Raw Counts)"
    ax.set_title(f"{model_name}{title_suffix}", fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel("Predicted Sentiment Label", fontweight="bold")
    ax.set_ylabel("Actual Sentiment Label", fontweight="bold")
    fig.tight_layout()
    try:
        fig.savefig(norm_path, dpi=300, bbox_inches="tight")
    except Exception as e:
        print(f"Warning: Failed to save confusion matrix image to {output_path}: {e}")
    finally:
        plt.close(fig)

