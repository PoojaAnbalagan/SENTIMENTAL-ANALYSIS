# 📊 Customer Review Sentiment Analytics Platform

> An enterprise-grade Machine Learning & NLP Analytics Web Dashboard for real-time customer review sentiment prediction, multi-model benchmarking, interactive visualizations, and automated executive reporting.

---

## 🚀 Key Features

- ⚡ **Live Review Sentiment Analyzer**: Real-time NLP sentiment prediction with TF-IDF vectorization and Logistic Regression classification, complete with confidence scores, probability breakdown, key word contribution explainability, and dynamic SVG face emoji expressions.
- 📈 **Interactive Sentiment Analytics**: Rich data visualizations using Recharts including sentiment share distribution, star rating cross-tabulation, and store location review volume analytics with responsive formatted labels.
- 🤖 **Multi-Model Benchmark Suite**: Rigorous comparison of 3 supervised machine learning models (Logistic Regression, Linear SVM, Multinomial Naive Bayes) against the rule-based VADER baseline.
- 🔎 **Review Explorer & Filtering**: Advanced multi-dimensional filtering (Date Range, Star Ratings, Sentiment Scope, Keyword Search, Store Location) with pagination and Blob-based CSV exports.
- 📄 **Executive Reports**: Dynamic printable report generation summarizing sentiment breakdown, top complaint categories, rating distributions, and model performance metrics.
- 🔴 **Real-Time API Health Monitoring**: Continuous status monitoring with pulsating Online/Offline visual indicators and automatic server reconnection prompts.
- 🎨 **Modern Purple-Gradient Aesthetics**: 2026-level user interface designed with Tailwind CSS, custom CSS variable tokens, clean typography, and full responsiveness.

---

## 🛠️ Technology Stack

### Backend & Machine Learning
- **Framework**: Python 3.9+ / FastAPI
- **ML & NLP Libraries**: Scikit-Learn, NLTK (VADER Sentiment), Pandas, NumPy, Joblib
- **Server**: Uvicorn ASGI Server

### Frontend & Data Visualization
- **Framework**: React 18 / Vite
- **Styling**: Tailwind CSS, Vanilla CSS Variables
- **Charts**: Recharts (PieChart, BarChart, Vertical Bar Layouts)
- **Icons**: Lucide React Icons
- **HTTP Client**: Axios

---

## 📂 Project Structure

```
├── server.py                   # FastAPI REST Backend API Server
├── models/
│   ├── best_sentiment_model.pkl # Trained Logistic Regression Classifier
│   └── tfidf_vectorizer.pkl    # Fitted TF-IDF Vectorizer Asset
├── data/
│   └── cleaned_reviews.csv     # Preprocessed Customer Review Dataset
├── results/
│   ├── summary.json            # Model evaluation summary metrics
│   └── model_results.csv       # Multi-model comparative benchmark results
├── Figures/                    # Generated matplotlib diagnostic charts
├── notebooks/
│   └── Sentiment_Analysis.ipynb# Data preprocessing & model training notebook
└── frontend/                   # React 18 + Vite Web Application
    ├── index.html
    ├── package.json
    ├── tailwind.config.js
    ├── vite.config.js
    └── src/
        ├── App.jsx             # Main Application Shell & State Management
        ├── index.css           # Global Theme & CSS Variables System
        ├── components/
        │   ├── Header.jsx      # Top Bar with Real-Time API Health Indicator
        │   ├── Sidebar.jsx     # Collapsible Navigation Sidebar with Brand Logo
        │   ├── KpiCards.jsx     # High-Level Metrics & Sentiment Share Cards
        │   └── FilterBar.jsx   # Global Multi-Filter Bar Component
        ├── views/
        │   ├── OverviewView.jsx         # Executive Summary Dashboard
        │   ├── PredictorView.jsx        # Real-Time Sentiment Predictor
        │   ├── AnalyticsView.jsx        # Interactive Charts & Diagnostic Gallery
        │   ├── ExplorerView.jsx         # Paginated Dataset Search & CSV Export
        │   ├── ModelPerformanceView.jsx # Multi-Model Benchmarks & Figures
        │   ├── ReportsView.jsx          # Dynamic Printable Executive Report
        │   └── ProjectInfoView.jsx      # System Architecture & Methodology
        └── services/
            └── api.js          # Axios API Client & Export Utilities
```

---

## 📊 Machine Learning Model Performance

| Model | Model Type | Accuracy | Macro F1-Score | Gain vs VADER |
|-------|------------|----------|----------------|---------------|
| **Logistic Regression** *(Selected)* | Supervised (TF-IDF) | **74.1%** | **67.0%** | **+9.7%** |
| **Linear SVM** | Supervised (TF-IDF) | 73.5% | 66.4% | +9.1% |
| **Multinomial Naive Bayes** | Supervised (TF-IDF) | 70.8% | 61.2% | +6.4% |
| **VADER Baseline** | Lexicon / Rule-Based | 64.3% | 55.8% | Baseline |

---

## ⚙️ Quick Start Guide

### Prerequisites
- Python 3.9 or higher
- Node.js 18.x or higher & npm

### 1. Launch FastAPI Backend Server

```bash
# Install Python dependencies
pip install fastapi uvicorn pydantic pandas numpy scikit-learn nltk joblib

# Start the API server on port 8000
python server.py
```
*The API will start running at `http://localhost:8000`. You can inspect interactive API documentation at `http://localhost:8000/docs`.*

### 2. Launch React Frontend Application

```bash
# Navigate to the frontend directory
cd frontend

# Install Node dependencies
npm install

# Start the Vite development server
npm run dev
```
*Open `http://localhost:5173` in your browser to access the dashboard.*

---

## 📡 API Endpoints Documentation

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | `GET` | Health check endpoint returning server & model status |
| `/api/metrics` | `GET` | Corpus summary counts and benchmark metrics |
| `/api/predict` | `POST` | Accepts review text payload and returns sentiment prediction + probabilities |
| `/api/reviews` | `GET` | Paginated review search with multi-filter query parameters |
| `/api/analytics` | `GET` | Aggregated analytics metrics for filtered scope |
| `/api/models` | `GET` | Multi-model benchmark performance table |
| `/api/export` | `GET` | Stream formatted CSV file download for filtered review data |

---

## 📄 License & Credits

Developed for Customer Review Sentiment Intelligence Research. Built with Python, Scikit-Learn, FastAPI, React, and Tailwind CSS.
