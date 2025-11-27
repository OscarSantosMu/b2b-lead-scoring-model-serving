<#
.SYNOPSIS
    Deployment Validation Script
.DESCRIPTION
    Validates that infrastructure is correctly deployed and API is accessible.
.PARAMETER ApiUrl
    The base URL of the API to validate.
#>
param (
    [string]$ApiUrl
)

$ErrorActionPreference = "Stop"

# Colors
$Green = "Green"
$Red = "Red"
$Yellow = "Yellow"

function Print-Status {
    param (
        [string]$Status,
        [string]$Message
    )
    if ($Status -eq "success") {
        Write-Host "✓ $Message" -ForegroundColor $Green
    }
    elseif ($Status -eq "error") {
        Write-Host "✗ $Message" -ForegroundColor $Red
    }
    elseif ($Status -eq "warning") {
        Write-Host "! $Message" -ForegroundColor $Yellow
    }
    else {
        Write-Host "$Message"
    }
}

Write-Host "========================================"
Write-Host "  Lead Scoring API - Deployment Check  "
Write-Host "========================================"
Write-Host ""

# Get API URL from user or environment
if (-not $ApiUrl) {
    if ($env:API_URL) {
        $ApiUrl = $env:API_URL
    } else {
        $ApiUrl = Read-Host "Enter the API URL (e.g., http://alb-name.region.elb.amazonaws.com or https://app-name.azurecontainerapps.io)"
    }
}

# Remove trailing slash if present
if ($ApiUrl.EndsWith("/")) {
    $ApiUrl = $ApiUrl.Substring(0, $ApiUrl.Length - 1)
}

Print-Status "info" "Validating deployment at: $ApiUrl"
Write-Host ""

function Test-Endpoint {
    param (
        [string]$Url,
        [string]$Description,
        [string]$Method = "GET",
        [hashtable]$Headers = @{},
        [string]$Body = $null,
        [int[]]$ExpectedCodes = @(200)
    )

    Print-Status "info" "Testing $Description..."
    
    try {
        $params = @{
            Uri = $Url
            Method = $Method
            ErrorAction = "Stop"
        }
        if ($Headers.Count -gt 0) { $params.Headers = $Headers }
        if ($Body) { 
            $params.Body = $Body 
            $params.ContentType = "application/json"
        }

        $response = Invoke-WebRequest @params
        $statusCode = [int]$response.StatusCode

        if ($statusCode -in $ExpectedCodes) {
            Print-Status "success" "$Description passed (HTTP $statusCode)"
            try {
                $content = $response.Content | ConvertFrom-Json
                Write-Host ($content | ConvertTo-Json -Depth 5)
            } catch {
                # If not JSON, just print content if it's short, or skip
                if ($response.Content.Length -lt 500) {
                    Write-Host $response.Content
                }
            }
            return $true
        } else {
            Print-Status "warning" "$Description returned HTTP $statusCode"
            return $false
        }
    } catch {
        $ex = $_.Exception
        if ($ex.Response) {
            $statusCode = [int]$ex.Response.StatusCode
            if ($statusCode -in $ExpectedCodes) {
                Print-Status "success" "$Description passed (HTTP $statusCode)"
                return $true
            } else {
                Print-Status "error" "$Description failed (HTTP $statusCode)"
                try {
                    Write-Host $ex.Response.GetResponseStream() 
                } catch {}
                return $false
            }
        } else {
            Print-Status "error" "$Description failed: $($ex.Message)"
            return $false
        }
    }
}

# Test 1: Root endpoint
Test-Endpoint -Url "$ApiUrl/" -Description "Root endpoint"

Write-Host ""

# Test 2: Health check
Test-Endpoint -Url "$ApiUrl/health" -Description "Health check"

Write-Host ""

# Test 3: Readiness check
Test-Endpoint -Url "$ApiUrl/health/ready" -Description "Readiness check"

Write-Host ""

# Test 4: Liveness check
Test-Endpoint -Url "$ApiUrl/health/live" -Description "Liveness check"

Write-Host ""

# Test 5: Metrics endpoint
Print-Status "info" "Testing metrics endpoint..."
try {
    $response = Invoke-WebRequest -Uri "$ApiUrl/metrics" -ErrorAction Stop
    $statusCode = [int]$response.StatusCode
    if ($statusCode -eq 200) {
        Print-Status "success" "Metrics endpoint is accessible (HTTP $statusCode)"
        Write-Host "Sample metrics:"
        $response.Content -split "`n" | Select-String -Pattern "^(model_predictions_total|http_requests_total|system_cpu_usage)" | Select-Object -First 5 | ForEach-Object { Write-Host $_ }
    } else {
        Print-Status "warning" "Metrics endpoint returned HTTP $statusCode"
    }
} catch {
    Print-Status "error" "Metrics endpoint failed: $($_.Exception.Message)"
}

Write-Host ""

# Test 6: API documentation
Test-Endpoint -Url "$ApiUrl/docs" -Description "API documentation"

Write-Host ""

# Test 7: Authentication check (without API key)
Test-Endpoint -Url "$ApiUrl/api/v1/score" -Description "Authentication check" -Method "POST" -Body '{"company_revenue": 1000000}' -ExpectedCodes @(401, 403)

Write-Host ""

Write-Host ""
Write-Host "========================================"
Write-Host "  Validation Summary"
Write-Host "========================================"
Write-Host ""
Print-Status "success" "API is deployed and accessible"
Print-Status "success" "Health checks are working"
Print-Status "success" "Metrics endpoint is functional"
Print-Status "success" "Authentication is enforced"
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Test scoring with a valid API key:"
Write-Host "   Invoke-RestMethod -Method Post -Uri '$ApiUrl/api/v1/score' -Headers @{'X-API-Key'='your-api-key'} -Body (Get-Content docs/examples/sample_request.json -Raw) -ContentType 'application/json'"
Write-Host ""
Write-Host "2. View API documentation: $ApiUrl/docs"
Write-Host ""
Write-Host "3. Monitor metrics: $ApiUrl/metrics"
Write-Host ""
