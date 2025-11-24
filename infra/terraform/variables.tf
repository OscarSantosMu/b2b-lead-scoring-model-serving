# Cloud Provider Selection
variable "cloud_provider" {
  description = "Cloud provider to deploy to: 'aws' or 'azure'"
  type        = string
  validation {
    condition     = contains(["aws", "azure"], var.cloud_provider)
    error_message = "Cloud provider must be either 'aws' or 'azure'."
  }
}

# Common Variables
variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "lead-scoring"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "docker_image" {
  description = "Docker image for the API service"
  type        = string
}

variable "api_keys" {
  description = "Comma-separated list of API keys"
  type        = string
  sensitive   = true
}

# Scaling Configuration
variable "min_replicas" {
  description = "Minimum number of replicas/instances"
  type        = number
  default     = 2
}

variable "max_replicas" {
  description = "Maximum number of replicas/instances"
  type        = number
  default     = 10
}

# Model Endpoint Configuration
variable "model_endpoint_provider" {
  description = "Model endpoint provider: 'local', 'sagemaker', or 'azure'"
  type        = string
  default     = "local"
  validation {
    condition     = contains(["local", "sagemaker", "azure"], var.model_endpoint_provider)
    error_message = "Model endpoint provider must be 'local', 'sagemaker', or 'azure'."
  }
}

# AWS-specific Variables
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "enable_sagemaker_endpoint" {
  description = "Whether to provision SageMaker endpoint resources"
  type        = bool
  default     = false
}

variable "sagemaker_endpoint_name" {
  description = "Name of the SageMaker endpoint (if using existing)"
  type        = string
  default     = ""
}

# Azure-specific Variables
variable "azure_location" {
  description = "Azure region"
  type        = string
  default     = "East US"
}

variable "enable_azure_ml" {
  description = "Whether to provision Azure ML workspace resources"
  type        = bool
  default     = false
}

variable "azure_ml_endpoint_url" {
  description = "Azure ML endpoint URL (if using existing)"
  type        = string
  default     = ""
  sensitive   = true
}

variable "azure_ml_api_key" {
  description = "Azure ML endpoint API key (if using existing)"
  type        = string
  default     = ""
  sensitive   = true
}
