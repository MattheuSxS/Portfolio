# resource "google_service_account" "creating_sa" {
#     project     = local.project
#     count       = length(var.creating_sa)
#     account_id  = var.creating_sa[count.index]
#     description = "Creating Service Account to project ${local.project}"

#     lifecycle {
#         prevent_destroy = false
#     }
# }


# resource "google_project_iam_member" "roles_sa_pubsub" {
#     project = local.project
#     count   = length(var.roles_sa_pub_sub)
#     role    = var.roles_sa_pub_sub[count.index]
#     member  = "serviceAccount:service-${local.project_id}@gcp-sa-pubsub.iam.gserviceaccount.com"
# }


# resource "google_project_iam_member" "roles_sa_composer" {
#     project = local.project
#     count   = length(var.roles_sa_composer)
#     role    = var.roles_sa_composer[count.index]
#     member  = "serviceAccount:${local.sa_composer}"
# }


# resource "google_project_iam_member" "roles_sa_dataflow" {
#     project = local.project
#     count   = length(var.roles_sa_dataflow)
#     role    = var.roles_sa_dataflow[count.index]
#     member  = "serviceAccount:${local.sa_dataflow}"
# }


# resource "google_project_iam_member" "roles_sa_cf_default" {
#     project = local.project
#     count   = length(var.roles_sa_cf_default)
#     role    = var.roles_sa_cf_default[count.index]
#     member  = "serviceAccount:${local.sa_cf_default}"
# }


# resource "google_project_iam_member" "roles_sa_cf_pb_sensor" {
#     project = local.project
#     count   = length(var.roles_sa_cf_pb_sensor)
#     role    = var.roles_sa_cf_pb_sensor[count.index]
#     member  = "serviceAccount:${local.sa_cf_pb_sensor}"
# }


# resource "google_project_iam_member" "roles_sa_default_compute" {
#     project = local.project
#     count   = length(var.roles_sa_default_compute)
#     role    = var.roles_sa_default_compute[count.index]
#     member  = "serviceAccount:${local.project_id}-compute@developer.gserviceaccount.com"
# }

# # resource "google_cloud_run_v2_service_iam_member" "dashboard_invoker" {
# #     project  = local.project
# #     location = google_cloud_run_v2_service.logistream_dashboard.location
# #     name     = google_cloud_run_v2_service.logistream_dashboard.name
# #     role     = "roles/run.invoker"
# #     member   = "allUsers"
# # }

# resource "google_project_iam_member" "roles_sa_cloud_run" {
#     project = local.project
#     count   = length(var.roles_sa_cloud_run)
#     role    = var.roles_sa_cloud_run[count.index]
#     member  = "serviceAccount:${local.sa_cloud_run}"
# }