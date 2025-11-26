"""
FastAPI application for B2B lead scoring.
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.middleware.logging_middleware import RequestLoggingMiddleware, setup_logging
from api.middleware.metrics import MetricsMiddleware
from api.routes import health, scoring

# Setup logging
setup_logging(os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    # Startup
    logger.info("Starting B2B Lead Scoring API")

    # Initialize model
    from api.app.model import get_model

    model = get_model()
    logger.info(f"Model initialized: version {model.model_version}")

    yield

    # Shutdown
    logger.info("Shutting down B2B Lead Scoring API")


# Create FastAPI app
app = FastAPI(
    title="B2B Lead Scoring API",
    description="Real-time B2B lead scoring with XGBoost and 50-feature model",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add middleware (order matters - metrics first, then logging)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(MetricsMiddleware)

# Include routers
app.include_router(health.router)
app.include_router(scoring.router)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.exception(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "type": type(exc).__name__,
        },
    )


@app.get("/", tags=["root"])
async def root():
    """Root endpoint."""
    return {
        "service": "B2B Lead Scoring API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("ENV", "production") != "production",
    )
