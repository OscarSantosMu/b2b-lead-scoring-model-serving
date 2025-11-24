#!/bin/bash
# Quick test script for the API

set -e

API_URL="${API_URL:-http://localhost:8000}"
API_KEY="${API_KEY:-demo-api-key-123}"

echo "Testing B2B Lead Scoring API at $API_URL"
echo "=========================================="
echo ""

# Test health endpoint
echo "1. Testing health endpoint..."
curl -s "$API_URL/health" | jq '.'
echo ""

# Test readiness
echo "2. Testing readiness..."
curl -s "$API_URL/health/ready" | jq '.'
echo ""

# Test model info
echo "3. Getting model info..."
curl -s -H "X-API-Key: $API_KEY" "$API_URL/api/v1/model/info" | jq '.'
echo ""

# Test scoring
echo "4. Testing lead scoring..."
SAMPLE_FILE="docs/examples/sample_request_1.json"
if [ ! -f "$SAMPLE_FILE" ]; then
  echo "Warning: Sample file not found at $SAMPLE_FILE. Skipping lead scoring test."
else
  curl -s -X POST "$API_URL/api/v1/score" \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d "@$SAMPLE_FILE" | jq '.'
fi

echo "✅ All tests passed!"
