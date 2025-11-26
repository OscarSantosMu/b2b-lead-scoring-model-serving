"""
Unit tests for API endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


@pytest.fixture
def sample_request():
    """Sample scoring request."""
    return {
        "lead_id": "TEST-001",
        "features": {
            "company_revenue": 5000000.0,
            "company_employee_count": 50,
            "company_age_years": 5.5,
            "company_funding_total": 2000000.0,
            "company_growth_rate": 0.35,
            "industry_tech_score": 0.8,
            "geographic_tier": 1,
            "company_public_status": 0,
            "parent_company_exists": 1,
            "subsidiary_count": 2,
            "website_visits_30d": 45,
            "page_views_30d": 120,
            "avg_session_duration_sec": 180.5,
            "bounce_rate": 0.35,
            "pricing_page_visits": 5,
            "demo_page_visits": 3,
            "documentation_views": 10,
            "email_open_rate": 0.65,
            "email_click_rate": 0.25,
            "emails_received": 8,
            "whitepaper_downloads": 2,
            "webinar_attendance": 1,
            "social_media_engagement": 15,
            "customer_success_interactions": 2,
            "support_ticket_count": 0,
            "days_since_first_touch": 30.0,
            "days_since_last_touch": 2.0,
            "total_touchpoints": 25,
            "multi_channel_engagement": 1,
            "decision_maker_contacted": 1,
            "champion_identified": 1,
            "budget_confirmed": 0,
            "timeline_confirmed": 1,
            "competitor_evaluation": 1,
            "technical_evaluation_started": 1,
            "contract_reviewed": 0,
            "security_questionnaire_completed": 0,
            "roi_calculator_used": 1,
            "custom_demo_requested": 1,
            "integration_questions_asked": 3,
            "lead_source_quality": 0.75,
            "attribution_touchpoints": 5,
            "paid_channel_source": 1,
            "referral_source": 0,
            "event_source": 0,
            "product_tier_interest": 2,
            "feature_requests_count": 2,
            "use_case_alignment": 0.85,
            "integration_requirements": 3,
            "deployment_preference": 0,
        },
    }


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert "version" in data


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_readiness_check():
    """Test readiness check endpoint."""
    response = client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert "model_version" in data


def test_liveness_check():
    """Test liveness check endpoint."""
    response = client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"
    assert "uptime_seconds" in data


def test_score_lead_with_auth(sample_request):
    """Test scoring endpoint with authentication."""
    headers = {"X-API-Key": "demo-api-key-123"}
    response = client.post("/api/v1/score", json=sample_request, headers=headers)

    assert response.status_code == 200
    data = response.json()

    # Check new response structure
    assert "request_id" in data
    assert "model" in data
    assert data["model"]["name"].startswith("xgboost_lead_score_v")
    assert "version" in data["model"]
    assert data["lead_id"] == "TEST-001"
    assert "score" in data
    assert 0 <= data["score"]["raw_score"] <= 1
    assert 1 <= data["score"]["bucket"] <= 5
    assert data["score"]["tier"] in ["A", "B", "C", "D", "E"]
    # Without include_details, timing and api_version should be None
    assert data["timing"] is None
    assert data["api_version"] is None


def test_score_lead_with_details(sample_request):
    """Test scoring endpoint with include_details=true."""
    headers = {"X-API-Key": "demo-api-key-123"}
    response = client.post(
        "/api/v1/score?include_details=true", json=sample_request, headers=headers
    )

    assert response.status_code == 200
    data = response.json()

    # Check that details are included
    assert "request_id" in data
    assert data["timing"] is not None
    assert "latency_ms" in data["timing"]
    assert data["api_version"] is not None
    assert "ranking" in data["score"]
    assert data["score"]["ranking"] is not None
    assert "tier_definition" in data["score"]["ranking"]


def test_score_lead_without_auth(sample_request):
    """Test scoring endpoint without authentication."""
    response = client.post("/api/v1/score", json=sample_request)
    assert response.status_code == 401


def test_score_lead_invalid_api_key(sample_request):
    """Test scoring endpoint with invalid API key."""
    headers = {"X-API-Key": "invalid-key"}
    response = client.post("/api/v1/score", json=sample_request, headers=headers)
    assert response.status_code == 401


def test_score_batch(sample_request):
    """Test batch scoring endpoint."""
    headers = {"X-API-Key": "demo-api-key-123"}
    batch_request = [sample_request, sample_request.copy()]

    response = client.post("/api/v1/score/batch", json=batch_request, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    for item in data:
        assert 1 <= item["score"]["bucket"] <= 5
        assert item["score"]["tier"] in ["A", "B", "C", "D", "E"]
        assert 0 <= item["score"]["raw_score"] <= 1


def test_score_batch_with_details(sample_request):
    """Test batch scoring endpoint with include_details=true."""
    headers = {"X-API-Key": "demo-api-key-123"}
    batch_request = [sample_request, sample_request.copy()]

    response = client.post(
        "/api/v1/score/batch?include_details=true", json=batch_request, headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    for item in data:
        assert item["timing"] is not None
        assert item["api_version"] is not None
        assert item["score"]["ranking"] is not None


def test_score_batch_too_large(sample_request):
    """Test batch scoring with too many requests."""
    headers = {"X-API-Key": "demo-api-key-123"}
    batch_request = [sample_request.copy() for _ in range(101)]

    response = client.post("/api/v1/score/batch", json=batch_request, headers=headers)
    assert response.status_code == 400


def test_get_model_info():
    """Test model info endpoint."""
    headers = {"X-API-Key": "demo-api-key-123"}
    response = client.get("/api/v1/model/info", headers=headers)

    assert response.status_code == 200
    data = response.json()

    assert "version" in data
    assert "n_features" in data
    assert "features" in data
    assert data["n_features"] == 50


def test_get_feature_names():
    """Test feature names endpoint."""
    headers = {"X-API-Key": "demo-api-key-123"}
    response = client.get("/api/v1/model/features", headers=headers)

    assert response.status_code == 200
    data = response.json()

    assert "features" in data
    assert "count" in data
    assert data["count"] == 50
    assert len(data["features"]) == 50


def test_get_feature_importance():
    """Test feature importance endpoint."""
    headers = {"X-API-Key": "demo-api-key-123"}
    response = client.get("/api/v1/model/importance", headers=headers)

    assert response.status_code == 200
    data = response.json()

    assert "importance" in data
    assert "top_10" in data
    assert len(data["top_10"]) == 10


def test_invalid_feature_values(sample_request):
    """Test scoring with invalid feature values."""
    headers = {"X-API-Key": "demo-api-key-123"}

    # Invalid bounce rate (> 1)
    invalid_request = sample_request.copy()
    invalid_request["features"]["bounce_rate"] = 1.5

    response = client.post("/api/v1/score", json=invalid_request, headers=headers)
    assert response.status_code == 422  # Validation error


def test_missing_required_field(sample_request):
    """Test scoring with missing required field."""
    headers = {"X-API-Key": "demo-api-key-123"}

    invalid_request = sample_request.copy()
    del invalid_request["features"]["company_revenue"]

    response = client.post("/api/v1/score", json=invalid_request, headers=headers)
    assert response.status_code == 422  # Validation error


def test_metrics_endpoint():
    """Test Prometheus metrics endpoint."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]


def test_status_endpoint():
    """Test status endpoint."""
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()

    assert "status" in data
    assert "model" in data
    assert "environment" in data
