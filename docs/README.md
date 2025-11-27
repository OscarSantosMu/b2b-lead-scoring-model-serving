# B2B Lead Scoring API Documentation

Welcome to the documentation for the B2B Lead Scoring API. This service provides real-time scoring capabilities for sales leads using an XGBoost model.

## Documentation Index

### Getting Started

| Document | Description |
|----------|-------------|
| [API Reference](API.md) | Complete API endpoint documentation, authentication, and examples |
| [Features Schema](FEATURES.md) | Detailed documentation of all 50 lead scoring features |

### Architecture & Design

| Document | Description |
|----------|-------------|
| [Architecture](ARCHITECTURE.md) | System design, components, data flow, and infrastructure |

### Deployment & Operations

| Document | Description |
|----------|-------------|
| [Deployment Guide](DEPLOYMENT.md) | CI/CD pipelines, infrastructure provisioning, and rollback procedures |
| [Operations Guide](OPERATIONS.md) | Day-to-day operations, troubleshooting, and runbooks |
| [Scripts Reference](SCRIPTS.md) | Utility scripts for development, testing, and deployment |

### Monitoring & Performance

| Document | Description |
|----------|-------------|
| [Monitoring Guide](MONITORING.md) | Metrics, dashboards, alerting (local Prometheus/Grafana vs cloud-native) |
| [Load Testing Guide](LOAD_TESTING.md) | Performance testing with Locust |

### Examples

| Resource | Description |
|----------|-------------|
| [examples/](examples/) | Sample request/response JSON files |

## Quick Links

### Service Endpoints

| Environment | API URL | Docs |
|-------------|---------|------|
| Local | http://localhost:8000 | http://localhost:8000/docs |
| Local Monitoring | http://localhost:3000 (Grafana) | http://localhost:9090 (Prometheus) |

### Common Commands

```bash
# Start development server
make dev

# Run tests
make test

# Start with Docker (full stack)
docker-compose up --build

# Run load tests
make load-test

# Quick health check
curl http://localhost:8000/health
```

### Key Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `API_KEYS` | Comma-separated API keys | `demo-api-key-123` |
| `MODEL_ENDPOINT_PROVIDER` | Model source | `local` |
| `LOG_LEVEL` | Logging verbosity | `INFO` |

## Monitoring Strategy

| Environment | Tools |
|-------------|-------|
| **Local/Development** | Prometheus + Grafana + AlertManager |
| **Production (Azure)** | Azure Monitor + Application Insights |
| **Production (AWS)** | CloudWatch + X-Ray |

> **Note**: Prometheus and Grafana are for local development only. Production environments use cloud-native monitoring tools.

## Documentation Updates

When updating documentation:

1. Keep examples up-to-date with code changes
2. Update API.md when adding/modifying endpoints
3. Update FEATURES.md when changing the feature schema
4. Update OPERATIONS.md with new runbooks
5. Update DEPLOYMENT.md with infrastructure changes

## Related Resources

- [Main README](../README.md) - Project overview and quick start
- [Makefile](../Makefile) - Available make commands
- [pyproject.toml](../pyproject.toml) - Project dependencies