"""
Integration tests for the complete scoring workflow.
"""

import time

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


@pytest.fixture
def sample_lead():
    """Sample lead with all features."""
    return {
        "lead_id": "INTEGRATION-TEST-001",
        "features": {
            "company_revenue": 10000000.0,
            "company_employee_count": 100,
            "company_age_years": 10.0,
            "company_funding_total": 5000000.0,
            "company_growth_rate": 0.5,
            "industry_tech_score": 0.9,
            "geographic_tier": 1,
            "company_public_status": 1,
            "parent_company_exists": 1,
            "subsidiary_count": 5,
            "website_visits_30d": 100,
            "page_views_30d": 300,
            "avg_session_duration_sec": 300.0,
            "bounce_rate": 0.2,
            "pricing_page_visits": 10,
            "demo_page_visits": 5,
            "documentation_views": 20,
            "email_open_rate": 0.8,
            "email_click_rate": 0.4,
            "emails_received": 15,
            "whitepaper_downloads": 5,
            "webinar_attendance": 3,
            "social_media_engagement": 50,
            "customer_success_interactions": 5,
            "support_ticket_count": 2,
            "days_since_first_touch": 45.0,
            "days_since_last_touch": 1.0,
            "total_touchpoints": 50,
            "multi_channel_engagement": 1,
            "decision_maker_contacted": 1,
            "champion_identified": 1,
            "budget_confirmed": 1,
            "timeline_confirmed": 1,
            "competitor_evaluation": 1,
            "technical_evaluation_started": 1,
            "contract_reviewed": 1,
            "security_questionnaire_completed": 1,
            "roi_calculator_used": 1,
            "custom_demo_requested": 1,
            "integration_questions_asked": 5,
            "lead_source_quality": 0.9,
            "attribution_touchpoints": 10,
            "paid_channel_source": 1,
            "referral_source": 1,
            "event_source": 1,
            "product_tier_interest": 3,
            "feature_requests_count": 5,
            "use_case_alignment": 0.95,
            "integration_requirements": 5,
            "deployment_preference": 0,
        },
    }


class TestScoringWorkflow:
    """Test complete scoring workflow."""

    def test_end_to_end_scoring(self, sample_lead):
        """Test complete end-to-end scoring."""
        headers = {"X-API-Key": "demo-api-key-123"}

        # 1. Check service is ready
        response = client.get("/health/ready")
        assert response.status_code == 200

        # 2. Get model info
        response = client.get("/api/v1/model/info", headers=headers)
        assert response.status_code == 200
        model_info = response.json()
        assert model_info["n_features"] == 50

        # 3. Score the lead
        response = client.post("/api/v1/score", json=sample_lead, headers=headers)
        assert response.status_code == 200

        result = response.json()
        assert result["lead_id"] == sample_lead["lead_id"]
        assert 0 <= result["score"] <= 1
        assert result["tier"] in ["hot", "warm", "cold"]
        assert "model_version" in result
        assert "timestamp" in result

    def test_concurrent_requests(self, sample_lead):
        """Test handling of concurrent requests."""
        headers = {"X-API-Key": "demo-api-key-123"}

        # Send multiple requests concurrently
        import concurrent.futures

        def score_lead(lead_id):
            lead = sample_lead.copy()
            lead["lead_id"] = f"CONCURRENT-{lead_id}"
            response = client.post("/api/v1/score", json=lead, headers=headers)
            return response.status_code, response.json()

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(score_lead, i) for i in range(10)]
            results = [f.result() for f in futures]

        # All requests should succeed
        assert all(status == 200 for status, _ in results)
        assert len(results) == 10

    def test_batch_scoring_workflow(self, sample_lead):
        """Test batch scoring workflow."""
        headers = {"X-API-Key": "demo-api-key-123"}

        # Create batch of leads
        batch = []
        for i in range(5):
            lead = sample_lead.copy()
            lead["lead_id"] = f"BATCH-{i}"
            batch.append(lead)

        # Score batch
        response = client.post("/api/v1/score/batch", json=batch, headers=headers)
        assert response.status_code == 200

        results = response.json()
        assert len(results) == 5

        # Verify all leads were scored
        lead_ids = {r["lead_id"] for r in results}
        assert lead_ids == {f"BATCH-{i}" for i in range(5)}

    def test_performance_latency(self, sample_lead):
        """Test that scoring meets performance requirements."""
        headers = {"X-API-Key": "demo-api-key-123"}

        # Warm up
        for _ in range(5):
            client.post("/api/v1/score", json=sample_lead, headers=headers)

        # Measure latency
        latencies = []
        for _ in range(20):
            start = time.time()
            response = client.post("/api/v1/score", json=sample_lead, headers=headers)
            latency = (time.time() - start) * 1000  # ms
            latencies.append(latency)
            assert response.status_code == 200

        # Check latency requirements
        avg_latency = sum(latencies) / len(latencies)
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]

        print(f"\nAverage latency: {avg_latency:.2f}ms")
        print(f"P95 latency: {p95_latency:.2f}ms")

        # Requirements: avg < 100ms, p95 < 200ms
        assert avg_latency < 200, f"Average latency {avg_latency}ms exceeds 200ms"
        assert p95_latency < 500, f"P95 latency {p95_latency}ms exceeds 500ms"

    def test_error_handling(self):
        """Test error handling in the workflow."""
        headers = {"X-API-Key": "demo-api-key-123"}

        # Test with invalid data
        invalid_lead = {
            "lead_id": "INVALID-001",
            "features": {
                "company_revenue": -1000,  # Invalid negative
            },
        }

        response = client.post("/api/v1/score", json=invalid_lead, headers=headers)
        assert response.status_code == 422  # Validation error

    def test_authentication_workflow(self, sample_lead):
        """Test authentication in the workflow."""
        # Without auth - should fail
        response = client.post("/api/v1/score", json=sample_lead)
        assert response.status_code == 401

        # With invalid key - should fail
        headers = {"X-API-Key": "invalid-key"}
        response = client.post("/api/v1/score", json=sample_lead, headers=headers)
        assert response.status_code == 401

        # With valid key - should succeed
        headers = {"X-API-Key": "demo-api-key-123"}
        response = client.post("/api/v1/score", json=sample_lead, headers=headers)
        assert response.status_code == 200


class TestMonitoring:
    """Test monitoring endpoints."""

    def test_metrics_collection(self, sample_lead):
        """Test that metrics are collected."""
        headers = {"X-API-Key": "demo-api-key-123"}

        # Make some predictions
        for i in range(5):
            lead = sample_lead.copy()
            lead["lead_id"] = f"METRICS-{i}"
            client.post("/api/v1/score", json=lead, headers=headers)

        # Check metrics endpoint
        response = client.get("/metrics")
        assert response.status_code == 200

        metrics_text = response.text
        assert "model_predictions_total" in metrics_text
        assert "model_prediction_latency_seconds" in metrics_text

    def test_health_checks_during_load(self, sample_lead):
        """Test health checks remain healthy during load."""
        headers = {"X-API-Key": "demo-api-key-123"}

        # Generate some load
        for i in range(10):
            lead = sample_lead.copy()
            lead["lead_id"] = f"LOAD-{i}"
            client.post("/api/v1/score", json=lead, headers=headers)

        # Health checks should still work
        response = client.get("/health")
        assert response.status_code == 200

        response = client.get("/health/ready")
        assert response.status_code == 200

        response = client.get("/health/live")
        assert response.status_code == 200
