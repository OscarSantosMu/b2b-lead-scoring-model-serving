"""
Health check and monitoring routes.
"""

import logging
import os
from datetime import UTC, datetime

from fastapi import APIRouter, Response, status
from prometheus_client import CONTENT_TYPE_LATEST, REGISTRY, generate_latest

from api.app.model import get_model

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])

# Track startup time
_startup_time = datetime.now(UTC)


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Simple health check endpoint",
)
async def health_check():
    """Basic health check."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.get(
    "/health/ready",
    status_code=status.HTTP_200_OK,
    summary="Readiness check",
    description="Check if service is ready to accept requests",
)
async def readiness_check():
    """Readiness check - verifies model is loaded."""
    try:
        model = get_model()
        if model is None or model.model is None:
            return Response(
                content="Model not loaded",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return {
            "status": "ready",
            "model_version": model.model_version,
            "timestamp": datetime.now(UTC).isoformat(),
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return Response(
            content=f"Service not ready: {str(e)}",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


@router.get(
    "/health/live",
    status_code=status.HTTP_200_OK,
    summary="Liveness check",
    description="Check if service is alive",
)
async def liveness_check():
    """Liveness check."""
    uptime_seconds = (datetime.now(UTC) - _startup_time).total_seconds()

    return {
        "status": "alive",
        "uptime_seconds": uptime_seconds,
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.get(
    "/metrics",
    summary="Prometheus metrics",
    description="Expose Prometheus metrics",
)
async def metrics():
    """Prometheus metrics endpoint."""
    data = generate_latest(REGISTRY)
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


@router.get(
    "/status",
    summary="Detailed status",
    description="Get detailed service status",
)
async def status_check():
    """Detailed status information."""
    try:
        model = get_model()
        uptime_seconds = (datetime.now(UTC) - _startup_time).total_seconds()

        return {
            "status": "operational",
            "uptime_seconds": uptime_seconds,
            "model": {
                "version": model.model_version,
                "loaded": model.model is not None,
                "n_features": len(model.feature_names),
            },
            "environment": {
                "python_version": os.sys.version,
                "hostname": os.getenv("HOSTNAME", "unknown"),
            },
            "timestamp": datetime.now(UTC).isoformat(),
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return {
            "status": "degraded",
            "error": str(e),
            "timestamp": datetime.now(UTC).isoformat(),
        }
