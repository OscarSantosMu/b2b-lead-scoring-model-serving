"""
Logging middleware for request/response tracking and structured logging.
"""

import json
import logging
import time
import uuid
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging all requests and responses with structured data."""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log details."""
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Start timing
        start_time = time.time()

        # Extract request details
        request_details = {
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "client_host": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        }

        # Log request
        logger.info("Request started", extra=request_details)

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Log response
            response_details = {
                **request_details,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
            }

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            # Log based on status code
            if response.status_code >= 500:
                logger.error("Request failed", extra=response_details)
            elif response.status_code >= 400:
                logger.warning("Request error", extra=response_details)
            else:
                logger.info("Request completed", extra=response_details)

            return response

        except Exception as e:
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Log exception
            error_details = {
                **request_details,
                "duration_ms": round(duration_ms, 2),
                "error": str(e),
                "error_type": type(e).__name__,
            }
            logger.exception("Request exception", extra=error_details)
            raise


def setup_logging(log_level: str = "INFO"):
    """Configure structured JSON logging."""

    class JSONFormatter(logging.Formatter):
        """Format logs as JSON."""

        def format(self, record: logging.LogRecord) -> str:
            """Format log record as JSON."""
            log_data = {
                "timestamp": self.formatTime(record, self.datefmt),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
            }

            # Add extra fields
            if hasattr(record, "request_id"):
                log_data["request_id"] = record.request_id
            if hasattr(record, "method"):
                log_data["method"] = record.method
            if hasattr(record, "url"):
                log_data["url"] = record.url
            if hasattr(record, "status_code"):
                log_data["status_code"] = record.status_code
            if hasattr(record, "duration_ms"):
                log_data["duration_ms"] = record.duration_ms
            if hasattr(record, "client_host"):
                log_data["client_host"] = record.client_host

            # Add exception info if present
            if record.exc_info:
                log_data["exception"] = self.formatException(record.exc_info)

            return json.dumps(log_data)

    # Configure root logger
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())

    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        handlers=[handler],
        force=True,
    )

    # Set third-party loggers to WARNING to reduce noise
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
