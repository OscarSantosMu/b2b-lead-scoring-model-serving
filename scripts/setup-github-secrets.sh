#!/bin/bash
# GitHub Secrets Setup Helper
# Helps configure required secrets for CI/CD deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}!${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

echo "========================================"
echo "  GitHub Secrets Setup Helper"
echo "========================================"
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    print_error "GitHub CLI (gh) is not installed"
    echo ""
    echo "Please install it from: https://cli.github.com/"
    echo ""
    echo "Or use the GitHub web interface:"
    echo "  Settings → Secrets and variables → Actions → New repository secret"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    print_error "Not authenticated with GitHub CLI"
    echo ""
    echo "Please run: gh auth login"
    exit 1
fi

print_success "GitHub CLI is installed and authenticated"
echo ""

# Get repository information
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || echo "")

if [ -z "$REPO" ]; then
    print_error "Not in a GitHub repository or unable to detect repository"
    echo ""
    echo "Please run this script from within your repository"
    exit 1
fi

print_info "Repository: $REPO"
echo ""

# Ask which cloud provider
echo "Which cloud provider do you want to configure?"
echo "1) Azure"
echo "2) AWS"
echo "3) Both"
read -rp "Enter choice (1-3): " CLOUD_CHOICE

echo ""

# Common secrets
print_info "Setting up common secrets..."
echo ""

read -rp "Enter API keys (comma-separated): " API_KEYS
if [ -n "$API_KEYS" ]; then
    gh secret set API_KEYS --body "$API_KEYS" --repo "$REPO"
    print_success "Set API_KEYS"
fi

echo ""

# Azure setup
if [ "$CLOUD_CHOICE" = "1" ] || [ "$CLOUD_CHOICE" = "3" ]; then
    print_info "Setting up Azure secrets..."
    echo ""
    
    echo "Azure Service Principal details (from az ad sp create-for-rbac):"
    read -rp "AZURE_CLIENT_ID: " AZURE_CLIENT_ID
    read -rp "AZURE_SUBSCRIPTION_ID: " AZURE_SUBSCRIPTION_ID
    read -rp "AZURE_TENANT_ID: " AZURE_TENANT_ID
    
    if [ -n "$AZURE_CLIENT_ID" ]; then
        gh secret set AZURE_CLIENT_ID --body "$AZURE_CLIENT_ID" --repo "$REPO"
        print_success "Set AZURE_CLIENT_ID"
    fi
    
    if [ -n "$AZURE_SUBSCRIPTION_ID" ]; then
        gh secret set AZURE_SUBSCRIPTION_ID --body "$AZURE_SUBSCRIPTION_ID" --repo "$REPO"
        print_success "Set AZURE_SUBSCRIPTION_ID"
    fi
    
    if [ -n "$AZURE_TENANT_ID" ]; then
        gh secret set AZURE_TENANT_ID --body "$AZURE_TENANT_ID" --repo "$REPO"
        print_success "Set AZURE_TENANT_ID"
    fi
    
    echo ""
    echo "Terraform state storage account details:"
    read -rp "TFSTATE_RESOURCE_GROUP: " TFSTATE_RESOURCE_GROUP
    read -rp "TFSTATE_STORAGE_ACCOUNT: " TFSTATE_STORAGE_ACCOUNT
    read -rp "TFSTATE_CONTAINER_NAME (default: tfstate): " TFSTATE_CONTAINER_NAME
    TFSTATE_CONTAINER_NAME=${TFSTATE_CONTAINER_NAME:-tfstate}
    
    if [ -n "$TFSTATE_RESOURCE_GROUP" ]; then
        gh secret set TFSTATE_RESOURCE_GROUP --body "$TFSTATE_RESOURCE_GROUP" --repo "$REPO"
        print_success "Set TFSTATE_RESOURCE_GROUP"
    fi
    
    if [ -n "$TFSTATE_STORAGE_ACCOUNT" ]; then
        gh secret set TFSTATE_STORAGE_ACCOUNT --body "$TFSTATE_STORAGE_ACCOUNT" --repo "$REPO"
        print_success "Set TFSTATE_STORAGE_ACCOUNT"
    fi
    
    if [ -n "$TFSTATE_CONTAINER_NAME" ]; then
        gh secret set TFSTATE_CONTAINER_NAME --body "$TFSTATE_CONTAINER_NAME" --repo "$REPO"
        print_success "Set TFSTATE_CONTAINER_NAME"
    fi
    
    echo ""
    echo "Azure Container Registry (ACR) details:"
    read -rp "ACR_LOGIN_SERVER (e.g., myregistry.azurecr.io): " ACR_LOGIN_SERVER
    read -rp "ACR_USERNAME: " ACR_USERNAME
    read -rsp "ACR_PASSWORD: " ACR_PASSWORD
    echo ""
    
    if [ -n "$ACR_LOGIN_SERVER" ]; then
        gh secret set ACR_LOGIN_SERVER --body "$ACR_LOGIN_SERVER" --repo "$REPO"
        print_success "Set ACR_LOGIN_SERVER"
    fi
    
    if [ -n "$ACR_USERNAME" ]; then
        gh secret set ACR_USERNAME --body "$ACR_USERNAME" --repo "$REPO"
        print_success "Set ACR_USERNAME"
    fi
    
    if [ -n "$ACR_PASSWORD" ]; then
        gh secret set ACR_PASSWORD --body "$ACR_PASSWORD" --repo "$REPO"
        print_success "Set ACR_PASSWORD"
    fi
    
    echo ""
fi

# AWS setup
if [ "$CLOUD_CHOICE" = "2" ] || [ "$CLOUD_CHOICE" = "3" ]; then
    print_info "Setting up AWS secrets..."
    echo ""
    
    echo "AWS IAM Role for GitHub OIDC:"
    read -rp "AWS_ROLE_ARN (e.g., arn:aws:iam::123456789:role/GitHubActionsRole): " AWS_ROLE_ARN
    read -rp "AWS_REGION (default: us-east-1): " AWS_REGION
    AWS_REGION=${AWS_REGION:-us-east-1}
    
    if [ -n "$AWS_ROLE_ARN" ]; then
        gh secret set AWS_ROLE_ARN --body "$AWS_ROLE_ARN" --repo "$REPO"
        print_success "Set AWS_ROLE_ARN"
    fi
    
    if [ -n "$AWS_REGION" ]; then
        gh secret set AWS_REGION --body "$AWS_REGION" --repo "$REPO"
        print_success "Set AWS_REGION"
    fi
    
    echo ""
    echo "AWS Elastic Container Registry (ECR) details:"
    read -rp "ECR_REGISTRY (e.g., 123456789.dkr.ecr.us-east-1.amazonaws.com): " ECR_REGISTRY
    read -rp "ECR_REPOSITORY (e.g., lead-scoring-dev): " ECR_REPOSITORY
    
    if [ -n "$ECR_REGISTRY" ]; then
        gh secret set ECR_REGISTRY --body "$ECR_REGISTRY" --repo "$REPO"
        print_success "Set ECR_REGISTRY"
    fi
    
    if [ -n "$ECR_REPOSITORY" ]; then
        gh secret set ECR_REPOSITORY --body "$ECR_REPOSITORY" --repo "$REPO"
        print_success "Set ECR_REPOSITORY"
    fi
    
    echo ""
fi

echo ""
echo "========================================"
print_success "Secrets setup complete!"
echo "========================================"
echo ""
echo "To verify secrets were set, run:"
echo "  gh secret list --repo $REPO"
echo ""
echo "Next steps:"
echo "1. Push code to trigger CI/CD pipeline"
echo "2. Run 'Deploy Infrastructure' workflow from GitHub Actions"
echo "3. Monitor deployment in GitHub Actions tab"
echo ""
echo "For detailed instructions, see:"
echo "  docs/CICD_GUIDE.md"
echo ""
