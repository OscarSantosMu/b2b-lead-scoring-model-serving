output "api_url" {
  description = "API URL"
  value       = "https://${azurerm_container_app.main.ingress[0].fqdn}"
}

output "app_insights_connection_string" {
  description = "Application Insights connection string"
  value       = azurerm_application_insights.main.connection_string
  sensitive   = true
}

output "ml_workspace_name" {
  description = "ML Workspace name"
  value       = var.enable_azure_ml ? azurerm_machine_learning_workspace.main[0].name : null
}

output "resource_group_name" {
  description = "Resource group name"
  value       = azurerm_resource_group.main.name
}

output "container_registry_login_server" {
  description = "Container registry login server"
  value       = azurerm_container_registry.main.login_server
}
