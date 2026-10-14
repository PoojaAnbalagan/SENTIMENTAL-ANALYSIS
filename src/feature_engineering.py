"""
feature_engineering.py
======================
Text preprocessing and TF-IDF feature extraction.
Enforces strict prevention of data leakage: fit_transform is ONLY called on training data.
"""

import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

CONTRACTIONS = {
    "won't": "will not", "can't": "cannot", "n't": " not",
    "i'm": "i am", "it's": "it is", "that's": "that is",
    "there's": "there is", "they're": "they are", "we're": "we are",
    "you're": "you are", "i've": "i have", "we've": "we have",
    "didn't": "did not", "doesn't": "does not", "don't": "do not",
    "isn't": "is not", "aren't": "are not", "wasn't": "was not",
    "weren't": "were not", "hasn't": "has not", "haven't": "have not"
}

NEGATION_WORDS = {
    "not", "no", "never", "none", "neither", "nor", "hardly", "scarcely",
    "barely", "nothing", "nowhere", "cannot", "without"
}

DOMAIN_STOPWORDS = {
    "mcdonald", "mcdonalds", "mcd", "mcds", "restaurant", "store",
    "location", "place", "drive", "thru", "order", "ordered"
}

def clean_text_for_classical(text: str) -> str:
    """
    Standard preprocessing for classical bag-of-words / TF-IDF models:
    - Lowercase
    - URL removal
    - Contraction expansion
    - Non-alphabetic character removal
    - Negation preservation & token filtering
    """
    if not isinstance(text, str) or not text.strip():
        return ""
    
    text = text.lower()
    text = re.sub(r"http\S+|www\.\S+", " ", text)
    
    for contraction, replacement in CONTRACTIONS.items():
        text = text.replace(contraction, replacement)
        
    text = re.sub(r"[^a-z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    tokens = []
    for word in text.split():
        if word in NEGATION_WORDS:
            tokens.append(word)
        elif word in DOMAIN_STOPWORDS:
            continue
        elif len(word) <= 2:
            continue
        else:
            tokens.append(word)
            
    return " ".join(tokens)


def build_tfidf_pipeline(
    train_texts: pd.Series,
    val_texts: pd.Series = None,
    test_texts: pd.Series = None,
    max_features: int = 25000,
    ngram_range: tuple = (1, 2),
    min_df: int = 3,
    max_df: float = 0.95,
    sublinear_tf: bool = True
) -> tuple[TfidfVectorizer, any, any, any]:
    """
    Fits TF-IDF vectorizer strictly on training texts and transforms validation/test sets.
    """
    vectorizer = TfidfVectorizer(
        max_features=max_features,
        ngram_range=ngram_range,
        min_df=min_df,
        max_df=max_df,
        sublinear_tf=sublinear_tf
    )

    clean_train = train_texts.apply(clean_text_for_classical)
    X_train = vectorizer.fit_transform(clean_train)

    X_val = None
    if val_texts is not None:
        clean_val = val_texts.apply(clean_text_for_classical)
        X_val = vectorizer.transform(clean_val)

    X_test = None
    if test_texts is not None:
        clean_test = test_texts.apply(clean_text_for_classical)
        X_test = vectorizer.transform(clean_test)

    return vectorizer, X_train, X_val, X_test
