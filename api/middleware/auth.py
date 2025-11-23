"""
Authentication middleware for API.
Simple API key authentication for production model serving.
"""

import logging
import os

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

logger = logging.getLogger(__name__)

# API Keys (in production, store in secrets manager)
VALID_API_KEYS = set(os.getenv("API_KEYS", "demo-api-key-123,test-key-456").split(","))

# Security scheme
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str | None = Security(api_key_header)) -> str:
    """Verify API key authentication."""
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    if api_key not in VALID_API_KEYS:
        logger.warning(f"Invalid API key attempted: {api_key[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    return api_key


async def get_current_user(api_key: str = Security(verify_api_key)) -> dict:
    """
    Get current authenticated user from API key.
    Returns client information.
    """
    return {
        "auth_type": "api_key",
        "client_id": api_key[:10],
        "authenticated": True,
    }
