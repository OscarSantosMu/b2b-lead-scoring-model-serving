# Scripts Documentation

The `scripts/` directory contains utility scripts for development, testing, deployment, and validation.

## Table of Contents

- [Overview](#overview)
- [Development Scripts](#development-scripts)
- [Deployment Scripts](#deployment-scripts)
- [Monitoring Scripts](#monitoring-scripts)
- [CI/CD Scripts](#cicd-scripts)

## Overview

| Script | Purpose | Usage Context |
|--------|---------|---------------|
| `quick_test.sh` | Quick API sanity check | Development |
| `validate-deployment.sh` | Comprehensive deployment validation | CI/CD, Operations |
| `validate-deployment.ps1` | Comprehensive deployment validation (Windows) | CI/CD, Operations |
| `start-monitoring.sh` | Start local Prometheus/Grafana | Development |
| `start-monitoring.ps1` | Start local monitoring (Windows) | Development |
| `entrypoint.sh` | Docker container entrypoint | Docker |
| `setup-github-secrets.sh` | Configure GitHub Actions secrets | Setup |

## Development Scripts

### quick_test.sh

**Purpose:** Sends quick curl requests to verify the API is responding correctly.

**Usage:**
```bash
./scripts/quick_test.sh

# With custom URL and API key
API_URL=http://custom-url:8000 API_KEY=my-key ./scripts/quick_test.sh
```

**What It Does:**
1. Tests `/health` endpoint
2. Tests `/health/ready` endpoint
3. Retrieves model info (`/api/v1/model/info`)
4. Scores a sample lead using `docs/examples/sample_request_1.json`

**Environment Variables:**
| Variable | Default | Description |
|----------|---------|-------------|
| `API_URL` | `http://localhost:8000` | API base URL |
| `API_KEY` | `demo-api-key-123` | API key for authentication |

**Example Output:**
```
Testing B2B Lead Scoring API at http://localhost:8000
==========================================

1. Testing health endpoint...
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00.000000"
}

2. Testing readiness...
{
  "status": "ready",
  "model_version": "1.0.0",
  "timestamp": "2024-01-01T12:00:00.000000"
}

3. Getting model info...
{
  "version": "1.0.0",
  "n_features": 50,
  ...
}

4. Testing lead scoring...
{
  "request_id": "uuid",
  "lead_id": "LEAD-45678",
  "score": {"raw_score": 0.85, "bucket": 4, "tier": "B"}
}

✅ All tests passed!
```

## Deployment Scripts

### validate-deployment.sh

**Purpose:** Comprehensive validation script for deployed environments.

**Usage:**
```bash
# Interactive mode
./scripts/validate-deployment.sh

# With environment variable
API_URL=https://api.example.com ./scripts/validate-deployment.sh
```

**Validation Steps:**

| # | Check | Expected | Purpose |
|---|-------|----------|---------|
| 1 | Root endpoint | 200 OK | Service accessible |
| 2 | Health check | 200 OK | Basic health |
| 3 | Readiness | 200 OK | Model loaded |
| 4 | Liveness | 200 OK | Process alive |
| 5 | Metrics | 200 OK | Monitoring working |
| 6 | API docs | 200 OK | Documentation accessible |
| 7 | Auth check | 401/403 | Security enforced |
| 8 | Model info | 200 OK | Model accessible |

**Requirements:**
- `curl` (required)
- `jq` (optional, for pretty JSON output)

**Example Output:**
```
========================================
  Lead Scoring API - Deployment Check  
========================================

✓ curl is installed
✓ jq is installed

Validating deployment at: https://api.example.com

✓ Root endpoint is accessible (HTTP 200)
✓ Health check passed (HTTP 200)
✓ Readiness check passed (HTTP 200)
✓ Liveness check passed (HTTP 200)
✓ Metrics endpoint is accessible (HTTP 200)
✓ API documentation is accessible at https://api.example.com/docs
✓ Authentication is properly enforced (HTTP 401)
✓ Model info endpoint is accessible

========================================
  Validation Summary
========================================

✓ API is deployed and accessible
✓ Health checks are working
✓ Metrics endpoint is functional
✓ Authentication is enforced
```

### validate-deployment.ps1

**Purpose:** Windows PowerShell version of deployment validation.

**Usage:**
```powershell
# Interactive mode
.\scripts\validate-deployment.ps1

# With environment variable
$env:API_URL="https://api.example.com"; .\scripts\validate-deployment.ps1
```

**Same functionality as `validate-deployment.sh` but for Windows environments.**

### entrypoint.sh

**Purpose:** Docker container entrypoint script.

**Usage:** Internal (called by Docker)

**What It Does:**
1. Initializes environment
2. Performs any startup tasks
3. Launches Uvicorn server with configured settings

**Environment Variables Used:**
| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8000` | Server port |
| `WORKERS` | `4` | Number of Uvicorn workers |
| `LOG_LEVEL` | `INFO` | Logging level |
| `HOST` | `0.0.0.0` | Bind address |

## Monitoring Scripts

### start-monitoring.sh (Linux/Mac)

**Purpose:** Starts the local Prometheus and Grafana monitoring stack.

**Usage:**
```bash
./scripts/start-monitoring.sh
```

**What It Does:**
1. Starts Prometheus container (port 9090)
2. Starts Grafana container (port 3000)
3. Starts AlertManager container (port 9093)
4. Configures networking between containers

**Access After Starting:**
| Service | URL | Credentials |
|---------|-----|-------------|
| Prometheus | http://localhost:9090 | None |
| Grafana | http://localhost:3000 | admin/admin |
| AlertManager | http://localhost:9093 | None |

### start-monitoring.ps1 (Windows)

**Purpose:** Windows PowerShell version of monitoring startup.

**Usage:**
```powershell
.\scripts\start-monitoring.ps1
```

**Same functionality as `start-monitoring.sh` but for Windows environments.**

## CI/CD Scripts

### setup-github-secrets.sh

**Purpose:** Helps configure GitHub Actions secrets for CI/CD.

**Usage:**
```bash
./scripts/setup-github-secrets.sh
```

**Prerequisites:**
- GitHub CLI (`gh`) installed and authenticated
- Repository admin access

**Secrets Configured:**

| Secret | Description |
|--------|-------------|
| `API_KEYS` | Application API keys |
| `AZURE_CLIENT_ID` | Azure service principal |
| `AZURE_TENANT_ID` | Azure tenant ID |
| `AZURE_SUBSCRIPTION_ID` | Azure subscription |
| `TFSTATE_RESOURCE_GROUP` | Terraform state RG |
| `TFSTATE_STORAGE_ACCOUNT` | Terraform state storage |
| `TFSTATE_CONTAINER_NAME` | Terraform state container |
| `AWS_ROLE_ARN` | AWS IAM role for OIDC |
| `AWS_REGION` | AWS region |

**Manual Alternative:**
```bash
# Using GitHub CLI directly
gh secret set API_KEYS -b "key1,key2,key3"
gh secret set AZURE_CLIENT_ID -b "your-client-id"
```

## Makefile Commands

In addition to scripts, the project provides standardized commands via `Makefile`:

```bash
# Development
make install          # Install dependencies
make dev              # Run development server
make test             # Run all tests
make test-unit        # Run unit tests only
make test-integration # Run integration tests

# Code quality
make lint             # Run linters
make format           # Auto-format code
make clean            # Clean temporary files

# Docker
make docker-build     # Build Docker image
make docker-run       # Run container locally
make docker-compose-up    # Start full stack
make docker-compose-down  # Stop full stack

# Load testing
make load-test        # Run Locust load tests
```

## Creating New Scripts

When adding new scripts:

1. **Add to `/scripts` directory**
2. **Make executable:** `chmod +x scripts/new-script.sh`
3. **Include shebang:** `#!/bin/bash`
4. **Add error handling:** `set -e`
5. **Document in this file**

**Script Template:**
```bash
#!/bin/bash
# Description: What this script does
# Usage: ./scripts/script-name.sh [args]

set -e

# Configuration
VAR="${VAR:-default}"

# Functions
function main() {
    echo "Starting..."
    # Script logic
    echo "Done!"
}

# Run
main "$@"
```

## Related Documentation

- [OPERATIONS.md](OPERATIONS.md) - Operational runbooks
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment procedures
- [LOAD_TESTING.md](LOAD_TESTING.md) - Load testing guide