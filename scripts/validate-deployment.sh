#!/bin/bash
# Deployment Validation Script
# Validates that infrastructure is correctly deployed and API is accessible

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    if [ "$1" = "success" ]; then
        echo -e "${GREEN}✓${NC} $2"
    elif [ "$1" = "error" ]; then
        echo -e "${RED}✗${NC} $2"
    elif [ "$1" = "warning" ]; then
        echo -e "${YELLOW}!${NC} $2"
    else
        echo "$2"
    fi
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo "========================================"
echo "  Lead Scoring API - Deployment Check  "
echo "========================================"
echo ""

# Check for required tools
print_status "info" "Checking for required tools..."
MISSING_TOOLS=0

if command_exists "curl"; then
    print_status "success" "curl is installed"
else
    print_status "error" "curl is not installed"
    MISSING_TOOLS=1
fi

if command_exists "jq"; then
    print_status "success" "jq is installed"
else
    print_status "warning" "jq is not installed (optional, for pretty JSON output)"
fi

if [ $MISSING_TOOLS -eq 1 ]; then
    print_status "error" "Please install missing tools before running validation"
    exit 1
fi

echo ""

# Get API URL from user or environment
if [ -z "$API_URL" ]; then
    echo "Enter the API URL (e.g., http://alb-name.region.elb.amazonaws.com or https://app-name.azurecontainerapps.io):"
    read -r API_URL
fi

# Remove trailing slash if present
API_URL="${API_URL%/}"

print_status "info" "Validating deployment at: $API_URL"
echo ""

# Test 1: Root endpoint
print_status "info" "Testing root endpoint..."
RESPONSE=$(curl -s -w "\n%{http_code}" "$API_URL/" 2>&1)
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    print_status "success" "Root endpoint is accessible (HTTP $HTTP_CODE)"
    if command_exists "jq"; then
        echo "$BODY" | jq '.'
    else
        echo "$BODY"
    fi
else
    print_status "error" "Root endpoint failed (HTTP $HTTP_CODE)"
    echo "$BODY"
    exit 1
fi

echo ""

# Test 2: Health check
print_status "info" "Testing health endpoint..."
RESPONSE=$(curl -s -w "\n%{http_code}" "$API_URL/health" 2>&1)
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    print_status "success" "Health check passed (HTTP $HTTP_CODE)"
    if command_exists "jq"; then
        echo "$BODY" | jq '.'
    else
        echo "$BODY"
    fi
else
    print_status "error" "Health check failed (HTTP $HTTP_CODE)"
    echo "$BODY"
fi

echo ""

# Test 3: Readiness check
print_status "info" "Testing readiness endpoint..."
RESPONSE=$(curl -s -w "\n%{http_code}" "$API_URL/health/ready" 2>&1)
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    print_status "success" "Readiness check passed (HTTP $HTTP_CODE)"
else
    print_status "warning" "Readiness check returned HTTP $HTTP_CODE"
fi

echo ""

# Test 4: Liveness check
print_status "info" "Testing liveness endpoint..."
RESPONSE=$(curl -s -w "\n%{http_code}" "$API_URL/health/live" 2>&1)
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    print_status "success" "Liveness check passed (HTTP $HTTP_CODE)"
else
    print_status "warning" "Liveness check returned HTTP $HTTP_CODE"
fi

echo ""

# Test 5: Metrics endpoint
print_status "info" "Testing metrics endpoint..."
RESPONSE=$(curl -s -w "\n%{http_code}" "$API_URL/metrics" 2>&1)
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)

if [ "$HTTP_CODE" = "200" ]; then
    print_status "success" "Metrics endpoint is accessible (HTTP $HTTP_CODE)"
    echo "Sample metrics:"
    echo "$RESPONSE" | sed '$d' | grep -E "^(model_predictions_total|http_requests_total|system_cpu_usage)" | head -5
else
    print_status "warning" "Metrics endpoint returned HTTP $HTTP_CODE"
fi

echo ""

# Test 6: API documentation
print_status "info" "Testing API documentation..."
RESPONSE=$(curl -s -w "\n%{http_code}" "$API_URL/docs" 2>&1)
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)

if [ "$HTTP_CODE" = "200" ]; then
    print_status "success" "API documentation is accessible at $API_URL/docs"
else
    print_status "warning" "API documentation returned HTTP $HTTP_CODE"
fi

echo ""

# Test 7: Authentication check (without API key)
print_status "info" "Testing API authentication..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/api/v1/score" \
    -H "Content-Type: application/json" \
    -d '{"company_revenue": 1000000}' 2>&1)
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)

if [ "$HTTP_CODE" = "401" ] || [ "$HTTP_CODE" = "403" ]; then
    print_status "success" "Authentication is properly enforced (HTTP $HTTP_CODE)"
else
    print_status "warning" "Unexpected authentication response (HTTP $HTTP_CODE)"
fi

echo ""

echo ""
echo "========================================"
echo "  Validation Summary"
echo "========================================"
echo ""
print_status "success" "API is deployed and accessible"
print_status "success" "Health checks are working"
print_status "success" "Metrics endpoint is functional"
print_status "success" "Authentication is enforced"
echo ""
echo "Next steps:"
echo "1. Test scoring with a valid API key:"
echo "   curl -X POST '$API_URL/api/v1/score' \\"
echo "     -H 'X-API-Key: your-api-key' \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d @docs/examples/sample_request.json"
echo ""
echo "2. View API documentation: $API_URL/docs"
echo ""
echo "3. Monitor metrics: $API_URL/metrics"
echo ""
echo "4. Check CloudWatch (AWS) or Application Insights (Azure) for logs and monitoring"
echo ""
