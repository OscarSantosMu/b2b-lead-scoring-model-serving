variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "docker_image" {
  description = "Docker image for the API"
  type        = string
}

variable "api_keys" {
  description = "API keys"
  type        = string
  sensitive   = true
}

variable "min_instances" {
  description = "Minimum instances"
  type        = number
}

variable "max_instances" {
  description = "Maximum instances"
  type        = number
}

variable "model_endpoint_provider" {
  description = "Model endpoint provider"
  type        = string
}

variable "enable_sagemaker_endpoint" {
  description = "Enable SageMaker endpoint"
  type        = bool
}

variable "sagemaker_endpoint_name" {
  description = "SageMaker endpoint name"
  type        = string
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
}
