"""
Load test for B2B Lead Scoring API targeting 300 RPS.
Run with: locust -f tests/load/locustfile.py --host=http://localhost:8000
"""

import random

from locust import HttpUser, between, task


class LeadScoringUser(HttpUser):
    """Simulated user for load testing the lead scoring API."""

    wait_time = between(0.01, 0.1)  # Wait 10-100ms between requests

    def on_start(self):
        """Setup - authenticate user."""
        self.headers = {
            "X-API-Key": "demo-api-key-123",
            "Content-Type": "application/json",
        }

    def generate_lead_features(self):
        """Generate randomized but realistic lead features."""
        return {
            # Company Firmographics
            "company_revenue": random.uniform(100000, 100000000),
            "company_employee_count": random.randint(1, 10000),
            "company_age_years": random.uniform(0.5, 50),
            "company_funding_total": random.uniform(0, 50000000),
            "company_growth_rate": random.uniform(-0.5, 2.0),
            "industry_tech_score": random.uniform(0, 1),
            "geographic_tier": random.randint(1, 3),
            "company_public_status": random.randint(0, 1),
            "parent_company_exists": random.randint(0, 1),
            "subsidiary_count": random.randint(0, 20),
            # Engagement Metrics
            "website_visits_30d": random.randint(0, 200),
            "page_views_30d": random.randint(0, 500),
            "avg_session_duration_sec": random.uniform(10, 600),
            "bounce_rate": random.uniform(0, 1),
            "pricing_page_visits": random.randint(0, 20),
            "demo_page_visits": random.randint(0, 10),
            "documentation_views": random.randint(0, 50),
            "email_open_rate": random.uniform(0, 1),
            "email_click_rate": random.uniform(0, 1),
            "emails_received": random.randint(0, 50),
            "whitepaper_downloads": random.randint(0, 10),
            "webinar_attendance": random.randint(0, 5),
            "social_media_engagement": random.randint(0, 100),
            "customer_success_interactions": random.randint(0, 10),
            "support_ticket_count": random.randint(0, 20),
            # Behavioral Signals
            "days_since_first_touch": random.uniform(0, 365),
            "days_since_last_touch": random.uniform(0, 30),
            "total_touchpoints": random.randint(1, 100),
            "multi_channel_engagement": random.randint(0, 1),
            "decision_maker_contacted": random.randint(0, 1),
            "champion_identified": random.randint(0, 1),
            "budget_confirmed": random.randint(0, 1),
            "timeline_confirmed": random.randint(0, 1),
            "competitor_evaluation": random.randint(0, 1),
            "technical_evaluation_started": random.randint(0, 1),
            "contract_reviewed": random.randint(0, 1),
            "security_questionnaire_completed": random.randint(0, 1),
            "roi_calculator_used": random.randint(0, 1),
            "custom_demo_requested": random.randint(0, 1),
            "integration_questions_asked": random.randint(0, 10),
            # Lead Source & Attribution
            "lead_source_quality": random.uniform(0, 1),
            "attribution_touchpoints": random.randint(1, 20),
            "paid_channel_source": random.randint(0, 1),
            "referral_source": random.randint(0, 1),
            "event_source": random.randint(0, 1),
            # Product Interest Signals
            "product_tier_interest": random.randint(1, 3),
            "feature_requests_count": random.randint(0, 10),
            "use_case_alignment": random.uniform(0, 1),
            "integration_requirements": random.randint(0, 10),
            "deployment_preference": random.randint(0, 2),
        }

    @task(10)
    def score_single_lead(self):
        """Score a single lead - most common operation."""
        payload = {
            "lead_id": f"LEAD-{random.randint(1000, 9999)}",
            "features": self.generate_lead_features(),
        }

        with self.client.post(
            "/api/v1/score",
            json=payload,
            headers=self.headers,
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")

    @task(2)
    def score_batch(self):
        """Score a batch of leads - less common but important."""
        batch_size = random.randint(5, 20)
        payload = [
            {
                "lead_id": f"LEAD-{random.randint(1000, 9999)}",
                "features": self.generate_lead_features(),
            }
            for _ in range(batch_size)
        ]

        with self.client.post(
            "/api/v1/score/batch",
            json=payload,
            headers=self.headers,
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")

    @task(1)
    def get_model_info(self):
        """Get model information - monitoring/debugging."""
        with self.client.get(
            "/api/v1/model/info",
            headers=self.headers,
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")

    @task(1)
    def health_check(self):
        """Health check endpoint."""
        with self.client.get(
            "/health",
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")


# For running targeted 300 RPS test:
# locust -f tests/load/locustfile.py --host=http://localhost:8000 \
#   --users=300 --spawn-rate=10 --run-time=5m --headless
