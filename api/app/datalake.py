"""
Data lake writer for scoring results.
Supports writing to AWS S3 and Azure Data Lake Storage.
"""

import logging
import os
from abc import ABC, abstractmethod
from datetime import UTC, datetime

logger = logging.getLogger(__name__)


class DataLakeWriter(ABC):
    """Abstract base class for data lake writers."""

    @abstractmethod
    def write_result(
        self,
        lead_id: str,
        bucket: int,
        tier: str,
        raw_score: float,
        model_version: str,
        timestamp: str,
        features: dict,
    ) -> bool:
        """Write a scoring result to the data lake."""
        pass

    @abstractmethod
    def write_batch_results(self, results: list[dict]) -> bool:
        """Write batch scoring results to the data lake."""
        pass


class S3DataLakeWriter(DataLakeWriter):
    """Writer for AWS S3 data lake (placeholder)."""

    def __init__(
        self,
        bucket: str = None,
        prefix: str = "scoring-results",
        region: str = None,
    ):
        """
        Initialize S3 data lake writer (no-op for now).

        Args:
            bucket: S3 bucket name
            prefix: Key prefix for storing results
            region: AWS region
        """
        self.bucket = bucket or os.getenv("DATALAKE_S3_BUCKET")
        self.prefix = prefix
        self.region = region or os.getenv("AWS_REGION", "us-east-1")
        self.enabled = False
        logger.info("S3DataLakeWriter is a placeholder and disabled for now")

    def _generate_key(self, lead_id: str, timestamp: str) -> str:
        """Generate S3 key for storing result (placeholder)."""
        try:
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            dt = datetime.now(UTC)
        return (
            f"{self.prefix}/year={dt.year:04d}/month={dt.month:02d}/"
            f"day={dt.day:02d}/{lead_id}_{dt.strftime('%H%M%S%f')}.json"
        )

    def write_result(
        self,
        lead_id: str,
        bucket: int,
        tier: str,
        raw_score: float,
        model_version: str,
        timestamp: str,
        features: dict,
    ) -> bool:
        """No-op write to S3 (placeholder)."""
        logger.debug("S3DataLakeWriter.write_result called but writer is disabled")
        return False

    def write_batch_results(self, results: list[dict]) -> bool:
        """No-op batch write to S3 (placeholder)."""
        logger.debug("S3DataLakeWriter.write_batch_results called but writer is disabled")
        return False


class AzureDataLakeWriter(DataLakeWriter):
    """Writer for Azure Data Lake Storage Gen2 (placeholder)."""

    def __init__(
        self,
        storage_account: str = None,
        container: str = None,
        prefix: str = "scoring-results",
    ):
        """
        Initialize Azure Data Lake writer (no-op for now).

        Args:
            storage_account: Azure storage account name
            container: Container/filesystem name
            prefix: Path prefix for storing results
        """
        self.storage_account = storage_account or os.getenv("AZURE_STORAGE_ACCOUNT")
        self.container = container or os.getenv("AZURE_DATALAKE_CONTAINER", "datalake")
        self.prefix = prefix
        self.enabled = False
        logger.info("AzureDataLakeWriter is a placeholder and disabled for now")

    def _generate_path(self, lead_id: str, timestamp: str) -> str:
        """Generate path for storing result (placeholder)."""
        try:
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            dt = datetime.now(UTC)
        return (
            f"{self.prefix}/year={dt.year:04d}/month={dt.month:02d}/"
            f"day={dt.day:02d}/{lead_id}_{dt.strftime('%H%M%S%f')}.json"
        )

    def write_result(
        self,
        lead_id: str,
        bucket: int,
        tier: str,
        raw_score: float,
        model_version: str,
        timestamp: str,
        features: dict,
    ) -> bool:
        """No-op write to Azure Data Lake (placeholder)."""
        logger.debug("AzureDataLakeWriter.write_result called but writer is disabled")
        return False

    def write_batch_results(self, results: list[dict]) -> bool:
        """No-op batch write to Azure Data Lake (placeholder)."""
        logger.debug("AzureDataLakeWriter.write_batch_results called but writer is disabled")
        return False


class NoOpDataLakeWriter(DataLakeWriter):
    """No-op writer for when data lake is disabled or not configured."""

    def write_result(
        self,
        lead_id: str,
        bucket: int,
        tier: str,
        raw_score: float,
        model_version: str,
        timestamp: str,
        features: dict,
    ) -> bool:
        """No-op write."""
        logger.debug(f"Data lake write skipped (no-op mode): lead_id={lead_id}")
        return True

    def write_batch_results(self, results: list[dict]) -> bool:
        """No-op batch write."""
        logger.debug(f"Data lake batch write skipped (no-op mode): {len(results)} results")
        return True


# Global writer instance
_writer_instance: DataLakeWriter | None = None


def get_datalake_writer() -> DataLakeWriter:
    """Get or create the global data lake writer instance."""
    global _writer_instance

    if _writer_instance is None:
        provider = os.getenv("DATALAKE_PROVIDER", "none").lower()

        if provider == "s3":
            _writer_instance = S3DataLakeWriter()
        elif provider == "azure":
            _writer_instance = AzureDataLakeWriter()
        else:
            _writer_instance = NoOpDataLakeWriter()
            if provider != "none":
                logger.warning(f"Unknown data lake provider '{provider}', using no-op writer")

        logger.info(f"Data lake writer initialized: {type(_writer_instance).__name__}")

    return _writer_instance


def write_scoring_result(
    lead_id: str,
    bucket: int,
    tier: str,
    raw_score: float,
    model_version: str,
    timestamp: str,
    features: dict,
) -> bool:
    """
    Write a scoring result to the configured data lake.

    This is the main entry point for writing scoring results.
    It's designed to be non-blocking and fail gracefully.
    """
    try:
        writer = get_datalake_writer()
        return writer.write_result(
            lead_id=lead_id,
            bucket=bucket,
            tier=tier,
            raw_score=raw_score,
            model_version=model_version,
            timestamp=timestamp,
            features=features,
        )
    except Exception as e:
        logger.error(f"Error writing to data lake: {e}")
        return False
