variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "location" {
  description = "Azure region"
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

variable "log_level" {
  description = "Logging level"
  type        = string
}

variable "min_replicas" {
  description = "Minimum replicas"
  type        = number
}

variable "max_replicas" {
  description = "Maximum replicas"
  type        = number
}

variable "model_endpoint_provider" {
  description = "Model endpoint provider"
  type        = string
}

variable "enable_azure_ml" {
  description = "Enable Azure ML workspace"
  type        = bool
}

variable "azure_ml_endpoint_url" {
  description = "Azure ML endpoint URL"
  type        = string
  default     = ""
}

variable "azure_ml_api_key" {
  description = "Azure ML API key"
  type        = string
  default     = ""
  sensitive   = true
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
}
