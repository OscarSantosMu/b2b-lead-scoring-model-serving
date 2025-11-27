# Operations Guide

This guide covers the day-to-day operations, troubleshooting, and maintenance of the Lead Scoring Service.

## Table of Contents

- [Quick Reference](#quick-reference)
- [Common Tasks](#common-tasks)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Runbooks](#runbooks)
- [Maintenance Procedures](#maintenance-procedures)

## Quick Reference

### Service URLs

| Environment | API URL | Monitoring |
|-------------|---------|------------|
| Local | http://localhost:8000 | http://localhost:3000 (Grafana) |
| Dev (Azure) | `https://<app-name>.azurecontainerapps.io` | Azure Portal |
| Prod (Azure) | `https://<app-name>.azurecontainerapps.io` | Azure Portal |
| Dev (AWS) | `https://<alb-name>.<region>.elb.amazonaws.com` | CloudWatch |
| Prod (AWS) | `https://<alb-name>.<region>.elb.amazonaws.com` | CloudWatch |

*Note: Replace `<app-name>`, `<alb-name>`, and `<region>` with your actual deployment values.*

### Key Contacts

Define on-call rotation and escalation paths in your organization's runbook.

## Common Tasks

### Development Commands

We use a `Makefile` to standardize common tasks.

```bash
# Show all available commands
make help

# Install dependencies
make install

# Run development server
make dev

# Run tests
make test            # All tests
make test-unit       # Unit tests only
make test-integration # Integration tests only

# Code quality
make lint            # Run linters
make format          # Auto-format code

# Docker operations
make docker-build    # Build image
make docker-run      # Run container
make docker-compose-up   # Start full stack
make docker-compose-down # Stop full stack

# Load testing
make load-test       # Run load tests
```

### Quick Health Check

```bash
# Check if service is healthy
curl http://localhost:8000/health

# Check readiness (model loaded)
curl http://localhost:8000/health/ready

# Check detailed status
curl http://localhost:8000/status

# Check resource usage
curl http://localhost:8000/resources
```

### Score a Lead (Quick Test)

```bash
# Using the quick test script
./scripts/quick_test.sh

# Or manually
curl -X POST "http://localhost:8000/api/v1/score" \
  -H "X-API-Key: demo-api-key-123" \
  -H "Content-Type: application/json" \
  -d @docs/examples/sample_request_1.json
```

### View Logs

**Local (Docker):**
```bash
docker-compose logs -f api
```

**Azure:**
```bash
az monitor log-analytics query \
  --workspace <workspace-id> \
  --analytics-query "ContainerAppConsoleLogs_CL | where ContainerName_s == 'api' | take 100"
```

**AWS:**
```bash
aws logs tail /ecs/lead-scoring --follow
```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ENV` | Environment name | `production` | No |
| `LOG_LEVEL` | Logging verbosity | `INFO` | No |
| `API_KEYS` | Comma-separated API keys | `demo-api-key-123` | Yes |
| `PORT` | Server port | `8000` | No |
| `WORKERS` | Uvicorn workers | `4` | No |
| `HOST` | Server host | `0.0.0.0` | No |
| `CORS_ORIGINS` | Allowed CORS origins | `*` | No |
| `MODEL_ENDPOINT_PROVIDER` | Model source | `local` | No |
| `MODEL_PATH` | Local model path | `models/model.json` | No |

### Model Endpoint Configuration

**Local Model (Default):**
```bash
MODEL_ENDPOINT_PROVIDER=local
MODEL_PATH=models/model.json
MODEL_VERSION=1.0.0
```

**AWS SageMaker:**
```bash
MODEL_ENDPOINT_PROVIDER=sagemaker
SAGEMAKER_ENDPOINT_NAME=lead-scoring-endpoint
AWS_REGION=us-east-1
# AWS credentials configured via IAM role or environment
```

**Azure ML:**
```bash
MODEL_ENDPOINT_PROVIDER=azure
AZURE_ML_ENDPOINT_URL=https://endpoint.azureml.net/score
AZURE_ML_API_KEY=your-api-key
# AZURE_ML_DEPLOYMENT_NAME=blue  # Optional
```

### Scaling Configuration

Configuration is environment-specific in `infra/config/environments.json`:

```json
{
  "dev": {
    "log_level": "DEBUG",
    "min_replicas": 2,
    "max_replicas": 5
  },
  "prod": {
    "log_level": "INFO",
    "min_replicas": 3,
    "max_replicas": 10
  }
}
```

## Troubleshooting

### Common Issues

#### 1. High Latency

**Symptoms:** P95 latency > 1000ms, slow responses

**Diagnosis:**
```bash
# Check CPU/Memory usage
curl http://localhost:8000/resources | jq '.alerts'

# Check if model endpoint is slow
curl http://localhost:8000/metrics | grep model_prediction_latency
```

**Possible Causes & Actions:**

| Cause | Check | Action |
|-------|-------|--------|
| High CPU | `resources.cpu.usage_percent > 80` | Scale out instances |
| Model endpoint slow | `model_prediction_latency > 100ms` | Check cloud endpoint health |
| Memory pressure | `resources.memory.usage_percent > 80` | Increase memory, check leaks |
| Large batch sizes | `model_batch_size` histogram | Reduce batch size limits |

#### 2. 500 Internal Server Errors

**Symptoms:** API returning 500 errors

**Diagnosis:**
```bash
# Check application logs
docker-compose logs api | grep ERROR

# Check error metrics
curl http://localhost:8000/metrics | grep model_prediction_errors
```

**Possible Causes & Actions:**

| Cause | Symptoms | Action |
|-------|----------|--------|
| Model not loaded | Readiness check fails | Restart container, check model path |
| Feature validation | ValidationError in logs | Check request format |
| Cloud endpoint down | EndpointError in logs | Check SageMaker/Azure ML status |
| Memory exhaustion | OOM in container logs | Increase memory, reduce batch size |

#### 3. 401 Unauthorized Errors

**Symptoms:** All requests returning 401

**Diagnosis:**
```bash
# Check if API key is being sent
curl -v http://localhost:8000/api/v1/model/info \
  -H "X-API-Key: your-key"
```

**Possible Causes & Actions:**

| Cause | Check | Action |
|-------|-------|--------|
| Missing header | Request doesn't have `X-API-Key` | Add header |
| Invalid key | Key not in `API_KEYS` env | Update environment variable |
| Key expired | Check key management | Generate new key |

#### 4. Container Won't Start

**Symptoms:** Container crashes on startup

**Diagnosis:**
```bash
# Check container logs
docker logs lead-scoring-api

# Check health endpoint
curl http://localhost:8000/health
```

**Possible Causes & Actions:**

| Cause | Symptoms | Action |
|-------|----------|--------|
| Port conflict | "Address in use" | Change port or stop conflicting service |
| Model file missing | FileNotFoundError | Ensure model exists in image |
| Invalid config | Environment parse error | Fix environment variables |
| Dependency issue | ImportError | Rebuild image |

### Performance Troubleshooting

#### Latency Analysis

```bash
# Get latency breakdown from metrics
curl http://localhost:8000/metrics | grep -E "(http_request_duration|model_prediction_latency)"

# Calculate overhead
# Total Latency - Model Latency = API Overhead
```

#### Memory Investigation

```bash
# Check process memory
curl http://localhost:8000/resources | jq '.process.memory_mb'

# Check for memory growth over time (local)
watch -n 10 'curl -s http://localhost:8000/resources | jq ".process.memory_mb"'
```

## Runbooks

### Runbook: High Error Rate

**Trigger:** Alert `HighErrorRate` fires (error rate > 5% for 3min)

**Steps:**

1. **Assess Impact**
   ```bash
   # Check current error rate
   curl http://localhost:8000/metrics | grep 'http_requests_total{.*status="5'
   ```

2. **Check Recent Changes**
   - Review recent deployments
   - Check for configuration changes

3. **Analyze Errors**
   ```bash
   # Get recent error logs
   docker-compose logs api 2>&1 | grep ERROR | tail -50
   ```

4. **Mitigate**
   - If deployment-related: Rollback
   - If resource-related: Scale out
   - If external service: Enable fallback

5. **Verify Recovery**
   ```bash
   # Confirm error rate decreasing
   curl http://localhost:8000/metrics | grep model_prediction_errors
   ```

### Runbook: Service Down

**Trigger:** Alert `ServiceDown` fires (health check fails)

**Steps:**

1. **Confirm Outage**
   ```bash
   curl -f http://localhost:8000/health || echo "CONFIRMED DOWN"
   ```

2. **Check Container Status**
   ```bash
   # Local
   docker ps -a | grep lead-scoring

   # Azure
   az containerapp revision list --name lead-scoring-api -g rg-name

   # AWS
   aws ecs describe-services --cluster lead-scoring --services lead-scoring-service
   ```

3. **Check Logs for Cause**
   ```bash
   docker logs --tail 100 lead-scoring-api
   ```

4. **Restart Service**
   ```bash
   # Local
   docker-compose restart api

   # Azure
   az containerapp revision restart ...

   # AWS
   aws ecs update-service --force-new-deployment ...
   ```

5. **Verify Recovery**
   ```bash
   curl http://localhost:8000/health/ready
   ```

### Runbook: Model Endpoint Failure

**Trigger:** `model_prediction_errors` increasing

**Steps:**

1. **Identify Endpoint Provider**
   ```bash
   curl http://localhost:8000/status | jq '.model.endpoint_provider'
   ```

2. **Check Endpoint Health**
   ```bash
   # SageMaker
   aws sagemaker describe-endpoint --endpoint-name lead-scoring-endpoint

   # Azure ML
   az ml online-endpoint show --name lead-scoring-endpoint
   ```

3. **Fall Back to Local** (if configured)
   ```bash
   # Update environment
   MODEL_ENDPOINT_PROVIDER=local
   # Restart service
   ```

4. **Investigate Root Cause**
   - Check cloud provider console
   - Review endpoint logs
   - Verify credentials

## Maintenance Procedures

### Updating API Keys

1. Generate new keys
2. Update `API_KEYS` environment variable
3. Restart service (or update secret in cloud)
4. Distribute new keys to clients
5. Remove old keys after transition period

### Updating the Model

1. Upload new model to storage
2. Update `MODEL_PATH` or endpoint configuration
3. Deploy new container version
4. Validate predictions with test data
5. Monitor for drift or performance changes

### Scaling Operations

**Manual Scaling:**
```bash
# Azure
az containerapp update --name lead-scoring-api --min-replicas 5 --max-replicas 20

# AWS
aws ecs update-service --desired-count 5 ...
```

**Verify Scaling:**
```bash
# Check replica count
az containerapp revision list --name lead-scoring-api | jq '.[0].properties.replicas'
```

### Log Rotation

Logs are automatically rotated by the container platform. For long-term storage:

- **Azure:** Configure Log Analytics retention
- **AWS:** Configure CloudWatch Logs retention
- **Local:** Docker handles log rotation

## Related Documentation

- [API.md](API.md) - API reference
- [MONITORING.md](MONITORING.md) - Metrics and dashboards
- [DEPLOYMENT.md](DEPLOYMENT.md) - CI/CD and infrastructure
- [SCRIPTS.md](SCRIPTS.md) - Utility scripts