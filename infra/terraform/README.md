# Infrastructure as Code - Terraform

This directory contains Terraform configurations for deploying the B2B Lead Scoring API to AWS or Azure.

## Architecture

The infrastructure is designed with a modular approach, allowing deployment to either AWS or Azure based on configuration:

- **AWS Module**: ECS/Fargate + ALB + CloudWatch + Optional SageMaker
- **Azure Module**: Container Apps + Application Gateway + App Insights + Optional Azure ML

## Quick Start

### Prerequisites

1. **Terraform** >= 1.5
2. **Azure CLI** (for Azure deployments with OIDC)
3. **AWS CLI** (for AWS deployments)
4. **Storage Account for Terraform State** (Azure)

### Setup Backend

1. Create backend configuration:
```bash
cp backend.hcl.example backend.hcl
# Edit backend.hcl with your storage account details
```

2. Create tfvars file:
```bash
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your configuration
```

### Deploy to Azure

```bash
# Initialize Terraform
terraform init -backend-config=backend.hcl

# Plan deployment
terraform plan -var="cloud_provider=azure"

# Apply deployment
terraform apply -var="cloud_provider=azure"
```

### Deploy to AWS

```bash
# Initialize Terraform
terraform init -backend-config=backend.hcl

# Plan deployment
terraform plan -var="cloud_provider=aws"

# Apply deployment
terraform apply -var="cloud_provider=aws"
```

## Configuration

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `cloud_provider` | Cloud platform (`aws` or `azure`) | `azure` |
| `docker_image` | Docker image for API | `ghcr.io/org/api:latest` |
| `api_keys` | Comma-separated API keys | `key1,key2` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `environment` | Environment name | `dev` |
| `min_replicas` | Min instances/replicas | `2` |
| `max_replicas` | Max instances/replicas | `10` |
| `model_endpoint_provider` | `local`, `sagemaker`, or `azure` | `local` |

### Model Endpoint Configuration

#### Local Model (Default)
```hcl
model_endpoint_provider = "local"
```

#### AWS SageMaker
```hcl
cloud_provider              = "aws"
model_endpoint_provider     = "sagemaker"
enable_sagemaker_endpoint   = true
sagemaker_endpoint_name     = "lead-scoring-endpoint"
```

#### Azure ML
```hcl
cloud_provider          = "azure"
model_endpoint_provider = "azure"
enable_azure_ml         = true
azure_ml_endpoint_url   = "https://your-endpoint.azureml.net/score"
azure_ml_api_key        = "your-api-key"
```

## Module Structure

```
terraform/
├── main.tf              # Main configuration with provider and module calls
├── variables.tf         # Input variables
├── outputs.tf           # Output values
├── backend.hcl.example  # Backend configuration example
├── terraform.tfvars.example  # Variables example
└── modules/
    ├── aws/             # AWS-specific resources
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    └── azure/           # Azure-specific resources
        ├── main.tf
        ├── variables.tf
        └── outputs.tf
```

## Resources Created

### Azure Deployment

- Resource Group
- Virtual Network with subnets
- **Azure Container Registry (ACR)** - for Docker images
- Container App Environment
- Container App (auto-scaling 2-10 replicas)
- Application Insights
- Log Analytics Workspace
- Key Vault (for secrets)
- Optional: Azure ML Workspace
- Monitoring Alerts (CPU, Memory)

### AWS Deployment

- VPC with public/private subnets
- NAT Gateway (for private subnet internet access)
- Internet Gateway
- **Elastic Container Registry (ECR)** - for Docker images
- Application Load Balancer
- ECS Cluster (Fargate)
- ECS Service (auto-scaling 2-10 tasks)
- CloudWatch Log Group
- Secrets Manager (for API keys)
- IAM Roles and Policies (including ECR pull permissions)
- Optional: SageMaker endpoint access
- CloudWatch Alarms (CPU, Memory)

## CI/CD Integration

The infrastructure can be deployed using the GitHub Actions workflow:

```yaml
# .github/workflows/deploy-infrastructure.yml
```

### Workflow Triggers

1. **Manual Dispatch**: Deploy to specific environment
2. **Push to main**: Auto-deploy on infrastructure changes

### Required Secrets

Configure these in GitHub repository secrets:

**Azure Deployment:**
- `AZURE_CLIENT_ID` - Azure service principal client ID
- `AZURE_SUBSCRIPTION_ID` - Azure subscription ID
- `AZURE_TENANT_ID` - Azure tenant ID
- `TFSTATE_RESOURCE_GROUP` - Resource group for Terraform state
- `TFSTATE_STORAGE_ACCOUNT` - Storage account for Terraform state
- `TFSTATE_CONTAINER_NAME` - Container name for Terraform state
- `ACR_LOGIN_SERVER` - ACR login server (e.g., myregistry.azurecr.io)
- `ACR_USERNAME` - ACR admin username
- `ACR_PASSWORD` - ACR admin password

**AWS Deployment:**
- `AWS_ROLE_ARN` - AWS IAM role ARN for OIDC
- `AWS_REGION` - AWS region (default: us-east-1)
- `ECR_REGISTRY` - ECR registry URL (e.g., 123456789.dkr.ecr.us-east-1.amazonaws.com)
- `ECR_REPOSITORY` - ECR repository name (e.g., lead-scoring-dev)

**Common:**
- `API_KEYS` - Comma-separated API keys for the application
- `DOCKER_IMAGE` - Docker image path (for Terraform deployment)

## Backend State Management

Terraform state is stored in Azure Storage Account with OIDC authentication:

```hcl
terraform {
  backend "azurerm" {
    resource_group_name  = "tfstate-rg"
    storage_account_name = "tfstateleadscoring"
    container_name       = "tfstate"
    key                  = "dev/lead-scoring.tfstate"
    use_oidc             = true
  }
}
```

## Outputs

After deployment, Terraform outputs:

- `api_url`: API endpoint URL
- `deployed_cloud_provider`: Cloud provider used
- `container_registry_url`: Container registry URL (ECR or ACR)
- `ecr_repository_url`: AWS ECR repository URL (if AWS)
- `ecr_repository_name`: AWS ECR repository name (if AWS)
- `acr_login_server`: Azure ACR login server (if Azure)
- Cloud-specific outputs (log groups, workspace names, etc.)

### Using Container Registry Outputs

After deployment, push images to the appropriate registry:

**For AWS:**
```bash
# Get ECR login
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $(terraform output -raw ecr_repository_url)

# Tag and push
docker tag lead-scoring-api:latest $(terraform output -raw ecr_repository_url):latest
docker push $(terraform output -raw ecr_repository_url):latest
```

**For Azure:**
```bash
# Login to ACR
az acr login --name $(terraform output -raw acr_login_server | cut -d'.' -f1)

# Tag and push
docker tag lead-scoring-api:latest $(terraform output -raw acr_login_server)/lead-scoring:latest
docker push $(terraform output -raw acr_login_server)/lead-scoring:latest
```

## Cost Estimates

### Azure
- **Dev**: ~$65-100/month
- **Production**: ~$150-250/month

### AWS
- **Dev**: ~$96-120/month
- **Production**: ~$180-300/month

Costs include compute, networking, monitoring, and logging.

## Security

- Secrets stored in Key Vault (Azure) or Secrets Manager (AWS)
- Network isolation with VNet/VPC
- HTTPS/TLS encryption
- IAM/RBAC with least privilege
- Container security scanning

## Monitoring

Both deployments include:

- CPU and memory utilization alerts (threshold: 80%)
- Application performance monitoring
- Structured logging
- Auto-scaling based on metrics

## Troubleshooting

### Terraform Init Fails

Check backend configuration and Azure authentication:
```bash
az login
terraform init -backend-config=backend.hcl
```

### Plan Shows No Changes

Verify cloud_provider variable matches existing deployment:
```bash
terraform plan -var="cloud_provider=azure"
```

### State Lock Issues

Unlock state if needed:
```bash
terraform force-unlock <lock-id>
```

## Clean Up

```bash
# Destroy infrastructure
terraform destroy -var="cloud_provider=azure"
```

## Additional Resources

- [Terraform Azure Provider](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/)
- [AWS ECS Fargate](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/AWS_Fargate.html)
