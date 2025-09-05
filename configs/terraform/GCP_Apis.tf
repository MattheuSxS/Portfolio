resource "google_project_service" "Api_enabled" {
  project             = local.project
  count               = length(var.api_enabled)
  service             = var.api_enabled[count.index]
  disable_on_destroy  = false
}
