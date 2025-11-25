# Multi-stage Dockerfile for B2B Lead Scoring API (Model Serving Only)
FROM python:3.11-slim AS builder

WORKDIR /app

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

# Install uv for fast package management
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml ./
COPY uv.lock ./
COPY README.md ./

# Install dependencies into system site-packages
# Use uv export to generate requirements from lock file, then install them
# This avoids needing the source code present during the build stage
RUN uv export --frozen --no-dev --format requirements-txt > requirements.txt && \
    uv pip install --system --no-cache -r requirements.txt

# Production stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    WORKERS=4

# Runtime OS deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy Python deps from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY api/ ./api/
COPY models/ ./models/
# Copy entry point
COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Expose API port
EXPOSE 8000

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "api.main:app"]