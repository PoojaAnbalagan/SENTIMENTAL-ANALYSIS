import os
import re
import json
import joblib
import datetime
import pandas as pd
import numpy as np
from typing import Optional, List

try:
    from fastapi import FastAPI, Query, HTTPException, Response
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.staticfiles import StaticFiles
    from pydantic import BaseModel
except ImportError:
    # If fastapi is not installed, provide helpful message
    raise ImportError("FastAPI is required. Please install with: pip install fastapi uvicorn pydantic")

# -----------------------------------------------------------------------------
# 1. APPLICATION SETUP & CORS
# -----------------------------------------------------------------------------
app = FastAPI(
    title="McDonald's Customer Review Sentiment Intelligence API",
    description="REST API for ML sentiment inference, filtered review analytics, model benchmarks, and executive reports.",
    version="2026.1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Figures Directory for Static PNG Serving
figures_dir = os.path.join(os.path.dirname(__file__), "Figures")
if os.path.exists(figures_dir):
    app.mount("/static/figures", StaticFiles(directory=figures_dir), name="figures")

# -----------------------------------------------------------------------------
# 2. CACHED ASSETS & DATA PIPELINE
# -----------------------------------------------------------------------------
MODEL_PATH = os.path.join("models", "best_sentiment_model.pkl")
VECTORIZER_PATH = os.path.join("models", "tfidf_vectorizer.pkl")
CSV_PATH = os.path.join("data", "final_pseudo_labeled_dataset.csv")
if not os.path.exists(CSV_PATH):
    CSV_PATH = os.path.join("data", "cleaned_reviews.csv")
SUMMARY_PATH = os.path.join("results", "summary.json")
RESULTS_PATH = os.path.join("results", "model_results.csv")

model = None
vectorizer = None
df_reviews = None
summary_info = {}
model_results = []

def load_ml_assets():
    global model, vectorizer
    try:
        if os.path.exists(MODEL_PATH):
            loaded = joblib.load(MODEL_PATH)
            if isinstance(loaded, dict) and "classifier" in loaded:
                model = loaded["classifier"]
                if "vectorizer" in loaded:
                    vectorizer = loaded["vectorizer"]
            else:
                model = loaded

        if vectorizer is None and os.path.exists(VECTORIZER_PATH):
            vectorizer = joblib.load(VECTORIZER_PATH)
        print("Successfully loaded pre-trained model & TF-IDF vectorizer.")
    except Exception as e:
        print(f"Warning: Failed to load ML assets: {e}")

def load_dataset():
    global df_reviews, summary_info, model_results
    if os.path.exists(CSV_PATH):
        try:
            df_reviews = pd.read_csv(CSV_PATH)
            # Standardize column aliases across schemas
            if "review" in df_reviews.columns and "review_clean" not in df_reviews.columns:
                df_reviews["review_clean"] = df_reviews["review"]
            if "rating" in df_reviews.columns and "rating_num" not in df_reviews.columns:
                df_reviews["rating_num"] = df_reviews["rating"]
            if "review_id" in df_reviews.columns and "reviewer_id" not in df_reviews.columns:
                df_reviews["reviewer_id"] = df_reviews["review_id"]
            if "is_autotag" not in df_reviews.columns:
                df_reviews["is_autotag"] = False

            anchor_date = pd.to_datetime("2023-06-01")
            if "days_ago" in df_reviews.columns:
                df_reviews["derived_date"] = anchor_date - pd.to_timedelta(df_reviews["days_ago"].fillna(0), unit="D")
            else:
                df_reviews["derived_date"] = anchor_date
            print(f"Successfully loaded dataset from {CSV_PATH} with {len(df_reviews):,} reviews.")
        except Exception as e:
            print(f"Error loading CSV dataset: {e}")

    if os.path.exists(SUMMARY_PATH):
        try:
            with open(SUMMARY_PATH, "r") as f:
                summary_info = json.load(f)
        except Exception:
            pass

    if os.path.exists(RESULTS_PATH):
        try:
            res_df = pd.read_csv(RESULTS_PATH)
            if "Unnamed: 0" in res_df.columns:
                res_df.rename(columns={"Unnamed: 0": "model"}, inplace=True)
            model_results = res_df.to_dict(orient="records")
        except Exception:
            pass

load_ml_assets()
load_dataset()

# -----------------------------------------------------------------------------
# 3. HELPER FUNCTIONS
# -----------------------------------------------------------------------------
def preprocess_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"http\S+|www\.\S+", " ", text)
    text = re.sub(r"[^a-z\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()

def get_token_contributions(text: str, predicted_class: str):
    if model is None or vectorizer is None:
        return []
    cleaned = preprocess_text(text)
    words = list(set(cleaned.split()))
    if not words or not hasattr(model, "coef_"):
        return []
    vocab = vectorizer.vocabulary_
    try:
        class_idx = list(model.classes_).index(predicted_class)
        coefs = model.coef_[class_idx]
        contribs = []
        for w in words:
            if w in vocab:
                score = float(coefs[vocab[w]])
                contribs.append({"word": w, "score": score})
        contribs.sort(key=lambda x: abs(x["score"]), reverse=True)
        return contribs[:8]
    except Exception:
        return []

def apply_global_filters(
    date_option: str = "All Time",
    sentiments: Optional[List[str]] = None,
    ratings: Optional[List[int]] = None,
    store: str = "All Stores",
    search: str = ""
):
    if df_reviews is None or df_reviews.empty:
        return pd.DataFrame()

    filtered = df_reviews.copy()
    max_ref = filtered["derived_date"].max()

    # Date Range Filter
    if date_option == "Last 7 Days":
        filtered = filtered[filtered["derived_date"] >= (max_ref - pd.Timedelta(days=7))]
    elif date_option == "Last 30 Days":
        filtered = filtered[filtered["derived_date"] >= (max_ref - pd.Timedelta(days=30))]
    elif date_option == "Last 90 Days":
        filtered = filtered[filtered["derived_date"] >= (max_ref - pd.Timedelta(days=90))]
    elif date_option == "Last 6 Months":
        filtered = filtered[filtered["derived_date"] >= (max_ref - pd.Timedelta(days=180))]
    elif date_option == "Last 12 Months":
        filtered = filtered[filtered["derived_date"] >= (max_ref - pd.Timedelta(days=365))]

    # Sentiment Filter
    if sentiments:
        filtered = filtered[filtered["sentiment"].isin(sentiments)]

    # Rating Filter
    if ratings:
        filtered = filtered[filtered["rating_num"].isin(ratings)]

    # Store Filter
    if store and store != "All Stores" and "store_name" in filtered.columns:
        filtered = filtered[filtered["store_name"] == store]

    # Keyword Search
    if search and search.strip():
        q = search.strip().lower()
        filtered = filtered[filtered["review_clean"].astype(str).str.lower().str.contains(q, na=False)]

    return filtered

# -----------------------------------------------------------------------------
# 4. REST API ENDPOINTS
# -----------------------------------------------------------------------------
class PredictRequest(BaseModel):
    text: str

@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.datetime.now().isoformat(),
        "model_loaded": model is not None,
        "dataset_loaded": df_reviews is not None,
        "total_reviews": len(df_reviews) if df_reviews is not None else 0
    }

@app.get("/api/health")
def get_health():
    return {
        "status": "online",
        "model_loaded": model is not None,
        "vectorizer_loaded": vectorizer is not None,
        "dataset_loaded": df_reviews is not None and len(df_reviews) > 0,
        "timestamp": datetime.datetime.now().isoformat()
    }

@app.get("/api/metrics")
def get_metrics():
    total_count = summary_info.get("n_total", len(df_reviews) if df_reviews is not None else 22366)
    return {
        "total_corpus_count": total_count,
        "best_accuracy": summary_info.get("best_supervised_accuracy", 0.7405),
        "best_f1": summary_info.get("best_supervised_macro_f1", 0.6701),
        "vader_accuracy": summary_info.get("vader_accuracy", 0.6434),
        "accuracy_gain": summary_info.get("best_supervised_accuracy", 0.7405) - summary_info.get("vader_accuracy", 0.6434),
        "vocab_size": summary_info.get("tfidf_features", 20000)
    }

@app.post("/api/predict")
def predict_sentiment(req: PredictRequest):
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Review text cannot be empty.")
    if model is None or vectorizer is None:
        raise HTTPException(status_code=500, detail="ML model assets are not loaded.")

    clean_t = preprocess_text(req.text)
    x_vec = vectorizer.transform([clean_t])
    pred_class = str(model.predict(x_vec)[0])

    if hasattr(model, "predict_proba"):
        proba_arr = model.predict_proba(x_vec)[0]
    elif hasattr(model, "decision_function"):
        decision = model.decision_function(x_vec)[0]
        if np.isscalar(decision) or decision.ndim == 0 or len(model.classes_) == 2:
            prob_pos = 1.0 / (1.0 + np.exp(-decision))
            proba_arr = np.array([1.0 - prob_pos, prob_pos])
        else:
            exp_scores = np.exp(decision - np.max(decision))
            proba_arr = exp_scores / np.sum(exp_scores)
    else:
        proba_arr = np.array([1.0 if c == pred_class else 0.0 for c in model.classes_])

    proba_dict = {str(c): float(p) for c, p in zip(model.classes_, proba_arr)}
    conf_pct = float(proba_dict.get(pred_class, 1.0) * 100)

    contribs = get_token_contributions(req.text, pred_class)

    return {
        "predicted_sentiment": pred_class,
        "confidence_percentage": round(conf_pct, 1),
        "probabilities": proba_dict,
        "contributions": contribs
    }

@app.get("/api/reviews")
def get_reviews(
    dateRange: str = "All Time",
    sentiments: Optional[str] = Query(None), # Comma separated
    ratings: Optional[str] = Query(None),   # Comma separated
    store: str = "All Stores",
    search: str = "",
    sortBy: str = "Newest First",
    page: int = 1,
    pageSize: int = 50
):
    sent_list = sentiments.split(",") if sentiments else ["Positive", "Neutral", "Negative"]
    rate_list = [int(r) for r in ratings.split(",")] if ratings else [1, 2, 3, 4, 5]

    filtered = apply_global_filters(dateRange, sent_list, rate_list, store, search)

    # Sorting
    if sortBy == "Newest First":
        filtered = filtered.sort_values("derived_date", ascending=False)
    elif sortBy == "Oldest First":
        filtered = filtered.sort_values("derived_date", ascending=True)
    elif sortBy == "Highest Rating":
        filtered = filtered.sort_values("rating_num", ascending=False)
    elif sortBy == "Lowest Rating":
        filtered = filtered.sort_values("rating_num", ascending=True)

    total_filtered = len(filtered)
    start_idx = (page - 1) * pageSize
    end_idx = start_idx + pageSize

    cols = [
        "reviewer_id", "review_id", "store_name", "store_address", "rating_num", "rating",
        "sentiment", "review_clean", "review", "derived_date", "label_source", "prediction_confidence", "split_role"
    ]
    available_cols = [c for c in cols if c in filtered.columns]
    
    subset = filtered[available_cols].iloc[start_idx:end_idx].copy()
    if "derived_date" in subset.columns:
        subset["derived_date"] = subset["derived_date"].dt.strftime("%Y-%m-%d")

    # Available Stores List
    stores_list = ["All Stores"]
    if df_reviews is not None and "store_name" in df_reviews.columns:
        stores_list += sorted(df_reviews["store_name"].dropna().unique().tolist())

    return {
        "total_filtered": total_filtered,
        "total_corpus": len(df_reviews) if df_reviews is not None else 0,
        "page": page,
        "pageSize": pageSize,
        "reviews": subset.to_dict(orient="records"),
        "stores": stores_list
    }

@app.get("/api/analytics")
def get_analytics(
    dateRange: str = "All Time",
    sentiments: Optional[str] = Query(None),
    ratings: Optional[str] = Query(None),
    store: str = "All Stores",
    search: str = ""
):
    sent_list = sentiments.split(",") if sentiments else ["Positive", "Neutral", "Negative"]
    rate_list = [int(r) for r in ratings.split(",")] if ratings else [1, 2, 3, 4, 5]

    filtered = apply_global_filters(dateRange, sent_list, rate_list, store, search)
    tot_f = max(len(filtered), 1)

    # 1. Sentiment Share Counts
    s_counts = filtered["sentiment"].value_counts().to_dict() if not filtered.empty else {}
    pos_c = s_counts.get("Positive", 0)
    neu_c = s_counts.get("Neutral", 0)
    neg_c = s_counts.get("Negative", 0)

    sentiment_share = [
        {"name": "Positive", "count": pos_c, "percentage": round((pos_c / tot_f) * 100, 1)},
        {"name": "Neutral", "count": neu_c, "percentage": round((neu_c / tot_f) * 100, 1)},
        {"name": "Negative", "count": neg_c, "percentage": round((neg_c / tot_f) * 100, 1)}
    ]

    # 2. Rating Breakdown by Sentiment
    rating_breakdown = []
    if not filtered.empty:
        r_grp = filtered.groupby(["rating_num", "sentiment"]).size().unstack(fill_value=0)
        for r in range(1, 6):
            if r in r_grp.index:
                rating_breakdown.append({
                    "rating": f"{r} Stars",
                    "Positive": int(r_grp.loc[r, "Positive"]) if "Positive" in r_grp.columns else 0,
                    "Neutral": int(r_grp.loc[r, "Neutral"]) if "Neutral" in r_grp.columns else 0,
                    "Negative": int(r_grp.loc[r, "Negative"]) if "Negative" in r_grp.columns else 0,
                })
            else:
                rating_breakdown.append({"rating": f"{r} Stars", "Positive": 0, "Neutral": 0, "Negative": 0})

    # 3. Top Stores Volume
    top_stores = []
    if not filtered.empty and "store_address" in filtered.columns:
        ts = filtered["store_address"].value_counts().head(7)
        top_stores = [{"store": str(idx), "count": int(val)} for idx, val in ts.items()]

    # 4. Key Metrics Summary
    avg_rating = float(filtered["rating_num"].mean()) if not filtered.empty and "rating_num" in filtered.columns else 0.0
    dom_sent = filtered["sentiment"].mode()[0] if not filtered.empty else "N/A"

    return {
        "filtered_count": len(filtered),
        "average_rating": round(avg_rating, 2),
        "dominant_sentiment": dom_sent,
        "sentiment_share": sentiment_share,
        "rating_breakdown": rating_breakdown,
        "top_stores": top_stores
    }

@app.get("/api/models")
def get_model_benchmarks():
    # Build from real CSV data if available
    if model_results:
        # model_results already loaded from model_results.csv
        # The first column (empty header → renamed to "model") holds the model name
        supervised = []
        for row in model_results:
            # Depending on how CSV was parsed the name key might be "model" or "Unnamed: 0"
            name = row.get("model") or row.get("Unnamed: 0") or "Unknown"
            supervised.append({
                "model": name,
                "accuracy":        float(row.get("accuracy", 0)),
                "macro_precision": float(row.get("macro_precision", 0)),
                "macro_recall":    float(row.get("macro_recall", 0)),
                "macro_f1":        float(row.get("macro_f1", 0)),
                "type": "supervised"
            })
        # Append VADER from summary.json if available
        if summary_info.get("vader_accuracy"):
            supervised.append({
                "model":           "VADER (Baseline)",
                "accuracy":        float(summary_info.get("vader_accuracy", 0.6434)),
                "macro_precision": float(summary_info.get("vader_macro_precision", 0.5752)),
                "macro_recall":    float(summary_info.get("vader_macro_recall", 0.5628)),
                "macro_f1":        float(summary_info.get("vader_macro_f1", 0.5627)),
                "type": "unsupervised"
            })
        return {"models": supervised}

    # Hard-coded fallback matching model_results.csv + summary.json
    return {
        "models": [
            {"model": "Logistic Regression",     "accuracy": 0.7405, "macro_precision": 0.6711, "macro_recall": 0.6780, "macro_f1": 0.6701, "type": "supervised"},
            {"model": "Linear SVM",              "accuracy": 0.7456, "macro_precision": 0.6434, "macro_recall": 0.6423, "macro_f1": 0.6426, "type": "supervised"},
            {"model": "Multinomial Naive Bayes", "accuracy": 0.7664, "macro_precision": 0.7535, "macro_recall": 0.5982, "macro_f1": 0.5576, "type": "supervised"},
            {"model": "VADER (Baseline)",         "accuracy": 0.6434, "macro_precision": 0.5752, "macro_recall": 0.5628, "macro_f1": 0.5627, "type": "unsupervised"},
        ]
    }


@app.get("/api/export")
def export_csv(
    dateRange: str = "All Time",
    sentiments: Optional[str] = Query(None),
    ratings: Optional[str] = Query(None),
    store: str = "All Stores",
    search: str = ""
):
    sent_list = sentiments.split(",") if sentiments else ["Positive", "Neutral", "Negative"]
    rate_list = [int(r) for r in ratings.split(",")] if ratings else [1, 2, 3, 4, 5]

    filtered = apply_global_filters(dateRange, sent_list, rate_list, store, search)

    # Convert Timestamp columns to strings to avoid CSV serialization errors
    export_df = filtered.copy()
    for col in export_df.select_dtypes(include=["datetime64[ns]", "datetime64[ns, UTC]"]).columns:
        export_df[col] = export_df[col].dt.strftime("%Y-%m-%d")

    csv_str = export_df.to_csv(index=False)

    return Response(
        content=csv_str,
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=mcdonalds_sentiment_filtered.csv",
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )

# -----------------------------------------------------------------------------
# MAIN SERVER LAUNCH
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
