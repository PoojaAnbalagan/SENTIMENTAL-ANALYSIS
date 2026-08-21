import os
import re
import json
import joblib
import datetime
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from theme_utils import THEMES, get_svg_icon, get_chart_theme, get_custom_css

# -----------------------------------------------------------------------------
# 1. PAGE SETUP & THEME INJECTION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="McDonald's Customer Review Sentiment Intelligence Platform",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Active Theme State
if "app_theme" not in st.session_state:
    st.session_state["app_theme"] = "Light"

# Inject Dynamic Theme CSS
st.markdown(get_custom_css(st.session_state["app_theme"]), unsafe_allow_html=True)
st.markdown('<script src="https://cdn.tailwindcss.com"></script>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. CACHED ASSETS & DATA PIPELINE
# -----------------------------------------------------------------------------
@st.cache_resource
def load_ml_assets():
    """Load cached model & TF-IDF vectorizer."""
    try:
        m_path = os.path.join("models", "best_sentiment_model.pkl")
        v_path = os.path.join("models", "tfidf_vectorizer.pkl")
        if not os.path.exists(m_path) or not os.path.exists(v_path):
            return None, None
        return joblib.load(m_path), joblib.load(v_path)
    except Exception:
        return None, None

@st.cache_data
def load_dataset_and_metrics():
    """Load and process cached dataset and evaluation metrics."""
    data, summary, model_results = None, {}, None
    csv_path = os.path.join("data", "cleaned_reviews.csv")
    if os.path.exists(csv_path):
        try:
            data = pd.read_csv(csv_path)
            # Calculate derived_date from days_ago relative to anchor 2023-06-01
            anchor_date = pd.to_datetime("2023-06-01")
            if "days_ago" in data.columns:
                data["derived_date"] = anchor_date - pd.to_timedelta(data["days_ago"].fillna(0), unit="D")
            else:
                data["derived_date"] = anchor_date
        except Exception:
            pass

    summary_path = os.path.join("results", "summary.json")
    if os.path.exists(summary_path):
        try:
            with open(summary_path, "r") as f:
                summary = json.load(f)
        except Exception:
            pass

    results_path = os.path.join("results", "model_results.csv")
    if os.path.exists(results_path):
        try:
            model_results = pd.read_csv(results_path, index_col=0)
        except Exception:
            pass

    return data, summary, model_results

def preprocess_text(text: str) -> str:
    """Standard NLP text normalization."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"http\S+|www\.\S+", " ", text)
    text = re.sub(r"[^a-z\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()

def get_token_contributions(text: str, model, vectorizer, predicted_class: str):
    """Extract token coefficients for explainable predictions."""
    cleaned = preprocess_text(text)
    words = list(set(cleaned.split()))
    if not words or not hasattr(model, "coef_"):
        return []
    vocab = vectorizer.vocabulary_
    class_idx = list(model.classes_).index(predicted_class)
    coefs = model.coef_[class_idx]
    
    contribs = []
    for w in words:
        if w in vocab:
            score = coefs[vocab[w]]
            contribs.append((w, score))
    contribs.sort(key=lambda x: abs(x[1]), reverse=True)
    return contribs[:8]

# Load Core Data
model, vectorizer = load_ml_assets()
df_reviews, summary_info, df_models = load_dataset_and_metrics()

# Base System Stats
total_corpus_count = summary_info.get("n_total", len(df_reviews) if df_reviews is not None else 22366)
best_acc = summary_info.get("best_supervised_accuracy", 0.7405)
best_f1 = summary_info.get("best_supervised_macro_f1", 0.6701)
vader_acc = summary_info.get("vader_accuracy", 0.6434)

t_colors = THEMES.get(st.session_state["app_theme"], THEMES["Light"])

# -----------------------------------------------------------------------------
# 3. SIDEBAR & GLOBAL FILTERS
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(f"""
    <div class="flex items-center gap-3 pb-3 mb-3 border-b border-slate-200">
        <div class="p-2.5 rounded-xl flex items-center justify-center" style="background-color: {t_colors['accent_bg']}; color: {t_colors['accent']}; border: 1px solid {t_colors['border']}">
            {get_svg_icon("predictor", 22, t_colors['accent'])}
        </div>
        <div>
            <h3 class="font-extrabold text-base leading-tight m-0" style="color: {t_colors['text_primary']}">McDonald's Intelligence</h3>
            <p class="text-xs font-semibold m-0" style="color: {t_colors['accent']}">Capstone II • DS3206 (SUSL)</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Interface Theme Switcher
    st.markdown(f"<p class='font-bold text-xs uppercase tracking-wider mb-1' style='color: {t_colors['text_muted']}'>Interface Theme</p>", unsafe_allow_html=True)
    selected_theme = st.selectbox(
        "Select Theme:",
        ["Light", "Dark", "Soft"],
        index=["Light", "Dark", "Soft"].index(st.session_state["app_theme"]),
        label_visibility="collapsed"
    )
    if selected_theme != st.session_state["app_theme"]:
        st.session_state["app_theme"] = selected_theme
        st.rerun()

    st.markdown(f"<hr class='my-3' style='border-color: {t_colors['border']}'>", unsafe_allow_html=True)

    # Navigation Menu
    st.markdown(f"<p class='font-bold text-xs uppercase tracking-wider mb-1' style='color: {t_colors['text_muted']}'>Navigation Menu</p>", unsafe_allow_html=True)
    navigation = st.radio(
        "Navigation",
        [
            "Overview",
            "Live Predictor",
            "Sentiment Analytics",
            "Review Explorer",
            "Model Performance",
            "Reports",
            "Project Information"
        ],
        index=0,
        label_visibility="collapsed"
    )

    st.markdown(f"<hr class='my-3' style='border-color: {t_colors['border']}'>", unsafe_allow_html=True)
    st.markdown(f"<p class='font-bold text-xs uppercase tracking-wider mb-2' style='color: {t_colors['text_muted']}'>Global Analytics Filters</p>", unsafe_allow_html=True)

    # Date Range Filter
    date_option = st.selectbox(
        "Date Range:",
        ["All Time", "Last 7 Days", "Last 30 Days", "Last 90 Days", "Last 6 Months", "Last 12 Months", "Custom Range"]
    )

    custom_start_date, custom_end_date = None, None
    if date_option == "Custom Range" and df_reviews is not None:
        max_d = df_reviews["derived_date"].max().date()
        min_d = df_reviews["derived_date"].min().date()
        date_tuple = st.date_input("Select Date Range:", value=(min_d, max_d), min_value=min_d, max_value=max_d)
        if isinstance(date_tuple, (tuple, list)) and len(date_tuple) == 2:
            custom_start_date, custom_end_date = date_tuple

    # Multi-field Filters
    sentiment_filter = st.multiselect("Sentiment Filter:", ["Positive", "Neutral", "Negative"], default=["Positive", "Neutral", "Negative"])
    
    ratings_available = [1, 2, 3, 4, 5]
    rating_filter = st.multiselect("Rating Filter:", ratings_available, default=ratings_available)

    # Store Filter
    store_options = ["All Stores"]
    if df_reviews is not None and "store_name" in df_reviews.columns:
        store_options += sorted(df_reviews["store_name"].dropna().unique().tolist())
    selected_store = st.selectbox("Store Location:", store_options)

    search_keyword = st.text_input("Search Keyword:", placeholder="e.g. cold fries, service")

    # Filter Execution
    df_filtered = df_reviews.copy() if df_reviews is not None else None

    if df_filtered is not None:
        # Date Filter
        max_ref = df_filtered["derived_date"].max()
        if date_option == "Last 7 Days":
            df_filtered = df_filtered[df_filtered["derived_date"] >= (max_ref - pd.Timedelta(days=7))]
        elif date_option == "Last 30 Days":
            df_filtered = df_filtered[df_filtered["derived_date"] >= (max_ref - pd.Timedelta(days=30))]
        elif date_option == "Last 90 Days":
            df_filtered = df_filtered[df_filtered["derived_date"] >= (max_ref - pd.Timedelta(days=90))]
        elif date_option == "Last 6 Months":
            df_filtered = df_filtered[df_filtered["derived_date"] >= (max_ref - pd.Timedelta(days=180))]
        elif date_option == "Last 12 Months":
            df_filtered = df_filtered[df_filtered["derived_date"] >= (max_ref - pd.Timedelta(days=365))]
        elif date_option == "Custom Range" and custom_start_date and custom_end_date:
            df_filtered = df_filtered[(df_filtered["derived_date"].dt.date >= custom_start_date) & (df_filtered["derived_date"].dt.date <= custom_end_date)]

        # Sentiment Filter
        if sentiment_filter:
            df_filtered = df_filtered[df_filtered["sentiment"].isin(sentiment_filter)]

        # Rating Filter
        if rating_filter:
            df_filtered = df_filtered[df_filtered["rating_num"].isin(rating_filter)]

        # Store Filter
        if selected_store != "All Stores":
            df_filtered = df_filtered[df_filtered["store_name"] == selected_store]

        # Search Keyword
        if search_keyword.strip():
            df_filtered = df_filtered[df_filtered["review_clean"].astype(str).str.contains(search_keyword.strip(), case=False, na=False)]

    filtered_count = len(df_filtered) if df_filtered is not None else 0

    st.markdown(f"""
    <div class="rounded-xl p-3 text-xs mt-3 border" style="background-color: {t_colors['accent_bg']}; border-color: {t_colors['border']}; color: {t_colors['text_primary']}">
        <div class="font-bold mb-1 flex items-center gap-1.5" style="color: {t_colors['accent']}">
            {get_svg_icon("filter", 14, t_colors['accent'])} Filter Status
        </div>
        <span class="font-extrabold">{filtered_count:,}</span> reviews matching active filter scope
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. HERO BANNER & KPI CARDS
# -----------------------------------------------------------------------------
st.markdown(f"""
<div class="flex items-center justify-between mb-4 pb-3 border-b" style="border-color: {t_colors['border']};">
    <div>
        <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider mb-1" style="background-color: {t_colors['accent_bg']}; color: {t_colors['accent']};">
            {get_svg_icon("predictor", 14, t_colors['accent'])} McDonald's Customer Review Intelligence
        </div>
        <h1 class="text-2xl font-extrabold tracking-tight" style="color: {t_colors['text_primary']};">
            AI-Powered Customer Sentiment Analytics Platform
        </h1>
    </div>
    <div class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-xl border text-xs font-extrabold" style="background-color: {t_colors['surface']}; border-color: {t_colors['border']}; color: {t_colors['text_primary']}; shadow: {t_colors['shadow']}">
        {get_svg_icon("explorer", 16, t_colors['accent'])} {filtered_count:,} / {total_corpus_count:,} Reviews Analyzed
    </div>
</div>
""", unsafe_allow_html=True)

# Calculate Filtered Counts
pos_c = len(df_filtered[df_filtered['sentiment'] == 'Positive']) if df_filtered is not None and not df_filtered.empty else 0
neu_c = len(df_filtered[df_filtered['sentiment'] == 'Neutral']) if df_filtered is not None and not df_filtered.empty else 0
neg_c = len(df_filtered[df_filtered['sentiment'] == 'Negative']) if df_filtered is not None and not df_filtered.empty else 0
tot_f = max(filtered_count, 1)

# Active Removable Filter Chips Render
chip_list = []
if date_option != "All Time":
    chip_list.append(f"Scope: {date_option}")
if len(sentiment_filter) < 3:
    chip_list.append(f"Sentiments: {', '.join(sentiment_filter)}")
if len(rating_filter) < 5:
    chip_list.append(f"Ratings: {', '.join(map(str, rating_filter))}")
if selected_store != "All Stores":
    chip_list.append(f"Store: {selected_store}")
if search_keyword.strip():
    chip_list.append(f"Search: '{search_keyword.strip()}'")

if chip_list:
    chips_html = "".join([f'<span class="filter-chip">{c}</span>' for c in chip_list])
    st.markdown(f"<div class='mb-3 flex flex-wrap items-center'>{chips_html}</div>", unsafe_allow_html=True)

# KPI Cards Row
k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(f"""
    <div class="kpi-card-2026">
        <div class="kpi-icon-badge">{get_svg_icon("explorer", 20, t_colors['accent'])}</div>
        <div class="kpi-label">Filtered Dataset</div>
        <div class="kpi-value">{filtered_count:,}</div>
        <div class="kpi-desc">Reviews in active date scope</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card-2026">
        <div class="kpi-icon-badge">{get_svg_icon("performance", 20, t_colors['accent'])}</div>
        <div class="kpi-label">Supervised Accuracy</div>
        <div class="kpi-value">{best_acc * 100:.1f}%</div>
        <div class="kpi-desc">Logistic Regression Classifier</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card-2026">
        <div class="kpi-icon-badge">{get_svg_icon("analytics", 20, t_colors['accent'])}</div>
        <div class="kpi-label">Macro F1-Score</div>
        <div class="kpi-value">{best_f1 * 100:.1f}%</div>
        <div class="kpi-desc">Balanced Multi-Class Metric</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi-card-2026">
        <div class="kpi-icon-badge">{get_svg_icon("positive", 20, t_colors['accent'])}</div>
        <div class="kpi-label">Gain vs VADER</div>
        <div class="kpi-value">+{(best_acc - vader_acc)*100:.1f}%</div>
        <div class="kpi-desc">Outperforms Rule-Based Baseline</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# Sentiment Breakdown Row
s1, s2, s3 = st.columns(3)

with s1:
    pct = (pos_c / tot_f) * 100
    st.markdown(f"""
    <div class="sent-card-pos">
        <div class="flex items-center justify-between mb-1">
            <span class="font-bold text-sm flex items-center gap-1.5" style="color: {t_colors['positive']}">
                {get_svg_icon("positive", 18, t_colors['positive'])} Positive Sentiment
            </span>
            <span class="font-extrabold text-base" style="color: {t_colors['positive']}">{pct:.1f}%</span>
        </div>
        <div class="font-extrabold text-xl" style="color: {t_colors['text_primary']}">{pos_c:,} <span class="text-xs font-semibold" style="color: {t_colors['text_muted']}">reviews</span></div>
        <div class="progress-bar-bg">
            <div class="progress-bar-fill" style="width: {pct:.1f}%; background-color: {t_colors['positive']}"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with s2:
    pct = (neu_c / tot_f) * 100
    st.markdown(f"""
    <div class="sent-card-neu">
        <div class="flex items-center justify-between mb-1">
            <span class="font-bold text-sm flex items-center gap-1.5" style="color: {t_colors['neutral']}">
                {get_svg_icon("neutral", 18, t_colors['neutral'])} Neutral Sentiment
            </span>
            <span class="font-extrabold text-base" style="color: {t_colors['neutral']}">{pct:.1f}%</span>
        </div>
        <div class="font-extrabold text-xl" style="color: {t_colors['text_primary']}">{neu_c:,} <span class="text-xs font-semibold" style="color: {t_colors['text_muted']}">reviews</span></div>
        <div class="progress-bar-bg">
            <div class="progress-bar-fill" style="width: {pct:.1f}%; background-color: {t_colors['neutral']}"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with s3:
    pct = (neg_c / tot_f) * 100
    st.markdown(f"""
    <div class="sent-card-neg">
        <div class="flex items-center justify-between mb-1">
            <span class="font-bold text-sm flex items-center gap-1.5" style="color: {t_colors['negative']}">
                {get_svg_icon("negative", 18, t_colors['negative'])} Negative Sentiment
            </span>
            <span class="font-extrabold text-base" style="color: {t_colors['negative']}">{pct:.1f}%</span>
        </div>
        <div class="font-extrabold text-xl" style="color: {t_colors['text_primary']}">{neg_c:,} <span class="text-xs font-semibold" style="color: {t_colors['text_muted']}">reviews</span></div>
        <div class="progress-bar-bg">
            <div class="progress-bar-fill" style="width: {pct:.1f}%; background-color: {t_colors['negative']}"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# -----------------------------------------------------------------------------
# 5. TAB CONTENT ROUTING
# -----------------------------------------------------------------------------

# --- OVERVIEW TAB ---
if navigation == "Overview":
    st.markdown("### Overview Dashboard")
    st.caption("High-level summary of customer sentiment distribution and model benchmark insights.")
    
    col_l, col_r = st.columns([1.1, 0.9])
    
    with col_l:
        st.markdown("##### Sentiment Share Distribution")
        if df_filtered is not None and not df_filtered.empty:
            s_counts = df_filtered["sentiment"].value_counts().reset_index()
            s_counts.columns = ["Sentiment", "Count"]
            
            fig_donut = px.pie(
                s_counts,
                values="Count",
                names="Sentiment",
                hole=0.55,
                color="Sentiment",
                color_discrete_map={"Positive": t_colors["positive"], "Neutral": t_colors["neutral"], "Negative": t_colors["negative"]}
            )
            fig_donut.update_traces(textposition="outside", textinfo="percent+label")
            fig_donut.update_layout(get_chart_theme(st.session_state["app_theme"]))
            st.plotly_chart(fig_donut, use_container_width=True)
            
    with col_r:
        st.markdown("##### Key Project Insights")
        avg_rating = df_filtered["rating_num"].mean() if df_filtered is not None and "rating_num" in df_filtered and not df_filtered.empty else 0.0
        st.markdown(f"""
        <div class="card-2026 space-y-3">
            <div class="flex justify-between border-b pb-2" style="border-color: {t_colors['border']}">
                <span class="font-semibold text-sm" style="color: {t_colors['text_primary']}">Average Customer Rating</span>
                <span class="font-extrabold" style="color: {t_colors['accent']}">{avg_rating:.2f} / 5.0 Stars</span>
            </div>
            <div class="flex justify-between border-b pb-2" style="border-color: {t_colors['border']}">
                <span class="font-semibold text-sm" style="color: {t_colors['text_primary']}">Supervised vs Baseline Gain</span>
                <span class="font-extrabold" style="color: {t_colors['positive']}">+{(best_acc - vader_acc)*100:.1f}% Accuracy</span>
            </div>
            <div class="flex justify-between border-b pb-2" style="border-color: {t_colors['border']}">
                <span class="font-semibold text-sm" style="color: {t_colors['text_primary']}">Vocabulary Size</span>
                <span class="font-extrabold" style="color: {t_colors['text_secondary']}">{summary_info.get('tfidf_features', 20000):,} n-gram features</span>
            </div>
            <div class="flex justify-between">
                <span class="font-semibold text-sm" style="color: {t_colors['text_primary']}">Primary Complaint Categories</span>
                <span class="font-extrabold" style="color: {t_colors['negative']}">Drive-thru delay, Cold food</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


# --- LIVE PREDICTOR TAB ---
elif navigation == "Live Predictor":
    st.markdown("### Live Review Sentiment Analyzer")
    st.caption("Perform real-time NLP sentiment evaluation on custom customer review text.")

    col_in, col_res = st.columns([1.1, 0.9])

    sample_presets = {
        "Custom Review Text": "",
        "Negative Review (Slow & Cold)": "The drive-thru was extremely slow, took over 25 minutes! The fries were cold, soggy, and un-salted. Terrible customer service.",
        "Positive Review (Fast & Fresh)": "Amazing experience! The staff was super friendly, order was accurate, and the burger was fresh and delicious. Quick service!",
        "Neutral Review (Standard Visit)": "It was okay. Ordered a coffee and a donut. Nothing special, average waiting time."
    }

    with col_in:
        preset_choice = st.selectbox("Select Preset Example:", list(sample_presets.keys()))
        default_val = sample_presets[preset_choice]

        user_review = st.text_area("Review Text Input:", value=default_val, height=140, placeholder="Type or paste a customer review here...")
        
        words_count = len(user_review.split()) if user_review else 0
        chars_count = len(user_review) if user_review else 0

        st.caption(f"Word count: **{words_count}** | Character count: **{chars_count}**")

        b1, b2 = st.columns(2)
        with b1:
            analyze_btn = st.button("Analyze Sentiment", use_container_width=True, type="primary")
        with b2:
            clear_btn = st.button("Clear Input", use_container_width=True)
            if clear_btn:
                user_review = ""

    with col_res:
        if analyze_btn or (user_review.strip() and preset_choice != "Custom Review Text"):
            if not user_review.strip():
                st.warning("Please enter review text to analyze.")
            elif model is None or vectorizer is None:
                st.error("ML model assets not available.")
            else:
                clean_t = preprocess_text(user_review)
                x_vec = vectorizer.transform([clean_t])
                pred_class = model.predict(x_vec)[0]
                proba_arr = model.predict_proba(x_vec)[0]
                proba_dict = dict(zip(model.classes_, proba_arr))
                conf_pct = proba_dict[pred_class] * 100

                icon_name = pred_class.lower()
                c_color = t_colors.get(icon_name, t_colors["accent"])

                st.markdown(f"""
                <div class="card-2026 text-center" style="border-left: 6px solid {c_color};">
                    <div class="inline-flex p-2.5 rounded-full mb-2" style="background-color: {t_colors[icon_name+'_bg']}">
                        {get_svg_icon(icon_name, 28, c_color)}
                    </div>
                    <div class="font-extrabold text-2xl" style="color: {c_color}">{pred_class} Sentiment</div>
                    <div class="text-xs font-semibold text-slate-500">Confidence Score: {conf_pct:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)

                st.write("")
                st.markdown("##### Prediction Confidence Breakdown")
                cats = list(proba_dict.keys())
                probs = [proba_dict[c] * 100 for c in cats]
                bar_colors = [t_colors.get(c.lower(), t_colors["accent"]) for c in cats]

                fig_p = go.Figure(go.Bar(
                    x=probs,
                    y=cats,
                    orientation='h',
                    marker=dict(color=bar_colors, cornerradius=4),
                    text=[f"{p:.1f}%" for p in probs],
                    textposition='outside'
                ))
                layout_cfg = get_chart_theme(st.session_state["app_theme"])
                layout_cfg["height"] = 180
                layout_cfg["xaxis"]["range"] = [0, 118]
                fig_p.update_layout(layout_cfg)
                st.plotly_chart(fig_p, use_container_width=True)

                # Key Terms Explainability
                contribs = get_token_contributions(user_review, model, vectorizer, pred_class)
                if contribs:
                    st.markdown("##### Key Contributing Terms")
                    chip_htmls = []
                    for w, s in contribs:
                        bg_c = t_colors["positive_bg"] if s > 0 else t_colors["negative_bg"]
                        tx_c = t_colors["positive"] if s > 0 else t_colors["negative"]
                        sign = "+" if s > 0 else ""
                        chip_htmls.append(f'<span class="filter-chip" style="background-color: {bg_c}; color: {tx_c}; border-color: {tx_c}">{w} ({sign}{s:.2f})</span>')
                    st.markdown("".join(chip_htmls), unsafe_allow_html=True)
        else:
            st.info("Enter custom text on the left or select a preset review to run live AI analysis.")


# --- SENTIMENT ANALYTICS TAB ---
elif navigation == "Sentiment Analytics":
    st.markdown("### Interactive Sentiment Analytics")
    st.caption("Deep-dive analytics on review sentiment distributions, temporal trends, star ratings, and store volume.")

    if df_filtered is not None and not df_filtered.empty:
        tab_interactive, tab_artifacts = st.tabs(["Interactive Visualizations", "Diagnostic Figures Gallery"])

        with tab_interactive:
            r1_c1, r1_c2 = st.columns(2)

            with r1_c1:
                st.markdown("##### Sentiment Share Distribution")
                s_counts = df_filtered["sentiment"].value_counts().reset_index()
                s_counts.columns = ["Sentiment", "Count"]

                fig_donut = px.pie(
                    s_counts,
                    values="Count",
                    names="Sentiment",
                    hole=0.5,
                    color="Sentiment",
                    color_discrete_map={"Positive": t_colors["positive"], "Neutral": t_colors["neutral"], "Negative": t_colors["negative"]}
                )
                fig_donut.update_traces(textposition="outside", textinfo="percent+label")
                fig_donut.update_layout(get_chart_theme(st.session_state["app_theme"]))
                st.plotly_chart(fig_donut, use_container_width=True)

            with r1_c2:
                st.markdown("##### Sentiment Breakdown by Star Rating")
                r_group = df_filtered.groupby(["rating_num", "sentiment"]).size().reset_index(name="Count")
                fig_bar = px.bar(
                    r_group,
                    x="rating_num",
                    y="Count",
                    color="sentiment",
                    barmode="group",
                    labels={"rating_num": "Star Rating (1-5)", "Count": "Reviews"},
                    color_discrete_map={"Positive": t_colors["positive"], "Neutral": t_colors["neutral"], "Negative": t_colors["negative"]}
                )
                fig_bar.update_layout(get_chart_theme(st.session_state["app_theme"]))
                st.plotly_chart(fig_bar, use_container_width=True)

            r2_c1, r2_c2 = st.columns(2)

            with r2_c1:
                st.markdown("##### Review Word Count by Sentiment")
                df_copy = df_filtered.copy()
                df_copy["word_count"] = df_copy["review_clean"].astype(str).apply(lambda x: len(x.split()))
                fig_box = px.box(
                    df_copy,
                    x="sentiment",
                    y="word_count",
                    color="sentiment",
                    points=False,
                    color_discrete_map={"Positive": t_colors["positive"], "Neutral": t_colors["neutral"], "Negative": t_colors["negative"]}
                )
                fig_box.update_layout(get_chart_theme(st.session_state["app_theme"]))
                st.plotly_chart(fig_box, use_container_width=True)

            with r2_c2:
                st.markdown("##### Top Store Locations by Volume")
                if "store_address" in df_filtered.columns:
                    top_stores = df_filtered["store_address"].value_counts().head(7).reset_index()
                    top_stores.columns = ["Store", "Count"]
                    fig_stores = px.bar(
                        top_stores,
                        x="Count",
                        y="Store",
                        orientation="h",
                        text="Count",
                        color_discrete_sequence=[t_colors["accent"]]
                    )
                    fig_stores.update_traces(textposition="outside")
                    layout_cfg = get_chart_theme(st.session_state["app_theme"])
                    layout_cfg["yaxis"]["autorange"] = "reversed"
                    fig_stores.update_layout(layout_cfg)
                    st.plotly_chart(fig_stores, use_container_width=True)

        with tab_artifacts:
            st.markdown("##### Diagnostic Project Figures Gallery")
            fig_files = [
                ("01_sentiment_rating_dist.png", "Sentiment Rating Distribution"),
                ("02_length_by_sentiment.png", "Review Length Distribution"),
                ("03_autotag_share.png", "Auto-Tag Share Analysis"),
                ("04_sentiment_over_time.png", "Sentiment Over Time Trends"),
                ("05_wordclouds.png", "Sentiment Word Clouds"),
                ("06_top_bigrams.png", "Top N-Gram Bigrams")
            ]
            fig_cols = st.columns(2)
            for i, (fname, title) in enumerate(fig_files):
                fpath = os.path.join("Figures", fname)
                if os.path.exists(fpath):
                    with fig_cols[i % 2]:
                        st.markdown(f"**{title}**")
                        st.image(fpath, use_column_width=True)
    else:
        st.warning("No records found matching active filters.")


# --- REVIEW EXPLORER TAB ---
elif navigation == "Review Explorer":
    st.markdown("### Review Dataset Explorer")
    st.caption("Search, sort, filter, and inspect individual customer reviews.")

    if df_filtered is not None and not df_filtered.empty:
        sort_choice = st.selectbox("Sort Reviews By:", ["Newest First", "Oldest First", "Highest Rating", "Lowest Rating"])
        df_display = df_filtered.copy()

        if sort_choice == "Newest First":
            df_display = df_display.sort_values("derived_date", ascending=False)
        elif sort_choice == "Oldest First":
            df_display = df_display.sort_values("derived_date", ascending=True)
        elif sort_choice == "Highest Rating":
            df_display = df_display.sort_values("rating_num", ascending=False)
        elif sort_choice == "Lowest Rating":
            df_display = df_display.sort_values("rating_num", ascending=True)

        st.markdown(f"Displaying **{len(df_display):,}** matching reviews:")
        
        # Display Columns
        cols_to_show = ["reviewer_id", "store_name", "rating_num", "sentiment", "review_clean"]
        cols_to_show = [c for c in cols_to_show if c in df_display.columns]

        st.dataframe(
            df_display[cols_to_show].head(100),
            use_container_width=True,
            height=360
        )

        st.write("")
        st.markdown("##### Expandable Sample Review Inspector")
        sample_row = df_display.iloc[0]
        with st.expander(f"Inspect Review ID: {sample_row.get('reviewer_id', 'N/A')}", expanded=True):
            st.markdown(f"""
            <div class="card-2026 space-y-2">
                <div class="flex justify-between text-xs border-b pb-2" style="border-color: {t_colors['border']}">
                    <span>Store: <b>{sample_row.get('store_name', 'N/A')}</b></span>
                    <span>Rating: <b>{sample_row.get('rating_num', 'N/A')} Stars</b></span>
                    <span>Sentiment: <b>{sample_row.get('sentiment', 'N/A')}</b></span>
                </div>
                <div class="text-sm pt-2" style="color: {t_colors['text_primary']}">
                    <i>"{sample_row.get('review_clean', sample_row.get('review_text', ''))}"</i>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.write("")
        csv_data = df_display.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Filtered CSV Dataset",
            data=csv_data,
            file_name=f"mcdonalds_filtered_reviews_{datetime.date.today()}.csv",
            mime="text/csv"
        )
    else:
        st.warning("No records match current filter criteria.")


# --- MODEL PERFORMANCE TAB ---
elif navigation == "Model Performance":
    st.markdown("### Model Performance & Evaluation Metrics")
    st.caption("Comparative benchmarking of supervised machine learning algorithms vs. unsupervised VADER baseline.")

    if df_models is not None:
        st.markdown("##### Model Metrics Comparison Table")
        st.dataframe(df_models.style.highlight_max(axis=0, color="#EEF2FF").format("{:.4f}"), use_container_width=True)

        metric_sel = st.selectbox("Select Benchmark Metric:", ["accuracy", "macro_precision", "macro_recall", "macro_f1"])
        df_p = df_models.reset_index()
        df_p.columns = ["Model", "accuracy", "macro_precision", "macro_recall", "macro_f1"]

        fig_comp = px.bar(
            df_p,
            x="Model",
            y=metric_sel,
            color="Model",
            text_auto=".3f",
            color_discrete_sequence=[t_colors["accent"], t_colors["positive"], t_colors["neutral"]]
        )
        fig_comp.update_layout(get_chart_theme(st.session_state["app_theme"]))
        st.plotly_chart(fig_comp, use_container_width=True)

    m1, m2 = st.columns(2)
    cm_path = os.path.join("Figures", "07_confusion_matrix.png")
    feat_path = os.path.join("Figures", "09_top_predictive_words.png")

    with m1:
        if os.path.exists(cm_path):
            st.markdown("**Supervised Logistic Regression Confusion Matrix**")
            st.image(cm_path, use_column_width=True)
    with m2:
        if os.path.exists(feat_path):
            st.markdown("**Top Feature Terms (Predictive Importance)**")
            st.image(feat_path, use_column_width=True)


# --- REPORTS TAB ---
elif navigation == "Reports":
    st.markdown("### Executive Review Intelligence Report")
    st.caption("Automated analytical summary generated dynamically from the currently filtered dataset scope.")

    if df_filtered is not None and not df_filtered.empty:
        rep_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        
        dom_sent = df_filtered["sentiment"].mode()[0] if not df_filtered.empty else "N/A"
        dom_pct = (len(df_filtered[df_filtered["sentiment"] == dom_sent]) / len(df_filtered)) * 100
        avg_r = df_filtered["rating_num"].mean() if "rating_num" in df_filtered else 0

        st.markdown(f"""
        <div class="card-2026 space-y-2 mb-4">
            <div class="flex items-center justify-between border-b pb-2" style="border-color: {t_colors['border']}">
                <h4 class="font-extrabold text-lg" style="color: {t_colors['text_primary']}">McDonald's Customer Intelligence Report</h4>
                <span class="text-xs font-semibold" style="color: {t_colors['text_muted']}">Generated: {rep_date}</span>
            </div>
            <div class="grid grid-cols-3 gap-4 text-xs font-medium pt-1" style="color: {t_colors['text_secondary']}">
                <div>• Date Scope: <b>{date_option}</b></div>
                <div>• Evaluated Reviews: <b>{filtered_count:,}</b></div>
                <div>• Supervised Accuracy: <b>{best_acc*100:.1f}%</b></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("##### Executive Key Findings (Data-Driven)")
        st.markdown(f"""
        * **Dominant Sentiment Share:** **{dom_sent}** sentiment leads the current scope with **{dom_pct:.1f}%** of evaluated feedback.
        * **Average Customer Satisfaction Rating:** **{avg_r:.2f} / 5.0 Stars**.
        * **Model Predictive Advantage:** Supervised Logistic Regression achieves **{best_acc*100:.1f}% Accuracy**, outperforming the baseline VADER lexicon by **+{(best_acc - vader_acc)*100:.1f}%**.
        """)

        rep_csv = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Filtered Report Dataset (CSV)",
            data=rep_csv,
            file_name=f"mcdonalds_sentiment_report_{datetime.date.today()}.csv",
            mime="text/csv"
        )
    else:
        st.warning("No records available to generate report. Adjust your filter criteria.")


# --- PROJECT INFORMATION TAB ---
elif navigation == "Project Information":
    st.markdown("### Capstone II Project Details & Methodology")
    st.caption("Academic overview, NLP pipeline architecture, and implementation details.")

    st.markdown(f"""
    <div class="card-2026 space-y-4">
        <div>
            <h4 class="font-extrabold text-lg" style="color: {t_colors['accent']}">Sabaragamuwa University of Sri Lanka (SUSL)</h4>
            <p class="text-xs font-semibold text-slate-500">Department of Data Science • Capstone II (DS3206)</p>
        </div>
        <hr style="border-color: {t_colors['border']}">
        <div>
            <h5 class="font-bold text-sm text-slate-900 mb-2">📌 Machine Learning Pipeline Architecture</h5>
            <ol class="list-decimal pl-5 text-xs text-slate-600 space-y-1.5 font-medium">
                <td><b>Data Collection:</b> 22,366 raw McDonald's customer reviews collected across nationwide branches.</td>
                <td><b>NLP Preprocessing:</b> Lowercasing, regex URL removal, non-alphabetic filtering, and tokenization.</td>
                <td><b>TF-IDF Vectorization:</b> Feature extraction yielding 20,000 top n-gram terms.</td>
                <td><b>Supervised Classification:</b> Multi-class Logistic Regression with 80/20 train-test split.</td>
                <td><b>Baseline Evaluation:</b> Benchmarked against rule-based VADER lexicon analysis.</td>
            </ol>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.caption("McDonald's Customer Review Sentiment Intelligence System • 2026 Capstone Platform")