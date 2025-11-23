.PHONY: help install test lint format clean docker-build docker-run load-test

help:
	@echo "Available commands:"
	@echo "  install      - Install dependencies"
	@echo "  test         - Run tests"
	@echo "  lint         - Run linters"
	@echo "  format       - Format code"
	@echo "  clean        - Clean temporary files"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run Docker container"
	@echo "  load-test    - Run load test"

install:
	uv pip install -e ".[dev]"

test:
	pytest tests/ -v --cov=api --cov-report=html --cov-report=term

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

lint:
	ruff check api/ tests/
	bandit -r api/

format:
	ruff check --fix api/ tests/
	ruff format api/ tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .coverage htmlcov/ .mypy_cache/ .tox/

docker-build:
	docker build -t lead-scoring-api:latest .

docker-run:
	docker run -p 8000:8000 \
		-e JWT_SECRET_KEY=demo-secret \
		-e API_KEYS=demo-api-key-123 \
		lead-scoring-api:latest

docker-compose-up:
	docker-compose up -d

docker-compose-down:
	docker-compose down

load-test:
	locust -f tests/load/locustfile.py \
		--host=http://localhost:8000 \
		--users=100 \
		--spawn-rate=10 \
		--run-time=1m \
		--headless \
		--html=loadtest-report.html

dev:
	uvicorn api.main:app --reload --port 8000
