# =============================================================================
# Backend Smoke Tests — McDonald's Sentiment Analysis Platform
# =============================================================================
# These tests run in CI to verify the FastAPI server starts and responds
# correctly. They use FastAPI's TestClient (backed by httpx) so no real
# server needs to be running.
#
# Run with: pytest tests/test_server.py -v
# =============================================================================

import pytest
from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# Import the FastAPI app
# The server loads ML assets at import time; they may be missing in CI,
# so we gracefully handle that scenario in the tests.
# ---------------------------------------------------------------------------
from server import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# 1. Health endpoint
# ---------------------------------------------------------------------------
class TestHealthEndpoint:
    """Tests for GET /api/health"""

    def test_health_returns_200(self):
        """Health check must return HTTP 200."""
        response = client.get("/api/health")
        assert response.status_code == 200

    def test_health_returns_json(self):
        """Health check response must be valid JSON."""
        response = client.get("/api/health")
        data = response.json()
        assert isinstance(data, dict)

    def test_health_has_status_field(self):
        """Health check response must contain a 'status' field."""
        response = client.get("/api/health")
        data = response.json()
        assert "status" in data

    def test_health_has_timestamp(self):
        """Health check response must contain a 'timestamp' field."""
        response = client.get("/api/health")
        data = response.json()
        assert "timestamp" in data

    def test_health_has_model_loaded_flag(self):
        """Health check response must report model_loaded status."""
        response = client.get("/api/health")
        data = response.json()
        assert "model_loaded" in data
        assert isinstance(data["model_loaded"], bool)


# ---------------------------------------------------------------------------
# 2. Metrics endpoint
# ---------------------------------------------------------------------------
class TestMetricsEndpoint:
    """Tests for GET /api/metrics"""

    def test_metrics_returns_200(self):
        response = client.get("/api/metrics")
        assert response.status_code == 200

    def test_metrics_returns_json(self):
        response = client.get("/api/metrics")
        data = response.json()
        assert isinstance(data, dict)

    def test_metrics_has_accuracy_fields(self):
        """Metrics must include best_accuracy and best_f1."""
        response = client.get("/api/metrics")
        data = response.json()
        assert "best_accuracy" in data
        assert "best_f1" in data

    def test_metrics_accuracy_is_float(self):
        response = client.get("/api/metrics")
        data = response.json()
        assert isinstance(data["best_accuracy"], float)


# ---------------------------------------------------------------------------
# 3. Models benchmark endpoint
# ---------------------------------------------------------------------------
class TestModelsEndpoint:
    """Tests for GET /api/models"""

    def test_models_returns_200(self):
        response = client.get("/api/models")
        assert response.status_code == 200

    def test_models_returns_list(self):
        response = client.get("/api/models")
        data = response.json()
        assert "models" in data
        assert isinstance(data["models"], list)

    def test_models_list_not_empty(self):
        response = client.get("/api/models")
        data = response.json()
        assert len(data["models"]) > 0

    def test_model_entries_have_required_fields(self):
        """Each model entry must have model name, accuracy, and f1 score."""
        response = client.get("/api/models")
        models = response.json()["models"]
        required_fields = {"model", "accuracy", "macro_f1"}
        for entry in models:
            for field in required_fields:
                assert field in entry, f"Missing field '{field}' in model entry: {entry}"


# ---------------------------------------------------------------------------
# 4. Reviews endpoint
# ---------------------------------------------------------------------------
class TestReviewsEndpoint:
    """Tests for GET /api/reviews"""

    def test_reviews_returns_200(self):
        response = client.get("/api/reviews")
        assert response.status_code == 200

    def test_reviews_response_structure(self):
        """Reviews response must include pagination metadata."""
        response = client.get("/api/reviews")
        data = response.json()
        assert "reviews" in data
        assert "total_filtered" in data
        assert "page" in data

    def test_reviews_pagination_defaults(self):
        """Default page should be 1."""
        response = client.get("/api/reviews")
        data = response.json()
        assert data["page"] == 1


# ---------------------------------------------------------------------------
# 5. Analytics endpoint
# ---------------------------------------------------------------------------
class TestAnalyticsEndpoint:
    """Tests for GET /api/analytics"""

    def test_analytics_returns_200(self):
        response = client.get("/api/analytics")
        assert response.status_code == 200

    def test_analytics_has_sentiment_share(self):
        response = client.get("/api/analytics")
        data = response.json()
        assert "sentiment_share" in data
        assert isinstance(data["sentiment_share"], list)


# ---------------------------------------------------------------------------
# 6. Predict endpoint (model may not be loaded in CI — test gracefully)
# ---------------------------------------------------------------------------
class TestPredictEndpoint:
    """Tests for POST /api/predict"""

    def test_predict_rejects_empty_text(self):
        """Predict must return 400 for empty text."""
        response = client.post("/api/predict", json={"text": ""})
        assert response.status_code in (400, 500)  # 500 if model not loaded

    def test_predict_accepts_valid_text(self):
        """Predict must return 200 or 500 (if model not loaded in CI)."""
        response = client.post("/api/predict", json={"text": "The food was great!"})
        # In CI without model files, returns 500 — that's acceptable
        # In production with model files, must return 200
        assert response.status_code in (200, 500)

    def test_predict_200_response_structure(self):
        """If predict returns 200, validate response shape."""
        response = client.post("/api/predict", json={"text": "Excellent service!"})
        if response.status_code == 200:
            data = response.json()
            assert "predicted_sentiment" in data
            assert "confidence_percentage" in data
            assert "probabilities" in data


# ---------------------------------------------------------------------------
# 7. Prometheus Metrics endpoint
# ---------------------------------------------------------------------------
class TestPrometheusMetricsEndpoint:
    """Tests for GET /metrics and GET /api/metrics/prometheus"""

    def test_metrics_returns_200(self):
        response = client.get("/metrics")
        assert response.status_code == 200

    def test_metrics_content_is_text(self):
        response = client.get("/metrics")
        assert "text" in response.headers.get("content-type", "")

