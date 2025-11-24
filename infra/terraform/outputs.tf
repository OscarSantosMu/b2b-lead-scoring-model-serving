# Azure Outputs
output "azure_api_url" {
  description = "Azure API endpoint URL"
  value       = var.cloud_provider == "azure" ? module.azure[0].api_url : null
}

output "azure_app_insights_connection_string" {
  description = "Azure Application Insights connection string"
  value       = var.cloud_provider == "azure" ? module.azure[0].app_insights_connection_string : null
  sensitive   = true
}

output "azure_ml_workspace_name" {
  description = "Azure ML Workspace name"
  value       = var.cloud_provider == "azure" && var.enable_azure_ml ? module.azure[0].ml_workspace_name : null
}

# AWS Outputs
output "aws_api_url" {
  description = "AWS API endpoint URL"
  value       = var.cloud_provider == "aws" ? module.aws[0].api_url : null
}

output "aws_cloudwatch_log_group" {
  description = "CloudWatch log group name"
  value       = var.cloud_provider == "aws" ? module.aws[0].cloudwatch_log_group : null
}

output "aws_sagemaker_endpoint_name" {
  description = "SageMaker endpoint name"
  value       = var.cloud_provider == "aws" && var.enable_sagemaker_endpoint ? module.aws[0].sagemaker_endpoint_name : null
}

# Common Outputs
output "deployed_cloud_provider" {
  description = "The cloud provider that was deployed to"
  value       = var.cloud_provider
}

output "api_url" {
  description = "API endpoint URL"
  value       = var.cloud_provider == "azure" ? module.azure[0].api_url : module.aws[0].api_url
}

# Container Registry Outputs
output "container_registry_url" {
  description = "Container registry URL"
  value       = var.cloud_provider == "azure" ? module.azure[0].container_registry_login_server : module.aws[0].ecr_repository_url
}

output "ecr_repository_url" {
  description = "AWS ECR repository URL"
  value       = var.cloud_provider == "aws" ? module.aws[0].ecr_repository_url : null
}

output "ecr_repository_name" {
  description = "AWS ECR repository name"
  value       = var.cloud_provider == "aws" ? module.aws[0].ecr_repository_name : null
}

output "acr_login_server" {
  description = "Azure Container Registry login server"
  value       = var.cloud_provider == "azure" ? module.azure[0].container_registry_login_server : null
}
