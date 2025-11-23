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
PREDICTION_COUNTER = Counter("model_predictions_total", "Total predictions made")
PREDICTION_LATENCY = Histogram("model_prediction_latency_seconds", "Prediction latency")
PREDICTION_SCORE_HISTOGRAM = Histogram(
    "model_prediction_scores",
    "Distribution of prediction scores",
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
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
        self.endpoint_provider = endpoint_provider or os.getenv("MODEL_ENDPOINT_PROVIDER", "local")
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

        # Create dummy training data with 50 features
        n_samples = 1000
        np.random.seed(42)

        # Generate synthetic feature data
        X_train = np.random.randn(n_samples, 50)

        # Generate synthetic labels with some pattern
        # Higher engagement and firmographic signals -> higher conversion
        engagement_score = X_train[:, 10:25].mean(axis=1)  # Engagement features
        firmographic_score = X_train[:, 0:10].mean(axis=1)  # Firmographic features
        behavioral_score = X_train[:, 25:40].mean(axis=1)  # Behavioral features

        # Combine scores to create labels
        combined_score = 0.4 * engagement_score + 0.3 * firmographic_score + 0.3 * behavioral_score
        y_train = (combined_score > 0).astype(int)

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
                self.model_version = self.model_metadata.get("version", self.model_version)

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

            # Record metrics
            PREDICTION_COUNTER.inc()
            PREDICTION_SCORE_HISTOGRAM.observe(score)

            return score, confidence, tier

        finally:
            # Record latency
            latency = time.time() - start_time
            PREDICTION_LATENCY.observe(latency)

    def predict_batch(self, features_list: list[dict]) -> list[tuple[float, float, str]]:
        """Make predictions for multiple leads."""
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
