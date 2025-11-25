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
	uv run pytest tests/ -v --cov=api --cov-report=html --cov-report=term

test-unit:
	uv run pytest tests/unit/ -v

test-integration:
	uv run pytest tests/integration/ -v

lint:
	uv run ruff check api/ tests/
	uv run bandit -r api/

format:
	uv run ruff check --fix api/ tests/
	uv run ruff format api/ tests/

clean:
ifeq ($(OS),Windows_NT)
	@powershell -Command "Get-ChildItem -Path . -Recurse -Directory -Filter '__pycache__' | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue"
	@powershell -Command "Get-ChildItem -Path . -Recurse -Filter '*.pyc' | Remove-Item -Force -ErrorAction SilentlyContinue"
	@powershell -Command "Get-ChildItem -Path . -Recurse -Filter '*.pyo' | Remove-Item -Force -ErrorAction SilentlyContinue"
	@powershell -Command "Get-ChildItem -Path . -Recurse -Directory -Filter '*.egg-info' | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue"
	@if exist .pytest_cache rmdir /s /q .pytest_cache
	@if exist htmlcov rmdir /s /q htmlcov
	@if exist .mypy_cache rmdir /s /q .mypy_cache
	@if exist .tox rmdir /s /q .tox
	@if exist .ruff_cache rmdir /s /q .ruff_cache
	@if exist .coverage del /q .coverage
else
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .coverage htmlcov/ .mypy_cache/ .tox/ .ruff_cache/
endif

docker-build:
	docker build -t lead-scoring-api:latest .

docker-run:
	docker run -p 8000:8000 \
		-e API_KEYS=demo-api-key-123 \
		-e HOST=http://127.0.0.1 \
		lead-scoring-api:latest

docker-run-from-public-registry:
	docker run -p 8000:8000 \
		-e HOST=http://127.0.0.1 \
		-e PORT=8000 \
		-e API_KEYS=demo-api-key-123 \
		ghcr.io/oscarsantosmu/b2b-lead-scoring-model-serving:latest

docker-compose-up:
	docker-compose up -d

docker-compose-down:
	docker-compose down

load-test:
	uv run locust -f tests/load/locustfile.py \
		--host=http://localhost:8000 \
		--users=300 \
		--spawn-rate=10 \
		--run-time=1m \
		--headless \
		--html=loadtest-report.html

dev:
	uv run uvicorn api.main:app --reload --port 8000
