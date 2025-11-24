# Quick start script for local monitoring stack

$ErrorActionPreference = "Stop"

$ScriptDir = $PSScriptRoot
$ProjectRoot = Split-Path -Parent $ScriptDir

Set-Location $ProjectRoot

Write-Host "🚀 Starting B2B Lead Scoring API with Monitoring Stack..."
Write-Host ""

# Check if docker-compose is available
if (Get-Command "docker-compose" -ErrorAction SilentlyContinue) {
    $ComposeCmd = "docker-compose"
} elseif (Get-Command "docker" -ErrorAction SilentlyContinue) {
    Write-Host "ℹ️  Using 'docker compose' instead of 'docker-compose'"
    $ComposeCmd = "docker compose"
} else {
    Write-Host "❌ Docker is not installed. Please install Docker first."
    exit 1
}

# Start services
Write-Host "📦 Building and starting services..."
Invoke-Expression "$ComposeCmd up -d --build"

Write-Host ""
Write-Host "✅ Services started successfully!"
Write-Host ""
Write-Host "📊 Access URLs:"
Write-Host "   API:          http://localhost:8000"
Write-Host "   API Docs:     http://localhost:8000/docs"
Write-Host "   API Metrics:  http://localhost:8000/metrics"
Write-Host "   Prometheus:   http://localhost:9090"
Write-Host "   AlertManager: http://localhost:9093"
Write-Host "   Grafana:      http://localhost:3000 (admin/admin)"
Write-Host ""
Write-Host "📝 View logs:"
Write-Host "   All:          $ComposeCmd logs -f"
Write-Host "   API:          $ComposeCmd logs -f api"
Write-Host "   Prometheus:   $ComposeCmd logs -f prometheus"
Write-Host "   Grafana:      $ComposeCmd logs -f grafana"
Write-Host ""
Write-Host "🛑 Stop services:"
Write-Host "   $ComposeCmd down"
Write-Host ""
Write-Host "🔍 Check health:"
Write-Host "   curl http://localhost:8000/health"
Write-Host ""
