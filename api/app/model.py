"""
XGBoost model wrapper for B2B lead scoring.
Supports local model, SageMaker endpoints, and Azure ML endpoints.
"""

import json
import logging
import os
import time
from pathlib import Path

import numpy as np
import xgboost as xgb
from prometheus_client import Counter, Histogram

from api.app.endpoint_client import EndpointClient, get_endpoint_client

logger = logging.getLogger(__name__)

# Metrics
PREDICTION_COUNTER = Counter(
    "model_predictions_total", "Total predictions made", ["endpoint_provider", "tier"]
)
PREDICTION_LATENCY = Histogram(
    "model_prediction_latency_seconds",
    "Prediction latency",
    ["endpoint_provider"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 1.0],
)
PREDICTION_SCORE_HISTOGRAM = Histogram(
    "model_prediction_scores",
    "Distribution of prediction scores",
    ["endpoint_provider"],
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
)
PREDICTION_CONFIDENCE_HISTOGRAM = Histogram(
    "model_prediction_confidence",
    "Distribution of prediction confidence scores",
    ["endpoint_provider", "tier"],
    buckets=[0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99, 1.0],
)
PREDICTION_ERRORS = Counter(
    "model_prediction_errors_total",
    "Total prediction errors",
    ["endpoint_provider", "error_type"],
)
BATCH_SIZE_HISTOGRAM = Histogram(
    "model_batch_size", "Batch prediction sizes", buckets=[1, 5, 10, 25, 50, 75, 100]
)


class LeadScoringModel:
    """XGBoost model for B2B lead scoring with cloud endpoint support."""

    def __init__(
        self,
        model_path: str = None,
        endpoint_provider: str = None,
        endpoint_config: dict = None,
    ):
        """
        Initialize the model.

        Args:
            model_path: Path to local model file (for local mode)
            endpoint_provider: "sagemaker", "azure", or None for local
            endpoint_config: Configuration for endpoint client
        """
        self.model = None
        self.model_version = "1.0.0"
        self.feature_names = self._get_feature_names()
        self.model_metadata = {}

        # Determine mode: local or endpoint
        self.endpoint_provider = endpoint_provider or os.getenv(
            "MODEL_ENDPOINT_PROVIDER", "local"
        )
        self.endpoint_client: EndpointClient | None = None

        if self.endpoint_provider.lower() != "local":
            # Use cloud endpoint
            endpoint_config = endpoint_config or {}
            self.endpoint_client = get_endpoint_client(
                provider=self.endpoint_provider, **endpoint_config
            )
            logger.info(f"Using {self.endpoint_provider} endpoint for predictions")
        else:
            # Use local model
            if model_path:
                self.load_model(model_path)
            else:
                # Initialize with stub model
                self._init_stub_model()
            logger.info("Using local model for predictions")

    def _get_feature_names(self) -> list[str]:
        """Get the 50 feature names in order."""
        return [
            # Company Firmographics
            "company_revenue",
            "company_employee_count",
            "company_age_years",
            "company_funding_total",
            "company_growth_rate",
            "industry_tech_score",
            "geographic_tier",
            "company_public_status",
            "parent_company_exists",
            "subsidiary_count",
            # Engagement Metrics
            "website_visits_30d",
            "page_views_30d",
            "avg_session_duration_sec",
            "bounce_rate",
            "pricing_page_visits",
            "demo_page_visits",
            "documentation_views",
            "email_open_rate",
            "email_click_rate",
            "emails_received",
            "whitepaper_downloads",
            "webinar_attendance",
            "social_media_engagement",
            "customer_success_interactions",
            "support_ticket_count",
            # Behavioral Signals
            "days_since_first_touch",
            "days_since_last_touch",
            "total_touchpoints",
            "multi_channel_engagement",
            "decision_maker_contacted",
            "champion_identified",
            "budget_confirmed",
            "timeline_confirmed",
            "competitor_evaluation",
            "technical_evaluation_started",
            "contract_reviewed",
            "security_questionnaire_completed",
            "roi_calculator_used",
            "custom_demo_requested",
            "integration_questions_asked",
            # Lead Source & Attribution
            "lead_source_quality",
            "attribution_touchpoints",
            "paid_channel_source",
            "referral_source",
            "event_source",
            # Product Interest Signals
            "product_tier_interest",
            "feature_requests_count",
            "use_case_alignment",
            "integration_requirements",
            "deployment_preference",
        ]

    def _init_stub_model(self):
        """Initialize a stub XGBoost model with reasonable parameters."""
        logger.info("Initializing stub XGBoost model")

        # Create dummy training data with 50 features using realistic distributions
        n_samples = 1000
        np.random.seed(42)

        # Generate synthetic feature data with realistic ranges
        # Firmographics (0-9): mix of large numbers and ratios
        X_train = np.column_stack(
            [
                np.random.lognormal(15, 2, n_samples),  # company_revenue (millions)
                np.random.lognormal(3.5, 1.5, n_samples),  # company_employee_count
                np.random.uniform(0.5, 20, n_samples),  # company_age_years
                np.random.lognormal(14, 2, n_samples),  # company_funding_total
                np.random.uniform(-0.2, 0.8, n_samples),  # company_growth_rate
                np.random.uniform(0, 1, n_samples),  # industry_tech_score
                np.random.randint(1, 4, n_samples),  # geographic_tier
                np.random.binomial(1, 0.3, n_samples),  # company_public_status
                np.random.binomial(1, 0.4, n_samples),  # parent_company_exists
                np.random.poisson(2, n_samples),  # subsidiary_count
                # Engagement (10-24): counts and rates
                np.random.poisson(20, n_samples),  # website_visits_30d
                np.random.poisson(60, n_samples),  # page_views_30d
                np.random.uniform(30, 600, n_samples),  # avg_session_duration_sec
                np.random.uniform(0.2, 0.8, n_samples),  # bounce_rate
                np.random.poisson(3, n_samples),  # pricing_page_visits
                np.random.poisson(2, n_samples),  # demo_page_visits
                np.random.poisson(5, n_samples),  # documentation_views
                np.random.uniform(0.1, 0.8, n_samples),  # email_open_rate
                np.random.uniform(0.05, 0.4, n_samples),  # email_click_rate
                np.random.poisson(5, n_samples),  # emails_received
                np.random.poisson(1, n_samples),  # whitepaper_downloads
                np.random.binomial(2, 0.3, n_samples),  # webinar_attendance
                np.random.poisson(10, n_samples),  # social_media_engagement
                np.random.poisson(1, n_samples),  # customer_success_interactions
                np.random.poisson(1, n_samples),  # support_ticket_count
                # Behavioral (25-39): days and binary flags
                np.random.uniform(1, 180, n_samples),  # days_since_first_touch
                np.random.uniform(0, 30, n_samples),  # days_since_last_touch
                np.random.poisson(15, n_samples),  # total_touchpoints
                np.random.binomial(1, 0.5, n_samples),  # multi_channel_engagement
                np.random.binomial(1, 0.4, n_samples),  # decision_maker_contacted
                np.random.binomial(1, 0.3, n_samples),  # champion_identified
                np.random.binomial(1, 0.25, n_samples),  # budget_confirmed
                np.random.binomial(1, 0.3, n_samples),  # timeline_confirmed
                np.random.binomial(1, 0.5, n_samples),  # competitor_evaluation
                np.random.binomial(1, 0.35, n_samples),  # technical_evaluation_started
                np.random.binomial(1, 0.15, n_samples),  # contract_reviewed
                np.random.binomial(
                    1, 0.2, n_samples
                ),  # security_questionnaire_completed
                np.random.binomial(1, 0.3, n_samples),  # roi_calculator_used
                np.random.binomial(1, 0.25, n_samples),  # custom_demo_requested
                np.random.poisson(2, n_samples),  # integration_questions_asked
                # Attribution (40-44): quality scores and counts
                np.random.uniform(0.3, 1.0, n_samples),  # lead_source_quality
                np.random.poisson(3, n_samples),  # attribution_touchpoints
                np.random.binomial(1, 0.4, n_samples),  # paid_channel_source
                np.random.binomial(1, 0.2, n_samples),  # referral_source
                np.random.binomial(1, 0.15, n_samples),  # event_source
                # Product Interest (45-49): tiers and counts
                np.random.randint(0, 3, n_samples),  # product_tier_interest
                np.random.poisson(1, n_samples),  # feature_requests_count
                np.random.uniform(0.3, 1.0, n_samples),  # use_case_alignment
                np.random.poisson(2, n_samples),  # integration_requirements
                np.random.randint(0, 2, n_samples),  # deployment_preference
            ]
        )

        # Generate synthetic labels based on realistic patterns
        # Normalize scores to 0-1 range for each category
        engagement_score = np.clip(
            (
                X_train[:, 10] / 50  # website_visits normalized
                + X_train[:, 14] / 10  # pricing_page_visits
                + X_train[:, 15] / 10  # demo_page_visits
                + X_train[:, 17]  # email_open_rate (already 0-1)
                + X_train[:, 20] / 5  # whitepaper_downloads
            )
            / 5,
            0,
            1,
        )

        behavioral_score = np.clip(
            (
                X_train[:, 29]  # decision_maker_contacted
                + X_train[:, 30]  # champion_identified
                + X_train[:, 31]  # budget_confirmed
                + X_train[:, 32]  # timeline_confirmed
                + X_train[:, 34]  # technical_evaluation_started
            )
            / 5,
            0,
            1,
        )

        product_score = np.clip(
            (
                X_train[:, 45] / 3  # product_tier_interest normalized
                + X_train[:, 47]  # use_case_alignment (already 0-1)
            )
            / 2,
            0,
            1,
        )

        firmographic_score = np.clip(
            (
                (X_train[:, 0] > np.median(X_train[:, 0])).astype(float)  # high revenue
                + (X_train[:, 1] > 20).astype(float)  # medium+ employee count
                + X_train[:, 5]  # industry_tech_score (already 0-1)
            )
            / 3,
            0,
            1,
        )

        # Combine scores with weights to create conversion probability
        combined_score = (
            0.35 * engagement_score
            + 0.30 * behavioral_score
            + 0.20 * product_score
            + 0.15 * firmographic_score
        )

        # Add some noise and convert to binary labels
        # Adjust threshold to get ~40-50% conversion rate in training
        noise = np.random.normal(0, 0.15, n_samples)
        y_train = ((combined_score + noise) > 0.4).astype(int)

        # Train XGBoost model
        dtrain = xgb.DMatrix(X_train, label=y_train, feature_names=self.feature_names)

        params = {
            "objective": "binary:logistic",
            "eval_metric": "auc",
            "max_depth": 6,
            "learning_rate": 0.1,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "random_state": 42,
        }

        self.model = xgb.train(params, dtrain, num_boost_round=100, verbose_eval=False)

        self.model_metadata = {
            "version": self.model_version,
            "features": self.feature_names,
            "n_features": 50,
            "model_type": "xgboost",
            "training_date": "2024-01-01",
            "is_stub": True,
        }

        logger.info(f"Stub model initialized with {len(self.feature_names)} features")

    def load_model(self, model_path: str):
        """Load model from file."""
        logger.info(f"Loading model from {model_path}")
        path = Path(model_path)

        if not path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")

        self.model = xgb.Booster()
        self.model.load_model(str(path))

        # Load metadata if available
        metadata_path = path.parent / f"{path.stem}_metadata.json"
        if metadata_path.exists():
            with open(metadata_path) as f:
                self.model_metadata = json.load(f)
                self.model_version = self.model_metadata.get(
                    "version", self.model_version
                )

        logger.info(f"Model loaded successfully, version: {self.model_version}")

    def save_model(self, model_path: str):
        """Save model to file."""
        logger.info(f"Saving model to {model_path}")
        path = Path(model_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        self.model.save_model(str(path))

        # Save metadata
        metadata_path = path.parent / f"{path.stem}_metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(self.model_metadata, f, indent=2)

        logger.info("Model saved successfully")

    def preprocess_features(self, features: dict) -> np.ndarray:
        """Convert feature dict to numpy array in correct order."""
        feature_vector = []
        for feature_name in self.feature_names:
            value = features.get(feature_name)
            if value is None:
                raise ValueError(f"Missing required feature: {feature_name}")
            feature_vector.append(float(value))

        return np.array([feature_vector])

    def predict(self, features: dict) -> tuple[float, float, str]:
        """
        Make prediction for a single lead.
        Supports both local model and cloud endpoints.

        Returns:
            Tuple of (score, confidence, tier)
        """
        start_time = time.time()
        endpoint_provider = self.endpoint_provider

        try:
            # Preprocess features
            X = self.preprocess_features(features)

            # Get prediction based on mode
            if self.endpoint_client:
                # Use cloud endpoint
                pred = self.endpoint_client.predict(X)[0]
            else:
                # Use local model
                dmatrix = xgb.DMatrix(X, feature_names=self.feature_names)
                pred = self.model.predict(dmatrix)[0]

            score = float(pred)

            # Calculate confidence (based on distance from decision boundary)
            confidence = abs(2 * score - 1)  # 0 at boundary (0.5), 1 at extremes

            # Determine tier
            if score >= 0.7:
                tier = "hot"
            elif score >= 0.4:
                tier = "warm"
            else:
                tier = "cold"

            # Record detailed metrics
            PREDICTION_COUNTER.labels(
                endpoint_provider=endpoint_provider, tier=tier
            ).inc()

            PREDICTION_SCORE_HISTOGRAM.labels(
                endpoint_provider=endpoint_provider
            ).observe(score)

            PREDICTION_CONFIDENCE_HISTOGRAM.labels(
                endpoint_provider=endpoint_provider, tier=tier
            ).observe(confidence)

            # Log prediction with context
            logger.info(
                "Prediction completed",
                extra={
                    "endpoint_provider": endpoint_provider,
                    "score": round(score, 4),
                    "confidence": round(confidence, 4),
                    "tier": tier,
                    "latency_ms": round((time.time() - start_time) * 1000, 2),
                },
            )

            return score, confidence, tier

        except Exception as e:
            # Record error metrics
            error_type = type(e).__name__
            PREDICTION_ERRORS.labels(
                endpoint_provider=endpoint_provider, error_type=error_type
            ).inc()

            logger.error(
                "Prediction error",
                extra={
                    "endpoint_provider": endpoint_provider,
                    "error_type": error_type,
                    "error": str(e),
                },
            )
            raise

        finally:
            # Record latency
            latency = time.time() - start_time
            PREDICTION_LATENCY.labels(endpoint_provider=endpoint_provider).observe(
                latency
            )

    def predict_batch(
        self, features_list: list[dict]
    ) -> list[tuple[float, float, str]]:
        """Make predictions for multiple leads."""
        # Record batch size
        BATCH_SIZE_HISTOGRAM.observe(len(features_list))

        logger.info(
            "Batch prediction started",
            extra={
                "batch_size": len(features_list),
                "endpoint_provider": self.endpoint_provider,
            },
        )

        return [self.predict(features) for features in features_list]

    def get_feature_importance(self) -> dict[str, float]:
        """Get feature importance scores."""
        importance = self.model.get_score(importance_type="gain")
        return {feature: importance.get(feature, 0.0) for feature in self.feature_names}

    def get_model_info(self) -> dict:
        """Get model metadata and information."""
        return {
            "version": self.model_version,
            "n_features": len(self.feature_names),
            "features": self.feature_names,
            "metadata": self.model_metadata,
        }


# Global model instance
_model_instance = None


def get_model() -> LeadScoringModel:
    """Get or create the global model instance."""
    global _model_instance
    if _model_instance is None:
        _model_instance = LeadScoringModel()
    return _model_instance


def reload_model(model_path: str):
    """Reload the model from a new path."""
    global _model_instance
    _model_instance = LeadScoringModel(model_path)
    logger.info("Model reloaded successfully")
