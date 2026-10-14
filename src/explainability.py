"""
explainability.py
=================
Feature importance extraction and local token explainability for linear and probabilistic models.
"""

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

CLASSES = ["Negative", "Neutral", "Positive"]

def extract_global_feature_importance(
    model,
    vectorizer: TfidfVectorizer,
    top_k: int = 25
) -> pd.DataFrame:
    """
    Extracts the highest-magnitude positive and negative features per sentiment class.
    """
    if not hasattr(model, "coef_"):
        print("Model does not have linear coefficients (coef_). Skipping global feature extraction.")
        return pd.DataFrame()

    feature_names = np.array(vectorizer.get_feature_names_out())
    classes = model.classes_
    
    records = []
    
    for idx, cname in enumerate(classes):
        coefs = model.coef_[idx]
        top_positive_idx = np.argsort(coefs)[::-1][:top_k]
        top_negative_idx = np.argsort(coefs)[:top_k]
        
        for rank, (p_idx, n_idx) in enumerate(zip(top_positive_idx, top_negative_idx), start=1):
            records.append({
                "sentiment_class": cname,
                "rank": rank,
                "top_positive_term": feature_names[p_idx],
                "positive_coefficient": round(float(coefs[p_idx]), 4),
                "top_negative_term": feature_names[n_idx],
                "negative_coefficient": round(float(coefs[n_idx]), 4)
            })
            
    df_feat = pd.DataFrame(records)
    return df_feat


def get_sample_token_contributions(
    text: str,
    predicted_class: str,
    model,
    vectorizer: TfidfVectorizer,
    preprocess_fn = None,
    top_n: int = 8
) -> list[dict]:
    """
    Computes local token attribution scores for a single input text.
    """
    if not hasattr(model, "coef_") or not hasattr(model, "classes_"):
        return []
    
    clean_text = preprocess_fn(text) if preprocess_fn else text.lower()
    words = list(set(clean_text.split()))
    vocab = vectorizer.vocabulary_
    
    try:
        class_idx = list(model.classes_).index(predicted_class)
        coefs = model.coef_[class_idx]
        contribs = []
        for w in words:
            if w in vocab:
                score = float(coefs[vocab[w]])
                contribs.append({"word": w, "score": round(score, 4)})
        contribs.sort(key=lambda x: abs(x["score"]), reverse=True)
        return contribs[:top_n]
    except Exception:
        return []
