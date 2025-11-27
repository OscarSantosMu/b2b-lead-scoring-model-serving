# B2B Lead Scoring Model Serving

![CI/CD](https://github.com/OscarSantosMu/b2b-lead-scoring-model-serving/actions/workflows/ci-cd.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.0-009688.svg)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)
![Terraform](https://img.shields.io/badge/terraform-%235835CC.svg?style=flat&logo=terraform&logoColor=white)

Production-ready REST API for real-time B2B lead scoring using XGBoost. Supports local model serving and cloud endpoints (AWS SageMaker, Azure ML).

> **Challenge**: Score 300+ leads/second with <1s latency using a 50-feature XGBoost model.

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| **Real-time Inference** | XGBoost model serving with sub-second latency |
| **Robust API** | FastAPI-based REST API with Pydantic schema validation |
| **Cloud-Native** | Deploy to Azure Container Apps or AWS ECS Fargate |
| **Observability** | Prometheus/Grafana (local) • CloudWatch/Azure Monitor (prod) |
| **DevOps Ready** | Complete CI/CD with GitHub Actions and Terraform IaC |
| **Scalable** | Auto-scaling from 2 to 10+ replicas based on load |

## 📚 Documentation

Comprehensive documentation is available in the [`docs/`](docs/) directory:

| Document | Description |
|----------|-------------|
| [**API Reference**](docs/API.md) | Complete endpoint documentation with examples |
| [**Feature Schema**](docs/FEATURES.md) | All 50 features with validation rules |
| [**Architecture**](docs/ARCHITECTURE.md) | System design, components, data flow |
| [**Deployment**](docs/DEPLOYMENT.md) | CI/CD pipelines, Terraform, rollback procedures |
| [**Monitoring**](docs/MONITORING.md) | Metrics, dashboards, alerting strategy |
| [**Operations**](docs/OPERATIONS.md) | Runbooks, troubleshooting, configuration |
| [**Scripts**](docs/SCRIPTS.md) | Utility scripts reference |
| [**Load Testing**](docs/LOAD_TESTING.md) | Performance testing with Locust |

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- `uv` package manager (recommended) or `pip`

### Option 1: Local Development

```bash
# Clone the repository
git clone https://github.com/OscarSantosMu/b2b-lead-scoring-model-serving.git
cd b2b-lead-scoring-model-serving

# Install dependencies
make install

# Start the development server
make dev
```

Access the API at http://localhost:8000/docs

### Option 2: Docker (API Only)

```bash
# Build and run
docker build -t lead-scoring-api .
docker run -p 8000:8000 -e API_KEYS=demo-api-key-123 lead-scoring-api
```

### Option 3: Docker Compose (Full Stack with Monitoring)

```bash
# Start API + Prometheus + Grafana + AlertManager
docker-compose up --build
```

| Service | URL | Credentials |
|---------|-----|-------------|
| API | http://localhost:8000 | - |
| API Docs | http://localhost:8000/docs | - |
| Prometheus | http://localhost:9090 | - |
| Grafana | http://localhost:3000 | admin/admin |
| AlertManager | http://localhost:9093 | - |

### Quick Test

```bash
# Health check
curl http://localhost:8000/health

# Score a lead
curl -X POST http://localhost:8000/api/v1/score \
  -H "X-API-Key: demo-api-key-123" \
  -H "Content-Type: application/json" \
  -d @docs/examples/sample_request_1.json
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Load Balancer                             │
└─────────────────────────────┬───────────────────────────────────┘
                              │
┌─────────────────────────────┴───────────────────────────────────┐
│                     FastAPI Application                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   Auth      │  │  Validation │  │  XGBoost Model          │  │
│  │   Middleware│  │  (Pydantic) │  │  (Local/SageMaker/Azure)│  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed system design.

## 📊 Monitoring Strategy

| Environment | Monitoring Stack |
|-------------|------------------|
| **Local/Development** | Prometheus + Grafana + AlertManager |
| **Production (Azure)** | Azure Monitor + Application Insights |
| **Production (AWS)** | CloudWatch (Metrics + Logs) + X-Ray |

> **Note**: Prometheus/Grafana are for local development only. Production uses cloud-native tools.

See [MONITORING.md](docs/MONITORING.md) for complete observability setup.

## 🧪 Testing

```bash
# Unit and integration tests
make test

# Load tests (300 users, 1 minute)
make load-test
```

### Performance Targets

| Metric | Target | Description |
|--------|--------|-------------|
| **Latency** | < 1000ms (P95) | 95th percentile response time |
| **Throughput** | 300 RPS | Requests per second |
| **Availability** | 99.9% | Uptime SLA |

## 🔧 Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `API_KEYS` | Comma-separated API keys | `demo-api-key-123` |
| `MODEL_ENDPOINT_PROVIDER` | Model source: `local`, `sagemaker`, `azure` | `local` |
| `LOG_LEVEL` | Logging verbosity | `INFO` |
| `WORKERS` | Uvicorn workers | `4` |

See [OPERATIONS.md](docs/OPERATIONS.md) for complete configuration reference.

## 🏢 Project Structure

```
b2b-lead-scoring-model-serving/
├── .github/             # CI/CD workflows
├── alertmanager/        # Alertmanager configuration
├── api/                 # Application source code
│   ├── app/             # Core business logic (Model, Data Lake)
│   ├── middleware/      # Auth, Logging, Metrics middleware
│   ├── routes/          # API Endpoints (Health, Scoring)
│   └── schemas/         # Pydantic models & validation
├── docs/                # Comprehensive documentation
│   └── examples/        # Request/Response examples
├── grafana/             # Grafana provisioning (Dashboards, Datasources)
├── infra/               # Infrastructure as Code
│   └── config/          # Environment configuration
│   └── terraform/       # Terraform modules
│       ├── modules/     # Cloud-specific modules (AWS, Azure)
│       └── ...
├── models/              # Model artifacts storage
├── prometheus/          # Prometheus configuration & rules
├── reports/             # Load test & security reports (ignored by gitignore)
├── scripts/             # Utility & automation scripts
├── tests/               # Test suite
│   ├── integration/     # Integration tests
│   ├── load/            # Locust load tests
│   └── unit/            # Unit tests
├── docker-compose.yml   # Local development stack
├── Dockerfile           # Container definition
├── Makefile             # Task runner
└── pyproject.toml       # Python dependencies & config
```

## 🛠️ Technology Stack

| Category | Technologies |
|----------|--------------|
| **API** | FastAPI, Uvicorn, Pydantic |
| **ML** | XGBoost, NumPy |
| **Infrastructure** | Terraform, Docker |
| **Cloud** | AWS (ECS, ECR, CloudWatch), Azure (Container Apps, ACR, Monitor) |
| **CI/CD** | GitHub Actions |
| **Monitoring** | Prometheus, Grafana, AlertManager |
| **Testing** | pytest, Locust |
| **Linting** | Ruff, Bandit |

## 🔒 Security

- **Authentication**: API Key-based (`X-API-Key` header)
- **Validation**: Strict Pydantic schema validation
- **Scanning**: Automated security scanning (Bandit, Safety) in CI
- **Secrets**: Managed via Azure Key Vault / AWS Secrets Manager

## 📝 API Quick Reference

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/score` | POST | ✅ | Score a single lead |
| `/api/v1/score/batch` | POST | ✅ | Score up to 100 leads |
| `/api/v1/model/info` | GET | ✅ | Model metadata |
| `/api/v1/model/features` | GET | ✅ | Feature list |
| `/api/v1/model/importance` | GET | ✅ | Feature importance |
| `/health` | GET | ❌ | Health check |
| `/health/ready` | GET | ❌ | Readiness probe |
| `/health/live` | GET | ❌ | Liveness probe |
| `/metrics` | GET | ❌ | Prometheus metrics |

See [API.md](docs/API.md) for complete reference with examples.

## 🚢 Deployment

The service can be deployed to:

- **Azure Container Apps** - Serverless containers with auto-scaling
- **AWS ECS Fargate** - Serverless container orchestration

```bash
# Deploy to Azure (via GitHub Actions)
# Push to main branch triggers automatic deployment

# Manual Terraform deployment
cd infra/terraform
terraform init -backend-config=backend.hcl
terraform apply -var="cloud_provider=azure" -var="environment=prod"
```

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for complete deployment guide.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`make test`)
5. Run linter (`make lint`)
6. Commit and push
7. Open a Pull Request

> This project is for demonstration purposes.

---

**Questions?** Check the [documentation](docs/) or open an issue.