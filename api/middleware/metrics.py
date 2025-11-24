"""
Enhanced metrics collection middleware with system resource monitoring.
"""

import logging
import os
import platform
import time
from collections.abc import Callable

import psutil
from fastapi import Request, Response
from prometheus_client import Counter, Gauge, Histogram, Info
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)

# HTTP Request Metrics
HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"]
)

HTTP_REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0],
)

HTTP_REQUEST_SIZE = Histogram(
    "http_request_size_bytes", "HTTP request size in bytes", ["method", "endpoint"]
)

HTTP_RESPONSE_SIZE = Histogram(
    "http_response_size_bytes", "HTTP response size in bytes", ["method", "endpoint"]
)

HTTP_ERRORS_TOTAL = Counter(
    "http_errors_total",
    "Total HTTP errors",
    ["method", "endpoint", "status", "exception_type"],
)

# System Resource Metrics
CPU_USAGE_PERCENT = Gauge("system_cpu_usage_percent", "Current CPU usage percentage")

MEMORY_USAGE_PERCENT = Gauge(
    "system_memory_usage_percent", "Current memory usage percentage"
)

MEMORY_USAGE_BYTES = Gauge("system_memory_usage_bytes", "Current memory usage in bytes")

DISK_USAGE_PERCENT = Gauge("system_disk_usage_percent", "Current disk usage percentage")

ACTIVE_REQUESTS = Gauge("http_requests_active", "Number of active HTTP requests")

# Process Metrics
PROCESS_CPU_PERCENT = Gauge("process_cpu_usage_percent", "Process CPU usage percentage")

PROCESS_MEMORY_BYTES = Gauge(
    "process_memory_usage_bytes", "Process memory usage in bytes"
)

PROCESS_THREADS = Gauge("process_threads_count", "Number of threads in the process")

# Application Info
APP_INFO = Info("application", "Application metadata")
APP_INFO.info(
    {
        "version": "1.0.0",
        "python_version": platform.python_version(),
        "platform": platform.system(),
        "hostname": os.getenv("HOSTNAME", platform.node()),
    }
)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting HTTP and system metrics."""

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self._process = psutil.Process()
        self._last_resource_update = 0
        self._resource_update_interval = 5  # Update system metrics every 5 seconds

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and collect metrics."""
        # Update system resources periodically
        current_time = time.time()
        if current_time - self._last_resource_update >= self._resource_update_interval:
            self._update_system_metrics()
            self._last_resource_update = current_time

        # Increment active requests
        ACTIVE_REQUESTS.inc()

        # Extract endpoint info
        method = request.method
        endpoint = self._get_endpoint(request)

        # Measure request size
        request_size = int(request.headers.get("content-length", 0))
        if request_size > 0:
            HTTP_REQUEST_SIZE.labels(method=method, endpoint=endpoint).observe(
                request_size
            )

        # Start timing
        start_time = time.time()

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Record metrics
            status = str(response.status_code)
            HTTP_REQUESTS_TOTAL.labels(
                method=method, endpoint=endpoint, status=status
            ).inc()

            HTTP_REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(
                duration
            )

            # Measure response size
            if hasattr(response, "body"):
                response_size = len(response.body)
                HTTP_RESPONSE_SIZE.labels(method=method, endpoint=endpoint).observe(
                    response_size
                )

            # Log performance metrics
            if duration > 1.0:  # Log slow requests
                logger.warning(
                    "Slow request detected",
                    extra={
                        "method": method,
                        "endpoint": endpoint,
                        "duration_seconds": round(duration, 3),
                        "status": status,
                        "cpu_percent": self._process.cpu_percent(),
                        "memory_mb": self._process.memory_info().rss / 1024 / 1024,
                    },
                )

            return response

        except Exception as e:
            # Calculate duration even on error
            duration = time.time() - start_time

            # Record error metrics
            status = "500"
            exception_type = type(e).__name__

            HTTP_REQUESTS_TOTAL.labels(
                method=method, endpoint=endpoint, status=status
            ).inc()

            HTTP_ERRORS_TOTAL.labels(
                method=method,
                endpoint=endpoint,
                status=status,
                exception_type=exception_type,
            ).inc()

            HTTP_REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(
                duration
            )

            logger.error(
                "Request error",
                extra={
                    "method": method,
                    "endpoint": endpoint,
                    "duration_seconds": round(duration, 3),
                    "exception_type": exception_type,
                    "error": str(e),
                },
            )

            raise

        finally:
            # Decrement active requests
            ACTIVE_REQUESTS.dec()

    def _get_endpoint(self, request: Request) -> str:
        """Extract endpoint path from request."""
        # Get route path if available, otherwise use URL path
        if hasattr(request, "scope") and "route" in request.scope:
            route = request.scope["route"]
            if hasattr(route, "path"):
                return route.path

        # Fallback to URL path
        path = request.url.path

        # Normalize paths to avoid cardinality explosion
        if path.startswith("/api/v1"):
            parts = path.split("/")
            if len(parts) >= 4:
                return "/".join(parts[:4])  # /api/v1/{resource}

        return path

    def _update_system_metrics(self):
        """Update system resource metrics."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            CPU_USAGE_PERCENT.set(cpu_percent)

            # Memory metrics
            memory = psutil.virtual_memory()
            MEMORY_USAGE_PERCENT.set(memory.percent)
            MEMORY_USAGE_BYTES.set(memory.used)

            # Disk metrics
            disk = psutil.disk_usage("/")
            DISK_USAGE_PERCENT.set(disk.percent)

            # Process metrics
            PROCESS_CPU_PERCENT.set(self._process.cpu_percent())
            PROCESS_MEMORY_BYTES.set(self._process.memory_info().rss)
            PROCESS_THREADS.set(self._process.num_threads())

        except Exception as e:
            logger.error(f"Error updating system metrics: {e}")
