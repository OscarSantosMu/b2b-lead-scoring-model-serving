# Load Testing Guide

This guide covers performance testing for the B2B Lead Scoring API using **Locust**. The system is designed to handle ~300 requests/second with < 1s latency (P95).

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Test Configuration](#test-configuration)
- [Running Load Tests](#running-load-tests)
- [Interpreting Results](#interpreting-results)
- [Performance Tuning](#performance-tuning)
- [CI/CD Integration](#cicd-integration)

## Prerequisites

- Python 3.11+ installed
- Dependencies installed (`make install`)
- API running locally or remotely
- For remote testing: Network access to target API

```bash
# Install dependencies
make install

# Verify Locust is available
uv run locust --version
```

## Quick Start

```bash
# 1. Start the API
make dev

# 2. Run load test (in another terminal)
make load-test

# Results will be in loadtest-report.html
```

## Test Configuration

### Test File Location

`tests/load/locustfile.py`

### Test Scenarios

The load test simulates realistic user behavior with weighted tasks:

| Task | Weight | Description |
|------|--------|-------------|
| `score_single_lead` | 10 | Score a single lead (most common) |
| `score_batch` | 2 | Batch scoring (5-20 leads) |
| `get_model_info` | 1 | Get model information |
| `health_check` | 1 | Health check endpoint |

### User Behavior

```python
class LeadScoringUser(HttpUser):
    wait_time = between(0.01, 0.1)  # 10-100ms between requests
    
    @task(10)  # 10x more likely than weight=1 tasks
    def score_single_lead(self):
        # POST /api/v1/score with random features
        
    @task(2)
    def score_batch(self):
        # POST /api/v1/score/batch with 5-20 leads
```

### Generated Test Data

Each request uses randomly generated but realistic feature values:

| Category | Features | Value Range |
|----------|----------|-------------|
| Firmographics | Revenue, employees, age | Realistic distributions |
| Engagement | Website visits, email rates | Typical ranges |
| Behavioral | Decision maker, budget | Binary flags |
| Attribution | Source quality, channels | Normalized scores |
| Product | Tier interest, use case | Categorical values |

## Running Load Tests

### Using Makefile (Recommended)

```bash
# Standard load test (300 users, 1 minute)
make load-test
```

This runs:
```bash
locust -f tests/load/locustfile.py \
  --host=http://localhost:8000 \
  --users=300 \
  --spawn-rate=10 \
  --run-time=1m \
  --headless \
  --html=loadtest-report.html
```

### Using Locust Directly

#### Headless Mode (CI/CD)

```bash
# Basic headless test
uv run locust -f tests/load/locustfile.py \
  --host=http://localhost:8000 \
  --users=300 \
  --spawn-rate=10 \
  --run-time=5m \
  --headless

# With HTML report
uv run locust -f tests/load/locustfile.py \
  --host=http://localhost:8000 \
  --users=300 \
  --spawn-rate=10 \
  --run-time=5m \
  --headless \
  --html=reports/load-test-$(date +%Y%m%d).html

# With CSV output
uv run locust -f tests/load/locustfile.py \
  --host=http://localhost:8000 \
  --users=300 \
  --spawn-rate=10 \
  --run-time=5m \
  --headless \
  --csv=reports/load-test
```

#### Web UI Mode (Interactive)

```bash
# Start Locust with web interface
uv run locust -f tests/load/locustfile.py

# Access at http://localhost:8089
# Configure users and spawn rate in the UI
```

### Parameters Explained

| Parameter | Description | Recommended |
|-----------|-------------|-------------|
| `--users` / `-u` | Number of concurrent users | 300 (target RPS) |
| `--spawn-rate` / `-r` | Users to spawn per second | 10-20 |
| `--run-time` | Test duration | 5m for thorough test |
| `--host` | Target URL | API base URL |
| `--headless` | No web UI | Use for CI/CD |
| `--html` | HTML report output | Always generate |
| `--csv` | CSV report prefix | For analysis |

### Testing Remote Environments

```bash
# Test development environment
uv run locust -f tests/load/locustfile.py \
  --host=https://lead-scoring-dev.azurecontainerapps.io \
  --users=100 \
  --spawn-rate=5 \
  --run-time=2m

# Test production (with care!)
uv run locust -f tests/load/locustfile.py \
  --host=https://lead-scoring-prod.azurecontainerapps.io \
  --users=50 \
  --spawn-rate=2 \
  --run-time=1m
```

## Interpreting Results

### Key Metrics

| Metric | Target | Description |
|--------|--------|-------------|
| **RPS** | ~300 | Requests per second sustained |
| **P50 Latency** | < 50ms | Median response time |
| **P95 Latency** | < 1000ms | 95th percentile (SLA) |
| **P99 Latency** | < 2000ms | 99th percentile |
| **Failure Rate** | 0% | Percentage of failed requests |

### Sample Output

```
Type     Name                    # reqs   # fails  Avg   Min   Max   Median  req/s  failures/s
-------|----------------------|--------|---------|-----|-----|-------|------|------|----------
POST     /api/v1/score           28456    0(0.00%) 23    5    523    15     285.5     0.00
POST     /api/v1/score/batch     5691     0(0.00%) 45    12   892    32     56.9      0.00
GET      /api/v1/model/info      2845     0(0.00%) 8     2    156    5      28.5      0.00
GET      /health                 2846     0(0.00%) 3     1    45     2      28.5      0.00
-------|----------------------|--------|---------|-----|-----|-------|------|------|----------
         Aggregated             39838    0(0.00%) 25    1    892    15     398.4     0.00

Response time percentiles (approximated)
Type     Name                    50%    66%    75%    80%    90%    95%    98%    99%   99.9%  99.99%  100%
-------|----------------------|------|------|------|------|------|------|------|------|------|-------|-----
POST     /api/v1/score          15     20     25     28     35     45     78     120    320    523    523
POST     /api/v1/score/batch    32     45     58     68     95     145    280    450    780    892    892
GET      /api/v1/model/info     5      6      8      9      15     22     45     85     140    156    156
GET      /health                2      3      3      4      5      8      15     25     40     45     45
-------|----------------------|------|------|------|------|------|------|------|------|------|-------|-----
         Aggregated             15     22     28     32     45     65     120    180    520    892    892
```

### Reading the HTML Report

The HTML report (`loadtest-report.html`) includes:

1. **Charts**: RPS, response times, and concurrent users over time
2. **Statistics**: Summary table with all metrics
3. **Failures**: Details of any failed requests
4. **Percentiles**: Response time distribution

### Success Criteria

| Criteria | Threshold | Status |
|----------|-----------|--------|
| RPS sustained | ≥ 300 | ✅ PASS / ❌ FAIL |
| P95 latency | < 1000ms | ✅ PASS / ❌ FAIL |
| Error rate | 0% | ✅ PASS / ❌ FAIL |
| Consistent performance | No degradation over time | ✅ PASS / ❌ FAIL |

## Performance Tuning

### If Latency is High

1. **Check CPU usage**
   ```bash
   curl http://localhost:8000/resources | jq '.cpu'
   ```
   - If > 80%: Scale out or add workers

2. **Check memory**
   ```bash
   curl http://localhost:8000/resources | jq '.memory'
   ```
   - If > 80%: Increase memory allocation

3. **Check model latency**
   ```bash
   curl http://localhost:8000/metrics | grep model_prediction_latency
   ```
   - If model is slow: Consider caching or optimization

### If RPS is Low

1. **Increase workers**
   ```bash
   WORKERS=8 make docker-run
   ```

2. **Scale out replicas** (production)
   ```bash
   # Azure
   az containerapp update --min-replicas 5

   # AWS
   aws ecs update-service --desired-count 5
   ```

3. **Check for bottlenecks**
   - Database connections
   - Network latency
   - Model endpoint (if using cloud)

### Optimization Checklist

- [ ] Uvicorn workers = CPU cores
- [ ] Model loaded in memory (not reloading)
- [ ] Connection pooling enabled
- [ ] Async operations where possible
- [ ] Response serialization optimized
- [ ] No N+1 queries or loops

## CI/CD Integration

### GitHub Actions Example

```yaml
- name: Run Load Tests
  run: |
    uv run locust -f tests/load/locustfile.py \
      --host=http://localhost:8000 \
      --users=100 \
      --spawn-rate=10 \
      --run-time=2m \
      --headless \
      --html=loadtest-report.html \
      --csv=loadtest
    
    # Check if P95 is under threshold
    P95=$(tail -1 loadtest_stats.csv | cut -d',' -f10)
    if [ "$P95" -gt 1000 ]; then
      echo "P95 latency ($P95 ms) exceeds threshold (1000 ms)"
      exit 1
    fi

- name: Upload Load Test Report
  uses: actions/upload-artifact@v4
  with:
    name: load-test-report
    path: loadtest-report.html
```

### Performance Regression Detection

```bash
# Compare with baseline
CURRENT_P95=$(tail -1 loadtest_stats.csv | cut -d',' -f10)
BASELINE_P95=50

REGRESSION=$(echo "scale=2; ($CURRENT_P95 - $BASELINE_P95) / $BASELINE_P95 * 100" | bc)

if (( $(echo "$REGRESSION > 20" | bc -l) )); then
  echo "Performance regression detected: ${REGRESSION}% slower"
  exit 1
fi
```

## Recent Benchmarks (stub model)

| Date | RPS | P95 Latency | Result |
|------|-----|-------------|--------|
| 2023-11-26 | 350 | 45ms | PASS |
| 2023-11-25 | 100 | 12ms | PASS |

*Add your benchmark results here after running load tests.*

## Related Documentation

- [MONITORING.md](MONITORING.md) - Metrics during load tests
- [OPERATIONS.md](OPERATIONS.md) - Scaling procedures
- [ARCHITECTURE.md](ARCHITECTURE.md) - Performance design

