terraform {
  required_version = ">= 1.5"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.80"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "azurerm" {
    # Backend configuration will be provided via backend config file or CLI
    # Example: terraform init -backend-config=backend.hcl
    use_oidc = true
  }
}

# Provider configuration - only one will be used based on cloud_provider variable
provider "azurerm" {
  features {
    key_vault {
      # CI/CD apply-destroy-apply-destroy for DEV ENV only
      # 1) DO NOT purge on destroy → keep soft delete as a safety net
      purge_soft_delete_on_destroy = false

      # 2) On next apply, if a soft-deleted KV with same name exists → recover it instead of erroring
      recover_soft_deleted_key_vaults = true
    }
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }

  skip_provider_registration = true
}

provider "aws" {
  region = var.aws_region

  # Skip validation when not deploying to AWS to avoid credential errors
  skip_credentials_validation = var.cloud_provider != "aws"
  skip_requesting_account_id  = var.cloud_provider != "aws"
  skip_metadata_api_check     = var.cloud_provider != "aws"
  skip_region_validation      = var.cloud_provider != "aws"
}

# Data sources
data "azurerm_client_config" "current" {
  count = var.cloud_provider == "azure" ? 1 : 0
}

# Local variables
locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Azure Resources
module "azure" {
  count  = var.cloud_provider == "azure" ? 1 : 0
  source = "./modules/azure"

  project_name            = var.project_name
  environment             = var.environment
  location                = var.azure_location
  docker_image            = var.docker_image
  api_keys                = var.api_keys
  log_level               = var.log_level
  min_replicas            = var.min_replicas
  max_replicas            = var.max_replicas
  model_endpoint_provider = var.model_endpoint_provider
  enable_azure_ml         = var.enable_azure_ml
  azure_ml_endpoint_url   = var.azure_ml_endpoint_url
  azure_ml_api_key        = var.azure_ml_api_key

  tags = local.common_tags
}

# AWS Resources
module "aws" {
  count  = var.cloud_provider == "aws" ? 1 : 0
  source = "./modules/aws"

  project_name              = var.project_name
  environment               = var.environment
  aws_region                = var.aws_region
  docker_image              = var.docker_image
  api_keys                  = var.api_keys
  log_level                 = var.log_level
  min_instances             = var.min_replicas
  max_instances             = var.max_replicas
  model_endpoint_provider   = var.model_endpoint_provider
  enable_sagemaker_endpoint = var.enable_sagemaker_endpoint
  sagemaker_endpoint_name   = var.sagemaker_endpoint_name

  tags = local.common_tags
}
