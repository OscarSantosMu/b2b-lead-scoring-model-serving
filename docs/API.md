# API Documentation

The B2B Lead Scoring API provides real-time scoring capabilities for sales leads using an XGBoost model. This document provides a complete reference for all available endpoints.

## Table of Contents

- [Base URL](#base-url)
- [Authentication](#authentication)
- [Endpoints](#endpoints)
  - [Root Endpoint](#root-endpoint)
  - [Health Checks](#health-checks)
  - [Lead Scoring](#lead-scoring)
  - [Model Information](#model-information)
  - [Monitoring](#monitoring)
- [Error Handling](#error-handling)
- [Examples](#examples)

## Base URL

| Environment | URL |
|-------------|-----|
| Local Development | `http://localhost:8000` |
| Production (Azure) | `https://<app-name>.azurecontainerapps.io` |
| Production (AWS) | `https://<alb-name>.<region>.elb.amazonaws.com` |

*Note: Replace `<app-name>`, `<alb-name>`, and `<region>` with your actual deployment values.*

## Authentication

The API uses API Key authentication. Include the `X-API-Key` header in all requests to protected endpoints.

```http
X-API-Key: <your-api-key>
```

**Protected Endpoints:**
- `POST /api/v1/score`
- `POST /api/v1/score/batch`
- `GET /api/v1/model/info`
- `GET /api/v1/model/features`
- `GET /api/v1/model/importance`

**Public Endpoints (no authentication required):**
- `GET /` (root)
- `GET /health`
- `GET /health/ready`
- `GET /health/live`
- `GET /status`
- `GET /resources`
- `GET /metrics`
- `GET /docs` (Swagger UI)
- `GET /redoc` (ReDoc)

**Error Response (401 Unauthorized):**
```json
{
  "detail": "Invalid or missing API key"
}
```

## Endpoints

### Root Endpoint

#### GET /

Service information and navigation links.

**Response (200 OK):**
```json
{
  "service": "B2B Lead Scoring API",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/health"
}
```

---

### Health Checks

#### GET /health

Simple health check endpoint for basic availability monitoring.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

#### GET /health/ready

Readiness check - verifies the model is loaded and service is ready to accept requests. Used by Kubernetes/container orchestrators for readiness probes.

**Response (200 OK):**
```json
{
  "status": "ready",
  "model_version": "1.0.0",
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

**Response (503 Service Unavailable):**
```
Model not loaded
```

#### GET /health/live

Liveness check - verifies the service process is alive. Used by Kubernetes/container orchestrators for liveness probes.

**Response (200 OK):**
```json
{
  "status": "alive",
  "uptime_seconds": 3600.5,
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

#### GET /status

Detailed service status including model information and environment details.

**Response (200 OK):**
```json
{
  "status": "operational",
  "uptime_seconds": 3600.5,
  "model": {
    "version": "1.0.0",
    "loaded": true,
    "n_features": 50,
    "endpoint_provider": "local"
  },
  "environment": {
    "python_version": "3.11.0",
    "hostname": "api-server-1"
  },
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

#### GET /resources

Real-time system resource usage metrics including CPU, memory, disk, and network.

**Response (200 OK):**
```json
{
  "status": "ok",
  "cpu": {
    "usage_percent": 25.5,
    "count": 4,
    "per_cpu": [30.0, 20.0, 25.0, 27.0]
  },
  "memory": {
    "total_mb": 8192.0,
    "available_mb": 4096.0,
    "used_mb": 4096.0,
    "usage_percent": 50.0
  },
  "disk": {
    "total_gb": 100.0,
    "used_gb": 40.0,
    "free_gb": 60.0,
    "usage_percent": 40.0
  },
  "process": {
    "memory_mb": 256.0,
    "cpu_percent": 5.0,
    "threads": 8,
    "open_files": 12
  },
  "network": {
    "bytes_sent_mb": 100.5,
    "bytes_recv_mb": 250.3,
    "packets_sent": 50000,
    "packets_recv": 75000
  },
  "alerts": {
    "high_cpu": false,
    "high_memory": false,
    "low_disk": false
  },
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

---

### Lead Scoring

#### POST /api/v1/score

Calculate the conversion probability score for a single lead based on provided features.

**Headers:**
- `X-API-Key: <your-api-key>` (required)
- `Content-Type: application/json` (required)

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `include_details` | boolean | false | Include timing, tier definitions, and API version |

**Request Body:**

See [FEATURES.md](FEATURES.md) for complete feature definitions.

```json
{
  "lead_id": "LEAD-12345",
  "features": {
    "company_revenue": 5000000.0,
    "company_employee_count": 50,
    "company_age_years": 5.5,
    "company_funding_total": 2000000.0,
    "company_growth_rate": 0.35,
    "industry_tech_score": 0.8,
    "geographic_tier": 1,
    "company_public_status": 0,
    "parent_company_exists": 1,
    "subsidiary_count": 2,
    "website_visits_30d": 45,
    "page_views_30d": 120,
    "avg_session_duration_sec": 180.5,
    "bounce_rate": 0.35,
    "pricing_page_visits": 5,
    "demo_page_visits": 3,
    "documentation_views": 10,
    "email_open_rate": 0.65,
    "email_click_rate": 0.25,
    "emails_received": 8,
    "whitepaper_downloads": 2,
    "webinar_attendance": 1,
    "social_media_engagement": 15,
    "customer_success_interactions": 2,
    "support_ticket_count": 0,
    "days_since_first_touch": 30.0,
    "days_since_last_touch": 2.0,
    "total_touchpoints": 25,
    "multi_channel_engagement": 1,
    "decision_maker_contacted": 1,
    "champion_identified": 1,
    "budget_confirmed": 0,
    "timeline_confirmed": 1,
    "competitor_evaluation": 1,
    "technical_evaluation_started": 1,
    "contract_reviewed": 0,
    "security_questionnaire_completed": 0,
    "roi_calculator_used": 1,
    "custom_demo_requested": 1,
    "integration_questions_asked": 3,
    "lead_source_quality": 0.75,
    "attribution_touchpoints": 5,
    "paid_channel_source": 1,
    "referral_source": 0,
    "event_source": 0,
    "product_tier_interest": 2,
    "feature_requests_count": 2,
    "use_case_alignment": 0.85,
    "integration_requirements": 3,
    "deployment_preference": 0
  }
}
```

**Response (200 OK):**

```json
{
  "request_id": "f7f46f8d-5b72-4d3d-9a5f-9a5b9800c123",
  "model": {
    "name": "xgboost_lead_score_v100",
    "version": "1.0.0"
  },
  "lead_id": "LEAD-12345",
  "score": {
    "raw_score": 0.82,
    "bucket": 4,
    "tier": "B"
  }
}
```

**Response with `include_details=true`:**

```json
{
  "request_id": "f7f46f8d-5b72-4d3d-9a5f-9a5b9800c123",
  "model": {
    "name": "xgboost_lead_score_v100",
    "version": "1.0.0"
  },
  "lead_id": "LEAD-12345",
  "score": {
    "raw_score": 0.82,
    "bucket": 4,
    "tier": "B",
    "ranking": {
      "tier_definition": {
        "A": "Highest conversion likelihood (bucket 5)",
        "B": "High conversion likelihood (bucket 4)",
        "C": "Medium conversion likelihood (bucket 3)",
        "D": "Low conversion likelihood (bucket 2)",
        "E": "Lowest conversion likelihood (bucket 1)"
      }
    }
  },
  "timing": {
    "latency_ms": 12.5
  },
  "api_version": "1.0.0"
}
```

#### POST /api/v1/score/batch

Score multiple leads in a single request. Maximum 100 leads per batch.

**Headers:**
- `X-API-Key: <your-api-key>` (required)
- `Content-Type: application/json` (required)

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `include_details` | boolean | false | Include timing and tier definitions |

**Request Body:**

Array of scoring requests (max 100):

```json
[
  {
    "lead_id": "LEAD-001",
    "features": { ... }
  },
  {
    "lead_id": "LEAD-002",
    "features": { ... }
  }
]
```

**Response (200 OK):**

Array of scoring responses:

```json
[
  {
    "request_id": "uuid-1",
    "model": { "name": "xgboost_lead_score_v100", "version": "1.0.0" },
    "lead_id": "LEAD-001",
    "score": { "raw_score": 0.82, "bucket": 4, "tier": "B" }
  },
  {
    "request_id": "uuid-2",
    "model": { "name": "xgboost_lead_score_v100", "version": "1.0.0" },
    "lead_id": "LEAD-002",
    "score": { "raw_score": 0.45, "bucket": 3, "tier": "C" }
  }
]
```

**Error (400 Bad Request):**
```json
{
  "detail": "Maximum 100 leads per batch request"
}
```

---

### Model Information

#### GET /api/v1/model/info

Get model version, features, and metadata.

**Headers:**
- `X-API-Key: <your-api-key>` (required)

**Response (200 OK):**
```json
{
  "version": "1.0.0",
  "n_features": 50,
  "features": ["company_revenue", "company_employee_count", ...],
  "metadata": {
    "version": "1.0.0",
    "features": [...],
    "n_features": 50,
    "model_type": "xgboost",
    "training_date": "2024-01-01",
    "is_stub": false
  }
}
```

#### GET /api/v1/model/features

Get the list of 50 features used by the model.

**Headers:**
- `X-API-Key: <your-api-key>` (required)

**Response (200 OK):**
```json
{
  "features": [
    "company_revenue",
    "company_employee_count",
    "company_age_years",
    ...
  ],
  "count": 50
}
```

#### GET /api/v1/model/importance

Get feature importance scores from the model, sorted by importance.

**Headers:**
- `X-API-Key: <your-api-key>` (required)

**Response (200 OK):**
```json
{
  "importance": {
    "decision_maker_contacted": 125.5,
    "budget_confirmed": 98.3,
    "pricing_page_visits": 87.2,
    ...
  },
  "top_10": [
    ["decision_maker_contacted", 125.5],
    ["budget_confirmed", 98.3],
    ...
  ]
}
```

---

### Monitoring

#### GET /metrics

Prometheus metrics endpoint for monitoring. Returns metrics in Prometheus text format.

**Response (200 OK):**
```
# HELP model_predictions_total Total predictions made
# TYPE model_predictions_total counter
model_predictions_total{endpoint_provider="local",tier="A"} 1234
model_predictions_total{endpoint_provider="local",tier="B"} 2345

# HELP model_prediction_latency_seconds Prediction latency
# TYPE model_prediction_latency_seconds histogram
model_prediction_latency_seconds_bucket{endpoint_provider="local",le="0.001"} 100
model_prediction_latency_seconds_bucket{endpoint_provider="local",le="0.005"} 500
...

# HELP model_prediction_errors_total Total prediction errors
# TYPE model_prediction_errors_total counter
model_prediction_errors_total{endpoint_provider="local",error_type="ValueError"} 5

# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="POST",endpoint="/api/v1/score",status="200"} 10000
```

**Available Metrics:**

| Metric | Type | Description |
|--------|------|-------------|
| `model_predictions_total` | Counter | Total predictions by tier and endpoint |
| `model_prediction_latency_seconds` | Histogram | Prediction latency distribution |
| `model_prediction_buckets` | Histogram | Distribution of prediction buckets (1-5) |
| `model_prediction_raw_scores` | Histogram | Distribution of raw scores (0-1) |
| `model_prediction_errors_total` | Counter | Prediction errors by type |
| `model_batch_size` | Histogram | Batch prediction sizes |
| `http_requests_total` | Counter | Total HTTP requests by method/endpoint/status |
| `http_request_duration_seconds` | Histogram | Request latency distribution |

---

## Error Handling

### HTTP Status Codes

| Status | Description |
|--------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid input data |
| 401 | Unauthorized - Missing or invalid API key |
| 422 | Unprocessable Entity - Validation failed |
| 500 | Internal Server Error |
| 503 | Service Unavailable - Model not loaded |

### Error Response Format

**Validation Error (422):**
```json
{
  "detail": [
    {
      "loc": ["body", "features", "company_revenue"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Authentication Error (401):**
```json
{
  "detail": "Invalid or missing API key"
}
```

**Internal Error (500):**
```json
{
  "detail": "Internal server error",
  "type": "ExceptionType"
}
```

---

## Examples

### Python

```python
import requests

API_URL = "http://localhost:8000"
API_KEY = "demo-api-key-123"

# Score a single lead
response = requests.post(
    f"{API_URL}/api/v1/score",
    headers={
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    },
    json={
        "lead_id": "LEAD-12345",
        "features": {
            "company_revenue": 5000000.0,
            "company_employee_count": 50,
            # ... all 50 features
        }
    }
)

result = response.json()
print(f"Lead: {result['lead_id']}")
print(f"Score: {result['score']['raw_score']}")
print(f"Tier: {result['score']['tier']}")
```

### cURL

```bash
# Score a single lead
curl -X POST "http://localhost:8000/api/v1/score" \
  -H "X-API-Key: demo-api-key-123" \
  -H "Content-Type: application/json" \
  -d @docs/examples/sample_request_1.json

# Get model info
curl -H "X-API-Key: demo-api-key-123" \
  "http://localhost:8000/api/v1/model/info"

# Health check
curl "http://localhost:8000/health"
```

### JavaScript/Node.js

```javascript
const response = await fetch('http://localhost:8000/api/v1/score', {
  method: 'POST',
  headers: {
    'X-API-Key': 'demo-api-key-123',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    lead_id: 'LEAD-12345',
    features: {
      company_revenue: 5000000.0,
      // ... all 50 features
    }
  })
});

const result = await response.json();
console.log(`Tier: ${result.score.tier}`);
```

---

## Related Documentation

- [FEATURES.md](FEATURES.md) - Complete feature schema documentation
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture overview
- [MONITORING.md](MONITORING.md) - Monitoring and observability guide