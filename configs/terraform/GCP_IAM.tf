resource "google_service_account" "creating_sa" {
    project     = local.project
    count       = length(var.creating_sa)
    account_id  = var.creating_sa[count.index]
    description = "Creating Service Account to project ${local.project}"

    lifecycle {
        prevent_destroy = false
    }
}


resource "google_project_iam_member" "pubsub_bq_role" {
    project = local.project
    count   = length(var.roles_sa_pub_sub)
    role    = var.roles_sa_pub_sub[count.index]
    member  = "serviceAccount:service-${local.project_id}@gcp-sa-pubsub.iam.gserviceaccount.com"
}


resource "google_project_iam_member" "roles_sa_composer" {
    project = local.project
    count   = length(var.roles_sa_composer)
    role    = var.roles_sa_composer[count.index]
    member  = "serviceAccount:${local.sa_composer}"
}


# resource "google_project_iam_member" "data_tools_roles_sa_composer" {
#     project = local.project_data_tools
#     count   = length(var.roles_sa_composer)
#     role    = var.roles_sa_composer[count.index]
#     member  = "serviceAccount:${local.sa_composer}"
# }


resource "google_project_iam_member" "roles_sa_dataflow" {
    project = local.project
    count   = length(var.roles_sa_dataflow)
    role    = var.roles_sa_dataflow[count.index]
    member  = "serviceAccount:${local.sa_dataflow}"
}


resource "google_project_iam_member" "roles_sa_cf_default" {
    project = local.project
    count   = length(var.roles_sa_cf_default)
    role    = var.roles_sa_cf_default[count.index]
    member  = "serviceAccount:${local.sa_cf_default}"
}


resource "google_project_iam_member" "roles_sa_cf_pb_sensor" {
    project = local.project
    count   = length(var.roles_sa_cf_pb_sensor)
    role    = var.roles_sa_cf_pb_sensor[count.index]
    member  = "serviceAccount:${local.sa_cf_pb_sensor}"
}


resource "google_project_iam_member" "roles_sa_default_compute" {
    project = local.project
    count   = length(var.roles_sa_default_compute)
    role    = var.roles_sa_default_compute[count.index]
    member  = "serviceAccount:${local.project_id}-compute@developer.gserviceaccount.com"
}


# resource "google_project_iam_member" "data_tools_roles_sa_default_compute" {
#     project = local.project_data_tools
#     count   = length(var.roles_sa_default_compute)
#     role    = var.roles_sa_default_compute[count.index]
#     member  = "serviceAccount:${local.project_data_tools_id}-compute@developer.gserviceaccount.com"
# }