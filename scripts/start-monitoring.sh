#!/bin/bash
# Quick start script for local monitoring stack

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "🚀 Starting B2B Lead Scoring API with Monitoring Stack..."
echo ""

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed. Please install Docker first."
        exit 1
    fi
    echo "ℹ️  Using 'docker compose' instead of 'docker-compose'"
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

# Start services
echo "📦 Building and starting services..."
$COMPOSE_CMD up -d --build

echo ""
echo "✅ Services started successfully!"
echo ""
echo "📊 Access URLs:"
echo "   API:          http://localhost:8000"
echo "   API Docs:     http://localhost:8000/docs"
echo "   API Metrics:  http://localhost:8000/metrics"
echo "   Prometheus:   http://localhost:9090"
echo "   AlertManager: http://localhost:9093"
echo "   Grafana:      http://localhost:3000 (admin/admin)"
echo ""
echo "📝 View logs:"
echo "   All:          $COMPOSE_CMD logs -f"
echo "   API:          $COMPOSE_CMD logs -f api"
echo "   Prometheus:   $COMPOSE_CMD logs -f prometheus"
echo "   Grafana:      $COMPOSE_CMD logs -f grafana"
echo ""
echo "🛑 Stop services:"
echo "   $COMPOSE_CMD down"
echo ""
echo "🔍 Check health:"
echo "   curl http://localhost:8000/health"
echo ""
