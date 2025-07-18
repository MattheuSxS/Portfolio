resource "google_project_iam_member" "pubsub_bq_role" {
  project = var.project
  count   = length(var.roles_sa_pub_sub)
  role    = var.roles_sa_pub_sub[count.index]
  member  = "serviceAccount:service-${var.project_id}@gcp-sa-pubsub.iam.gserviceaccount.com"
}

resource "google_service_account" "creating_sa" {
  project     = var.project
  count       = length(var.creating_sa)
  account_id  = var.creating_sa[count.index]
  description = "Creating Service Account to project ${var.project}"

  lifecycle {
    prevent_destroy = false
  }
}

resource "google_project_iam_member" "roles_sa_dataflow" {
  project = var.project
  count   = length(var.roles_sa_dataflow)
  role    = var.roles_sa_dataflow[count.index]
  member  = "serviceAccount:${google_service_account.creating_sa[1].email}"
}

resource "google_project_iam_member" "roles_sa_cf_wh_sensor" {
  project = var.project
  count   = length(var.roles_sa_cf_wh_sensor)
  role    = var.roles_sa_cf_wh_sensor[count.index]
  member  = "serviceAccount:${google_service_account.creating_sa[3].email}"
}

resource "google_project_iam_member" "roles_sa_cf_feedback" {
  project = var.project
  count   = length(var.roles_sa_cf_feedback)
  role    = var.roles_sa_cf_feedback[count.index]
  member  = "serviceAccount:${google_service_account.creating_sa[6].email}"
}