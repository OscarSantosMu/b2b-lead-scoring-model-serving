# Monitoring & Observability

Effective monitoring is crucial for maintaining the reliability and performance of the Lead Scoring API. This guide covers the dual-strategy approach: **Prometheus/Grafana for local development** and **Cloud-Native tools for production**.

## Table of Contents

- [Monitoring Strategy Overview](#monitoring-strategy-overview)
- [Metrics Architecture](#metrics-architecture)
- [Local Monitoring (Prometheus & Grafana)](#local-monitoring-prometheus--grafana)
- [Production Monitoring](#production-monitoring)
- [Alerting Configuration](#alerting-configuration)
- [Dashboards](#dashboards)
- [Troubleshooting with Metrics](#troubleshooting-with-metrics)

## Monitoring Strategy Overview

| Environment | Tools | Purpose |
|-------------|-------|---------|
| **Local/Development** | Prometheus + Grafana + AlertManager | Development testing, load testing analysis, local debugging |
| **Production (Azure)** | Azure Monitor + Application Insights + Log Analytics | Production monitoring, distributed tracing, log aggregation |
| **Production (AWS)** | CloudWatch (Metrics + Logs) + X-Ray | Production monitoring, distributed tracing, log aggregation |

> **Important**: Prometheus and Grafana are configured for **local development only**. In production, use the cloud provider's native monitoring tools for better integration, scalability, and reduced operational overhead.

## Metrics Architecture

### Metrics Categories

We collect three types of metrics following the RED methodology:

```
┌─────────────────────────────────────────────────────────────────┐
│                      Metrics Collection                          │
├─────────────────────────────────────────────────────────────────┤
│  Rate (R)        │  Requests per second by endpoint             │
│  Errors (E)      │  Error rate by type and endpoint             │
│  Duration (D)    │  Latency distribution (histograms)           │
├─────────────────────────────────────────────────────────────────┤
│  Model-Specific  │  Prediction scores, tiers, batch sizes       │
│  Resource        │  CPU, Memory, Disk, Network                  │
└─────────────────────────────────────────────────────────────────┘
```

### Application Metrics

Metrics are exposed at `/metrics` in Prometheus format.

#### HTTP Metrics

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `http_requests_total` | Counter | method, endpoint, status | Total HTTP requests |
| `http_request_duration_seconds` | Histogram | method, endpoint | Request latency |
| `http_requests_active` | Gauge | - | Currently active requests |

#### Model Metrics

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `model_predictions_total` | Counter | endpoint_provider, tier | Total predictions by tier |
| `model_prediction_latency_seconds` | Histogram | endpoint_provider | Prediction latency |
| `model_prediction_buckets` | Histogram | endpoint_provider | Score bucket distribution (1-5) |
| `model_prediction_raw_scores` | Histogram | endpoint_provider | Raw score distribution (0-1) |
| `model_prediction_errors_total` | Counter | endpoint_provider, error_type | Prediction errors |
| `model_batch_size` | Histogram | - | Batch prediction sizes |

#### System Metrics (via `/resources` endpoint)

| Metric | Description |
|--------|-------------|
| CPU usage | Per-core and aggregate |
| Memory usage | Total, available, used |
| Disk usage | Total, used, free |
| Network I/O | Bytes and packets |
| Process metrics | Memory, threads, open files |

## Local Monitoring (Prometheus & Grafana)

The local monitoring stack is provided via Docker Compose for development and load testing.

### Starting the Stack

```bash
# Start full stack (API + monitoring)
docker-compose up -d

# Or use the helper script
./scripts/start-monitoring.sh   # Linux/Mac
./scripts/start-monitoring.ps1  # Windows
```

### Access URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| **API** | http://localhost:8000 | - |
| **API Docs** | http://localhost:8000/docs | - |
| **Prometheus** | http://localhost:9090 | - |
| **Grafana** | http://localhost:3000 | admin/admin |
| **AlertManager** | http://localhost:9093 | - |

### Prometheus Configuration

Configuration file: `prometheus/prometheus.yml`

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'lead-scoring-api'
    scrape_interval: 10s
    metrics_path: '/metrics'
    static_configs:
      - targets: ['api:8000']
        labels:
          service: 'lead-scoring-api'
```

### Grafana Dashboards

Pre-configured dashboards are provisioned automatically:

| Dashboard | Description |
|-----------|-------------|
| **Lead Scoring Overview** | Request rates, latency, error rates |
| **Model Performance** | Prediction distribution, tier breakdown |
| **System Resources** | CPU, memory, disk, network |

**Location:** `grafana/provisioning/dashboards/`

### AlertManager Configuration

Alert routing is configured in `alertmanager/alertmanager.yml`:

```yaml
route:
  group_by: ['alertname', 'service']
  receiver: 'default'
  routes:
    - match:
        severity: critical
      receiver: 'critical-alerts'
    - match:
        severity: warning
      receiver: 'warning-alerts'
```

## Production Monitoring

### Azure (Azure Monitor / Application Insights)

In Azure deployments, use the native monitoring stack:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Azure Monitor Stack                           │
├─────────────────────────────────────────────────────────────────┤
│  Application Insights  │  Request tracing, dependency calls     │
│  Container Insights    │  Container CPU, memory, health         │
│  Log Analytics         │  Centralized log queries (KQL)         │
│  Azure Alerts          │  Proactive alerting                    │
│  Azure Dashboards      │  Custom visualization                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Key Azure Monitor Features

| Feature | Use Case |
|---------|----------|
| **Live Metrics** | Real-time performance monitoring |
| **Application Map** | Visualize service dependencies |
| **Failure Analysis** | Automated exception grouping |
| **Performance Profiler** | CPU profiling in production |
| **Smart Detection** | AI-powered anomaly detection |

#### Setting Up Application Insights

Application Insights is automatically configured via Terraform. The connection string is injected as an environment variable:

```bash
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=xxx;IngestionEndpoint=https://xxx.in.applicationinsights.azure.com/
```

#### Sample KQL Queries

**Request latency by endpoint:**
```kql
requests
| where timestamp > ago(1h)
| summarize percentile(duration, 95) by name
| order by percentile_duration_95 desc
```

**Error rate:**
```kql
requests
| where timestamp > ago(1h)
| summarize errors = countif(success == false), total = count()
| project error_rate = todouble(errors) / total * 100
```

### AWS (CloudWatch)

In AWS deployments, use CloudWatch for monitoring:

```
┌─────────────────────────────────────────────────────────────────┐
│                    CloudWatch Stack                              │
├─────────────────────────────────────────────────────────────────┤
│  CloudWatch Metrics    │  Custom and ECS metrics                │
│  CloudWatch Logs       │  Centralized logging                   │
│  X-Ray                 │  Distributed tracing                   │
│  CloudWatch Alarms     │  Threshold-based alerts                │
│  CloudWatch Dashboards │  Custom visualization                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Key CloudWatch Features

| Feature | Use Case |
|---------|----------|
| **Container Insights** | ECS container metrics |
| **Logs Insights** | Log query and analysis |
| **ServiceLens** | End-to-end observability |
| **Contributor Insights** | Identify high-traffic patterns |
| **Anomaly Detection** | ML-based anomaly alerts |

#### Setting Up CloudWatch

CloudWatch is configured automatically via Terraform. Logs are streamed to CloudWatch Logs groups.

#### Sample Log Insights Queries

**P95 latency:**

```sql
fields @timestamp, @message
| filter @message like /latency_ms/
| parse @message /latency_ms[":]\s*(?<latency>\d+\.?\d*)/
| stats percentile(latency, 95) by bin(5m)
```

**Error count by type:**

```sql
fields @timestamp, @message
| filter @message like /ERROR/
| stats count() by bin(1h)
```

## Alerting Configuration

### Alert Rules

Alerts are defined in `prometheus/rules/alerts.yml` for local development. In production, use cloud-native alerting.

#### Performance Alerts

| Alert | Condition | Severity | Action |
|-------|-----------|----------|--------|
| `HighLatency` | P95 > 500ms for 2m | Warning | Check logs, scale up |
| `CriticalLatency` | P95 > 1s for 1m | Critical | Immediate investigation |
| `SlowModelPredictions` | Model P95 > 100ms for 3m | Warning | Check endpoint health |

#### Availability Alerts

| Alert | Condition | Severity | Action |
|-------|-----------|----------|--------|
| `HighErrorRate` | 5xx rate > 5% for 3m | Critical | Check logs, rollback |
| `ServiceDown` | Target down for 1m | Critical | Restart, investigate |
| `HighActiveRequests` | Active > 100 for 2m | Warning | Scale out |

#### Resource Alerts

| Alert | Condition | Severity | Action |
|-------|-----------|----------|--------|
| `HighCPU` | CPU > 80% for 5m | Warning | Scale out |
| `CriticalCPU` | CPU > 95% for 2m | Critical | Immediate scale |
| `HighMemory` | Memory > 80% for 5m | Warning | Check for leaks |
| `CriticalMemory` | Memory > 90% for 2m | Critical | Risk of OOM |

#### ML Model Alerts

| Alert | Condition | Severity | Action |
|-------|-----------|----------|--------|
| `ModelPredictionErrors` | Error rate > 0.01/sec | Critical | Check endpoint |
| `UnbalancedPredictions` | >50% tier A for 10m | Warning | Check for drift |
| `LowConfidencePredictions` | Median confidence < 0.6 | Warning | Investigate data |

### Alert Notification Channels

#### Local (AlertManager)

```yaml
receivers:
  - name: 'critical-alerts'
    email_configs:
      - to: 'oncall@example.com'
    slack_configs:
      - channel: '#alerts-critical'
```

#### Azure

Configure in Azure Monitor Action Groups:
- Email notifications
- SMS alerts
- Azure Functions webhooks
- Logic Apps integration

#### AWS

Configure in CloudWatch Alarm Actions:
- SNS topics
- Lambda functions
- Auto Scaling actions

## Dashboards

### Local Grafana Dashboard

The pre-configured dashboard includes:

**Overview Row:**
- Total requests (gauge)
- Error rate (gauge)
- P95 latency (gauge)
- Active requests (gauge)

**Traffic Row:**
- Requests per second (graph)
- Requests by endpoint (pie)
- Request latency heatmap

**Model Row:**
- Predictions by tier (bar)
- Score distribution (histogram)
- Prediction latency (graph)

**Resources Row:**
- CPU usage (graph)
- Memory usage (graph)
- Network I/O (graph)

### Production Dashboard Recommendations

Create dashboards showing:

1. **Golden Signals**
   - Latency (P50, P95, P99)
   - Error rate
   - Traffic (RPS)
   - Saturation (CPU, Memory)

2. **Business Metrics**
   - Leads scored per hour
   - Tier distribution
   - Batch vs single requests

3. **SLA Tracking**
   - Availability (uptime %)
   - Latency SLA compliance
   - Error budget remaining

## Troubleshooting with Metrics

### High Latency Investigation

```promql
# Check if model or API is slow
histogram_quantile(0.95, 
  sum by (le) (rate(model_prediction_latency_seconds_bucket[5m]))
)

# Compare with overall request latency
histogram_quantile(0.95,
  sum by (le) (rate(http_request_duration_seconds_bucket[5m]))
)
```

### Error Rate Analysis

```promql
# Error rate by endpoint
sum by (endpoint) (rate(http_requests_total{status=~"5.."}[5m]))
/
sum by (endpoint) (rate(http_requests_total[5m]))

# Model prediction errors
sum by (error_type) (rate(model_prediction_errors_total[5m]))
```

### Capacity Planning

```promql
# Current RPS
sum(rate(http_requests_total[1m]))

# Headroom calculation
(300 - sum(rate(http_requests_total[1m]))) / 300 * 100
```

## Related Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [OPERATIONS.md](OPERATIONS.md) - Runbooks
- [DEPLOYMENT.md](DEPLOYMENT.md) - CI/CD setup