# resource "google_project_service" "Api_enabled" {
#   project             = var.project[terraform.workspace]
#   count               = length(var.api_enabled)
#   service             = var.api_enabled[count.index]
#   disable_on_destroy  = false
# }
