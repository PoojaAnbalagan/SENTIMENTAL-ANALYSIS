"""
cross_validation.py
===================
5-Fold Stratified Cross-Validation on the development set.
Computes Mean ± Standard Deviation across all folds for classical ML models.
Ensures the final test set remains completely untouched.
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.base import clone

from src.feature_engineering import clean_text_for_classical, build_tfidf_pipeline
from src.models import get_classical_models, CLASSES, LABEL_MAP, SEED

def run_stratified_kfold_cv(
    dev_df: pd.DataFrame,
    n_splits: int = 5,
    seed: int = SEED
) -> pd.DataFrame:
    """
    Executes 5-fold Stratified Cross-Validation on development dataframe.
    """
    print(f"\n[CrossValidation] Running {n_splits}-Fold Stratified CV on {len(dev_df):,} development samples...")
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    
    models = get_classical_models(seed=seed)
    raw_col = "review" if "review" in dev_df.columns else "review_clean"
    
    cv_records = []
    
    for model_name, model_instance in models.items():
        print(f"  -> Evaluating {model_name} across {n_splits} folds...")
        fold_accs = []
        fold_macro_p = []
        fold_macro_r = []
        fold_macro_f1 = []
        fold_neg_f1 = []
        fold_neu_f1 = []
        fold_pos_f1 = []
        
        for fold, (train_idx, val_idx) in enumerate(skf.split(dev_df, dev_df["label_id"])):
            fold_train = dev_df.iloc[train_idx]
            fold_val = dev_df.iloc[val_idx]
            
            # Prevent leakage: fit TF-IDF strictly on fold training data
            vectorizer, X_tr, X_v, _ = build_tfidf_pipeline(
                fold_train[raw_col],
                val_texts=fold_val[raw_col],
                ngram_range=(1, 2),
                max_features=25000
            )
            
            y_tr = fold_train["sentiment"]
            y_v = fold_val["sentiment"]
            
            clf = clone(model_instance)
            clf.fit(X_tr, y_tr)
            y_pred = clf.predict(X_v)
            
            acc = accuracy_score(y_v, y_pred)
            p, r, f1, _ = precision_recall_fscore_support(y_v, y_pred, average="macro", zero_division=0)
            class_f1 = precision_recall_fscore_support(y_v, y_pred, labels=CLASSES, average=None, zero_division=0)[2]
            
            fold_accs.append(acc)
            fold_macro_p.append(p)
            fold_macro_r.append(r)
            fold_macro_f1.append(f1)
            fold_neg_f1.append(class_f1[0])
            fold_neu_f1.append(class_f1[1])
            fold_pos_f1.append(class_f1[2])
            
        cv_records.append({
            "model": model_name,
            "accuracy_mean": round(float(np.mean(fold_accs)), 4),
            "accuracy_std": round(float(np.std(fold_accs)), 4),
            "macro_precision_mean": round(float(np.mean(fold_macro_p)), 4),
            "macro_precision_std": round(float(np.std(fold_macro_p)), 4),
            "macro_recall_mean": round(float(np.mean(fold_macro_r)), 4),
            "macro_recall_std": round(float(np.std(fold_macro_r)), 4),
            "macro_f1_mean": round(float(np.mean(fold_macro_f1)), 4),
            "macro_f1_std": round(float(np.std(fold_macro_f1)), 4),
            "negative_f1_mean": round(float(np.mean(fold_neg_f1)), 4),
            "neutral_f1_mean": round(float(np.mean(fold_neu_f1)), 4),
            "positive_f1_mean": round(float(np.mean(fold_pos_f1)), 4),
            "cv_macro_f1_display": f"{np.mean(fold_macro_f1):.4f} ± {np.std(fold_macro_f1):.4f}"
        })
        
    cv_results_df = pd.DataFrame(cv_records)
    return cv_results_df
