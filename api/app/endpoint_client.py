"""
Client for calling SageMaker and Azure ML real-time endpoints.
Provides unified interface for both cloud providers.
"""

import json
import logging
import os
from abc import ABC, abstractmethod

import boto3
import numpy as np

logger = logging.getLogger(__name__)


class EndpointClient(ABC):
    """Abstract base class for ML endpoint clients."""

    @abstractmethod
    def predict(self, features: np.ndarray) -> np.ndarray:
        """Make prediction using the endpoint."""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Check if endpoint is healthy."""
        pass


class SageMakerEndpointClient(EndpointClient):
    """Client for AWS SageMaker real-time endpoints."""

    def __init__(self, endpoint_name: str, region: str | None = None):
        """
        Initialize SageMaker endpoint client.

        Args:
            endpoint_name: Name of the SageMaker endpoint
            region: AWS region (defaults to AWS_REGION env var or us-east-1)
        """
        self.endpoint_name = endpoint_name
        self.region = region or os.getenv("AWS_REGION", "us-east-1")

        try:
            self.runtime_client = boto3.client("sagemaker-runtime", region_name=self.region)
            logger.info(f"SageMaker client initialized for endpoint: {endpoint_name}")
        except Exception as e:
            logger.error(f"Failed to initialize SageMaker client: {e}")
            raise

    def predict(self, features: np.ndarray) -> np.ndarray:
        """
        Make prediction using SageMaker endpoint.

        Args:
            features: Input features as numpy array (n_samples, n_features)

        Returns:
            Predictions as numpy array
        """
        try:
            # Convert features to JSON payload
            payload = json.dumps(features.tolist())

            # Invoke endpoint
            response = self.runtime_client.invoke_endpoint(
                EndpointName=self.endpoint_name, ContentType="application/json", Body=payload
            )

            # Parse response
            result = json.loads(response["Body"].read().decode())
            predictions = np.array(result)

            logger.debug(f"SageMaker prediction successful for {len(features)} samples")
            return predictions

        except Exception as e:
            logger.error(f"SageMaker prediction failed: {e}")
            raise RuntimeError(f"Failed to get prediction from SageMaker: {e}") from e

    def health_check(self) -> bool:
        """
        Check if SageMaker endpoint is healthy.

        Returns:
            True if endpoint is in service, False otherwise
        """
        try:
            client = boto3.client("sagemaker", region_name=self.region)
            response = client.describe_endpoint(EndpointName=self.endpoint_name)
            status = response["EndpointStatus"]

            is_healthy = status == "InService"
            logger.debug(f"SageMaker endpoint {self.endpoint_name} status: {status}")
            return is_healthy

        except Exception as e:
            logger.error(f"Failed to check SageMaker endpoint health: {e}")
            return False


class AzureMLEndpointClient(EndpointClient):
    """Client for Azure Machine Learning real-time endpoints."""

    def __init__(
        self, endpoint_url: str, api_key: str | None = None, deployment_name: str | None = None
    ):
        """
        Initialize Azure ML endpoint client.

        Args:
            endpoint_url: URL of the Azure ML endpoint
            api_key: API key for authentication (defaults to AZURE_ML_API_KEY env var)
            deployment_name: Specific deployment name (optional)
        """
        self.endpoint_url = endpoint_url.rstrip("/")
        self.api_key = api_key or os.getenv("AZURE_ML_API_KEY")
        self.deployment_name = deployment_name

        if not self.api_key:
            raise ValueError("Azure ML API key is required")

        # Setup headers
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        if self.deployment_name:
            self.headers["azureml-model-deployment"] = self.deployment_name

        logger.info(f"Azure ML client initialized for endpoint: {endpoint_url}")

    def predict(self, features: np.ndarray) -> np.ndarray:
        """
        Make prediction using Azure ML endpoint.

        Args:
            features: Input features as numpy array (n_samples, n_features)

        Returns:
            Predictions as numpy array
        """
        try:
            import requests

            # Convert features to JSON payload
            payload = {"data": features.tolist()}

            # Make request
            response = requests.post(
                f"{self.endpoint_url}/score", headers=self.headers, json=payload, timeout=30
            )

            response.raise_for_status()

            # Parse response
            result = response.json()
            predictions = np.array(result)

            logger.debug(f"Azure ML prediction successful for {len(features)} samples")
            return predictions

        except Exception as e:
            logger.error(f"Azure ML prediction failed: {e}")
            raise RuntimeError(f"Failed to get prediction from Azure ML: {e}") from e

    def health_check(self) -> bool:
        """
        Check if Azure ML endpoint is healthy.

        Returns:
            True if endpoint responds, False otherwise
        """
        try:
            import requests

            # Try to get endpoint metadata
            response = requests.get(self.endpoint_url, headers=self.headers, timeout=10)

            is_healthy = response.status_code == 200
            logger.debug(f"Azure ML endpoint health check: {response.status_code}")
            return is_healthy

        except Exception as e:
            logger.error(f"Failed to check Azure ML endpoint health: {e}")
            return False


def get_endpoint_client(provider: str = "local", **kwargs) -> EndpointClient | None:
    """
    Factory function to create appropriate endpoint client.

    Args:
        provider: "sagemaker", "azure", or "local" (for local stub model)
        **kwargs: Provider-specific arguments

    Returns:
        EndpointClient instance or None for local
    """
    provider = provider.lower()

    if provider == "local":
        # Use local stub model
        return None

    elif provider == "sagemaker":
        endpoint_name = kwargs.get("endpoint_name") or os.getenv("SAGEMAKER_ENDPOINT_NAME")
        if not endpoint_name:
            raise ValueError("SageMaker endpoint name is required")

        return SageMakerEndpointClient(endpoint_name=endpoint_name, region=kwargs.get("region"))

    elif provider == "azure":
        endpoint_url = kwargs.get("endpoint_url") or os.getenv("AZURE_ML_ENDPOINT_URL")
        if not endpoint_url:
            raise ValueError("Azure ML endpoint URL is required")

        return AzureMLEndpointClient(
            endpoint_url=endpoint_url,
            api_key=kwargs.get("api_key"),
            deployment_name=kwargs.get("deployment_name"),
        )

    else:
        raise ValueError(f"Unknown provider: {provider}")
