import streamlit as st
import joblib
import re
import pandas as pd
from PIL import Image

st.set_page_config(page_title="McDonald's Review Sentiment Analysis", layout="wide")

model = joblib.load("sentiment_model.pkl")
vectorizer = joblib.load("tfidf_vectorizer.pkl")

def preprocess(t):
    t = str(t).lower()
    t = re.sub(r"http\S+|www\.\S+", " ", t)
    t = re.sub(r"[^a-z\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()

st.title("🍔 Sentiment Analysis of McDonald's Customer Reviews")
st.caption("Capstone Project II (DS3206) — Data Science Department, SUSL")

tab1, tab2 = st.tabs(["🔍 Live Prediction", "📊 EDA Dashboard"])

with tab1:
    review = st.text_area("Enter a customer review:", height=120,
                           placeholder="e.g. The staff were rude and my order took 20 minutes...")
    if st.button("Analyze Sentiment"):
        if review.strip():
            clean = preprocess(review)
            X = vectorizer.transform([clean])
            pred = model.predict(X)[0]
            proba = dict(zip(model.classes_, model.predict_proba(X)[0]))
            color = {"Positive": "green", "Neutral": "orange", "Negative": "red"}[pred]
            st.markdown(f"### Predicted Sentiment: :{color}[{pred}]")
            st.bar_chart(pd.Series(proba))
        else:
            st.warning("Please enter a review.")

with tab2:
    st.subheader("Exploratory Data Analysis")
    figs = ["01_sentiment_rating_dist.png", "02_length_by_sentiment.png",
            "03_autotag_share.png", "04_sentiment_over_time.png",
            "05_wordclouds.png", "07_confusion_matrix.png"]
    cols = st.columns(2)
    for i, f in enumerate(figs):
        with cols[i % 2]:
            st.image(f"Figures/{f}", use_column_width=True)