"""
robustness_testing.py
=====================
Behavioral and Stress-Testing Suite for NLP Sentiment Analysis.
Evaluates model robustness on:
1. Negation
2. Intensifiers
3. Mixed Sentiment
4. Sarcasm
5. Short Text
6. Long Text
7. Spelling/Noise
8. Punctuation Variations
"""

import pandas as pd
import numpy as np

CHALLENGE_CASES = [
    # 1. Negation
    {"category": "Negation", "text": "The burger was good.", "expected_label": "Positive", "notes": "Baseline positive"},
    {"category": "Negation", "text": "The burger was not good.", "expected_label": "Negative", "notes": "Standard negation flip"},
    {"category": "Negation", "text": "The fries were never fresh.", "expected_label": "Negative", "notes": "Adverbial negation"},
    {"category": "Negation", "text": "Not bad at all, actually enjoyed it.", "expected_label": "Positive", "notes": "Double negation / positive sense"},

    # 2. Intensifiers
    {"category": "Intensifiers", "text": "The milkshake was good.", "expected_label": "Positive", "notes": "Base positive"},
    {"category": "Intensifiers", "text": "The milkshake was very good.", "expected_label": "Positive", "notes": "Moderately intensified"},
    {"category": "Intensifiers", "text": "The milkshake was extremely good and delightful.", "expected_label": "Positive", "notes": "Strongly intensified"},
    {"category": "Intensifiers", "text": "The staff was horribly rude and disrespectful.", "expected_label": "Negative", "notes": "Strongly intensified negative"},

    # 3. Mixed Sentiment
    {"category": "Mixed Sentiment", "text": "The food was excellent but the service was terrible.", "expected_label": "Negative", "notes": "Concession clause with dominant negative end"},
    {"category": "Mixed Sentiment", "text": "Long waiting line, but the manager was polite and food was hot.", "expected_label": "Positive", "notes": "Negative premise resolved positively"},
    {"category": "Mixed Sentiment", "text": "Average fries, decent drinks, nothing special.", "expected_label": "Neutral", "notes": "Balanced indifferent sentiment"},

    # 4. Sarcasm
    {"category": "Sarcasm", "text": "Great, another two-hour wait for a cold burger.", "expected_label": "Negative", "notes": "Sarcastic 'Great' with negative reality"},
    {"category": "Sarcasm", "text": "Oh wonderful, missing half my order once again!", "expected_label": "Negative", "notes": "Sarcastic exclamation with complaint"},

    # 5. Short Text
    {"category": "Short Text", "text": "Bad.", "expected_label": "Negative", "notes": "Single word negative"},
    {"category": "Short Text", "text": "Awesome!", "expected_label": "Positive", "notes": "Single word positive"},
    {"category": "Short Text", "text": "Okay.", "expected_label": "Neutral", "notes": "Single word neutral"},

    # 6. Long Multi-Sentence Text
    {
        "category": "Long Text",
        "text": "We stopped by during our road trip hoping for a quick lunch. The drive-thru was reasonably fast, the cashier greeted us with a genuine smile, and our customized burgers came out exactly as ordered, hot and fresh. Highly satisfied with this visit!",
        "expected_label": "Positive",
        "notes": "Multi-sentence coherent positive review"
    },
    {
        "category": "Long Text",
        "text": "Entered the restaurant at 8 PM and found trash overflowing from every bin. The floor was sticky, self-service kiosks were malfunctioning, and we waited thirty minutes for cold nuggets. Nobody apologized.",
        "expected_label": "Negative",
        "notes": "Multi-sentence coherent negative review"
    },

    # 7. Spelling & Typographical Noise
    {"category": "Spelling/Noise", "text": "gud food and suuuuper fast servce", "expected_label": "Positive", "notes": "Common typos & elongated positive"},
    {"category": "Spelling/Noise", "text": "servce was terrble and burgur waz completly coldd", "expected_label": "Negative", "notes": "Heavy typos in negative review"},

    # 8. Punctuation
    {"category": "Punctuation", "text": "Great food", "expected_label": "Positive", "notes": "Unpunctuated"},
    {"category": "Punctuation", "text": "Great food...", "expected_label": "Neutral", "notes": "Trailing ellipsis creating ambiguity"},
    {"category": "Punctuation", "text": "Great food!!!", "expected_label": "Positive", "notes": "Triple exclamation mark"}
]


def run_robustness_benchmark(
    models_dict: dict,
    vectorizer = None,
    preprocess_fn = None
) -> pd.DataFrame:
    """
    Evaluates all models against the challenge cases suite.
    """
    records = []
    
    for case in CHALLENGE_CASES:
        row = {
            "category": case["category"],
            "challenge_text": case["text"],
            "expected_sentiment": case["expected_label"],
            "linguistic_property": case["notes"]
        }
        
        text = case["text"]
        
        for name, model in models_dict.items():
            if hasattr(model, "predict_proba") and not hasattr(model, "coef_") and not hasattr(model, "feature_log_prob_") and not name.startswith("VADER"):
                # Transformer / Custom pipeline
                try:
                    pred = model.predict([text])[0]
                except Exception:
                    pred = "Error"
            elif name.startswith("VADER"):
                try:
                    pred = model.predict([text])[0]
                except Exception:
                    pred = "Error"
            else:
                # Classical TF-IDF model
                try:
                    clean_t = preprocess_fn(text) if preprocess_fn else text
                    x_vec = vectorizer.transform([clean_t])
                    pred = model.predict(x_vec)[0]
                except Exception as e:
                    pred = "Error"
                    
            row[f"pred_{name}"] = pred
            row[f"pass_{name}"] = (pred == case["expected_label"])
            
        records.append(row)
        
    df_robustness = pd.DataFrame(records)
    return df_robustness
