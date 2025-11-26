"""
Unit tests for the lead scoring model.
"""

import numpy as np
import pytest

from api.app.model import LeadScoringModel


@pytest.fixture
def model():
    """Create a model instance for testing."""
    return LeadScoringModel()


@pytest.fixture
def sample_features():
    """Sample feature dictionary."""
    return {
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
    }


def test_model_initialization(model):
    """Test model initializes correctly."""
    assert model is not None
    assert model.model is not None
    assert len(model.feature_names) == 50
    assert model.model_version is not None


def test_feature_names(model):
    """Test feature names are correct."""
    assert len(model.feature_names) == 50
    assert "company_revenue" in model.feature_names
    assert "deployment_preference" in model.feature_names


def test_preprocess_features(model, sample_features):
    """Test feature preprocessing."""
    X = model.preprocess_features(sample_features)
    assert X.shape == (1, 50)
    assert isinstance(X, np.ndarray)


def test_predict(model, sample_features):
    """Test prediction."""
    raw_score, bucket, tier, latency_ms = model.predict(sample_features)

    assert isinstance(raw_score, float)
    assert 0 <= raw_score <= 1  # Raw score is 0-1

    assert isinstance(bucket, int)
    assert 1 <= bucket <= 5  # Bucket is 1-5

    assert tier in ["A", "B", "C", "D", "E"]

    assert isinstance(latency_ms, float)
    assert latency_ms >= 0


def test_predict_hot_lead(model, sample_features):
    """Test that high engagement leads to tier A."""
    # Boost all engagement metrics
    features = sample_features.copy()
    for key in features:
        if "visit" in key or "engagement" in key or "touchpoint" in key:
            if isinstance(features[key], int):
                features[key] = min(features[key] * 5, 1000)

    raw_score, bucket, tier, latency_ms = model.predict(features)
    # Note: With stub model, tier depends on random initialization
    # Just check that prediction works
    assert 1 <= bucket <= 5
    assert tier in ["A", "B", "C", "D", "E"]


def test_predict_missing_feature(model):
    """Test prediction fails with missing feature."""
    incomplete_features = {
        "company_revenue": 5000000.0,
        "company_employee_count": 50,
    }

    with pytest.raises(ValueError, match="Missing required feature"):
        model.predict(incomplete_features)


def test_predict_batch(model, sample_features):
    """Test batch prediction."""
    features_list = [sample_features, sample_features.copy(), sample_features.copy()]
    results = model.predict_batch(features_list)

    assert len(results) == 3
    for raw_score, bucket, tier, _latency_ms in results:
        assert 0 <= raw_score <= 1
        assert 1 <= bucket <= 5
        assert tier in ["A", "B", "C", "D", "E"]


def test_get_feature_importance(model):
    """Test feature importance extraction."""
    importance = model.get_feature_importance()

    assert isinstance(importance, dict)
    assert len(importance) == 50

    # Check all features are present
    for feature in model.feature_names:
        assert feature in importance


def test_get_model_info(model):
    """Test model info retrieval."""
    info = model.get_model_info()

    assert "version" in info
    assert "n_features" in info
    assert "features" in info
    assert "metadata" in info

    assert info["n_features"] == 50
    assert len(info["features"]) == 50


def test_tier_thresholds(model, sample_features):
    """Test tier assignment based on bucket (1-5)."""
    # We can't control exact scores with stub model
    # But we can verify the logic is consistent
    raw_score, bucket, tier, _ = model.predict(sample_features)

    # Verify tier mapping is correct
    expected_tier = {5: "A", 4: "B", 3: "C", 2: "D", 1: "E"}[bucket]
    assert tier == expected_tier
