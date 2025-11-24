"""
Health check and monitoring routes.
"""

import logging
import os
from datetime import UTC, datetime

import psutil
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
                "endpoint_provider": model.endpoint_provider,
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


@router.get(
    "/resources",
    summary="Resource usage",
    description="Get real-time system resource usage metrics",
)
async def resource_check():
    """Resource usage information with detailed metrics."""
    try:
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_count = psutil.cpu_count()

        # Memory metrics
        memory = psutil.virtual_memory()

        # Disk metrics
        disk = psutil.disk_usage("/")

        # Process metrics
        process = psutil.Process()
        process_memory = process.memory_info()

        # Network metrics (if available)
        network = psutil.net_io_counters()

        return {
            "status": "ok",
            "cpu": {
                "usage_percent": round(cpu_percent, 2),
                "count": cpu_count,
                "per_cpu": [
                    round(p, 2) for p in psutil.cpu_percent(interval=0.1, percpu=True)
                ],
            },
            "memory": {
                "total_mb": round(memory.total / 1024 / 1024, 2),
                "available_mb": round(memory.available / 1024 / 1024, 2),
                "used_mb": round(memory.used / 1024 / 1024, 2),
                "usage_percent": round(memory.percent, 2),
            },
            "disk": {
                "total_gb": round(disk.total / 1024 / 1024 / 1024, 2),
                "used_gb": round(disk.used / 1024 / 1024 / 1024, 2),
                "free_gb": round(disk.free / 1024 / 1024 / 1024, 2),
                "usage_percent": round(disk.percent, 2),
            },
            "process": {
                "memory_mb": round(process_memory.rss / 1024 / 1024, 2),
                "cpu_percent": round(process.cpu_percent(), 2),
                "threads": process.num_threads(),
                "open_files": len(process.open_files()),
            },
            "network": {
                "bytes_sent_mb": round(network.bytes_sent / 1024 / 1024, 2),
                "bytes_recv_mb": round(network.bytes_recv / 1024 / 1024, 2),
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv,
            },
            "alerts": {
                "high_cpu": cpu_percent > 80,
                "high_memory": memory.percent > 80,
                "low_disk": disk.percent > 85,
            },
            "timestamp": datetime.now(UTC).isoformat(),
        }
    except Exception as e:
        logger.error(f"Resource check failed: {e}")
        return Response(
            content=f"Resource check failed: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
