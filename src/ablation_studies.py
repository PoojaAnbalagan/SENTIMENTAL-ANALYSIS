"""
ablation_studies.py
===================
Ablation experiments investigating the incremental contributions of:
1. Unigram vs. Unigram+Bigram vs. Trigram feature spaces
2. Unweighted vs. Balanced Cost-Sensitive Class Weighting
3. Sublinear TF scaling
Evaluated on the validation split to guide design decisions.
"""

import inspect
import pandas as pd
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

from src.feature_engineering import build_tfidf_pipeline
from src.models import CLASSES, SEED

def run_ablation_study(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    seed: int = SEED
) -> pd.DataFrame:
    """
    Executes a structured ablation benchmark on the validation set.
    """
    print("\n[Ablation] Running feature representation and class-weighting ablation studies...")
    raw_col = "review" if "review" in train_df.columns else "review_clean"
    
    configurations = [
        {
            "config_id": "A",
            "description": "TF-IDF Unigrams (1,1) + Linear SVM (Unweighted)",
            "ngram_range": (1, 1),
            "sublinear_tf": False,
            "class_weight": None
        },
        {
            "config_id": "B",
            "description": "TF-IDF Unigrams (1,1) + Linear SVM (Balanced Weights)",
            "ngram_range": (1, 1),
            "sublinear_tf": False,
            "class_weight": "balanced"
        },
        {
            "config_id": "C",
            "description": "TF-IDF Bigrams (1,2) + Linear SVM (Unweighted)",
            "ngram_range": (1, 2),
            "sublinear_tf": False,
            "class_weight": None
        },
        {
            "config_id": "D",
            "description": "TF-IDF Bigrams (1,2) + Linear SVM (Balanced Weights)",
            "ngram_range": (1, 2),
            "sublinear_tf": False,
            "class_weight": "balanced"
        },
        {
            "config_id": "E",
            "description": "TF-IDF Trigrams (1,3) + Sublinear TF + Linear SVM (Balanced)",
            "ngram_range": (1, 3),
            "sublinear_tf": True,
            "class_weight": "balanced"
        }
    ]
    
    records = []
    
    for cfg in configurations:
        vectorizer, X_tr, X_val, _ = build_tfidf_pipeline(
            train_df[raw_col],
            val_texts=val_df[raw_col],
            ngram_range=cfg["ngram_range"],
            sublinear_tf=cfg["sublinear_tf"],
            max_features=25000
        )
        
        clf = LinearSVC(
            class_weight=cfg["class_weight"],
            C=1.0,
            random_state=seed,
            dual="auto" if "dual" in inspect.signature(LinearSVC.__init__).parameters else True
        )
        clf.fit(X_tr, train_df["sentiment"])
        y_val_pred = clf.predict(X_val)
        
        acc = accuracy_score(val_df["sentiment"], y_val_pred)
        p, r, f1, _ = precision_recall_fscore_support(
            val_df["sentiment"], y_val_pred, average="macro", zero_division=0
        )
        class_f1s = precision_recall_fscore_support(
            val_df["sentiment"], y_val_pred, labels=CLASSES, average=None, zero_division=0
        )[2]
        
        records.append({
            "config": cfg["config_id"],
            "description": cfg["description"],
            "accuracy": round(float(acc), 4),
            "macro_precision": round(float(p), 4),
            "macro_recall": round(float(r), 4),
            "macro_f1": round(float(f1), 4),
            "negative_f1": round(float(class_f1s[0]), 4),
            "neutral_f1": round(float(class_f1s[1]), 4),
            "positive_f1": round(float(class_f1s[2]), 4)
        })
        
    df_ablation = pd.DataFrame(records)
    print(df_ablation.to_string(index=False))
    return df_ablation
